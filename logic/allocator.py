import logging
from typing import List, Dict, Any
from models import db
from models.inventory import InventoryItem
from models.allocation import Allocation

logger = logging.getLogger(__name__)

class AllocationRule:
    def __init__(self, channel: str, priority: int = 0, min_qty: int = 0, max_qty: int = None):
        self.channel = channel
        self.priority = priority
        self.min_qty = min_qty
        self.max_qty = max_qty

class AllocationEngine:
    def __init__(self):
        self.rules: List[AllocationRule] = []
    
    def add_rule(self, rule: AllocationRule):
        """Add an allocation rule."""
        self.rules.append(rule)
        # Sort rules by priority (higher priority first)
        self.rules.sort(key=lambda x: x.priority, reverse=True)
    
    def allocate(self, items: List[InventoryItem]) -> List[Allocation]:
        """Apply allocation rules to inventory items."""
        allocations = []
        
        try:
            for item in items:
                remaining_qty = item.qty_on_hand
                
                # Apply rules in priority order
                for rule in self.rules:
                    if remaining_qty <= 0:
                        break
                    
                    # Calculate allocation quantity
                    alloc_qty = min(
                        remaining_qty,
                        rule.max_qty if rule.max_qty is not None else remaining_qty
                    )
                    
                    if alloc_qty >= rule.min_qty:
                        # Create allocation
                        allocation = Allocation(
                            item_id=item.id,
                            channel=rule.channel,
                            qty=alloc_qty,
                            priority=rule.priority,
                            is_auto_allocated=True
                        )
                        allocations.append(allocation)
                        remaining_qty -= alloc_qty
                
                # If there's remaining quantity, create a default allocation
                if remaining_qty > 0:
                    allocation = Allocation(
                        item_id=item.id,
                        channel='default',
                        qty=remaining_qty,
                        priority=0,
                        is_auto_allocated=True,
                        notes='Unallocated quantity'
                    )
                    allocations.append(allocation)
            
            # Save allocations to database
            db.session.add_all(allocations)
            db.session.commit()
            
            return allocations
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during allocation: {str(e)}")
            raise
    
    def get_channel_summary(self, allocations: List[Allocation]) -> Dict[str, int]:
        """Get summary of allocations by channel."""
        summary = {}
        for allocation in allocations:
            summary[allocation.channel] = summary.get(allocation.channel, 0) + allocation.qty
        return summary
    
    def validate_allocation(self, allocation: Allocation) -> bool:
        """Validate if an allocation is valid."""
        try:
            item = InventoryItem.query.get(allocation.item_id)
            if not item:
                return False
            
            # Check if allocation quantity is valid
            if allocation.qty <= 0:
                return False
            
            # Check if allocation quantity is available
            allocated_qty = sum(
                a.qty for a in item.allocations 
                if a.id != allocation.id and a.status != 'rejected'
            )
            if allocated_qty + allocation.qty > item.qty_on_hand:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating allocation: {str(e)}")
            return False
