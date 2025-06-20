from app.extensions import db
from app.core.models import Organisation
from app.core.services.google import GoogleDriveService

class OrganisationService:
    def __init__(self, drive_service: GoogleDriveService):
        self.drive_service = drive_service

    def create_organisation(self, name: str, admin_email: str) -> Organisation:
        if Organisation.query.filter_by(name=name).first():
            raise ValueError("organisation exists")

        folder = self.drive_service.create_folder(name)
        org = Organisation(name=name, drive_folder_id=folder["id"])
        db.session.add(org)
        db.session.flush()

        self.drive_service.share_folder(folder["id"], admin_email, role="writer")

        db.session.commit()
        return org
