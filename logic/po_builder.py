import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from models import db
from models.inventory import InventoryItem
from models.allocation import Allocation

logger = logging.getLogger(__name__)

class POBuilder:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def build_po(self, allocations: List[Allocation], channel: str) -> str:
        """Build purchase order for a specific channel."""
        try:
            # Filter allocations for the channel
            channel_allocations = [a for a in allocations if a.channel == channel]
            if not channel_allocations:
                raise ValueError(f"No allocations found for channel: {channel}")
            
            # Get inventory items
            item_ids = [a.item_id for a in channel_allocations]
            items = InventoryItem.query.filter(InventoryItem.id.in_(item_ids)).all()
            items_dict = {item.id: item for item in items}
            
            # Prepare data for Excel
            data = []
            for allocation in channel_allocations:
                item = items_dict.get(allocation.item_id)
                if not item:
                    continue
                
                data.append({
                    'SKU': item.sku,
                    'Name': item.name,
                    'Description': item.description,
                    'Quantity': allocation.qty,
                    'Status': allocation.status,
                    'Notes': allocation.notes
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"PO_{channel}_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Write to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Purchase Order', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Purchase Order']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error building PO for channel {channel}: {str(e)}")
            raise
    
    def build_all_pos(self, allocations: List[Allocation]) -> Dict[str, str]:
        """Build purchase orders for all channels."""
        try:
            # Get unique channels
            channels = set(a.channel for a in allocations)
            
            # Build PO for each channel
            po_files = {}
            for channel in channels:
                if channel == 'default':
                    continue  # Skip default channel
                po_file = self.build_po(allocations, channel)
                po_files[channel] = po_file
            
            return po_files
            
        except Exception as e:
            logger.error(f"Error building all POs: {str(e)}")
            raise
    
    def generate_summary(self, allocations: List[Allocation]) -> str:
        """Generate summary report of all allocations."""
        try:
            # Get channel summary
            channels = set(a.channel for a in allocations)
            summary_data = []
            
            for channel in channels:
                channel_allocations = [a for a in allocations if a.channel == channel]
                total_qty = sum(a.qty for a in channel_allocations)
                total_items = len(set(a.item_id for a in channel_allocations))
                
                summary_data.append({
                    'Channel': channel,
                    'Total Items': total_items,
                    'Total Quantity': total_qty,
                    'Status': 'Complete' if all(a.status == 'approved' for a in channel_allocations) else 'Pending'
                })
            
            # Create DataFrame
            df = pd.DataFrame(summary_data)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Allocation_Summary_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Write to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Summary']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
