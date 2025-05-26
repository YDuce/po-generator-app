from .woot import WootConnector
# Future: from .amazon import AmazonConnector, etc.

def get_connector(name: str, session=None):
    if name == 'woot':
        return WootConnector(session=session)
    # Add more mappings as plugins arrive
    raise ValueError(f"Unknown channel: {name}") 