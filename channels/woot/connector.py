from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from channels.base import ChannelConnector
from channels.template_mixin import SpreadsheetTemplateProvider
from models.listing import Listing
from channels.woot.models import Batch, BatchLine
from pathlib import Path

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
            'po': str(Path(__file__).parent / 'templates' / 'po.xlsx'),
        } 