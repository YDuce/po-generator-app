import os
from app.channels import import_channel, ALLOWED_CHANNELS

def preload_adapters() -> None:
    names = os.getenv("SYNC_CHANNELS", ",".join(ALLOWED_CHANNELS)).split(",")
    for name in filter(None, names):
        try:
            import_channel(name)
        except ModuleNotFoundError:  # channel package not deployed
            continue
