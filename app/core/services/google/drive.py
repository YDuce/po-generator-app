import os, json, logging
from typing import List, Optional, TypedDict
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from tenacity import retry, stop_after_attempt, wait_exponential

logger=logging.getLogger(__name__)

class FileMetadata(TypedDict):
    id:str; name:str; mimeType:str; parents:Optional[List[str]]

class GoogleDriveService:
    def __init__(self,creds:Optional[Credentials]=None):
        if not creds:
            info=json.loads(os.getenv('GOOGLE_SVC_KEY','{}'))
            creds=service_account.Credentials.from_service_account_info(info,scopes=['https://www.googleapis.com/auth/drive'])
        self.files=build('drive','v3',credentials=creds).files()

    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def create_folder(self,name:str,parent_id:str)->FileMetadata:
        md={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent_id]}
        return self.files.create(body=md,fields='id').execute()
    @retry(stop=stop_after_attempt(3),wait=wait_exponential())
    def upload_file(self,file_path:str,mime_type:str,parents:Optional[List[str]]=None)->FileMetadata:
        media=MediaFileUpload(file_path,mimetype=mime_type,resumable=True)
        body={'name':os.path.basename(file_path),'mimeType':mime_type}
        if parents:body['parents']=parents
        return self.files.create(body=body,media_body=media,fields='id').execute()
    # add other methods similarly...
