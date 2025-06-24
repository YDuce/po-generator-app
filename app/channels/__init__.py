from __future__ import annotations

import abc
import importlib
from typing import Iterable, Final

from app.core.logic.orders import OrderPayload

__all__ = [
    "ChannelAdapter",
    "Channel",
    "ALLOWED_CHANNELS",
    "register",
    "get_adapter",
    "import_channel",
]

# ───────────────────────────── supported channels ───────────────────────────
from enum import Enum, unique

@unique
class Channel(str, Enum):
    WOOT = "woot"
    AMAZON = "amazon"
    EBAY = "ebay"
    SHOPIFY = "shopify"

    def __str__(self) -> str:  # pragma: no cover
        return self.value

# Single source of truth for validation elsewhere
ALLOWED_CHANNELS: Final[set[str]] = {c.value for c in Channel}

# ───────────────────────────── adapter contract ─────────────────────────────

class ChannelAdapter(abc.ABC):
    """Every concrete adapter must implement this interface."""

    @abc.abstractmethod
    def fetch_orders(self) -> Iterable[OrderPayload]:  # pragma: no cover
        """Yield raw order payloads from the remote channel."""

# ───────────────────────────── in‑memory registry ───────────────────────────

_REGISTRY: dict[str, type[ChannelAdapter]] = {}


def register(name: str):
    """Decorator to register a concrete adapter class under *name*."""
    if name not in ALLOWED_CHANNELS:
        raise ValueError(f"'{name}' is not a recognised channel name")

    def decorator(cls: type[ChannelAdapter]) -> type[ChannelAdapter]:
        # Cheap interface check: must implement fetch_orders
        if not callable(getattr(cls, "fetch_orders", None)):
            raise TypeError(f"{cls.__name__} lacks required method 'fetch_orders()'")
        _REGISTRY[name] = cls
        return cls

    return decorator


# ───────────────────────────── import helpers ───────────────────────────────

def import_channel(name: str) -> None:
    """Import ``app.channels.<name>`` so its decorators run.

    Safe to call multiple times – Python caches modules after the first import.
    """
    importlib.import_module(f"app.channels.{name}")


# Optional lazy‑import fallback (for zero‑downtime adapter rollout).
# Comment‑out this helper if you prefer to restart workers on every deploy.

def _lazy_import_if_needed(name: str) -> None:
    if name in _REGISTRY:
        return
    try:
        import_channel(name)
    except ModuleNotFoundError:
        # keep registry empty – caller will raise ValueError later
        pass


# ───────────────────────────── public accessor ──────────────────────────────

def get_adapter(name: str) -> ChannelAdapter:
    """Return a *new* adapter instance for ``name``.

    First call is O(module import); subsequent calls are O(1) dict lookup.
    """
    if name not in _REGISTRY:
        _lazy_import_if_needed(name)
    try:
        cls = _REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"unknown channel '{name}'") from exc
    return cls()  # type: ignore[call-arg]