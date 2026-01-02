# Quick Setup Script for SEO-GEO-AEO API with Azure AI Foundry
# This script automates the initial project setup

$ErrorActionPreference = "Stop"

Write-Host "🚀 SEO-GEO-AEO API - Quick Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

# Install root dependencies
Write-Host ""
Write-Host "Installing root dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Root dependencies installed" -ForegroundColor Green

# Install project dependencies
Write-Host ""
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
pip install -r project/requirements.txt --quiet
Write-Host "✓ Project dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host ""
Write-Host "Installing Playwright browsers (this may take a while)..." -ForegroundColor Yellow
playwright install chromium
Write-Host "✓ Playwright browsers installed" -ForegroundColor Green

# Install Node.js dependencies
Write-Host ""
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
Push-Location project/scripts
npm install --silent
Pop-Location
Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Setting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
} else {
    Copy-Item .env.example .env
    Write-Host "✓ .env file created from template" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env file and add your Azure OpenAI credentials!" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @("project/temp", "project/unlighthouse", "project/artifacts")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your Azure OpenAI credentials" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test Azure AI Foundry integration:" -ForegroundColor White
Write-Host "   python run_model.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run the API server:" -ForegroundColor White
Write-Host "   cd project" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access the API at:" -ForegroundColor White
Write-Host "   http://localhost:8001" -ForegroundColor Cyan
Write-Host "   http://localhost:8001/docs (API documentation)" -ForegroundColor Cyan
Write-Host ""
Write-Host "For deployment to Azure, see AZURE_DEPLOYMENT.md" -ForegroundColor Yellow
Write-Host ""
