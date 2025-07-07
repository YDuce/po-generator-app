from inventory_manager_app.logging import configure_logging
from inventory_manager_app import create_app

configure_logging()
app = create_app()

if __name__ == "__main__":
    app.run()
