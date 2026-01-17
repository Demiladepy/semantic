# PowerShell installation script for PNP SDK npm package

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PNP SDK Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed." -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Navigate to plugin directory
$PLUGIN_DIR = "plugin-polymarket"

if (-not (Test-Path $PLUGIN_DIR)) {
    Write-Host "❌ Directory $PLUGIN_DIR not found" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing pnp-sdk package..." -ForegroundColor Cyan
Set-Location $PLUGIN_DIR

# Install the package
npm install pnp-sdk

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ pnp-sdk installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Get your API key from PNP Exchange (when available)"
    Write-Host "2. Set PNP_API_KEY environment variable"
    Write-Host "3. Use the SDK with: use_nodejs_sdk=True in PNPSDKAdapter"
    Write-Host ""
    Write-Host "See INSTALL_PNP_SDK.md for more details." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Installation failed. Check the error messages above." -ForegroundColor Red
    exit 1
}

