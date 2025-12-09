"""
Database models for financial data.
"""
from sqlalchemy import Column, Integer, String, Float, Date, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FinancialPeriod(Base):
    """
    Unified financial data model for both QuickBooks and Rootfi sources.
    Stores monthly financial data with consistent schema.
    """
    __tablename__ = "financial_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Period identification
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    source = Column(String, nullable=False)  # 'quickbooks' or 'rootfi'
    
    # Core financial metrics
    revenue = Column(Float, default=0.0)
    cost_of_goods_sold = Column(Float, default=0.0)
    gross_profit = Column(Float, default=0.0)
    operating_expenses = Column(Float, default=0.0)
    operating_profit = Column(Float, default=0.0)
    non_operating_revenue = Column(Float, default=0.0)
    non_operating_expenses = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    
    # Detailed breakdown (stored as JSON for flexibility)
    revenue_breakdown = Column(JSON, nullable=True)
    expense_breakdown = Column(JSON, nullable=True)
    
    # Metadata
    currency = Column(String, default="USD")
    raw_data = Column(JSON, nullable=True)  # Store original for reference
    
    def __repr__(self):
        return f"<FinancialPeriod {self.period_start} to {self.period_end}: Net Profit ${self.net_profit:,.2f}>"

