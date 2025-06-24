import pytest

from app.core.models import User, Organisation
from app.extensions import db


def test_bad_channel_validation(app):
    with app.app_context():
        org = Organisation(name="Acme", drive_folder_id="F" * 25 + "1")
        db.session.add(org)
        db.session.commit()

        user = User(email="a@example.com", organisation=org, allowed_channels=["woot"])
        db.session.add(user)
        db.session.commit()

        with pytest.raises(ValueError):
            user.allowed_channels = user.allowed_channels + ["bogus"]
            db.session.flush()
