from dotenv import load_dotenv
from inventory_manager_app.logging import configure_logging
from inventory_manager_app import create_app

load_dotenv()

configure_logging()
app = create_app()

if __name__ == "__main__":
    app.run()
