"""Optional mixin for channels providing spreadsheet templates.

Layer: channels
"""

from abc import ABC, abstractmethod
from typing import Dict

__all__ = ["SpreadsheetTemplateProvider"]


class SpreadsheetTemplateProvider(ABC):
    """Provide paths to channel-specific spreadsheet templates."""

    @abstractmethod
    def list_templates(self) -> Dict[str, str]:
        """Return mapping of template keys to relative file paths."""
        raise NotImplementedError
