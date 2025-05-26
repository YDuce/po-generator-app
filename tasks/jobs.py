from datetime import datetime

from tasks.scheduler import scheduler


@scheduler.scheduled_job("interval", minutes=15)
def pull_po_emails():
    # TODO: IMAP search, save pdf, parse PO#, attach to PORF
    print(f"[{datetime.utcnow()}] pull_po_emails stub running")


@scheduler.scheduled_job("cron", hour=2)
def po_expiry_sweep():
    # TODO: expire old PORFs, roll leftover into new
    print(f"[{datetime.utcnow()}] po_expiry_sweep stub running")


@scheduler.scheduled_job("interval", hours=1)
def sync_shipstation():
    # TODO: call ShipStation API, create inventory_record deltas
    print(f"[{datetime.utcnow()}] sync_shipstation stub running") 