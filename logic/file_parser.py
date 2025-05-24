import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {'sku', 'title', 'cost', 'external_sku', 'status'}

class FileParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        self.supported_extensions = {'.xlsx', '.xls', '.csv'}
        if self.file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {self.file_path.suffix}")

    def parse_catalog(self) -> List[Dict[str, Any]]:
        """Parse catalog file and return list of validated product/listing dicts."""
        try:
            if self.file_path.suffix.lower() == '.csv':
                df = pd.read_csv(self.file_path)
            else:
                df = pd.read_excel(self.file_path)

            missing_columns = REQUIRED_COLUMNS - set(df.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Clean and validate data
            df['sku'] = df['sku'].astype(str).str.strip()
            df['title'] = df['title'].astype(str).str.strip()
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
            df['external_sku'] = df['external_sku'].astype(str).str.strip()
            df['status'] = df['status'].astype(str).str.strip().str.lower()

            items = df.to_dict('records')

            for item in items:
                if not item['sku']:
                    raise ValueError("SKU cannot be empty")
                if not item['title']:
                    raise ValueError("Title cannot be empty")
                if item['cost'] < 0:
                    raise ValueError(f"Cost cannot be negative for SKU: {item['sku']}")
                if not item['external_sku']:
                    raise ValueError(f"External SKU cannot be empty for SKU: {item['sku']}")
                if item['status'] not in {'active', 'inactive'}:
                    raise ValueError(f"Status must be 'active' or 'inactive' for SKU: {item['sku']}")

            return items
        except Exception as e:
            logger.error(f"Error parsing catalog file: {str(e)}")
            raise
