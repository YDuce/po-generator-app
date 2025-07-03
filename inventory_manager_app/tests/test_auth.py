from inventory_manager_app import create_app, db
from inventory_manager_app.core.models import User
from inventory_manager_app.core.utils.auth import hash_password


def test_login_flow(tmp_path):
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{tmp_path/'test.db'}"
    with app.app_context():
        db.create_all()
        user = User(email="test@example.com", password_hash=hash_password("secret"), organisation_id=1)
        db.session.add(user)
        db.session.commit()
    with app.test_client() as client:
        resp = client.post('/api/v1/login', json={'email': 'test@example.com', 'password': 'secret'})
        assert resp.status_code == 200
        assert 'token' in resp.get_json()
