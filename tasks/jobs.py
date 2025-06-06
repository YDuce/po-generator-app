from flask import current_app
from tasks.celery_app import create_celery

celery = create_celery(current_app)


@celery.task(acks_late=True, autoretry_for=(Exception,))
def po_expiry_sweep():
    """Sweep expired purchase orders and roll leftovers."""
    # Implementation placeholder
    current_app.logger.info("po_expiry_sweep called")


@celery.task
def email_dropbox_poll():
    """Poll email dropbox for new POs."""
    current_app.logger.info("email_dropbox_poll called")


@celery.task
def shipstation_sync():
    """Sync shipments from ShipStation."""
    current_app.logger.info("shipstation_sync called")
