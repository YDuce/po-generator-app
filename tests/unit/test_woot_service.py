"""Unit tests for Woot service."""

import pytest
from unittest.mock import patch, MagicMock
from app.channels.woot.service import WootService
from app.channels.woot.models import WootPorf, WootPorfLine, WootPorfStatus

@pytest.fixture
def mock_woot_client():
    """Create mock Woot client."""
    return MagicMock()

@pytest.fixture
def woot_service(mock_woot_client):
    """Create Woot service with mock client."""
    return WootService(mock_woot_client)

def test_create_porf(woot_service, mock_woot_client, db_session) -> None:
    """Test PORF creation."""
    # Mock Woot client response
    mock_woot_client.create_porf.return_value = {
        'porf_no': 'PORF-001',
        'status': 'draft',
        'total_value': 1000.00
    }
    
    # Create PORF
    porf_data = {
        'porf_no': 'PORF-001',
        'lines': [
            {
                'product_id': 'PROD-001',
                'product_name': 'Test Product 1',
                'quantity': 10,
                'unit_price': 50.00
            },
            {
                'product_id': 'PROD-002',
                'product_name': 'Test Product 2',
                'quantity': 5,
                'unit_price': 100.00
            }
        ]
    }
    porf = woot_service.create_porf(porf_data)
    
    # Verify PORF was created
    assert porf.porf_no == 'PORF-001'
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

def test_create_porf_error(woot_service, mock_woot_client, db_session) -> None:
    """Test PORF creation error handling."""
    # Mock Woot client error
    mock_woot_client.create_porf.side_effect = Exception('Woot API Error')
    
    # Attempt to create PORF
    porf_data = {
        'porf_no': 'PORF-001',
        'lines': [
            {
                'product_id': 'PROD-001',
                'product_name': 'Test Product',
                'quantity': 10,
                'unit_price': 100.00
            }
        ]
    }
    with pytest.raises(Exception) as exc_info:
        woot_service.create_porf(porf_data)
    
    # Verify error was raised
    assert str(exc_info.value) == 'Woot API Error'
    
    # Verify no PORF was created
    porf = WootPorf.query.filter_by(porf_no='PORF-001').first()
    assert porf is None

def test_get_porf(woot_service, mock_woot_client, db_session) -> None:
    """Test PORF retrieval."""
    # Create test PORF
    porf = WootPorf(
        porf_no='PORF-001',
        status=WootPorfStatus.DRAFT,
        total_value=1000.00
    )
    line = WootPorfLine(
        porf=porf,
        product_id='PROD-001',
        product_name='Test Product',
        quantity=10,
        unit_price=100.00,
        total_price=1000.00
    )
    db_session.add(porf)
    db_session.add(line)
    db_session.commit()
    
    # Mock Woot client response
    mock_woot_client.get_porf.return_value = {
        'porf_no': 'PORF-001',
        'status': 'draft',
        'total_value': 1000.00
    }
    
    # Get PORF
    result = woot_service.get_porf(porf.id)
    
    # Verify PORF was retrieved
    assert result.porf_no == 'PORF-001'
    assert result.status == WootPorfStatus.DRAFT
    assert float(result.total_value) == 1000.00
    assert len(result.lines) == 1
    assert result.lines[0].product_id == 'PROD-001'
    assert result.lines[0].product_name == 'Test Product'
    assert result.lines[0].quantity == 10
    assert float(result.lines[0].unit_price) == 100.00
    assert float(result.lines[0].total_price) == 1000.00

def test_get_porf_not_found(woot_service, mock_woot_client, db_session) -> None:
    """Test PORF retrieval when not found."""
    # Mock Woot client response
    mock_woot_client.get_porf.return_value = None
    
    # Get non-existent PORF
    result = woot_service.get_porf(999)
    
    # Verify None was returned
    assert result is None

def test_woot_service_init() -> None:
    pass

def test_woot_service_create() -> None:
    pass

def test_woot_service_update() -> None:
    pass 