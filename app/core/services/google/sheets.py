import os, logging
from typing import List, TypedDict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)
SyncEnabled = os.getenv('TWO_WAY_SYNC_ENABLED','false').lower()=='true'

class SheetResponse(TypedDict):
    spreadsheetId: str
    updatedRange: str
    updatedRows: int
    updatedColumns: int
    updatedCells: int

class GoogleSheetsService:
    def __init__(self, creds: Credentials):
        if not creds or not creds.valid:
            raise ValueError('Invalid credentials')
        self.spreadsheets = build('sheets','v4',credentials=creds).spreadsheets()

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def get_sheet_data(self,id:str,range_name:str)->List[List[Any]]:
        return self.spreadsheets.values().get(spreadsheetId=id,range=range_name).execute().get('values',[])

    def _check_sync(self):
        if not SyncEnabled:
            raise RuntimeError('two-way sync disabled')

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def update_sheet_data(self,id:str,range_name:str,values:List[List[Any]])->SheetResponse:
        self._check_sync()
        return self.spreadsheets.values().update(
            spreadsheetId=id,range=range_name,valueInputOption='RAW',body={'values':values}
        ).execute()

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def append_sheet_data(self,id:str,range_name:str,values:List[List[Any]])->SheetResponse:
        self._check_sync()
        return self.spreadsheets.values().append(
            spreadsheetId=id,range=range_name,insertDataOption='INSERT_ROWS',valueInputOption='RAW',body={'values':values}
        ).execute()

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def clear_sheet_data(self,id:str,range_name:str)->SheetResponse:
        self._check_sync()
        return self.spreadsheets.values().clear(spreadsheetId=id,range=range_name).execute()

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def create_sheet(self,title:str,folder_id:str)->dict:
        self._check_sync()
        return self.spreadsheets.create(body={'properties':{'title':title}}).execute()
