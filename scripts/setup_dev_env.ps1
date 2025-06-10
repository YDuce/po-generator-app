#!/bin/bash
set -e

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..."
    @"
# Flask
FLASK_APP=app.main:create_app
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/po_generator

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback/google

# Frontend
FRONTEND_URL=http://localhost:3000

# Two-way sync
TWO_WAY_SYNC_ENABLED=false
"@ | Out-File -FilePath .env -Encoding UTF8
}

# Initialize git hooks
git config core.hooksPath .githooks

Write-Host "Development environment setup complete!" 