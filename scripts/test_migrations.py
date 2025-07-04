"""Test migration chain on in-memory database."""

import sys

from sqlalchemy import create_engine, event
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext


def test_migrations() -> None:
    """Test the migration chain on an in-memory database."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create Alembic configuration
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    # Get the script directory
    script = ScriptDirectory.from_config(alembic_cfg)

    # Get all revisions
    revisions = list(script.walk_revisions())
    revisions.reverse()  # Start from oldest

    try:
        # Create initial tables
        with engine.begin() as connection:
            context = MigrationContext.configure(connection)
            context.run_migrations()

        # Run migrations
        print("Running migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration upgrade successful")

        # Test downgrade
        print("\nTesting downgrade...")
        command.downgrade(alembic_cfg, "-1")
        print("✅ Migration downgrade successful")

        # Test upgrade again
        print("\nTesting upgrade after downgrade...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration upgrade successful after downgrade")

        # Verify final state
        print("\nVerifying final state...")
        with engine.connect() as connection:
            result = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in result]
            print(f"Found tables: {', '.join(tables)}")

    except Exception as e:
        print(f"❌ Migration test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    test_migrations()
