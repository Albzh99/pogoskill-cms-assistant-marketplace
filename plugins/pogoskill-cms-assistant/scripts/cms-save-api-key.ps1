param(
  [switch]$ApiKeyFromClipboard
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CmsCredential.ps1')

$keyPtr = [IntPtr]::Zero
$apiKey = $null
try {
  if ($ApiKeyFromClipboard) {
    Write-Host 'Copy the full CMS API key now, then return to this window and press Enter.'
    Read-Host | Out-Null
    $apiKey = ([string](Get-Clipboard -Raw)).Trim()
  }
  else {
    $secureKey = Read-Host 'CMS API key' -AsSecureString
    $keyPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $apiKey = ([Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPtr)).Trim()
  }

  Set-CmsStoredApiKey -ApiKey $apiKey
  Set-Clipboard -Value ' '
  Write-Host 'CMS API key saved securely in Windows Credential Manager; clipboard cleared.'
}
finally {
  if ($keyPtr -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPtr)
  }
  $apiKey = $null
}

