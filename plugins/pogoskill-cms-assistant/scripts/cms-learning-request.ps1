param(
  [Parameter(Mandatory = $true)][string]$Path,
  [Parameter(Mandatory = $true)][string]$BodyPath,
  [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
# Only documented CMS lookup endpoints belong here. Never add a write/publish endpoint.
$readOnlyPaths = @(
  '/cms/site/list',
  '/cms/page/list',
  '/cms/page/info',
  '/cms/page/fields',
  '/cms/page/templatefield',
  '/cms/template/list',
  '/cms/template/fields',
  '/cms/templatefield/list',
  '/cms/author/list',
  '/cms/author/info',
  '/cms/author/select',
  '/cms/classify/displayclassifylist',
  '/cms/product/list',
  '/cms/product/info',
  '/cms/module/list',
  '/cms/module/info',
  '/cms/module/sidebar',
  '/cms/sidebar/list',
  '/cms/sidebar/info',
  '/cms/sidebar/select',
  '/cms/picture/list',
  '/cms/picture/dirs',
  '/cms/file/list'
)
if ($Path -cnotin $readOnlyPaths) {
  throw "Learning mode is read-only; endpoint not allowed: $Path"
}

$arguments = @{ Path = $Path; BodyPath = $BodyPath }
if ($OutputPath) { $arguments.OutputPath = $OutputPath }
& (Join-Path $PSScriptRoot 'cms-request.ps1') @arguments
