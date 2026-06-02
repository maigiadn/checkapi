$env:PROXY_TARGET = "https://apikey.maivangia.com"
$env:PROXY_PORT = "18080"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

node .\model-proxy.js
