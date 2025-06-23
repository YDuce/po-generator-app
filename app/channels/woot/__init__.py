"""Import side-effects: register adapter and expose blueprint."""
from .adapter import WootAdapter  # noqa: F401  # registers via decorator
from .routes import bp  # blueprint

__all__ = ["bp", "WootAdapter"]
