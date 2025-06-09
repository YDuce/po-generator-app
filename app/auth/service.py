"""Re-export AuthService for backward compatibility.

Layer: api
"""

from app.core.auth.service import AuthService

__all__ = ["AuthService"]
