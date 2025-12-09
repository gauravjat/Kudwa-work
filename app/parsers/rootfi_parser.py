"""
Parser for Rootfi data format.
"""
import json
from typing import Dict, List, Any

from app.exceptions import DataSourceError


class RootfiParser:
    """Parse Rootfi financial data format."""
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Rootfi JSON file and extract financial data.
        
        Args:
            file_path: Path to Rootfi JSON file
            
        Returns:
            List of dictionaries containing financial data
            
        Raises:
            DataSourceError: If file cannot be read or parsed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise DataSourceError(f"Rootfi data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DataSourceError(f"Invalid JSON in Rootfi file: {e}")
        
        try:
            return self._transform_data(data['data'])
        except Exception as e:
            raise DataSourceError(f"Failed to parse Rootfi data: {e}")
    
    def _transform_data(self, records: List[Dict]) -> List[Dict[str, Any]]:
        """Transform Rootfi records to unified format."""
        transformed = []
        
        for record in records:
            period_data = {
                'period_start': record['period_start'],
                'period_end': record['period_end'],
                'source': 'rootfi',
                'revenue': self._sum_line_items(record.get('revenue', [])),
                'cost_of_goods_sold': self._sum_line_items(record.get('cost_of_goods_sold', [])),
                'gross_profit': record.get('gross_profit', 0.0),
                'operating_expenses': self._sum_line_items(record.get('operating_expenses', [])),
                'operating_profit': record.get('operating_profit', 0.0),
                'non_operating_revenue': self._sum_line_items(record.get('non_operating_revenue', [])),
                'non_operating_expenses': self._sum_line_items(record.get('non_operating_expenses', [])),
                'net_profit': record.get('net_profit', 0.0),
                'revenue_breakdown': self._extract_breakdown(record.get('revenue', [])),
                'expense_breakdown': self._extract_breakdown(record.get('operating_expenses', []))
            }
            
            transformed.append(period_data)
        
        return transformed
    
    def _sum_line_items(self, line_items: List[Dict]) -> float:
        """Sum values from line items."""
        total = 0.0
        for item in line_items:
            total += item.get('value', 0.0)
        return total
    
    def _extract_breakdown(self, line_items: List[Dict]) -> Dict[str, float]:
        """Extract detailed breakdown from line items."""
        breakdown = {}
        
        for item in line_items:
            name = item.get('name', 'Unknown')
            value = item.get('value', 0.0)
            
            if value != 0:
                breakdown[name] = value
            
            # Include sub-items
            if 'line_items' in item and item['line_items']:
                sub_breakdown = self._extract_breakdown(item['line_items'])
                breakdown.update(sub_breakdown)
        
        return breakdown

