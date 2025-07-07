"""Webhook route registration."""

from inventory_manager_app.core.webhooks.shipstation import bp as shipstation_bp

routes = [shipstation_bp]
