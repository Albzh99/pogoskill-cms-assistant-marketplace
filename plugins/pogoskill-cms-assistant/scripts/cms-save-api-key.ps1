param(
  [Alias('ApiKeyFromClipboard')][switch]$FromClipboard,
  [switch]$Prompt,
  [switch]$KeepClipboard
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CmsCredential.ps1')

$keyPtr = [IntPtr]::Zero
$apiKey = $null
try {
  if ($Prompt) {
    $secureKey = Read-Host 'CMS API key' -AsSecureString
    $keyPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $apiKey = ([Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPtr)).Trim()
  }
  else {
    if (-not $FromClipboard) {
      Write-Host ''
      Write-Host '请现在复制完整的 CMS API Key。'
      [void](Read-Host '复制完成后，回到这个窗口直接按 Enter')
    }
    $apiKey = ([string](Get-Clipboard -Raw)).Trim()
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
      throw 'Clipboard is empty. Copy the complete CMS API key before pressing Enter, then try again.'
    }
  }

  Set-CmsStoredApiKey -ApiKey $apiKey
  if (-not $KeepClipboard) { Set-Clipboard -Value ' ' }
  Write-Host 'CMS API key saved securely in Windows Credential Manager.'
  if (-not $KeepClipboard) { Write-Host 'Clipboard cleared.' }
}
finally {
  if ($keyPtr -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPtr)
  }
  $apiKey = $null
}

