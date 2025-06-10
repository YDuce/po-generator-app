"""Set up complete environment configuration."""

import os
from pathlib import Path
from generate_keys import generate_keys

def setup_environment() -> None:
    """Set up complete environment configuration."""
    # First, generate the secret keys
    generate_keys()
    
    # Get the service account path
    service_account_path = 'config/inventory-manager-461101-1cc498327e1a.json'
    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found at: {service_account_path}")
        return
    
    # Get OAuth credentials from user
    print("\nPlease enter your Google OAuth credentials:")
    client_id = input("Google Client ID: ").strip()
    client_secret = input("Google Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Secret are required")
        return
    
    # Create/update .env file
    env_path = Path('.env')
    with open(env_path, 'a') as f:
        f.write(f'\n# Flask Configuration\n')
        f.write('FLASK_APP=app:create_app\n')
        f.write('FLASK_ENV=development\n')
        
        f.write(f'\n# Database Configuration\n')
        f.write('DATABASE_URL=sqlite:///app.db\n')
        
        f.write(f'\n# Google OAuth Configuration\n')
        f.write(f'GOOGLE_CLIENT_ID={client_id}\n')
        f.write(f'GOOGLE_CLIENT_SECRET={client_secret}\n')
        f.write('GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback/google\n')
        
        f.write(f'\n# Google Service Account\n')
        f.write(f'GOOGLE_SVC_KEY={service_account_path}\n')
    
    print("\n✅ Environment setup complete!")
    print("Your .env file has been created/updated with all necessary configuration.")
    print("\nTo verify the setup, run:")
    print("python scripts/test_auth.py")

if __name__ == '__main__':
    setup_environment() 