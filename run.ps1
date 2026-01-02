# Simple run script for SEO-GEO-AEO API with Frontend

Write-Host "🚀 Starting SEO-GEO-AEO API with Frontend..." -ForegroundColor Cyan
Write-Host ""

# Navigate to the correct directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\project\project"

# Check if we're in the right place
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)"
    exit 1
}

# Check if dependencies are installed
try {
    python -c "import fastapi" 2>$null
} catch {
    Write-Host "⚠️  Installing dependencies..." -ForegroundColor Yellow
    pip install --user -r ..\requirements.txt
}

# Start the server
Write-Host "✅ Starting server on http://localhost:8001" -ForegroundColor Green
Write-Host "📱 Frontend will be available at http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 API docs at http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py
