import io
import pytest


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