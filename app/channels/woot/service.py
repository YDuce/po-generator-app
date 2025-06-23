"""Helpers that turn PORF drafts into Google Sheets, etc."""
from __future__ import annotations

from flask import current_app
from sqlalchemy.orm import Session

from app.core.models.product import MasterProduct
from app.extensions import db
from app.core.services.google.drive import GoogleDriveService
from app.core.services.google.sheets import GoogleSheetsService
from .models import WootPorf, WootPorfLine


class WootService:
    def __init__(self, session: Session | None = None) -> None:
        self._db = session or db.session
        creds = current_app.config["GOOGLE_SVC_CREDS"]
        self.drive = GoogleDriveService(creds)
        self.sheets = GoogleSheetsService(creds)

    # ---------------------------------------------------------------- PORF

    def create_porf(self, data: dict) -> WootPorf:
        if self._db.query(WootPorf).filter_by(porf_no=data["porf_no"]).first():
            raise ValueError("PORF already exists")

        porf = WootPorf(porf_no=data["porf_no"])
        self._db.add(porf)

        for ln in data["lines"]:
            prod = self._db.query(MasterProduct).filter_by(sku=ln["sku"]).one()
            self._db.add(
                WootPorfLine(porf=porf, product=prod, quantity=int(ln["quantity"]))
            )

        self._db.flush()  # caller will commit
        return porf
