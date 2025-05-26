from pathlib import Path
from channels import get_connector
from logic.spreadsheet_builder import SpreadsheetBuilder

def export_document(channel: str, template_key: str, rows: list[dict], out_dir: Path) -> Path:
    """
    Generic spreadsheet exporter. Uses the channel's template map.
    """
    connector = get_connector(channel)
    templates = getattr(connector, 'list_templates', lambda: {})()
    tpl_rel = templates.get(template_key)
    if not tpl_rel:
        raise RuntimeError(f"{channel} provides no template '{template_key}'")
    tpl_path = Path("templates") / tpl_rel
    builder = SpreadsheetBuilder(tpl_path)
    out_path = out_dir / f"{channel}_{template_key}{tpl_path.suffix}"
    if tpl_path.suffix == '.csv':
        return builder.write_csv(rows, out_path)
    return builder.write_excel(rows, out_path) 