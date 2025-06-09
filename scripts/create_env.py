"""Create .env file with all necessary configuration."""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with all necessary configuration."""
    # Get the service account path
    service_account_path = 'config/inventory-manager-461101-1cc498327e1a.json'
    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found at: {service_account_path}")
        return

    # Create .env file
    env_path = Path('.env')
    with open(env_path, 'w') as f:
        f.write('# Flask Configuration\n')
        f.write('FLASK_APP=app:create_app\n')
        f.write('FLASK_ENV=development\n')
        f.write('SECRET_KEY=your-secret-key-here\n')
        
        f.write('\n# Database Configuration\n')
        f.write('DATABASE_URL=sqlite:///app.db\n')
        
        f.write('\n# Google OAuth Configuration\n')
        f.write('GOOGLE_CLIENT_ID=your-client-id-here\n')
        f.write('GOOGLE_CLIENT_SECRET=your-client-secret-here\n')
        f.write('GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback/google\n')
        
        f.write('\n# Google Service Account\n')
        f.write(f'GOOGLE_SVC_KEY={service_account_path}\n')
        
        f.write('\n# JWT Configuration\n')
        f.write('JWT_SECRET_KEY=your-jwt-secret-key-here\n')
        f.write('JWT_ACCESS_TOKEN_EXPIRES=3600\n')
        
        f.write('\n# Application Settings\n')
        f.write('DEBUG=True\n')
        f.write('TESTING=False\n')

    print("\n✅ .env file created!")
    print("\nPlease update the following values in your .env file:")
    print("1. SECRET_KEY - Generate a secure key")
    print("2. GOOGLE_CLIENT_ID - Your Google OAuth client ID")
    print("3. GOOGLE_CLIENT_SECRET - Your Google OAuth client secret")
    print("4. JWT_SECRET_KEY - Generate a secure key")
    print("\nTo generate secure keys, run:")
    print("python scripts/generate_keys.py")

if __name__ == '__main__':
    create_env_file() 