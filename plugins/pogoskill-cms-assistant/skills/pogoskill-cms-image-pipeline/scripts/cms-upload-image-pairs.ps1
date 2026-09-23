param(
  [Parameter(Mandatory = $true)][string]$ManifestPath,
  [Parameter(Mandatory = $true)][ValidatePattern('^[a-z0-9/_-]*$')][string]$CmsPath,
  [ValidateSet(286, 324)][int]$SiteId = 324,
  [switch]$Execute
)

$ErrorActionPreference = 'Stop'
if (-not $Execute) { throw 'Dry run only. Re-run with -Execute only after the current article image upload is explicitly authorized.' }

$manifestFile = [IO.Path]::GetFullPath($ManifestPath)
if (-not (Test-Path -LiteralPath $manifestFile -PathType Leaf)) { throw "Manifest not found: $manifestFile" }
$manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json

$credentialScript = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\scripts\CmsCredential.ps1'))
if (-not (Test-Path -LiteralPath $credentialScript -PathType Leaf)) { throw 'Plugin credential helper was not found.' }
. $credentialScript
$apiKey = Get-CmsStoredApiKey
if ([string]::IsNullOrWhiteSpace($apiKey)) { throw 'Stored CMS credential not found.' }
$curlCommand = Get-Command curl.exe -ErrorAction SilentlyContinue | Select-Object -First 1
$curl = if ($curlCommand) { $curlCommand.Source } else { 'C:\Windows\System32\curl.exe' }
if (-not (Test-Path -LiteralPath $curl -PathType Leaf)) { throw 'curl.exe was not found.' }

function Invoke-CmsJson([string]$Path, [hashtable]$Body) {
  $requestBody = Join-Path $env:TEMP ('cms-image-json-' + [guid]::NewGuid().ToString('N') + '.json')
  $responseBody = Join-Path $env:TEMP ('cms-image-json-response-' + [guid]::NewGuid().ToString('N') + '.json')
  try {
    [IO.File]::WriteAllText($requestBody, ($Body | ConvertTo-Json -Depth 10 -Compress), (New-Object Text.UTF8Encoding($false)))
    @("X-API-KEY: $apiKey", 'Accept: application/json', 'Content-Type: application/json; charset=utf-8') |
      & $curl -k -sS -X POST ('https://gw.afirstsoft.com' + $Path) -H '@-' --data-binary ('@' + $requestBody) -o $responseBody
    if ($LASTEXITCODE -ne 0) { throw "Transport error on ${Path}: curl exit=$LASTEXITCODE" }
    return [IO.File]::ReadAllText($responseBody, [Text.Encoding]::UTF8) | ConvertFrom-Json
  }
  finally {
    Remove-Item -LiteralPath $requestBody -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $responseBody -Force -ErrorAction SilentlyContinue
  }
}

function Test-UploadedUrl([string]$Url) {
  if ([string]::IsNullOrWhiteSpace($Url) -or $Url -notmatch '^https://') { return $false }
  $status = & $curl -k -sS -L --range '0-0' -o NUL -w '%{http_code}' $Url
  return ($LASTEXITCODE -eq 0 -and $status -in @('200', '206'))
}

function Get-PublicImageUrl([object]$UploadedFile, [object]$ListedFile, [int]$Width, [int]$Height) {
  $expectedPrefix = if ($SiteId -eq 324) { 'https://tw.pogoskill.com/images/' } else { 'https://images.pogoskill.com/' }
  $candidates = @([string]$UploadedFile.url, [string]$ListedFile.online)
  $url = $candidates | Where-Object {
    -not [string]::IsNullOrWhiteSpace($_) -and
    $_.StartsWith($expectedPrefix) -and
    $_ -notmatch 'site\.p\.cms\.afirstsoft\.cn|[?&]attachment=1'
  } | Select-Object -First 1
  if ([string]::IsNullOrWhiteSpace($url)) {
    throw "CMS response did not provide a valid public URL for $($UploadedFile.name); expected prefix $expectedPrefix"
  }
  if ($url -notmatch '[?&]w=') {
    $separator = if ($url.Contains('?')) { '&' } else { '?' }
    $url = $url + $separator + 'w=' + $Width + '&h=' + $Height
  }
  return $url
}

try {
  $dirResponse = Invoke-CmsJson '/cms/picture/dirs' @{ site_id = $SiteId; path = $CmsPath; tree = 0 }
  if ($dirResponse.code -ne 0) { throw "CMS image directory check failed: code=$($dirResponse.code), request_id=$($dirResponse.request_id), msg=$($dirResponse.msg)" }

  foreach ($item in $manifest.items) {
    foreach ($path in @($item.fallback_path, $item.webp_path)) {
      if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required image missing: $path" }
      $file = Get-Item -LiteralPath $path
      if ($file.Length -le 0 -or $file.Length -gt 31457280) { throw "Image size is invalid: $path" }
      if ($file.Name -cnotmatch '^[a-z0-9-_\.]{4,255}$') { throw "CMS filename is invalid: $($file.Name)" }
      if ($file.BaseName -match '-[0-9a-f]{10}$') { throw "Public filename must not end with a checksum: $($file.Name)" }
    }
    if ([string]::IsNullOrWhiteSpace($item.alt)) { throw "ALT is required before upload: $($item.image_key)" }
    if ([int]$item.width -ne [int]$item.webp_width -or [int]$item.height -ne [int]$item.webp_height) {
      throw "Local fallback and WebP dimensions differ for $($item.image_key)"
    }
  }

  foreach ($item in $manifest.items) {
    $existingResponse = Invoke-CmsJson '/cms/picture/list' @{ site_id = $SiteId; path = $CmsPath; type = 'file' }
    if ($existingResponse.code -ne 0) {
      throw "CMS picture list preflight failed: code=$($existingResponse.code), request_id=$($existingResponse.request_id), msg=$($existingResponse.msg)"
    }
    $existingFiles = @($existingResponse.data.list | ForEach-Object { @($_.fileChildren) })
    $existingFallback = $existingFiles | Where-Object { $_.name -eq $item.fallback_name } | Select-Object -First 1
    $existingWebp = $existingFiles | Where-Object { $_.name -eq $item.webp_name } | Select-Object -First 1
    if (($existingFallback -and -not $existingWebp) -or ($existingWebp -and -not $existingFallback)) {
      throw "Only one format already exists for $($item.image_key); do not upload or overwrite until the conflict is resolved."
    }
    if ($existingFallback -and $existingWebp) {
      if ([int]$existingFallback.w -ne [int]$item.width -or [int]$existingFallback.h -ne [int]$item.height -or
          [int]$existingWebp.w -ne [int]$item.width -or [int]$existingWebp.h -ne [int]$item.height) {
        throw "Existing CMS pair dimensions differ for $($item.image_key); do not overwrite."
      }
      $fallbackReadable = Test-UploadedUrl ([string]$existingFallback.upload)
      $webpReadable = Test-UploadedUrl ([string]$existingWebp.upload)
      if (-not $fallbackReadable -or -not $webpReadable) {
        throw "Existing CMS upload URL is not readable for $($item.image_key)"
      }
      $item | Add-Member -NotePropertyName fallback_upload_url -NotePropertyValue $existingFallback.upload -Force
      $item | Add-Member -NotePropertyName webp_upload_url -NotePropertyValue $existingWebp.upload -Force
      $item | Add-Member -NotePropertyName fallback_public_url -NotePropertyValue (Get-PublicImageUrl $existingFallback $existingFallback ([int]$item.width) ([int]$item.height)) -Force
      $item | Add-Member -NotePropertyName webp_public_url -NotePropertyValue (Get-PublicImageUrl $existingWebp $existingWebp ([int]$item.width) ([int]$item.height)) -Force
      $item | Add-Member -NotePropertyName site_id -NotePropertyValue $SiteId -Force
      $item | Add-Member -NotePropertyName cms_path -NotePropertyValue $CmsPath -Force
      $item | Add-Member -NotePropertyName fallback_url_readable -NotePropertyValue $fallbackReadable -Force
      $item | Add-Member -NotePropertyName webp_url_readable -NotePropertyValue $webpReadable -Force
      $item | Add-Member -NotePropertyName public_url_http_required_for_draft -NotePropertyValue $false -Force
      $item | Add-Member -NotePropertyName public_url_state_note -NotePropertyValue 'Frontend 404 is expected before image publication and does not block CMS draft HTML.' -Force
      $item | Add-Member -NotePropertyName list_request_id -NotePropertyValue $existingResponse.request_id -Force
      $item.status = 'reused_existing'
      continue
    }

    $responsePath = Join-Path $env:TEMP ('cms-image-upload-' + [guid]::NewGuid().ToString('N') + '.json')
    try {
      $formArgs = @(
        '-k', '-sS', '-X', 'POST', 'https://gw.afirstsoft.com/cms/picture/upload',
        '-H', '@-',
        '-F', ('site_id=' + $SiteId),
        '-F', ('path=' + $CmsPath),
        '-F', ('files[]=@' + $item.fallback_path),
        '-F', ('files[]=@' + $item.webp_path),
        '-o', $responsePath
      )
      @("X-API-KEY: $apiKey", 'Accept: application/json') | & $curl @formArgs
      if ($LASTEXITCODE -ne 0) { throw "Upload transport error for $($item.image_key): curl exit=$LASTEXITCODE" }
      $response = [IO.File]::ReadAllText($responsePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    finally {
      Remove-Item -LiteralPath $responsePath -Force -ErrorAction SilentlyContinue
    }

    if ($response.code -ne 0) { throw "CMS upload failed for $($item.image_key): code=$($response.code), request_id=$($response.request_id), msg=$($response.msg)" }
    if ([int]$response.data.total -ne 2 -or @($response.data.err_name_files).Count -ne 0) {
      throw "CMS did not accept both files for $($item.image_key); request_id=$($response.request_id)"
    }
    $files = @($response.data.list)
    $fallback = $files | Where-Object { $_.name -eq $item.fallback_name } | Select-Object -First 1
    $webp = $files | Where-Object { $_.name -eq $item.webp_name } | Select-Object -First 1
    if (-not $fallback -or -not $webp) { throw "Upload response is missing a paired file for $($item.image_key)" }
    if ([int]$fallback.w -ne [int]$webp.w -or [int]$fallback.h -ne [int]$webp.h) {
      throw "Uploaded dimensions differ for $($item.image_key)"
    }
    $fallbackReadable = Test-UploadedUrl ([string]$fallback.upload)
    $webpReadable = Test-UploadedUrl ([string]$webp.upload)
    if (-not $fallbackReadable -or -not $webpReadable) {
      throw "At least one uploaded preview URL is not readable for $($item.image_key)"
    }

    $listResponse = Invoke-CmsJson '/cms/picture/list' @{ site_id = $SiteId; path = $CmsPath; type = 'file' }
    if ($listResponse.code -ne 0) {
      throw "CMS picture list verification failed: code=$($listResponse.code), request_id=$($listResponse.request_id), msg=$($listResponse.msg)"
    }
    $listedFiles = @($listResponse.data.list | ForEach-Object { @($_.fileChildren) })
    $listedFallback = $listedFiles | Where-Object { $_.name -eq $item.fallback_name } | Select-Object -First 1
    $listedWebp = $listedFiles | Where-Object { $_.name -eq $item.webp_name } | Select-Object -First 1
    if (-not $listedFallback -or -not $listedWebp) { throw "Uploaded pair is missing from picture/list for $($item.image_key)" }
    if ([int]$listedFallback.w -ne [int]$item.width -or [int]$listedFallback.h -ne [int]$item.height -or
        [int]$listedWebp.w -ne [int]$item.width -or [int]$listedWebp.h -ne [int]$item.height) {
      throw "picture/list dimensions differ from local files for $($item.image_key)"
    }

    $item | Add-Member -NotePropertyName upload_request_id -NotePropertyValue $response.request_id -Force
    $item | Add-Member -NotePropertyName publish_id -NotePropertyValue $response.data.publish_id -Force
    $item | Add-Member -NotePropertyName fallback_upload_url -NotePropertyValue $fallback.upload -Force
    $item | Add-Member -NotePropertyName webp_upload_url -NotePropertyValue $webp.upload -Force
    $item | Add-Member -NotePropertyName fallback_public_url -NotePropertyValue (Get-PublicImageUrl $fallback $listedFallback ([int]$item.width) ([int]$item.height)) -Force
    $item | Add-Member -NotePropertyName webp_public_url -NotePropertyValue (Get-PublicImageUrl $webp $listedWebp ([int]$item.width) ([int]$item.height)) -Force
    $item | Add-Member -NotePropertyName site_id -NotePropertyValue $SiteId -Force
    $item | Add-Member -NotePropertyName cms_path -NotePropertyValue $CmsPath -Force
    $item | Add-Member -NotePropertyName fallback_url_readable -NotePropertyValue $fallbackReadable -Force
    $item | Add-Member -NotePropertyName webp_url_readable -NotePropertyValue $webpReadable -Force
    $item | Add-Member -NotePropertyName public_url_http_required_for_draft -NotePropertyValue $false -Force
    $item | Add-Member -NotePropertyName public_url_state_note -NotePropertyValue 'Frontend 404 is expected before image publication and does not block CMS draft HTML.' -Force
    $item | Add-Member -NotePropertyName list_request_id -NotePropertyValue $listResponse.request_id -Force
    $item | Add-Member -NotePropertyName fallback_online_url -NotePropertyValue $listedFallback.online -Force
    $item | Add-Member -NotePropertyName webp_online_url -NotePropertyValue $listedWebp.online -Force
    $item.status = 'uploaded_pending_publish'
  }

  $manifest | Add-Member -NotePropertyName site_id -NotePropertyValue $SiteId -Force
  $manifest | Add-Member -NotePropertyName uploaded_at -NotePropertyValue ([DateTimeOffset]::Now.ToString('o')) -Force
  [IO.File]::WriteAllText($manifestFile, ($manifest | ConvertTo-Json -Depth 16), (New-Object Text.UTF8Encoding($false)))
  [pscustomobject]@{
    manifest = $manifestFile
    uploaded_pairs = @($manifest.items | Where-Object status -eq 'uploaded_pending_publish').Count
    reused_pairs = @($manifest.items | Where-Object status -eq 'reused_existing').Count
    note = 'Existing pairs were reused; new pairs are pending records only. Nothing was published.'
  }
}
finally {
  $apiKey = $null
}
