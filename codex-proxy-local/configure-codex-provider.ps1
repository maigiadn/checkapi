param(
    [string]$ProviderUrl = "https://apikey.maivangia.com",
    [string]$ApiKey = "",
    [string]$Model = "cx/gpt-5.5",
    [int]$ProxyPort = 18080
)

function Prompt-ForInput {
    param(
        [string]$Message,
        [string]$Default = "",
        [bool]$Secret = $false
    )

    if ($Secret) {
        $result = Read-Host "$Message" -AsSecureString
        return [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($result))
    }

    if ([string]::IsNullOrWhiteSpace($Default)) {
        return Read-Host "$Message"
    }
    return Read-Host "$Message [$Default]" | ForEach-Object { if ([string]::IsNullOrWhiteSpace($_)) { $Default } else { $_ } }
}

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    $ApiKey = Prompt-ForInput -Message "Enter your OPENAI_API_KEY" -Secret $true
}

if ([string]::IsNullOrWhiteSpace($ProviderUrl) -or $ProviderUrl -eq "https://provider.example.com") {
    $ProviderUrl = Prompt-ForInput -Message "Enter your provider URL" -Default $ProviderUrl
}

if ([string]::IsNullOrWhiteSpace($ProviderUrl)) {
    Write-Error "Provider URL is required."
    exit 1
}

$home = $HOME
if (-not $home) { $home = $env:USERPROFILE }
$codexDir = Join-Path $home ".codex"
$configFile = Join-Path $codexDir "config.toml"

if (-not (Test-Path $codexDir)) {
    New-Item -ItemType Directory -Path $codexDir -Force | Out-Null
}

if (Test-Path $configFile) {
    $backupFile = "$configFile.backup.$((Get-Date).ToString('yyyyMMddHHmmss'))"
    Copy-Item -Path $configFile -Destination $backupFile -Force
    Write-Host "Backed up existing config to $backupFile"
}

$configText = @"
model_provider = "maivangia"
model = "$Model"
model_reasoning_effort = "medium"

[model_providers.maivangia]
name = "Mai Van Gia Provider"
base_url = "http://127.0.0.1:$ProxyPort/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
"@

Set-Content -Path $configFile -Value $configText -Encoding UTF8
Write-Host "Created/updated codex config at $configFile"

Write-Host "Setting persistent environment variables for current Windows user..."
[Environment]::SetEnvironmentVariable('OPENAI_BASE_URL', "http://127.0.0.1:$ProxyPort/v1", 'User')
[Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $ApiKey, 'User')

Write-Host "Environment variables set for the user. You may need to restart VS Code."
Write-Host "To start the proxy, run this in PowerShell from the repository folder:"
Write-Host "  $env:PROXY_TARGET = '$ProviderUrl'"
Write-Host "  $env:PROXY_PORT = '$ProxyPort'"
Write-Host "  node .\model-proxy.js"

Write-Host "If you want the proxy to always forward to your provider, you can also create a permanent environment variable in Windows with the same values."
