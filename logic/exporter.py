from pathlib import Path
from tempfile import NamedTemporaryFile

from channels import get_connector
from logic.spreadsheet_builder import SpreadsheetBuilder

def export_document(channel: str, template_key: str, context=None) -> Path:
    """Create a spreadsheet for *channel* using *template_key*.

    The *context* argument is intentionally flexible – callers may pass raw
    rows, a PORF id, or any other value required by the concrete exporter.
    For this MVP we accept:

    * ``None`` – produce an empty document.
    * ``list[dict]`` – treated as rows.
    * ``str`` or ``int`` – treated as a PORF id (stubbed).
    """

    connector = get_connector(channel)
    templates = getattr(connector, "list_templates", lambda: {})()
    tpl_rel = templates.get(template_key)
    if not tpl_rel:
        raise RuntimeError(f"{channel} provides no template '{template_key}'")

    tpl_path = Path(tpl_rel)
    if not tpl_path.exists():
        # Fallback to relative location inside channel package
        tpl_path = Path("channels") / channel / "templates" / tpl_rel

    builder = SpreadsheetBuilder(tpl_path)

    # Determine rows based on context
    if isinstance(context, list):
        rows = context
    else:
        # Stub: produce single dummy row.
        rows = [{"sku": "DUMMY", "qty": 0}]

    # Write to a temp file – caller can stream/send it.
    suffix = tpl_path.suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)

    if tpl_path.suffix == ".csv":
        return builder.write_csv(rows, tmp_path)

    return builder.write_excel(rows, tmp_path) 