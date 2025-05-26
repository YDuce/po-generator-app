import logging
from typing import List, Dict, Any
from models.listing import Listing
from models.allocation import Allocation
from channels import get_connector

logger = logging.getLogger(__name__)

class AllocationRule:
    def __init__(self, channel: str, priority: int = 0, min_qty: int = 0, max_qty: int = None):
        self.channel = channel
        self.priority = priority
        self.min_qty = min_qty
        self.max_qty = max_qty

class AllocationEngine:
    def __init__(self, session=None):
        self.rules: List[AllocationRule] = []
        self.session = session
    
    def add_rule(self, rule: AllocationRule):
        """Add an allocation rule."""
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)
    
    def allocate(self, listings: List[Listing]) -> List[Allocation]:
        """Apply allocation rules to listings."""
        allocations = []
        try:
            for listing in listings:
                remaining_qty = getattr(listing, 'current_quantity', 0)
                for rule in self.rules:
                    if remaining_qty <= 0:
                        break
                    alloc_qty = min(
                        remaining_qty,
                        rule.max_qty if rule.max_qty is not None else remaining_qty
                    )
                    if alloc_qty >= rule.min_qty:
                        allocation = Allocation(
                            listing_id=listing.id,
                            channel=rule.channel,
                            qty=alloc_qty,
                            priority=rule.priority,
                            is_auto_allocated=True
                        )
                        allocations.append(allocation)
                        remaining_qty -= alloc_qty
                if remaining_qty > 0:
                    allocation = Allocation(
                        listing_id=listing.id,
                        channel='default',
                        qty=remaining_qty,
                        priority=0,
                        is_auto_allocated=True,
                        notes='Unallocated quantity'
                    )
                    allocations.append(allocation)
            if self.session:
                self.session.add_all(allocations)
                self.session.commit()
            return allocations
        except Exception as e:
            if self.session:
                self.session.rollback()
            logger.error(f"Error during allocation: {str(e)}")
            raise
    
    def get_channel_summary(self, allocations: List[Allocation]) -> Dict[str, int]:
        summary = {}
        for allocation in allocations:
            summary[allocation.channel] = summary.get(allocation.channel, 0) + allocation.qty
        return summary
    
    def validate_allocation(self, allocation: Allocation) -> bool:
        try:
            # Validation logic can be implemented here
            if allocation.qty <= 0:
                return False
            return True
        except Exception as e:
            logger.error(f"Error validating allocation: {str(e)}")
            return False
