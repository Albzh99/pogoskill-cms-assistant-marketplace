param(
  [Parameter(Mandatory = $true)][ValidatePattern('^/cms/[a-z0-9/_-]+$')][string]$Path,
  [Parameter(Mandatory = $true)][string]$BodyPath,
  [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CmsCredential.ps1')
$apiKey = [string](Get-CmsStoredApiKey)
if ([string]::IsNullOrWhiteSpace($apiKey)) { throw 'Stored CMS credential not found. Run cms-save-api-key.ps1 first.' }

$body = [IO.Path]::GetFullPath($BodyPath)
if (-not (Test-Path -LiteralPath $body -PathType Leaf)) { throw "JSON body not found: $body" }
try { Get-Content -Raw -Encoding UTF8 -LiteralPath $body | ConvertFrom-Json | Out-Null }
catch { throw "Body is not valid JSON: $body" }

$curlCommand = Get-Command curl.exe -ErrorAction SilentlyContinue | Select-Object -First 1
$curl = if ($curlCommand) { $curlCommand.Source } else { 'C:\Windows\System32\curl.exe' }
if (-not (Test-Path -LiteralPath $curl -PathType Leaf)) { throw 'curl.exe was not found.' }

$responsePath = Join-Path $env:TEMP ('pogoskill-cms-response-' + [guid]::NewGuid().ToString('N') + '.json')
try {
  & $curl -sS --fail-with-body --connect-timeout 20 --max-time 90 -X POST `
    ('https://gw.afirstsoft.com' + $Path) `
    -H ("X-API-KEY: $apiKey") `
    -H 'Accept: application/json' `
    -H 'Content-Type: application/json; charset=utf-8' `
    --data-binary ('@' + $body) -o $responsePath
  if ($LASTEXITCODE -ne 0) { throw "CMS transport error on ${Path}: curl exit=$LASTEXITCODE" }
  $raw = [IO.File]::ReadAllText($responsePath, [Text.Encoding]::UTF8)
  $response = $raw | ConvertFrom-Json
  if ($null -eq $response.code -or [int]$response.code -ne 0) {
    throw "CMS business error on ${Path}: code=$($response.code), request_id=$($response.request_id), msg=$($response.msg)"
  }
  if ($OutputPath) {
    $resolvedOutput = [IO.Path]::GetFullPath($OutputPath)
    [IO.File]::WriteAllText($resolvedOutput, ($response | ConvertTo-Json -Depth 80), (New-Object Text.UTF8Encoding($false)))
  }
  $response | ConvertTo-Json -Depth 80
}
finally {
  $apiKey = $null
  Remove-Item -LiteralPath $responsePath -Force -ErrorAction SilentlyContinue
}
