import os
from pathlib import Path

import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine


@pytest.mark.skipif("POSTGRES_URL" not in os.environ, reason="Postgres not available")
def test_upgrade_and_downgrade(tmp_path: Path) -> None:
    """Ensure migrations upgrade and downgrade on Postgres."""
    url = os.environ["POSTGRES_URL"]
    engine = create_engine(url)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
    engine.dispose()
