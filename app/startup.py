import logging
import os

from app.channels import ALLOWED_CHANNELS, import_channel

log = logging.getLogger(__name__)


def preload_adapters() -> None:
    names = os.getenv("SYNC_CHANNELS", ",".join(ALLOWED_CHANNELS)).split(",")
    for name in filter(None, names):
        try:
            import_channel(name)
        except ModuleNotFoundError:
            log.warning("SYNC_CHANNELS lists '%s' but adapter package not deployed", name)
