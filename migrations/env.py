"""
Alembic migration environment, tweaked for Flask-SQLAlchemy **and** a
separate DeclarativeBase (BaseModel).

Changes from the stock template:
• target_metadata now merges db.Model.metadata *and* BaseModel.metadata
• keeps process_revision_directives guard to suppress empty revs
"""
from __future__ import annotations

import logging
from logging.config import fileConfig
from typing import Iterable

from alembic import context
from flask import current_app
from sqlalchemy.orm import DeclarativeMeta

# -------------------------------------------------------------------- setup
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# ----------------------------------------------------------------- helpers
def _get_engine():
    """Works with Flask-SQLAlchemy 2.x and 3.x."""
    try:  # Flask-SQLAlchemy < 3
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine


def _merged_metadata() -> Iterable[DeclarativeMeta]:
    """Return a list of MetaData objects for autogenerate."""
    db = current_app.extensions["migrate"].db

    metas = [db.metadata]

    # Pull in BaseModel.metadata (DeclarativeBase)
    from app.core.models.base import BaseModel  # local import avoids early app load

    if BaseModel.metadata is not db.metadata:  # keep unique
        metas.append(BaseModel.metadata)

    return metas


def _configure_offline(url: str) -> None:
    context.configure(
        url=url,
        target_metadata=_merged_metadata(),
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _configure_online() -> None:
    from sqlalchemy import pool

    connectable = _get_engine()

    # Prevent empty revisions
    def _skip_empty(ctx, rev, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=_merged_metadata(),
            process_revision_directives=_skip_empty,
            poolclass=pool.NullPool,
            **current_app.extensions["migrate"].configure_args,
        )
        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------------ entry
if context.is_offline_mode():
    _configure_offline(config.get_main_option("sqlalchemy.url"))
else:
    _configure_online()