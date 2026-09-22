param(
  [Parameter(Mandatory = $true)][string]$InputHtml,
  [Parameter(Mandatory = $true)][string]$ManifestPath,
  [Parameter(Mandatory = $true)][string]$OutputHtml
)

$ErrorActionPreference = 'Stop'
$inputFile = [IO.Path]::GetFullPath($InputHtml)
$manifestFile = [IO.Path]::GetFullPath($ManifestPath)
$outputFile = [IO.Path]::GetFullPath($OutputHtml)
if ($inputFile -eq $outputFile) { throw 'OutputHtml must be a new file; inspect it before replacing any draft source.' }
if (-not (Test-Path -LiteralPath $inputFile -PathType Leaf)) { throw "HTML not found: $inputFile" }
if (-not (Test-Path -LiteralPath $manifestFile -PathType Leaf)) { throw "Manifest not found: $manifestFile" }

$html = Get-Content -LiteralPath $inputFile -Raw -Encoding UTF8
$manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($item in $manifest.items) {
  if ($item.status -ne 'uploaded_pending_publish') { throw "Image is not uploaded and verified: $($item.image_key)" }
  foreach ($required in @('image_key','alt','fallback_upload_url','webp_upload_url','max_width')) {
    if ([string]::IsNullOrWhiteSpace([string]$item.$required)) { throw "Manifest field missing for $($item.image_key): $required" }
  }
  $escapedKey = [regex]::Escape([string]$item.image_key)
  $pattern = '(?s)<div class="img-wrap text-center">\s*<!--\s*IMAGE_PENDING(?:(?!-->).)*?image-key:\s*' + $escapedKey + '(?:(?!-->).)*?-->\s*</div>'
  $matches = [regex]::Matches($html, $pattern)
  if ($matches.Count -ne 1) { throw "Expected exactly one placeholder for $($item.image_key), found $($matches.Count)." }

  $alt = [Net.WebUtility]::HtmlEncode([string]$item.alt)
  $webpUrl = [Net.WebUtility]::HtmlEncode([string]$item.webp_upload_url)
  $fallbackUrl = [Net.WebUtility]::HtmlEncode([string]$item.fallback_upload_url)
  $maxWidth = [int]$item.max_width
  if ($maxWidth -le 0 -or $maxWidth -gt [int]$item.width) { throw "Invalid max_width for $($item.image_key)" }
  $block = @"
<div class="img-wrap text-center">
  <picture>
    <source class="lozad img-fluid"
            srcset="$webpUrl"
            data-srcset="$webpUrl"
            type="image/webp">
    <img class="lozad img-fluid"
         src="$fallbackUrl"
         data-src="$fallbackUrl"
         alt="$alt"
         style="max-width:${maxWidth}px;width:100%;height:auto;">
  </picture>
</div>
"@
  $html = [regex]::Replace($html, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($m) $block }, 1)
}

if ($html -match '<!--\s*IMAGE_PENDING(?:(?!-->).)*?image-key:\s*(?:' + (($manifest.items.image_key | ForEach-Object {[regex]::Escape($_)}) -join '|') + ')') {
  throw 'At least one manifest placeholder remains after replacement.'
}
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputFile)) | Out-Null
[IO.File]::WriteAllText($outputFile, $html, (New-Object Text.UTF8Encoding($false)))
[pscustomobject]@{ output = $outputFile; replaced = @($manifest.items).Count }

