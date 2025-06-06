from abc import ABC, abstractmethod
from typing import Dict


class SpreadsheetTemplateProvider(ABC):
    """
    Optional mix-in for channels that need to export data
    through CSV/XLSX templates.
    """

    @abstractmethod
    def list_templates(self) -> Dict[str, str]:
        """
        Return mapping  {'template_key': 'spreadsheets/relative_path.ext', …}
        Example for Woot:
           {'po': 'spreadsheets/woot_po.xlsx',
            'report': 'spreadsheets/woot_sales.xlsx'}
        """
        ...
