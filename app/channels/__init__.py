"""Channel-adapter registry and contract (explicit-import flavour)."""
from __future__ import annotations

import abc
import importlib
from typing import Iterable

from app.core.logic.orders import OrderPayload

__all__ = [
    "ChannelAdapter",
    "register",
    "get_adapter",
    "import_channel",
]


# ───────────────────────── contract ────────────────────────────


class ChannelAdapter(abc.ABC):
    @abc.abstractmethod
    def fetch_orders(self) -> Iterable[OrderPayload]:  # pragma: no cover
        ...


# ───────────────────────── registry ────────────────────────────

_REGISTRY: dict[str, type[ChannelAdapter]] = {}


def register(name: str):
    """Decorator: @register("woot")"""

    def _wrap(cls: type[ChannelAdapter]) -> type[ChannelAdapter]:
        _REGISTRY[name] = cls
        return cls

    return _wrap


def get_adapter(name: str) -> ChannelAdapter:
    try:
        return _REGISTRY[name]()  # type: ignore[call-arg]
    except KeyError as exc:
        raise ValueError(f"unknown channel '{name}'") from exc


# ───────────────────────── explicit import helper ──────────────

def import_channel(name: str) -> None:
    """
    Import ``app.channels.<name>`` so its @register runs.

    Safe to call repeatedly—Python caches imports.
    """
    importlib.import_module(f"app.channels.{name}")
