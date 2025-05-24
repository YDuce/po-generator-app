import logging
from typing import List, Dict, Any, Optional
import openai
from models.inventory import InventoryItem
from models.allocation import Allocation

logger = logging.getLogger(__name__)

class AIHelper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
    
    def validate_inventory_item(self, item: InventoryItem) -> Dict[str, Any]:
        """Use AI to validate inventory item data."""
        try:
            prompt = f"""
            Analyze this inventory item and provide validation feedback:
            SKU: {item.sku}
            Name: {item.name}
            Description: {item.description}
            Quantity: {item.qty_on_hand}
            
            Provide feedback on:
            1. Data quality and completeness
            2. Potential issues or inconsistencies
            3. Suggestions for improvement
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
                'is_valid': True,  # You might want to implement actual validation logic
                'feedback': response.choices[0].message.content,
                'suggestions': []  # You could parse the response to extract specific suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating inventory item: {str(e)}")
            return {
                'is_valid': False,
                'feedback': f"Error during validation: {str(e)}",
                'suggestions': []
            }
    
    def analyze_allocation_trends(self, allocations: List[Allocation]) -> Dict[str, Any]:
        """Analyze allocation patterns and trends."""
        try:
            # Prepare data for analysis
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
            
            # Calculate averages
            for channel in channel_data:
                if channel_data[channel]['item_count'] > 0:
                    channel_data[channel]['avg_qty'] = (
                        channel_data[channel]['total_qty'] / 
                        channel_data[channel]['item_count']
                    )
            
            # Generate AI analysis
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
                'recommendations': []  # You could parse the response to extract specific recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing allocation trends: {str(e)}")
            return {
                'channel_data': {},
                'analysis': f"Error during analysis: {str(e)}",
                'recommendations': []
            }
    
    def suggest_allocation_rules(self, 
                               items: List[InventoryItem],
                               allocations: List[Allocation]) -> List[Dict[str, Any]]:
        """Suggest optimal allocation rules based on historical data."""
        try:
            # Prepare historical data
            historical_data = {
                'items': [item.to_dict() for item in items],
                'allocations': [allocation.to_dict() for allocation in allocations]
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
            
            # Parse the response to extract specific rules
            # This is a simplified example - you might want to implement more sophisticated parsing
            suggested_rules = []
            for line in response.choices[0].message.content.split('\n'):
                if 'channel' in line.lower() and 'priority' in line.lower():
                    suggested_rules.append({
                        'channel': line.split(':')[0].strip(),
                        'priority': int(line.split(':')[1].strip()),
                        'min_qty': 0,  # You might want to extract these from the response
                        'max_qty': None
                    })
            
            return suggested_rules
            
        except Exception as e:
            logger.error(f"Error suggesting allocation rules: {str(e)}")
            return []
    
    def validate_allocation_decision(self, 
                                   allocation: Allocation,
                                   item: InventoryItem) -> Dict[str, Any]:
        """Validate an allocation decision using AI."""
        try:
            prompt = f"""
            Validate this allocation decision:
            Item: {item.to_dict()}
            Allocation: {allocation.to_dict()}
            
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
                'is_valid': True,  # You might want to implement actual validation logic
                'feedback': response.choices[0].message.content,
                'suggestions': []  # You could parse the response to extract specific suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating allocation decision: {str(e)}")
            return {
                'is_valid': False,
                'feedback': f"Error during validation: {str(e)}",
                'suggestions': []
            }
