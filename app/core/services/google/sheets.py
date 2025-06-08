"""Google Sheets service."""

from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsService:
    """Service for interacting with Google Sheets."""
    
    def __init__(self, credentials: Credentials):
        """Initialize the Google Sheets service.
        
        Args:
            credentials: Google API credentials
        """
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheets = self.service.spreadsheets()
    
    def get_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Get data from a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to get data from (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of rows containing the data
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            result = self.spreadsheets.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            raise error
    
    def update_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Update data in a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to update (e.g., 'Sheet1!A1:D10')
            values: List of rows to write
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails
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
            return result
        except HttpError as error:
            raise error
    
    def append_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Append data to a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to append to (e.g., 'Sheet1!A1:D')
            values: List of rows to append
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails
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
            return result
        except HttpError as error:
            raise error
    
    def clear_sheet_data(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Clear data from a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to clear (e.g., 'Sheet1!A1:D10')
            
        Returns:
            Response from the API
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            result = self.spreadsheets.values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return result
        except HttpError as error:
            raise error
    
    def create_sheet(self, title: str) -> Dict[str, Any]:
        """Create a new Google Sheet.
        
        Args:
            title: Title of the new spreadsheet
            
        Returns:
            Response from the API containing the new spreadsheet details
            
        Raises:
            HttpError: If the API request fails
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
            raise error 