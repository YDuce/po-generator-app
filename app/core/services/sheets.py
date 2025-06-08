from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsService:
    """Core service for interacting with Google Sheets."""
    
    def __init__(self, credentials: Credentials):
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheets = self.service.spreadsheets()
    
    def get_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Get data from a specific range in a spreadsheet."""
        try:
            result = self.spreadsheets.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            raise Exception(f"Error fetching sheet data: {error}")
    
    def update_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Update data in a specific range of a spreadsheet."""
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
            raise Exception(f"Error updating sheet data: {error}")
    
    def append_sheet_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Append data to a specific range in a spreadsheet."""
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
            raise Exception(f"Error appending sheet data: {error}")
    
    def clear_sheet_data(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Clear data from a specific range in a spreadsheet."""
        try:
            result = self.spreadsheets.values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return result
        except HttpError as error:
            raise Exception(f"Error clearing sheet data: {error}") 