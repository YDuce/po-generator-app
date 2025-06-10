"""Test script to verify authentication setup."""

import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_service_account() -> None:
    """Test service account credentials."""
    # Load environment variables
    load_dotenv()
    
    # Get service account path
    svc_key_path = os.getenv('GOOGLE_SVC_KEY')
    if not svc_key_path:
        print("❌ GOOGLE_SVC_KEY not found in .env")
        return
    
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            svc_key_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Test Drive API
        drive_service = build('drive', 'v3', credentials=credentials)
        about = drive_service.about().get(fields='user').execute()
        print(f"✅ Service account working! Email: {about['user']['emailAddress']}")
        
    except Exception as e:
        print(f"❌ Service account error: {str(e)}")

def test_oauth_config() -> None:
    """Test OAuth configuration."""
    # Load environment variables
    load_dotenv()
    
    # Check OAuth credentials
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ OAuth credentials not found in .env")
        return
    
    print("✅ OAuth credentials found")
    print(f"Client ID: {client_id[:10]}...")
    print(f"Client Secret: {client_secret[:10]}...")

if __name__ == '__main__':
    print("Testing authentication setup...")
    print("\n1. Testing Service Account:")
    test_service_account()
    
    print("\n2. Testing OAuth Configuration:")
    test_oauth_config() 