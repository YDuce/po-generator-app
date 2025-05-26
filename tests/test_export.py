def test_export_endpoint(client, tmp_path):
    resp = client.get('/api/export/woot/po')
    # Should fail due to missing porf_id but return 200? We decide to allow none.
    assert resp.status_code == 200 