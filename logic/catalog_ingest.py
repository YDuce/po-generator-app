import logging
from sqlalchemy.exc import SQLAlchemyError
from models.product import Product
from models.channel import Channel
from models.listing import Listing
from typing import List, Dict
from logic.file_parser import FileParser

logger = logging.getLogger(__name__)

def ingest_catalog_items(session, items: List[Dict], channel_name: str):
    """
    Ingests a list of validated product/listing dicts and upserts into the database for a given channel.
    """
    try:
        logger.info(f"Starting catalog ingestion for channel: {channel_name} with {len(items)} items")
        channel = session.query(Channel).filter_by(name=channel_name).first()
        if not channel:
            channel = Channel(name=channel_name)
            session.add(channel)
            session.flush()
            logger.info(f"Created new channel: {channel_name}")
        for item in items:
            product = session.query(Product).filter_by(sku=item['sku']).first()
            if not product:
                product = Product(sku=item['sku'], title=item['title'])
                session.add(product)
                session.flush()
                logger.info(f"Created new product: {item['sku']}")
            else:
                product.title = item['title']
                logger.info(f"Updated product: {item['sku']}")
            listing = session.query(Listing).filter_by(product_id=product.id, channel_id=channel.id).first()
            if not listing:
                listing = Listing(
                    product_id=product.id,
                    channel_id=channel.id,
                    external_sku=item['external_sku'],
                    status=item['status'],
                    price=item['price']
                )
                session.add(listing)
                logger.info(f"Created new listing for SKU {item['sku']} on channel {channel_name}")
            else:
                listing.external_sku = item['external_sku']
                listing.status = item['status']
                listing.price = item['price']
                logger.info(f"Updated listing for SKU {item['sku']} on channel {channel_name}")
        session.commit()
        logger.info(f"Catalog ingested successfully for channel: {channel_name}")
    except (SQLAlchemyError, Exception) as e:
        session.rollback()
        logger.error(f"Error during catalog ingestion: {str(e)}")
        raise

def parse_and_ingest_catalog(session, file_path: str, channel_name: str):
    logger.info(f"Parsing catalog file: {file_path}")
    items = FileParser(file_path).parse_catalog()
    logger.info(f"Parsed {len(items)} items from catalog file: {file_path}")
    ingest_catalog_items(session, items, channel_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python logic/catalog_ingest.py <file_path> <channel_name>")
        sys.exit(1)
    file_path, channel_name = sys.argv[1], sys.argv[2]
    parse_and_ingest_catalog(file_path, channel_name)
    print(f"Ingestion complete for {file_path} into channel {channel_name}") 