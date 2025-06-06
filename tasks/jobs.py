from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from logic.email_dropbox import poll as gmail_poll
from logic.inventory_sync import poll as shipstation_poll

scheduler = BackgroundScheduler()

# Gmail Dropbox poller every 15 min
scheduler.add_job(lambda: gmail_poll(user_id=1), "interval", minutes=15)

# ShipStation sync hourly
scheduler.add_job(lambda: shipstation_poll(user_id=1), "interval", hours=1)

scheduler.start()


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
