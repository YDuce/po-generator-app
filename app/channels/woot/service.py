"""Woot channel service implementation."""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, TypedDict, cast
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app import db
from app.channels.base import ChannelInterface
from app.channels.woot.models import WootPorf, WootPo, WootPorfLine, WootPoLine, WootPorfStatus, WootPoStatus, PORF, PO, PORFLine, POLine
from app.core.services.google.drive import GoogleDriveService as DriveService
from app.core.services.google.sheets import GoogleSheetsService as SheetsService
from app.channels.woot.client import WootClient, OrderData, InventoryItem
from app.core.interfaces import BaseChannelOrderService

class PorfData(TypedDict):
    """Type for PORF data."""
    porf_no: str
    lines: List[Dict[str, Any]]

class PoData(TypedDict):
    """Type for PO data."""
    po_no: str
    expires_at: Optional[datetime]
    ship_by: Optional[datetime]
    lines: List[Dict[str, Any]]

class WootService(ChannelInterface):
    """Service for Woot channel operations."""
    
    def __init__(self, credentials: Credentials) -> None:
        """Initialize the service.
        
        Args:
            credentials: Google API credentials
        """
        self.drive_service = DriveService(credentials)
        self.sheets_service = SheetsService(credentials)
        self.woot_client = WootClient(
            api_key=os.environ['WOOT_API_KEY'],
            api_url=os.environ['WOOT_API_URL']
        )
    
    def create_porf(self, data: Dict[str, Any]) -> WootPorf:
        """Create a new PORF.
        
        Args:
            data: PORF data including lines
            
        Returns:
            Created PORF instance
        """
        # Create PORF in Woot
        woot_data = self.woot_client.create_order(data)
        
        # Create PORF in database
        porf = WootPorf(
            porf_no=data['porf_no'],
            status=WootPorfStatus.DRAFT,
            total_value=sum(line['quantity'] * line['unit_price'] for line in data['lines'])
        )
        db.session.add(porf)
        
        # Create PORF lines
        for line_data in data['lines']:
            line = WootPorfLine(
                porf=porf,
                product_id=line_data['product_id'],
                product_name=line_data['product_name'],
                quantity=line_data['quantity'],
                unit_price=line_data['unit_price'],
                total_price=line_data['quantity'] * line_data['unit_price']
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
        porf = WootPorf.query.get_or_404(porf_id)
        
        # Create PO in Woot
        woot_data = self.woot_client.create_order(data)
        
        # Create PO in database
        po = WootPo(
            po_no=data['po_no'],
            porf_id=porf_id,
            status=WootPoStatus.DRAFT,
            expires_at=data.get('expires_at'),
            ship_by=data.get('ship_by'),
            total_ordered=sum(line['quantity'] * line['unit_price'] for line in data['lines'])
        )
        db.session.add(po)
        
        # Create PO lines
        for line_data in data['lines']:
            line = WootPoLine(
                po=po,
                product_id=line_data['product_id'],
                product_name=line_data['product_name'],
                quantity=line_data['quantity'],
                unit_price=line_data['unit_price'],
                total_price=line_data['quantity'] * line_data['unit_price']
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
            folder_id = self.drive_service.create_file(
                name=f"PO-{po.po_no}",
                mime_type="application/vnd.google-apps.folder"
            )['id']
            po.drive_folder_id = folder_id
            db.session.commit()
        
        # Upload file to Drive
        file_id = self.drive_service.upload_file(
            file_path=file_path,
            mime_type="application/pdf",
            parents=[po.drive_folder_id]
        )['id']
        
        # Upload file to Woot
        self.woot_client.create_order({
            'po_id': po_id,
            'file_path': file_path
        })
        
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
        spreadsheet = self.sheets_service.create_sheet(f"PORF-{porf.porf_no}")
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Add headers
        headers = ['Product ID', 'Product Name', 'Quantity', 'Unit Price', 'Total Price']
        self.sheets_service.update_sheet_data(
            spreadsheet_id=spreadsheet_id,
            range_name='Sheet1!A1:E1',
            values=[headers]
        )
        
        # Add data
        rows = []
        for line in porf.lines:
            rows.append([
                line.product_id,
                line.product_name,
                str(line.quantity),
                str(float(line.unit_price)),
                str(float(line.total_price))
            ])
        
        if rows:
            self.sheets_service.update_sheet_data(
                spreadsheet_id=spreadsheet_id,
                range_name='Sheet1!A2',
                values=rows
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
        self.woot_client.update_order(str(porf_id), {'status': status})
        
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
        self.woot_client.update_order(str(po_id), {'status': status})
        
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
        return query.all()
    
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
        return query.all()
    
    def fetch_orders(self, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch orders from Woot.
        
        Args:
            start_date: Optional start date for filtering
            
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
    """Service for Woot order operations."""
    
    def __init__(self, db: Session, sheets_service: SheetsService) -> None:
        """Initialize the service.
        
        Args:
            db: Database session
            sheets_service: Google Sheets service
        """
        self.db = db
        self.sheets_service = sheets_service
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch orders from Woot.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of orders
        """
        return self.woot_client.get_orders(start_date)
    
    def create_order(self, order_data: Dict[str, Any]) -> OrderData:
        """Create a new order.
        
        Args:
            order_data: Order data
            
        Returns:
            Created order
        """
        return self.woot_client.create_order(order_data)
    
    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> OrderData:
        """Update an existing order.
        
        Args:
            order_id: Order ID
            order_data: Updated order data
            
        Returns:
            Updated order
        """
        return self.woot_client.update_order(order_id, order_data)
    
    def get_order(self, order_id: str) -> Optional[OrderData]:
        """Get a single order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order data if found, None otherwise
        """
        return self.woot_client.get_order(order_id)
    
    def get_order_status(self, order_id: str) -> str:
        """Get the status of an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status
        """
        return self.woot_client.get_order_status(order_id)
    
    def export_to_sheets(self, spreadsheet_id: str, range_name: str) -> None:
        """Export orders to a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to write to
        """
        orders = self.fetch_orders(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        rows = []
        for order in orders:
            rows.append([
                order['id'],
                order['status'],
                order['created_at'],
                order['updated_at'],
                order['total'],
                order['currency']
            ])
        
        if rows:
            self.sheets_service.update_sheet_data(
                spreadsheet_id=spreadsheet_id,
                range_name=range_name,
                values=rows
            ) 