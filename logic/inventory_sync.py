import logging
from models.channel import Channel
from models.listing import Listing
from models.inventory_record import InventoryRecord
from typing import List, Dict

logger = logging.getLogger(__name__)

def sync_inventory(session, records: List[Dict], channel_name: str):
    try:
        channel = session.query(Channel).filter_by(name=channel_name).first()
        if not channel:
            logger.error(f"Channel '{channel_name}' not found.")
            raise ValueError(f"Channel '{channel_name}' not found.")
        for rec in records:
            sku = rec.get('sku')
            qty = rec.get('quantity')
            if not sku or qty is None:
                logger.warning(f"Missing sku or quantity in record: {rec}")
                continue
            listing = session.query(Listing).filter_by(product_id=session.query(Listing.product_id).filter(Listing.channel_id==channel.id, Listing.external_sku==sku).scalar(), channel_id=channel.id).first()
            if not listing:
                logger.warning(f"Listing not found for SKU {sku} on channel {channel_name}")
                continue
            inv = InventoryRecord(listing_id=listing.id, quantity=qty)
            session.add(inv)
            logger.info(f"Appended inventory record for SKU {sku} (listing {listing.id}) with quantity {qty}")
        session.commit()
        logger.info(f"Inventory sync complete for channel: {channel_name}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error during inventory sync: {str(e)}")
        raise 