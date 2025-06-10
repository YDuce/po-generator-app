"""Unit tests for ExportService."""

import pytest
from unittest.mock import MagicMock

from app.core.services.export import ExportService


def test_export_products_to_sheets_not_implemented() -> None:
    """Ensure exporting products to sheets is not implemented."""
    service = ExportService(MagicMock(), MagicMock())
    with pytest.raises(NotImplementedError):
        service.export_products_to_sheets([])


def test_export_inventory_to_sheets_not_implemented() -> None:
    """Ensure exporting inventory to sheets is not implemented."""
    service = ExportService(MagicMock(), MagicMock())
    with pytest.raises(NotImplementedError):
        service.export_inventory_to_sheets([])


def test_export_products_to_drive_not_implemented() -> None:
    """Ensure exporting products to drive is not implemented."""
    service = ExportService(MagicMock(), MagicMock())
    with pytest.raises(NotImplementedError):
        service.export_products_to_drive([])
