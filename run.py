# run.py
import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app

# Always load .env for both direct runs and scripts that import this module
dotenv_path = Path(__file__).with_name(".env")
if not load_dotenv(dotenv_path):
    print(f"Warning: no .env found at {dotenv_path}")

# Pick config via FLASK_CONFIG or default to development
app = create_app(os.getenv("FLASK_CONFIG", "development"))

if __name__ == "__main__":
    # Rely on app.config for debug
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )