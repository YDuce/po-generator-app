import logging
from app.extensions import db
from app.core.models.organisation import Organisation
from app.core.services.google.drive import GoogleDriveService

log = logging.getLogger(__name__)

class OrganisationService:
    def __init__(self, drive: GoogleDriveService): self.drive = drive
    def create_organisation(self, name: str, admin_email: str) -> Organisation:
        if Organisation.query.filter_by(name=name).first():
            raise ValueError("organisation exists")
        org = Organisation(name=name, drive_folder_id="")
        db.session.add(org)
        db.session.flush()
        folder = self.drive.create_folder(name)
        org.drive_folder_id = folder["id"]
        self.drive.service.permissions().create(
            fileId=folder["id"],
            body={"type": "user", "role": "writer", "emailAddress": admin_email}
        ).execute()
        db.session.commit()
        return org
