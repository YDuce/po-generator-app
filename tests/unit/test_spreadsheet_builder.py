"""Unit tests for SpreadsheetBuilder."""

from pathlib import Path
import pytest

from app.core.services.spreadsheet import SpreadsheetBuilder


def test_get_sheet_data_not_implemented(tmp_path: Path) -> None:
    """Ensure get_sheet_data is not implemented."""
    builder = SpreadsheetBuilder(tmp_path / "template.xlsx")
    with pytest.raises(NotImplementedError):
        builder.get_sheet_data()
