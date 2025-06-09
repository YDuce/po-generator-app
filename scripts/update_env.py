"""Update service account path in .env file."""

import os
from pathlib import Path

def update_service_account_path():
    """Update the service account path in .env file."""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        return

    # Read current .env file
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update service account path
    new_lines = []
    for line in lines:
        if line.startswith('GOOGLE_SVC_KEY='):
            new_lines.append('GOOGLE_SVC_KEY=config/inventory-manager-461101-1cc498327e1a.json\n')
        else:
            new_lines.append(line)

    # Write updated content back to .env
    with open(env_path, 'w') as f:
        f.writelines(new_lines)

    print("✅ Service account path updated in .env file")
    print("\nTo verify the changes, run:")
    print("python scripts/test_auth.py")

if __name__ == '__main__':
    update_service_account_path() 