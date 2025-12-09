"""
Parser for QuickBooks P&L data format.
"""
import json
from datetime import datetime
from typing import Dict, List, Any

from app.exceptions import DataSourceError


class QuickBooksParser:
    """Parse QuickBooks Profit and Loss report data."""
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse QuickBooks JSON file and extract monthly financial data.
        
        Args:
            file_path: Path to QuickBooks JSON file
            
        Returns:
            List of dictionaries containing monthly financial data
            
        Raises:
            DataSourceError: If file cannot be read or parsed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise DataSourceError(f"QuickBooks data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DataSourceError(f"Invalid JSON in QuickBooks file: {e}")
        
        try:
            return self._extract_monthly_data(data)
        except Exception as e:
            raise DataSourceError(f"Failed to parse QuickBooks data: {e}")
    
    def _extract_monthly_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Extract monthly financial data from QuickBooks structure."""
        periods = []
        
        # Extract columns (months)
        columns = data['data']['Columns']['Column']
        rows = data['data']['Rows']['Row']
        
        # Skip first column (Account column)
        month_columns = columns[1:]  # Skip the "Account" column
        
        for idx, col in enumerate(month_columns):
            col_title = col.get('ColTitle', '')
            
            # Skip if this is the "Total" column
            if col_title == 'Total':
                continue
            
            # Extract dates from metadata
            metadata = col.get('MetaData', [])
            start_date = None
            end_date = None
            
            for meta in metadata:
                if meta['Name'] == 'StartDate':
                    start_date = meta['Value']
                elif meta['Name'] == 'EndDate':
                    end_date = meta['Value']
            
            if not start_date or not end_date:
                continue
            
            # Extract financial metrics for this period
            financial_data = self._extract_period_metrics(rows, idx + 1)  # +1 because we skip Account column
            
            periods.append({
                'period_start': start_date,
                'period_end': end_date,
                'source': 'quickbooks',
                **financial_data
            })
        
        return periods
    
    def _extract_period_metrics(self, rows: List[Dict], col_index: int) -> Dict[str, Any]:
        """Extract financial metrics for a specific period from rows."""
        metrics = {
            'revenue': 0.0,
            'cost_of_goods_sold': 0.0,
            'gross_profit': 0.0,
            'operating_expenses': 0.0,
            'net_profit': 0.0,
            'revenue_breakdown': {},
            'expense_breakdown': {}
        }
        
        for row in rows:
            group = row.get('group', '')
            
            # Extract value from Summary or ColData
            if 'Summary' in row:
                col_data = row['Summary']['ColData']
                value_str = col_data[col_index].get('value', '0.00')
                value = self._parse_value(value_str)
                
                if group == 'Income':
                    metrics['revenue'] = value
                    metrics['revenue_breakdown'] = self._extract_breakdown(row, col_index)
                elif group == 'COGS':
                    metrics['cost_of_goods_sold'] = value
                elif group == 'GrossProfit':
                    metrics['gross_profit'] = value
                elif group == 'Expenses':
                    metrics['operating_expenses'] = value
                    metrics['expense_breakdown'] = self._extract_breakdown(row, col_index)
                elif group == 'NetIncome':
                    metrics['net_profit'] = value
        
        return metrics
    
    def _extract_breakdown(self, row: Dict, col_index: int) -> Dict[str, float]:
        """Extract detailed breakdown from row structure."""
        breakdown = {}
        
        if 'Rows' in row and 'Row' in row['Rows']:
            for sub_row in row['Rows']['Row']:
                # Get account name
                if 'Header' in sub_row:
                    col_data = sub_row['Header']['ColData']
                elif 'ColData' in sub_row:
                    col_data = sub_row['ColData']
                else:
                    continue
                
                account_name = col_data[0].get('value', 'Unknown')
                value_str = col_data[col_index].get('value', '0.00')
                value = self._parse_value(value_str)
                
                if value != 0:
                    breakdown[account_name] = value
        
        return breakdown
    
    def _parse_value(self, value_str: str) -> float:
        """Parse string value to float, handling empty strings."""
        if not value_str or value_str == '':
            return 0.0
        try:
            return float(value_str.replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0

