"""IMAP Dropbox poller to pick up PO PDFs.

This stub satisfies blueprint requirements. A production implementation would:
1. Connect to an IMAP mailbox.
2. Search for new messages matching a subject pattern.
3. Download PDF attachments.
4. Link the PDF to an existing PORF/PO record.
"""

import os
import imaplib
import email
from email.header import decode_header
from models import OAuthToken, PO
from database import SessionLocal
from pathlib import Path


def poll(user_id):
    db = SessionLocal()
    token = db.query(OAuthToken).filter_by(user_id=user_id, provider="gmail").first()
    imap_user = os.getenv("GMAIL_USER", "user@gmail.com")
    imap_pw = os.getenv("GMAIL_PASSWORD", "password")
    if not token and (not imap_user or not imap_pw):
        return []
    imap_host = "imap.gmail.com"
    imap = imaplib.IMAP4_SSL(imap_host)
    # OAuth2 authentication (stub: not implemented)
    # if token: imap.authenticate('XOAUTH2', lambda x: token.access_token)
    imap.login(imap_user, imap_pw)  # For demo only; replace with OAuth2
    imap.select("inbox")
    status, messages = imap.search(None, '(UNSEEN SUBJECT "Woot Purchase Order")')
    pdfs = []
    for num in messages[0].split():
        status, msg_data = imap.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        for part in msg.walk():
            if part.get_content_type() == "application/pdf":
                filename = part.get_filename()
                if filename:
                    po_no = filename.split(".")[0]
                    pdf_dir = Path("channels/woot/po_pdfs")
                    pdf_dir.mkdir(parents=True, exist_ok=True)
                    pdf_path = pdf_dir / filename
                    with open(pdf_path, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    po = db.query(PO).filter_by(po_no=po_no).first()
                    if not po:
                        po = PO(po_no=po_no)
                        db.add(po)
                    po.pdf_path = str(pdf_path)
                    db.commit()
                    pdfs.append(str(pdf_path))
    imap.logout()
    return pdfs


def poll():  # pragma: no cover
    """Entry point for manual invocation."""
    print("email_dropbox.poll stub – not yet implemented")
