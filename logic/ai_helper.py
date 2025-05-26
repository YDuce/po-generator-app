import logging
from typing import List, Dict, Any, Optional
import openai
from models.listing import Listing
from models.allocation import Allocation
from channels import get_connector

logger = logging.getLogger(__name__)

class AIHelper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
    
    def validate_listing(self, listing: Listing) -> Dict[str, Any]:
        """Use AI to validate listing data."""
        try:
            prompt = f"""
            Analyze this listing and provide validation feedback:
            SKU: {listing.external_sku}
            Title: {getattr(listing, 'title', '')}
            Quantity: {getattr(listing, 'current_quantity', 0)}
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an inventory data validation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return {
                'is_valid': True,
                'feedback': response.choices[0].message.content,
                'suggestions': []
            }
        except Exception as e:
            logger.error(f"Error validating listing: {str(e)}")
            return {
                'is_valid': False,
                'feedback': f"Error during validation: {str(e)}",
                'suggestions': []
            }
    
    def analyze_allocation_trends(self, allocations: List[Allocation]) -> Dict[str, Any]:
        try:
            channel_data = {}
            for allocation in allocations:
                if allocation.channel not in channel_data:
                    channel_data[allocation.channel] = {
                        'total_qty': 0,
                        'item_count': 0,
                        'avg_qty': 0
                    }
                channel_data[allocation.channel]['total_qty'] += allocation.qty
                channel_data[allocation.channel]['item_count'] += 1
            for channel in channel_data:
                if channel_data[channel]['item_count'] > 0:
                    channel_data[channel]['avg_qty'] = (
                        channel_data[channel]['total_qty'] /
                        channel_data[channel]['item_count']
                    )
            prompt = f"""
            Analyze these allocation patterns and provide insights:
            {channel_data}
            Provide analysis on:
            1. Channel distribution patterns
            2. Potential optimization opportunities
            3. Recommendations for allocation rules
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an inventory allocation optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return {
                'channel_data': channel_data,
                'analysis': response.choices[0].message.content,
                'recommendations': []
            }
        except Exception as e:
            logger.error(f"Error analyzing allocation trends: {str(e)}")
            return {
                'channel_data': {},
                'analysis': f"Error during analysis: {str(e)}",
                'recommendations': []
            }
    
    def suggest_allocation_rules(self, 
                               listings: List[Listing],
                               allocations: List[Allocation]) -> List[Dict[str, Any]]:
        try:
            historical_data = {
                'listings': [l.id for l in listings],
                'allocations': [a.id for a in allocations]
            }
            prompt = f"""
            Based on this historical data, suggest optimal allocation rules:
            {historical_data}
            Consider:
            1. Channel priorities
            2. Minimum and maximum quantities
            3. Special handling requirements
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an inventory allocation rules optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            suggested_rules = []
            for line in response.choices[0].message.content.split('\n'):
                if 'channel' in line.lower() and 'priority' in line.lower():
                    suggested_rules.append({
                        'channel': line.split(':')[0].strip(),
                        'priority': int(line.split(':')[1].strip()),
                        'min_qty': 0,
                        'max_qty': None
                    })
            return suggested_rules
        except Exception as e:
            logger.error(f"Error suggesting allocation rules: {str(e)}")
            return []
    
    def validate_allocation_decision(self, 
                                   allocation: Allocation,
                                   listing: Listing) -> Dict[str, Any]:
        try:
            prompt = f"""
            Validate this allocation decision:
            Listing: {listing.id}
            Allocation: {allocation.id}
            Consider:
            1. Business rules and constraints
            2. Historical patterns
            3. Channel requirements
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an allocation validation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return {
                'is_valid': True,
                'feedback': response.choices[0].message.content,
                'suggestions': []
            }
        except Exception as e:
            logger.error(f"Error validating allocation decision: {str(e)}")
            return {
                'is_valid': False,
                'feedback': f"Error during validation: {str(e)}",
                'suggestions': []
            }
