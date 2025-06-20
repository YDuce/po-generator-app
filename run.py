# run.py ─ dev-only launcher
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"), override=False)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
