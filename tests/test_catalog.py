import io
import pytest
from app import create_app
from database import SessionLocal, Base

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Create all tables for test DB
            Base.metadata.create_all(bind=SessionLocal().bind)
        yield client
        with app.app_context():
            # Drop all tables after test
            Base.metadata.drop_all(bind=SessionLocal().bind)

def test_catalog_upload_success(client):
    csv = b"sku,title,external_sku,status,price\nABC,Widget,WGT-1,active,9.99"
    data = {
        'inventory': (io.BytesIO(csv), 'test.csv'),
        'channel': 'woot'
    }
    resp = client.post('/api/catalog', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert resp.json['status'] == 'success'

def test_catalog_upload_missing_field(client):
    resp = client.post('/api/catalog', data={'channel': 'woot'})
    assert resp.status_code == 400
    assert 'error' in resp.json 