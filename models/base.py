from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects import postgresql
from database import Base  # Re-export existing declarative base


class JSONB(TypeDecorator):
    """Platform-independent JSONB column.

    Uses PostgreSQL's native JSONB when available; otherwise falls back to
    JSON, which is fully supported by SQLite. This keeps the schema identical
    across environments while retaining advanced features in Postgres.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):  # noqa: D401
        return value

    def process_result_value(self, value, dialect):  # noqa: D401
        return value


__all__ = ["Base", "JSONB"] 