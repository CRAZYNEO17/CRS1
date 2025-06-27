#!/usr/bin/env pwsh

Write-Host "Starting Agri-Wiz Flask Application in Development Mode..." -ForegroundColor Green

# Set environment variables for development
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "True"

# Display environment info
Write-Host "Environment: $env:FLASK_ENV" -ForegroundColor Yellow
Write-Host "Debug Mode: $env:FLASK_DEBUG" -ForegroundColor Yellow

# Run the Flask application
try {
    python app.py
} catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
}

# Keep the window open in case of error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
