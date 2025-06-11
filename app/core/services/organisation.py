from flask import current_app
from app.extensions import db
from app.core.models.organisation import Organisation
from app.core.services.google.drive import GoogleDriveService
from googleapiclient.errors import HttpError

class OrganisationService:
    """
    Service for creating and managing Organisations and their Drive folders.
    """

    @staticmethod
    def _get_or_create_folder(drive: GoogleDriveService, name: str, parent_id: str = None) -> str:
        """
        Idempotently find or create a Drive folder by name under an optional parent.
        Returns the folder ID.
        """
        # Build Drive API query
        query_parts = ["mimeType='application/vnd.google-apps.folder'", f"name='{name}'"]
        if parent_id:
            query_parts.append(f"'{parent_id}' in parents")
        query = ' and '.join(query_parts)
        try:
            result = drive.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id,name)',
            ).execute()
            items = result.get('files', [])
            if items:
                return items[0]['id']
        except HttpError as e:
            current_app.logger.error(f"Drive list query failed: {e}")
        # If not found or list failed, create new folder
        folder = drive.create_folder(name=name, parent_id=parent_id)
        return folder['id']

    @staticmethod
    def create_organisation(name: str, admin_user_email: str) -> Organisation:
        """
        Create a new Organisation record and its Drive folder. Shares folder with admin user.
        Raises ValueError on duplicate organisation name.
        """
        # Prevent duplicate organisations
        if Organisation.query.filter_by(name=name).first():
            raise ValueError(f"Organisation '{name}' already exists")

        org = Organisation(name=name, drive_folder_id='')
        db.session.add(org)
        db.session.flush()  # gets org.id without commit

        # Service-account credentials
        creds = current_app.config['GOOGLE_SVC_CREDS']
        drive = GoogleDriveService(creds)

        # Idempotent folder creation
        folder_id = OrganisationService._get_or_create_folder(drive, name, None)
        org.drive_folder_id = folder_id
        db.session.commit()

        # Share folder with admin user
        try:
            drive.service.permissions().create(
                fileId=folder_id,
                body={
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': admin_user_email
                }
            ).execute()
        except HttpError as e:
            current_app.logger.error(f"Failed to share organisation folder: {e}")

        return org

    @staticmethod
    def ensure_channel_folder(org: Organisation, channel_name: str) -> str:
        """
        Ensure a subfolder for the given channel under the organisation's Drive folder.
        Returns the channel folder ID.
        """
        creds = current_app.config['GOOGLE_SVC_CREDS']
        drive = GoogleDriveService(creds)
        return OrganisationService._get_or_create_folder(
            drive,
            channel_name,
            parent_id=org.drive_folder_id
        )
