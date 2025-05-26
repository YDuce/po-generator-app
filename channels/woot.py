from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from channels.base import ChannelConnector
from channels.template_mixin import SpreadsheetTemplateProvider
from models.listing import Listing
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Batch(Base):
    """Represents a Woot batch (purchase order)."""
    __tablename__ = 'woot_batch'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    lines = relationship('BatchLine', back_populates='batch', cascade='all, delete-orphan')

class BatchLine(Base):
    """Represents a line in a Woot batch (one SKU/qty)."""
    __tablename__ = 'woot_batch_line'
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('woot_batch.id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('listing.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    batch = relationship('Batch', back_populates='lines')
    listing = relationship('Listing')

class WootConnector(ChannelConnector, SpreadsheetTemplateProvider):
    def __init__(self, session: Session):
        self.session = session

    def fetch_orders(self, since: datetime) -> List[Dict]:
        # Implement Woot-specific order fetching logic
        return []

    def fetch_inventory(self) -> List[Dict]:
        # Implement Woot-specific inventory fetching logic
        return []

    def create_batch(self, listings: List[Listing], name: str | None = None, **opts):
        batch = Batch(name=name or f"Woot PO {datetime.utcnow().isoformat()}")
        for listing in listings:
            line = BatchLine(listing=listing, quantity=opts.get('quantity', 1))
            batch.lines.append(line)
        if self.session:
            self.session.add(batch)
            self.session.commit()
        return batch

    def submit_batch(self, batch: Batch):
        # Implement Woot-specific batch submission logic (e.g., API call)
        return {'status': 'submitted', 'batch_id': batch.id}

    def list_templates(self):
        return {
            'po': 'spreadsheets/woot_po.xlsx',
            'report': 'spreadsheets/woot_report.xlsx'
        } 