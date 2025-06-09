"""Unit tests for PORF ingestion."""

import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.channels.woot.logic import ingest_porf
from app.channels.woot.models import WootPorf, WootPorfLine, WootPorfStatus

@pytest.fixture
def mock_drive_service():
    """Create mock Drive service."""
    service = MagicMock()
    service.ensure_workspace.return_value = 'workspace_id'
    service.ensure_subfolder.return_value = 'folder_id'
    return service

@pytest.fixture
def mock_sheets_service():
    """Create mock Sheets service."""
    service = MagicMock()
    service.copy_template.return_value = ('sheet_id', 'https://docs.google.com/spreadsheets/d/sheet_id')
    return service

def test_ingest_porf(mock_drive_service, mock_sheets_service, db_session) -> None:
    """Test PORF ingestion."""
    # Create test CSV data
    csv_data = """product_id,product_name,quantity,unit_price
PROD-001,Test Product 1,10,50.00
PROD-002,Test Product 2,5,100.00"""
    
    # Ingest PORF
    result = ingest_porf(
        BytesIO(csv_data.encode()),
        mock_drive_service,
        mock_sheets_service
    )
    
    # Verify PORF was created
    porf = WootPorf.query.first()
    assert porf is not None
    assert porf.status == WootPorfStatus.DRAFT
    assert float(porf.total_value) == 1000.00
    
    # Verify PORF lines were created
    assert len(porf.lines) == 2
    assert porf.lines[0].product_id == 'PROD-001'
    assert porf.lines[0].product_name == 'Test Product 1'
    assert porf.lines[0].quantity == 10
    assert float(porf.lines[0].unit_price) == 50.00
    assert float(porf.lines[0].total_price) == 500.00
    assert porf.lines[1].product_id == 'PROD-002'
    assert porf.lines[1].product_name == 'Test Product 2'
    assert porf.lines[1].quantity == 5
    assert float(porf.lines[1].unit_price) == 100.00
    assert float(porf.lines[1].total_price) == 500.00
    
    # Verify Drive service was called
    mock_drive_service.ensure_workspace.assert_called_once_with('default')
    mock_drive_service.ensure_subfolder.assert_called_once_with('workspace_id', 'woot/porfs')
    
    # Verify Sheets service was called
    mock_sheets_service.copy_template.assert_called_once()
    mock_sheets_service.append_rows.assert_called_once()
    
    # Verify result
    assert result['porf_id'] == str(porf.id)
    assert result['sheet_url'] == 'https://docs.google.com/spreadsheets/d/sheet_id'

def test_ingest_porf_invalid_csv(mock_drive_service, mock_sheets_service, db_session) -> None:
    """Test PORF ingestion with invalid CSV."""
    # Create invalid CSV data
    csv_data = """invalid_column
invalid_data"""
    
    # Attempt to ingest PORF
    with pytest.raises(Exception):
        ingest_porf(
            BytesIO(csv_data.encode()),
            mock_drive_service,
            mock_sheets_service
        )
    
    # Verify no PORF was created
    porf = WootPorf.query.first()
    assert porf is None

def test_ingest_porf_empty_csv(mock_drive_service, mock_sheets_service, db_session) -> None:
    """Test PORF ingestion with empty CSV."""
    # Create empty CSV data
    csv_data = """product_id,product_name,quantity,unit_price"""
    
    # Ingest PORF
    result = ingest_porf(
        BytesIO(csv_data.encode()),
        mock_drive_service,
        mock_sheets_service
    )
    
    # Verify PORF was created
    porf = WootPorf.query.first()
    assert porf is not None
    assert porf.status == WootPorfStatus.DRAFT
    assert float(porf.total_value) == 0.00
    assert len(porf.lines) == 0
    
    # Verify result
    assert result['porf_id'] == str(porf.id)
    assert result['sheet_url'] == 'https://docs.google.com/spreadsheets/d/sheet_id'

def test_ingest_porf_drive_error(mock_drive_service, mock_sheets_service, db_session) -> None:
    """Test PORF ingestion with Drive error."""
    # Create test CSV data
    csv_data = """product_id,product_name,quantity,unit_price
PROD-001,Test Product,10,100.00"""
    
    # Mock Drive service error
    mock_drive_service.ensure_workspace.side_effect = Exception('Drive API Error')
    
    # Attempt to ingest PORF
    with pytest.raises(Exception) as exc_info:
        ingest_porf(
            BytesIO(csv_data.encode()),
            mock_drive_service,
            mock_sheets_service
        )
    
    # Verify error was raised
    assert str(exc_info.value) == 'Drive API Error'
    
    # Verify no PORF was created
    porf = WootPorf.query.first()
    assert porf is None

def test_porf_ingestion_init() -> None:
    pass

def test_porf_ingestion_process() -> None:
    pass

def test_porf_ingestion_validate() -> None:
    pass 