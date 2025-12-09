"""
Data validation utilities.
"""
from datetime import datetime
from typing import Dict, Any

from app.exceptions import DataValidationError


class FinancialDataValidator:
    """Validator for financial data."""
    
    @staticmethod
    def validate_period_data(data: Dict[str, Any]) -> bool:
        """
        Validate financial period data.
        
        Args:
            data: Dictionary containing period data
            
        Returns:
            True if valid
            
        Raises:
            DataValidationError: If validation fails
        """
        # Required fields
        required_fields = ['period_start', 'period_end', 'source']
        
        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"Missing required field: {field}")
        
        # Validate dates
        try:
            start_date = datetime.strptime(data['period_start'], '%Y-%m-%d')
            end_date = datetime.strptime(data['period_end'], '%Y-%m-%d')
            
            if start_date >= end_date:
                raise DataValidationError("period_start must be before period_end")
        except ValueError as e:
            raise DataValidationError(f"Invalid date format: {e}")
        
        # Validate source
        if data['source'] not in ['quickbooks', 'rootfi']:
            raise DataValidationError(f"Invalid source: {data['source']}")
        
        # Validate numeric fields if present
        numeric_fields = ['revenue', 'cost_of_goods_sold', 'gross_profit', 
                         'operating_expenses', 'net_profit']
        
        for field in numeric_fields:
            if field in data:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    raise DataValidationError(f"Invalid numeric value for {field}")
        
        return True
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """
        Validate date range.
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            
        Returns:
            True if valid
            
        Raises:
            DataValidationError: If validation fails
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start >= end:
                raise DataValidationError("start_date must be before end_date")
            
            return True
        except ValueError as e:
            raise DataValidationError(f"Invalid date format: {e}")

