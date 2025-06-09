"""PORF ingestion helpers.

Layer: channels
"""

from __future__ import annotations

import csv
import logging
from io import BytesIO
from typing import BinaryIO, Dict, List

from app import db
from app.core.services.drive import DriveService
from app.core.services.sheets import SheetsService
from app.core.logic.utils import slugify
from .models import WootPorf, WootPorfLine, WootPorfStatus

logger = logging.getLogger(__name__)

TEMPLATE_ID = "TEMPLATE_ID"


def ingest_porf(
    upload_file: BinaryIO, drive: DriveService, sheets: SheetsService
) -> Dict[str, str]:
    """Parse PORF spreadsheet, store rows and create a Sheets copy."""
    logger.debug("ingest_porf start")

    reader = csv.DictReader(BytesIO(upload_file.read()).read().decode().splitlines())
    porf = WootPorf(status=WootPorfStatus.DRAFT)
    db.session.add(porf)
    canonical_rows: List[List[str]] = []
    for row in reader:
        line = WootPorfLine(
            porf=porf,
            product_id=row.get("product_id", ""),
            product_name=row.get("product_name", ""),
            quantity=int(row.get("quantity", 0)),
            unit_price=float(row.get("unit_price", 0)),
            total_price=float(row.get("quantity", 0)) * float(row.get("unit_price", 0)),
        )
        db.session.add(line)
        canonical_rows.append(
            [
                line.product_id,
                line.product_name,
                str(line.quantity),
                str(line.unit_price),
                str(line.total_price),
            ]
        )
    db.session.commit()

    workspace = drive.ensure_workspace("default")
    dst_folder = drive.ensure_subfolder(workspace, "woot/porfs")
    sheet_id, url = sheets.copy_template(
        TEMPLATE_ID, slugify("PORF", porf.id), dst_folder
    )
    sheets.append_rows(sheet_id, canonical_rows)

    logger.info("ingest_porf success")
    return {"porf_id": str(porf.id), "sheet_url": url}
