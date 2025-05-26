import argparse, logging, uuid
from datetime import datetime, timedelta, timezone
from logic.shipstation_client import ShipStationConnector
from models.sales_order import SalesOrder
from models.channel import Channel

log = logging.getLogger("ingest.shipstation")

def run(session, hours: int):
    job = uuid.uuid4().hex
    log.info("%s start", job)
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        conn = ShipStationConnector()
        raw = conn.fetch_orders(since)
        if not raw:
            log.info("%s no orders", job)
            return
        chan = session.query(Channel).filter_by(name=conn.identifier()).one()
        for o in raw:
            session.merge(SalesOrder(
                external_id=o["orderId"],
                channel_id=chan.id,
                placed_at=o["createDate"],
                status=o["orderStatus"]))
        session.commit()
        log.info("%s success (%d orders)", job, len(raw))
    except Exception as e:
        session.rollback()
        log.exception("%s failed: %s", job, e)
        raise

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--since_hours", type=int, default=1)
    run(ap.parse_args().since_hours) 