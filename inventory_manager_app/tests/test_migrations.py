# pragma: no cover
from pathlib import Path
from alembic.config import Config
from alembic import command
import os
from uuid import uuid4
from sqlalchemy_utils import create_database, drop_database
from sqlalchemy.engine.url import make_url


def test_upgrade_and_downgrade(tmp_path: Path) -> None:
    """Ensure migrations upgrade and downgrade."""
    base_url = os.environ.get("APP_DATABASE_URL")
    if not base_url:
        base_url = f"sqlite:///{tmp_path}/app.db"
    url = make_url(base_url)

    if url.drivername.startswith("sqlite"):
        test_path = tmp_path / f"test_mig_{uuid4().hex}.db"
        test_url = make_url(f"sqlite:///{test_path}")
    else:
        test_db = (
            f"{url.database}_mig_{uuid4().hex}"
            if url.database
            else f"test_{uuid4().hex}"
        )
        test_url = url.set(database=test_db)
        create_database(str(test_url))
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(test_url))
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
    if not test_url.drivername.startswith("sqlite"):
        drop_database(str(test_url))
