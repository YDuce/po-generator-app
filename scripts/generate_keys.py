"""Generate secure keys for Flask and JWT."""

import secrets
from pathlib import Path


def generate_keys() -> None:
    """Generate secure keys and update .env file."""
    # Generate keys
    flask_secret = secrets.token_hex(32)
    jwt_secret = secrets.token_hex(32)

    print("\nGenerated Keys:")
    print(f"Flask Secret Key: {flask_secret}")
    print(f"JWT Secret Key: {jwt_secret}")

    # Check if .env exists
    env_path = Path(".env")
    if env_path.exists():
        print("\nFound existing .env file. Adding/updating keys...")
        with open(env_path, "r") as f:
            lines = f.readlines()

        # Update or add keys
        flask_key_found = False
        jwt_key_found = False

        for i, line in enumerate(lines):
            if line.startswith("SECRET_KEY="):
                lines[i] = f"SECRET_KEY={flask_secret}\n"
                flask_key_found = True
            elif line.startswith("JWT_SECRET_KEY="):
                lines[i] = f"JWT_SECRET_KEY={jwt_secret}\n"
                jwt_key_found = True

        # Add missing keys
        if not flask_key_found:
            lines.append(f"SECRET_KEY={flask_secret}\n")
        if not jwt_key_found:
            lines.append(f"JWT_SECRET_KEY={jwt_secret}\n")

        # Write back to file
        with open(env_path, "w") as f:
            f.writelines(lines)
    else:
        print("\nCreating new .env file...")
        with open(env_path, "w") as f:
            f.write(f"SECRET_KEY={flask_secret}\n")
            f.write(f"JWT_SECRET_KEY={jwt_secret}\n")

    print("\n✅ Keys have been generated and added to .env file")
    print(
        "Make sure to keep these keys secure and never commit them to version control!"
    )


if __name__ == "__main__":
    generate_keys()
