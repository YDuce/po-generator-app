from __future__ import annotations

from app.extensions import db
from app.core.models import Organisation
from .google import GoogleDriveService


class OrganisationService:
    def __init__(self, drive: GoogleDriveService) -> None:
        self._drive = drive

    def create(self, name: str, admin_email: str) -> Organisation:
        if Organisation.query.filter_by(name=name).first():
            raise ValueError("organisation exists")

        folder = self._drive.create_folder(name)
        org = Organisation(name=name, drive_folder_id=folder["id"])
        db.session.add(org)
        db.session.flush()

        self._drive.share_folder(folder["id"], admin_email, role="writer")

        db.session.commit()
        return org
