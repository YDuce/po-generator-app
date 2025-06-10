"""Google Sheets service."""

from typing import List, Dict, Any, Optional, TypedDict, cast
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import os

logger = logging.getLogger(__name__)

TWO_WAY_SYNC_ENABLED = os.environ.get("TWO_WAY_SYNC_ENABLED", "false").lower() == "true"

class SheetResponse(TypedDict):
    """Type for Google Sheets API response."""
    spreadsheetId: str
    updatedRange: str
    updatedRows: int
    updatedColumns: int
    updatedCells: int

class SheetsService:
    """Service for interacting with Google Sheets."""
    
    def __init__(self, credentials: Credentials) -> None:
        """Initialize the Google Sheets service.
        
        Args:
            credentials: Google API credentials
        """
        if not credentials or not credentials.valid:
            raise ValueError("Invalid or missing credentials")
            
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheets = self.service.spreadsheets()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """Get data from a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to get data from (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of rows containing the data
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            result = self.spreadsheets.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return cast(List[List[str]], result.get('values', []))
        except HttpError as error:
            logger.error(f"Failed to get data from sheet {spreadsheet_id} range {range_name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def update_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[str]]) -> SheetResponse:
        """Update data in a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to update (e.g., 'Sheet1!A1:D10')
            values: List of rows to write
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            body = {
                'values': values
            }
            result = self.spreadsheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return cast(SheetResponse, result)
        except HttpError as error:
            logger.error(f"Failed to update sheet {spreadsheet_id} range {range_name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def append_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[str]]) -> SheetResponse:
        """Append data to a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to append to (e.g., 'Sheet1!A1:D')
            values: List of rows to append
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            body = {
                'values': values
            }
            result = self.spreadsheets.values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return cast(SheetResponse, result)
        except HttpError as error:
            logger.error(f"Failed to append data to sheet {spreadsheet_id} range {range_name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def clear_sheet_data(self, spreadsheet_id: str, range_name: str) -> SheetResponse:
        """Clear data from a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to clear (e.g., 'Sheet1!A1:D10')
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            result = self.spreadsheets.values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return cast(SheetResponse, result)
        except HttpError as error:
            logger.error(f"Failed to clear data from sheet {spreadsheet_id} range {range_name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def create_sheet(self, title: str, folder_id: str) -> SheetMetadata:
        """Create a new Google Sheet.
        
        Args:
            title: Title of the new spreadsheet
            
        Returns:
            Response from the API containing the new spreadsheet details
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            result = self.spreadsheets.create(body=spreadsheet).execute()
            return result
        except HttpError as error:
            logger.error(f"Failed to create sheet with title {title}: {error}")
            raise

    def open_sheet(self, sheet_id: str) -> Dict[str, Any]:
        """Return the spreadsheet metadata."""
        return cast(Dict[str, Any], self.spreadsheets.get(spreadsheetId=sheet_id).execute())

    def copy_template(self, src_id: str, dst_title: str, folder_id: str) -> tuple[str, str]:
        """Copy ``src_id`` to ``dst_title`` inside ``folder_id``."""
        if not TWO_WAY_SYNC_ENABLED:
            raise RuntimeError("two-way sync disabled")
        body = {"name": dst_title, "parents": [folder_id]}
        copy = self.service.files().copy(fileId=src_id, body=body).execute()
        sheet_id = copy["id"]
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        return sheet_id, url

    def append_rows(self, sheet_id: str, rows: List[List[str]]) -> SheetResponse:
        """Append ``rows`` to the first worksheet."""
        if not TWO_WAY_SYNC_ENABLED:
            raise RuntimeError("two-way sync disabled")
        body = {"values": rows}
        result = self.spreadsheets.values().append(
            spreadsheetId=sheet_id,
            range="A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
        return cast(SheetResponse, result)
