"""Request validation helpers."""

from flask import abort


def require_fields(data: dict, fields: list[str]) -> None:
    missing = [f for f in fields if f not in data]
    if missing:
        abort(400, description=f"Missing fields: {', '.join(missing)}")
