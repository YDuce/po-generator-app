import logging
from typing import List, Dict
import os
import requests
from models import OAuthToken, InventoryRecord
from database import SessionLocal
from datetime import datetime

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


def poll(user_id):
    db = SessionLocal()
    token = db.query(OAuthToken).filter_by(user_id=user_id, provider='shipstation').first()
    api_key = token.access_token if token else os.getenv('SHIPSTATION_API_KEY')
    api_secret = token.refresh_token if token else os.getenv('SHIPSTATION_API_SECRET')
    if not api_key or not api_secret:
        return []
    url = 'https://ssapi.shipstation.com/shipments?createDateStart=2024-01-01'
    auth = (api_key, api_secret)
    resp = requests.get(url, auth=auth)
    shipments = resp.json().get('shipments', [])
    for shipment in shipments:
        for item in shipment.get('items', []):
            rec = InventoryRecord(
                product_id=item['productId'],
                channel_id=1,
                delta=-item['quantity'],
                recorded_at=datetime.utcnow()
            )
            db.add(rec)
    db.commit()
    return shipments 