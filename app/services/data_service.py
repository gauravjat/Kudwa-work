"""
Service for financial data operations.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import FinancialPeriod
from app.parsers.quickbooks_parser import QuickBooksParser
from app.parsers.rootfi_parser import RootfiParser
from app.config import settings
from app.exceptions import DataProcessingError, DataSourceError
from app.validators import FinancialDataValidator


class DataService:
    """Service for managing financial data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_data_from_sources(self) -> Dict[str, int]:
        """
        Load data from both QuickBooks and Rootfi sources.
        
        Returns:
            Dictionary with counts of loaded records
            
        Raises:
            DataSourceError: If data files cannot be accessed or parsed
            DataProcessingError: If data loading fails
        """
        try:
            # Parse QuickBooks data
            qb_parser = QuickBooksParser()
            qb_data = qb_parser.parse_file(settings.QUICKBOOKS_DATA_FILE)
            
            # Parse Rootfi data
            rootfi_parser = RootfiParser()
            rootfi_data = rootfi_parser.parse_file(settings.ROOTFI_DATA_FILE)
            
            # Load into database
            qb_count = self._load_periods(qb_data)
            rootfi_count = self._load_periods(rootfi_data)
            
            return {
                'quickbooks_records': qb_count,
                'rootfi_records': rootfi_count,
                'total_records': qb_count + rootfi_count
            }
        except FileNotFoundError as e:
            raise DataSourceError(f"Data file not found: {e}")
        except Exception as e:
            raise DataProcessingError(f"Failed to load data: {e}")
    
    def _load_periods(self, periods_data: List[Dict[str, Any]]) -> int:
        """
        Load period data into database.
        
        Args:
            periods_data: List of period dictionaries
            
        Returns:
            Count of new records loaded
        """
        count = 0
        validator = FinancialDataValidator()
        
        for period_data in periods_data:
            # Validate data before loading
            try:
                validator.validate_period_data(period_data)
            except Exception as e:
                print(f"Warning: Skipping invalid period data: {e}")
                continue
            # Check if period already exists
            existing = self.db.query(FinancialPeriod).filter(
                and_(
                    FinancialPeriod.period_start == datetime.strptime(period_data['period_start'], '%Y-%m-%d').date(),
                    FinancialPeriod.period_end == datetime.strptime(period_data['period_end'], '%Y-%m-%d').date(),
                    FinancialPeriod.source == period_data['source']
                )
            ).first()
            
            if existing:
                # Update existing record
                for key, value in period_data.items():
                    if key not in ['period_start', 'period_end', 'source']:
                        setattr(existing, key, value)
            else:
                # Create new record
                period = FinancialPeriod(
                    period_start=datetime.strptime(period_data['period_start'], '%Y-%m-%d').date(),
                    period_end=datetime.strptime(period_data['period_end'], '%Y-%m-%d').date(),
                    source=period_data['source'],
                    revenue=period_data.get('revenue', 0.0),
                    cost_of_goods_sold=period_data.get('cost_of_goods_sold', 0.0),
                    gross_profit=period_data.get('gross_profit', 0.0),
                    operating_expenses=period_data.get('operating_expenses', 0.0),
                    operating_profit=period_data.get('operating_profit', 0.0),
                    non_operating_revenue=period_data.get('non_operating_revenue', 0.0),
                    non_operating_expenses=period_data.get('non_operating_expenses', 0.0),
                    net_profit=period_data.get('net_profit', 0.0),
                    revenue_breakdown=period_data.get('revenue_breakdown'),
                    expense_breakdown=period_data.get('expense_breakdown'),
                    raw_data=period_data
                )
                self.db.add(period)
                count += 1
        
        self.db.commit()
        return count
    
    def get_all_periods(self, source: Optional[str] = None) -> List[FinancialPeriod]:
        """Get all financial periods, optionally filtered by source."""
        query = self.db.query(FinancialPeriod)
        
        if source:
            query = query.filter(FinancialPeriod.source == source)
        
        return query.order_by(FinancialPeriod.period_start).all()
    
    def get_period_range(self, start_date: str, end_date: str, source: Optional[str] = None) -> List[FinancialPeriod]:
        """
        Get financial periods within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Optional source filter
            
        Returns:
            List of financial periods
            
        Raises:
            DataValidationError: If date format is invalid
        """
        # Validate date range
        validator = FinancialDataValidator()
        validator.validate_date_range(start_date, end_date)
        
        query = self.db.query(FinancialPeriod).filter(
            and_(
                FinancialPeriod.period_start >= datetime.strptime(start_date, '%Y-%m-%d').date(),
                FinancialPeriod.period_end <= datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        )
        
        if source:
            query = query.filter(FinancialPeriod.source == source)
        
        return query.order_by(FinancialPeriod.period_start).all()
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics across all data."""
        periods = self.get_all_periods()
        
        if not periods:
            return {}
        
        total_revenue = sum(p.revenue for p in periods)
        total_expenses = sum(p.operating_expenses for p in periods)
        total_profit = sum(p.net_profit for p in periods)
        
        return {
            'total_periods': len(periods),
            'date_range': {
                'start': str(min(p.period_start for p in periods)),
                'end': str(max(p.period_end for p in periods))
            },
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'average_monthly_revenue': total_revenue / len(periods) if periods else 0,
            'average_monthly_profit': total_profit / len(periods) if periods else 0
        }

