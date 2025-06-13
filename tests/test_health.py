from app import create_app

def test_health_endpoint(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json == {'status': 'ok'}
