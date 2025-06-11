import os, logging
from flask import current_app
from app.core.services.google.drive import GoogleDriveService
from app.core.services.google.sheets import GoogleSheetsService
from app.channels.woot.models import WootPorf, WootPorfLine
from app.extensions import db

logger=logging.getLogger(__name__)

class WootService:
    def __init__(self):
        creds = current_app.config['GOOGLE_SVC_CREDS']
        self.drive=GoogleDriveService(creds)
        self.sheets=GoogleSheetsService(creds)

    def create_porf(self,data:dict)->WootPorf:
        porf=WootPorf(porf_no=data['porf_no'])
        db.session.add(porf)
        for ln in data['lines']:
            db.session.add(WootPorfLine(porf=porf,product_id=ln['product_id'],quantity=ln['quantity']))
        db.session.commit()
        return porf
