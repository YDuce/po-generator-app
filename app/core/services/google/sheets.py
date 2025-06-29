"""Google Sheets service."""

from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsService:
    """Service for interacting with Google Sheets."""

    def __init__(self, credentials: Credentials | None = None) -> None:
        """Initialize the Google Sheets service.

        Parameters
        ----------
        credentials:
            Google API credentials or ``None`` to disable Sheets access.
        """
        if credentials is None:
            self.service = None
            self.spreadsheets = None
            return

        self.service = build("sheets", "v4", credentials=credentials)
        self.spreadsheets = self.service.spreadsheets()

    @property
    def is_enabled(self) -> bool:
        """Return ``True`` if Sheets integration is active."""
        return self.spreadsheets is not None

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
            result = (
                self.spreadsheets.values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            return result.get("values", [])
        except HttpError as error:
            raise error

    def update_sheet_data(
        self, spreadsheet_id: str, range_name: str, values: List[List[Any]]
    ) -> Dict[str, Any]:
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
            body = {"values": values}
            result = (
                self.spreadsheets.values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
            return result
        except HttpError as error:
            raise error

    def append_sheet_data(
        self, spreadsheet_id: str, range_name: str, values: List[List[Any]]
    ) -> Dict[str, Any]:
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
            body = {"values": values}
            result = (
                self.spreadsheets.values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
            return result
        except HttpError as error:
            raise error

    def append_rows(
        self, spreadsheet_id: str, rows: List[List[Any]], range_name: str = "Sheet1!A1"
    ) -> Dict[str, Any]:
        """Append rows to the first worksheet.

        Args:
            spreadsheet_id: Target spreadsheet ID.
            rows: Row values to append.
            range_name: A1 range specifying the worksheet (defaults to first sheet).

        Returns:
            API response payload.
        """
        body = {"values": rows}
        result = (
            self.spreadsheets.values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        return result

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
            result = (
                self.spreadsheets.values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
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
            spreadsheet = {"properties": {"title": title}}
            result = self.spreadsheets.create(body=spreadsheet).execute()
            return result
        except HttpError as error:
            raise error
