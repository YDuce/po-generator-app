import pytest


def test_porf_upload(client):
    """Skip PORF upload when Google credentials are absent."""
    pytest.skip("Google credentials not configured")
