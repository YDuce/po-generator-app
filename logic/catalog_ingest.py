import logging
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models.product import Product
from models.channel import Channel
from models.listing import Listing
from typing import List, Dict
from logic.file_parser import FileParser

logger = logging.getLogger(__name__)

def ingest_catalog_items(items: List[Dict], channel_name: str):
    """
    Ingests a list of validated product/listing dicts and upserts into the database for a given channel.
    """
    session = SessionLocal()
    try:
        # Get or create channel
        channel = session.query(Channel).filter_by(name=channel_name).first()
        if not channel:
            channel = Channel(name=channel_name)
            session.add(channel)
            session.flush()

        # Build product and listing upserts
        for item in items:
            # Upsert product
            product = session.query(Product).filter_by(sku=item['sku']).first()
            if not product:
                product = Product(sku=item['sku'], title=item['title'], cost=item['cost'])
                session.add(product)
                session.flush()
            else:
                product.title = item['title']
                product.cost = item['cost']

            # Upsert listing
            listing = session.query(Listing).filter_by(product_id=product.id, channel_id=channel.id).first()
            if not listing:
                listing = Listing(
                    product_id=product.id,
                    channel_id=channel.id,
                    external_sku=item['external_sku'],
                    status=item['status']
                )
                session.add(listing)
            else:
                listing.external_sku = item['external_sku']
                listing.status = item['status']

        session.commit()
        logger.info(f"Catalog ingested successfully for channel: {channel_name}")
    except (SQLAlchemyError, Exception) as e:
        session.rollback()
        logger.error(f"Error during catalog ingestion: {str(e)}")
        raise
    finally:
        session.close()

def parse_and_ingest_catalog(file_path: str, channel_name: str):
    parser = FileParser(file_path)
    items = parser.parse_catalog()
    ingest_catalog_items(items, channel_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python logic/catalog_ingest.py <file_path> <channel_name>")
        sys.exit(1)
    file_path, channel_name = sys.argv[1], sys.argv[2]
    parse_and_ingest_catalog(file_path, channel_name)
    print(f"Ingestion complete for {file_path} into channel {channel_name}") 