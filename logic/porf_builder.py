"""Utilities for drafting PORF spreadsheets (XLSX) via openpyxl.

This is currently a stub to satisfy imports. The full implementation will
populate PORF templates based on product and quantity data.
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime

import openpyxl  # Required dependency per blueprint, assumed installed
from channels.woot.models import POStatus, PORFStatus
from models.po import PO
from logic.utils import add_months


def draft_porf_xlsx(rows: List[Dict], output_path: Path) -> Path:
    """Create a PORF draft spreadsheet.

    Parameters
    ----------
    rows
        List of dicts with at minimum ``sku`` and ``qty`` keys.
    output_path
        Target path for the generated file.

    Returns
    -------
    Path
        The written file path.
    """

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PORF"

    ws.append(["SKU", "QTY"])
    for row in rows:
        ws.append([row.get("sku"), row.get("qty")])

    wb.save(output_path)
    return output_path


def build_draft(porf, rows: List[Dict], output_path: Path):
    """Build a draft PORF spreadsheet.

    Parameters
    ----------
    porf
        The PORF object to update.
    rows
        List of dicts with at minimum ``sku`` and ``qty`` keys.
    output_path
        Target path for the generated file.

    Returns
    -------
    Path
        The written file path.
    """

    draft_porf_xlsx(rows, output_path)
    porf.status = PORFStatus.approved
    # po = PO(porf_id=porf.id, status=POStatus.open, expires_at=add_months(datetime.utcnow(), 7))
    # ...

    return output_path
