"""Verify application setup and environment variables."""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'FLASK_APP',
        'FLASK_ENV',
        'SECRET_KEY',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'FRONTEND_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("All required environment variables are set.")
    return True

def check_database():
    """Check if database file exists and is accessible."""
    db_path = Path('app/app.db')
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return True
    
    try:
        # Try to open the file
        with open(db_path, 'a'):
            pass
        print("Database file exists and is accessible.")
        return True
    except Exception as e:
        print(f"Error accessing database file: {e}")
        return False

def check_google_credentials():
    """Check if Google OAuth credentials are properly configured."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or client_id == 'your-google-client-id':
        print("Google Client ID not properly configured.")
        return False
    
    if not client_secret or client_secret == 'your-google-client-secret':
        print("Google Client Secret not properly configured.")
        return False
    
    print("Google OAuth credentials are configured.")
    return True

def main():
    """Run all checks."""
    print("Verifying application setup...")
    
    checks = [
        ("Environment Variables", check_environment),
        ("Database", check_database),
        ("Google OAuth", check_google_credentials)
    ]
    
    all_passed = True
    for name, check in checks:
        print(f"\nChecking {name}...")
        if not check():
            all_passed = False
    
    if all_passed:
        print("\nAll checks passed! The application is properly configured.")
    else:
        print("\nSome checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main() 