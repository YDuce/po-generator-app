"""Unit tests for Sheets service."""

import pytest
from unittest.mock import patch, MagicMock
from app.core.services.sheets import SheetsService

class MockSheetsAPI:
    """Mock Google Sheets API."""
    def __init__(self):
        self.spreadsheets = {}
        self.values = {}
    
    def create(self, body=None):
        """Mock create spreadsheet."""
        sheet_id = f"{body['properties']['title']}_id"
        self.spreadsheets[sheet_id] = body
        return {
            'spreadsheetId': sheet_id,
            'spreadsheetUrl': f'https://docs.google.com/spreadsheets/d/{sheet_id}'
        }
    
    def get(self, spreadsheetId=None, ranges=None, fields=None):
        """Mock get spreadsheet."""
        if spreadsheetId in self.spreadsheets:
            return {
                'spreadsheetId': spreadsheetId,
                'properties': self.spreadsheets[spreadsheetId]['properties']
            }
        return None
    
    def values(self):
        """Mock values API."""
        return self

    def append(self, spreadsheetId=None, range=None, valueInputOption=None, body=None):
        """Mock append values."""
        if spreadsheetId not in self.values:
            self.values[spreadsheetId] = []
        self.values[spreadsheetId].extend(body['values'])
        return {'updates': {'updatedRange': range}}

@pytest.fixture
def mock_sheets_api():
    """Create mock Sheets API."""
    return MockSheetsAPI()

@pytest.fixture
def sheets_service(mock_sheets_api):
    """Create Sheets service with mock API."""
    with patch('googleapiclient.discovery.build', return_value=mock_sheets_api):
        return SheetsService(None)

def test_copy_template(sheets_service, mock_sheets_api) -> None:
    """Test template copying."""
    # Copy template
    sheet_id, url = sheets_service.copy_template(
        'template_id',
        'Test Sheet',
        'folder_id'
    )
    
    # Verify sheet was created
    assert sheet_id == 'Test Sheet_id'
    assert url == 'https://docs.google.com/spreadsheets/d/Test Sheet_id'
    assert 'Test Sheet_id' in mock_sheets_api.spreadsheets

def test_append_rows(sheets_service, mock_sheets_api) -> None:
    """Test row appending."""
    # Create test sheet
    sheet_id = 'test_sheet_id'
    mock_sheets_api.spreadsheets[sheet_id] = {
        'properties': {'title': 'Test Sheet'}
    }
    
    # Append rows
    rows = [
        ['Product 1', '10', '100.00'],
        ['Product 2', '20', '200.00']
    ]
    sheets_service.append_rows(sheet_id, rows)
    
    # Verify rows were appended
    assert sheet_id in mock_sheets_api.values
    assert mock_sheets_api.values[sheet_id] == rows

def test_get_spreadsheet(sheets_service, mock_sheets_api) -> None:
    """Test spreadsheet retrieval."""
    # Create test sheet
    sheet_id = 'test_sheet_id'
    mock_sheets_api.spreadsheets[sheet_id] = {
        'properties': {'title': 'Test Sheet'}
    }
    
    # Get spreadsheet
    sheet = sheets_service.get_spreadsheet(sheet_id)
    
    # Verify sheet was retrieved
    assert sheet['spreadsheetId'] == sheet_id
    assert sheet['properties']['title'] == 'Test Sheet'

def test_get_spreadsheet_not_found(sheets_service, mock_sheets_api) -> None:
    """Test spreadsheet retrieval when not found."""
    # Get non-existent spreadsheet
    sheet = sheets_service.get_spreadsheet('non_existent_id')
    
    # Verify None was returned
    assert sheet is None

def test_sheets_service_init() -> None:
    pass

def test_sheets_service_get_data() -> None:
    pass

def test_sheets_service_update_data() -> None:
    pass 