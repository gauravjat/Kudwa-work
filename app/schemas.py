"""
Pydantic schemas for API request/response validation.
"""
from datetime import date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class FinancialPeriodResponse(BaseModel):
    """Response schema for financial period data."""
    id: int
    period_start: date
    period_end: date
    source: str
    revenue: float
    cost_of_goods_sold: float
    gross_profit: float
    operating_expenses: float
    operating_profit: float
    non_operating_revenue: float
    non_operating_expenses: float
    net_profit: float
    revenue_breakdown: Optional[Dict[str, Any]] = None
    expense_breakdown: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class DataLoadResponse(BaseModel):
    """Response schema for data loading operation."""
    message: str
    quickbooks_records: int
    rootfi_records: int
    total_records: int


class SummaryStatisticsResponse(BaseModel):
    """Response schema for summary statistics."""
    total_periods: int
    date_range: Dict[str, str]
    total_revenue: float
    total_expenses: float
    total_profit: float
    average_monthly_revenue: float
    average_monthly_profit: float


class NaturalLanguageQueryRequest(BaseModel):
    """Request schema for natural language query."""
    question: str = Field(..., description="Natural language question about financial data")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=None, description="Previous conversation messages")


class NaturalLanguageQueryResponse(BaseModel):
    """Response schema for natural language query."""
    answer: str
    supporting_data: Dict[str, Any]
    question: str
    timestamp: str


class InsightsRequest(BaseModel):
    """Request schema for insights generation."""
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")


class InsightsResponse(BaseModel):
    """Response schema for insights."""
    insights: str
    period_count: int
    data_summary: Dict[str, Any]
    timestamp: str


