"""Request validation helpers."""

import re
from flask import abort

__all__ = ["require_fields", "validate_drive_folder_id"]


def require_fields(
    data: dict, fields: list[str], limits: dict[str, int] | None = None
) -> None:
    """Ensure required fields exist and honor optional length limits."""

    missing = [f for f in fields if f not in data or data[f] in (None, "")]
    if missing:
        abort(400, description=f"Missing field(s): {', '.join(missing)}")
    if limits:
        for key, max_len in limits.items():
            if key in data and len(str(data[key])) > max_len:
                abort(400, description=f"{key} too long (max {max_len})")


def validate_drive_folder_id(value: str, max_len: int = 256) -> str:
    """Validate Google Drive folder ID value."""
    if len(value) > max_len or not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        abort(400, description="Invalid drive_folder_id")
    return value
