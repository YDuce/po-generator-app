"""Request validation helpers."""

import re
from flask import abort, jsonify, make_response
from typing import Any

_SAFE = re.compile(r"^[A-Za-z0-9._-]+$")

__all__ = ["require_fields", "validate_drive_folder_id", "abort_json"]


def require_fields(
    data: dict[str, Any], fields: list[str], limits: dict[str, int] | None = None
) -> None:
    """Ensure required fields exist and honor optional length limits."""

    missing = [f for f in fields if f not in data or data[f] in (None, "")]
    if missing:
        abort(400, description=f"Missing field(s): {', '.join(missing)}")
    if limits:
        for key, max_len in limits.items():
            if key in data and len(str(data[key])) > max_len:
                abort(400, description=f"{key} too long (max {max_len})")


def validate_drive_folder_id(folder_id: str) -> str:
    """Return the folder id if it matches allowed characters else raise."""
    if not _SAFE.fullmatch(folder_id):
        raise ValueError(f"Invalid Drive folder id: {folder_id!r}")
    return folder_id


def abort_json(code: int, message: str) -> None:
    """Abort the request with a JSON error message."""
    abort(make_response(jsonify(error=message), code))
