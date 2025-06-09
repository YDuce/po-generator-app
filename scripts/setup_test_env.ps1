# PowerShell script to set up Python 3.11 environment
$ErrorActionPreference = "Stop"

# Check if Python 3.11 is installed
$pythonVersion = python --version
if (-not $pythonVersion.Contains("3.11")) {
    Write-Host "Please install Python 3.11.8 from https://www.python.org/downloads/release/python-3118/"
    Write-Host "After installation, run this script again."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Environment setup complete!" 