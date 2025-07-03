"""Simple channel registry and loader."""

from importlib import import_module
from types import ModuleType
from typing import Dict

CHANNELS = ["amazon", "ebay", "woot"]


def load_channels() -> Dict[str, ModuleType]:
    loaded: Dict[str, ModuleType] = {}
    for name in CHANNELS:
        try:
            module = import_module(f"inventory_manager_app.channels.{name}.actions")
            loaded[name] = module
        except ModuleNotFoundError:
            continue
    return loaded
