import logging
from typing import List, Dict

from models.channel import Channel
from models.product import Product
from models.inventory_record import InventoryRecord

logger = logging.getLogger(__name__)


def sync_inventory(session, records: List[Dict], channel_name: str):
    """Insert *delta* inventory records for a channel.

    `records` is a list of dicts like `{"sku": "ABC-123", "delta": -5, "source": "shipstation"}`.
    All deltas are applied **as-is**; the function **does not** attempt to derive absolute on-hand counts – that
    responsibility is deferred to reporting queries.
    """

    channel = (
        session.query(Channel).filter_by(name=channel_name).one_or_none()
    )
    if channel is None:
        channel = Channel(name=channel_name)
        session.add(channel)
        session.flush()

    for rec in records:
        sku = rec.get("sku")
        delta = rec.get("delta")
        if sku is None or delta is None:
            logger.warning("Record missing sku or delta: %s", rec)
            continue

        product: Product = (
            session.query(Product).filter_by(sku=sku).one_or_none()
        )
        if product is None:
            logger.warning("Product not found for SKU %s – skipping", sku)
            continue

        inv = InventoryRecord(
            product_id=product.id,
            channel_id=channel.id,
            delta=delta,
            source=rec.get("source"),
        )
        session.add(inv)

    session.commit()
    logger.info("Inventory sync complete for channel %s with %d records", channel_name, len(records)) 