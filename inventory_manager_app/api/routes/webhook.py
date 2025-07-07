"""Webhook route registration."""

from inventory_manager_app.core.webhooks.shipstation import bp as shipstation_bp

bp = shipstation_bp

__all__ = ["bp"]
