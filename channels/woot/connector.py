from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from channels.base import ChannelConnector
from channels.template_mixin import SpreadsheetTemplateProvider
from pathlib import Path
from models.porf import PORF
from models.porf_line import PORFLine
from models.po import PO
from channels.woot.models import EventUploader


class WootConnector(ChannelConnector, SpreadsheetTemplateProvider):
    def __init__(self, session: Session):
        self.session = session

    def fetch_orders(self, since: datetime) -> List[Dict]:
        # Implement Woot-specific order fetching logic
        return []

    def fetch_inventory(self) -> List[Dict]:
        # Implement Woot-specific inventory fetching logic
        return []

    def list_templates(self):
        return {
            "po": str(Path(__file__).parent / "templates" / "po.xlsx"),
        }

    def create_event_uploader(self, porf_id, category, file_path):
        uploader = EventUploader(
            porf_id=porf_id, category=category, file_path=file_path
        )
        self.session.add(uploader)
        self.session.commit()
        return uploader

    def submit_event(self, uploader_id):
        uploader = self.session.query(EventUploader).get(uploader_id)
        if uploader:
            uploader.uploaded_at = datetime.utcnow()
            self.session.commit()
        return {"status": "submitted", "uploader_id": uploader_id}
