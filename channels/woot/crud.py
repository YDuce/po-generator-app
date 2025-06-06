from datetime import datetime
from sqlalchemy.orm import Session
from channels.woot.models import PORFStatus, POStatus
from models.woot_porf_line import WootPorfLine
from models.porf import PORF
from models.po import PO


def get_live_porf_lines(db: Session, product_id: int):
    now = datetime.utcnow()
    return (
        db.query(WootPorfLine)
        .join(PORF)
        .join(PO)
        .filter(
            PORF.status == PORFStatus.approved.value,
            PO.status == POStatus.open.value,
            PO.expires_at > now,
            WootPorfLine.product_id == product_id,
        )
        .all()
    )


def create_or_get_today_draft_porf(db: Session):
    today_str = datetime.utcnow().strftime("%y%m%d")
    porf_no = f"Auto-PORF-{today_str}"
    porf = (
        db.query(PORF).filter_by(porf_no=porf_no, status=PORFStatus.draft.value).first()
    )
    if not porf:
        porf = PORF(porf_no=porf_no, status=PORFStatus.draft.value)
        db.add(porf)
        db.commit()
    return porf
