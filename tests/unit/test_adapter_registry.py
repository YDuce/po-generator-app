from app.channels import import_channel, get_adapter


def test_get_adapter_returns_instance():
    import_channel("woot")
    adapter = get_adapter("woot")
    assert hasattr(adapter, "fetch_orders")
