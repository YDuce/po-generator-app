from pathlib import Path
from flask import Blueprint, send_file, request, abort
from logic.exporter import export_document

bp = Blueprint("export", __name__, url_prefix="/api/export")


@bp.get("/<channel>/<template>")
def export(channel: str, template: str):
    """Return a generated spreadsheet for the requested channel/template."""

    # For this MVP we only allow the `po` template.
    if template not in {"po"}:
        abort(400, "Unsupported template")

    # Delegate to the logic exporter which will return a file path.
    porf_id = request.args.get("porf_id")
    path: Path = export_document(channel, template, porf_id)

    if not path.exists():
        abort(404, "Export file not found")

    return send_file(path, as_attachment=True) 