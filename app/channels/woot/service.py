"""Woot channel service implementation."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app.channels.base import ChannelInterface
from app.channels.woot.client import WootClient
from app.channels.woot.models import (
    PORF,
    WootPo,
    WootPoLine,
    WootPorf,
    WootPorfLine,
    WootPorfStatus,
    WootPoStatus,
)
from app.core.interfaces import BaseChannelOrderService
from app.core.services import DriveService
from app.core.services.sheets import SheetsService
from app.extensions import db


class WootService(ChannelInterface):
    """Service for Woot channel operations."""

    def __init__(self, credentials: Credentials):
        """Initialize the service.

        Args:
            credentials: Google API credentials
        """
        self.drive_service = DriveService(credentials)
        self.sheets_service = SheetsService(credentials)
        self.woot_client = WootClient(
            api_key=os.environ["WOOT_API_KEY"],
            api_secret=os.environ["WOOT_API_SECRET"],
            api_url=os.environ["WOOT_API_URL"],
        )

    def create_porf(self, data: Dict[str, Any]) -> WootPorf:
        """Create a new PORF.

        Args:
            data: PORF data including lines

        Returns:
            Created PORF instance
        """
        # Create PORF in Woot
        self.woot_client.create_porf(data)

        # Create PORF in database
        porf = WootPorf(
            porf_no=data["porf_no"],
            status=WootPorfStatus.DRAFT,
            total_value=sum(line["quantity"] * line["unit_price"] for line in data["lines"]),
        )
        db.session.add(porf)

        # Create PORF lines
        for line_data in data["lines"]:
            line = WootPorfLine(
                porf=porf,
                product_id=line_data["product_id"],
                product_name=line_data["product_name"],
                quantity=line_data["quantity"],
                unit_price=line_data["unit_price"],
                total_price=line_data["quantity"] * line_data["unit_price"],
            )
            db.session.add(line)

        db.session.commit()
        return porf

    def create_po(self, porf_id: int, data: Dict[str, Any]) -> WootPo:
        """Create a new PO from a PORF.

        Args:
            porf_id: ID of the PORF to create PO from
            data: Additional PO data

        Returns:
            Created PO instance
        """
        WootPorf.query.get_or_404(porf_id)

        # Create PO in Woot
        self.woot_client.create_po(porf_id, data)

        # Create PO in database
        po = WootPo(
            po_no=data["po_no"],
            porf_id=porf_id,
            status=WootPoStatus.DRAFT,
            expires_at=data.get("expires_at"),
            ship_by=data.get("ship_by"),
            total_ordered=sum(line["quantity"] * line["unit_price"] for line in data["lines"]),
        )
        db.session.add(po)

        # Create PO lines
        for line_data in data["lines"]:
            line = WootPoLine(
                po=po,
                product_id=line_data["product_id"],
                product_name=line_data["product_name"],
                quantity=line_data["quantity"],
                unit_price=line_data["unit_price"],
                total_price=line_data["quantity"] * line_data["unit_price"],
            )
            db.session.add(line)

        db.session.commit()
        return po

    def upload_po_file(self, po_id: int, file_path: str) -> str:
        """Upload a PO file to Google Drive.

        Args:
            po_id: ID of the PO
            file_path: Path to the file to upload

        Returns:
            ID of the uploaded file
        """
        po = WootPo.query.get_or_404(po_id)

        # Create folder if needed
        if not po.drive_file_id:
            folder_id = self.drive_service.create_folder(f"PO-{po.po_no}")
            po.drive_folder_id = folder_id
            db.session.commit()

        # Upload file to Drive
        file_id = self.drive_service.upload_file(
            file_path=file_path, name=os.path.basename(file_path), parent_id=po.drive_folder_id
        )

        # Upload file to Woot
        self.woot_client.upload_po_file(po_id, file_path)

        po.drive_file_id = file_id
        db.session.commit()

        return file_id

    def create_porf_spreadsheet(self, porf_id: int) -> str:
        """Create a spreadsheet for a PORF.

        Args:
            porf_id: ID of the PORF

        Returns:
            ID of the created spreadsheet
        """
        porf = WootPorf.query.get_or_404(porf_id)

        # Create spreadsheet
        spreadsheet_id = self.sheets_service.create_spreadsheet(
            title=f"PORF-{porf.porf_no}",
            sheets=[{"title": "Lines", "gridProperties": {"rowCount": 1000, "columnCount": 10}}],
        )

        # Add headers
        headers = ["Product ID", "Product Name", "Quantity", "Unit Price", "Total Price"]
        self.sheets_service.update_values(
            spreadsheet_id=spreadsheet_id, range_name="Lines!A1:E1", values=[headers]
        )

        # Add data
        rows = []
        for line in porf.lines:
            rows.append(
                [
                    line.product_id,
                    line.product_name,
                    line.quantity,
                    float(line.unit_price),
                    float(line.total_price),
                ]
            )

        if rows:
            self.sheets_service.update_values(
                spreadsheet_id=spreadsheet_id, range_name="Lines!A2", values=rows
            )

        porf.sheets_file_id = spreadsheet_id
        db.session.commit()

        return spreadsheet_id

    def update_porf_status(self, porf_id: int, status: str) -> WootPorf:
        """Update a PORF's status.

        Args:
            porf_id: ID of the PORF
            status: New status

        Returns:
            Updated PORF instance
        """
        porf = WootPorf.query.get_or_404(porf_id)

        # Update status in Woot
        self.woot_client.update_porf_status(porf_id, status)

        # Update status in database
        porf.status = WootPorfStatus(status)
        db.session.commit()
        return porf

    def update_po_status(self, po_id: int, status: str) -> WootPo:
        """Update a PO's status.

        Args:
            po_id: ID of the PO
            status: New status

        Returns:
            Updated PO instance
        """
        po = WootPo.query.get_or_404(po_id)

        # Update status in Woot
        self.woot_client.update_po_status(po_id, status)

        # Update status in database
        po.status = WootPoStatus(status)
        db.session.commit()
        return po

    def get_porf(self, porf_id: int) -> WootPorf:
        """Get a PORF by ID.

        Args:
            porf_id: ID of the PORF

        Returns:
            PORF instance
        """
        return WootPorf.query.get_or_404(porf_id)

    def get_po(self, po_id: int) -> WootPo:
        """Get a PO by ID.

        Args:
            po_id: ID of the PO

        Returns:
            PO instance
        """
        return WootPo.query.get_or_404(po_id)

    def list_porfs(self, status: Optional[str] = None) -> List[WootPorf]:
        """List PORFs.

        Args:
            status: Optional status filter

        Returns:
            List of PORF instances
        """
        query = WootPorf.query
        if status:
            query = query.filter_by(status=WootPorfStatus(status))
        return query.order_by(WootPorf.created_at.desc()).all()

    def list_pos(self, status: Optional[str] = None) -> List[WootPo]:
        """List POs.

        Args:
            status: Optional status filter

        Returns:
            List of PO instances
        """
        query = WootPo.query
        if status:
            query = query.filter_by(status=WootPoStatus(status))
        return query.order_by(WootPo.created_at.desc()).all()

    def fetch_orders(self, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch orders from Woot.

        Args:
            start_date: Optional start date for order fetch

        Returns:
            List of order data
        """
        return self.woot_client.get_orders(start_date)

    def fetch_inventory(self) -> List[Dict[str, Any]]:
        """Fetch inventory from Woot.

        Returns:
            List of inventory data
        """
        return self.woot_client.get_inventory()


class WootOrderService(BaseChannelOrderService):
    """Woot-specific implementation of the channel order service."""

    def __init__(self, db: Session, sheets_service: SheetsService):
        self.db = db
        self.sheets_service = sheets_service

    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch orders from Woot within the specified date range."""
        porfs = (
            self.db.query(PORF)
            .filter(PORF.created_at >= start_date, PORF.created_at <= end_date)
            .all()
        )
        return [porf.to_dict() for porf in porfs]

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in Woot."""
        porf = PORF.from_dict(order_data)
        self.db.add(porf)
        self.db.commit()
        self.db.refresh(porf)
        return porf.to_dict()

    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing order in Woot."""
        porf = self.db.query(PORF).filter(PORF.external_id == order_id).first()
        if not porf:
            raise ValueError(f"Order {order_id} not found")

        for key, value in order_data.items():
            setattr(porf, key, value)

        self.db.commit()
        self.db.refresh(porf)
        return porf.to_dict()

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a single order by ID."""
        porf = self.db.query(PORF).filter(PORF.external_id == order_id).first()
        return porf.to_dict() if porf else None

    def get_order_status(self, order_id: str) -> str:
        """Get the current status of an order."""
        porf = self.db.query(PORF).filter(PORF.external_id == order_id).first()
        if not porf:
            raise ValueError(f"Order {order_id} not found")
        return porf.status

    def export_to_sheets(self, spreadsheet_id: str, range_name: str) -> None:
        """Export orders to Google Sheets."""
        porfs = self.db.query(PORF).all()
        data = [porf.to_dict() for porf in porfs]
        self.sheets_service.update_sheet_data(spreadsheet_id, range_name, data)
