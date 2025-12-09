"""
API routes for financial data system.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    FinancialPeriodResponse,
    DataLoadResponse,
    SummaryStatisticsResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    InsightsRequest,
    InsightsResponse
)
from app.services.data_service import DataService
from app.services.ai_service import AIService
from app.exceptions import (
    DataProcessingError,
    DataValidationError,
    DataSourceError,
    AIServiceError
)

router = APIRouter()


@router.post("/data/load", response_model=DataLoadResponse, tags=["Data Management"])
async def load_data(db: Session = Depends(get_db)):
    """
    Load financial data from both QuickBooks and Rootfi sources into database.
    This endpoint parses the JSON files and stores the data in a unified format.
    """
    try:
        data_service = DataService(db)
        result = data_service.load_data_from_sources()
        
        return DataLoadResponse(
            message="Data loaded successfully",
            quickbooks_records=result['quickbooks_records'],
            rootfi_records=result['rootfi_records'],
            total_records=result['total_records']
        )
    except DataSourceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DataProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/data/periods", response_model=List[FinancialPeriodResponse], tags=["Data Access"])
async def get_periods(
    source: Optional[str] = Query(None, description="Filter by source: 'quickbooks' or 'rootfi'"),
    db: Session = Depends(get_db)
):
    """
    Get all financial periods, optionally filtered by data source.
    Returns comprehensive financial data for each period.
    """
    try:
        data_service = DataService(db)
        periods = data_service.get_all_periods(source=source)
        return periods
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching periods: {str(e)}")


@router.get("/data/periods/range", response_model=List[FinancialPeriodResponse], tags=["Data Access"])
async def get_period_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    source: Optional[str] = Query(None, description="Filter by source: 'quickbooks' or 'rootfi'"),
    db: Session = Depends(get_db)
):
    """
    Get financial periods within a specific date range.
    Useful for analyzing specific time periods or quarters.
    """
    try:
        data_service = DataService(db)
        periods = data_service.get_period_range(start_date, end_date, source=source)
        return periods
    except DataValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching period range: {str(e)}")


@router.get("/data/summary", response_model=SummaryStatisticsResponse, tags=["Data Access"])
async def get_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics across all financial data.
    Provides high-level overview of total revenue, expenses, and profits.
    """
    try:
        data_service = DataService(db)
        stats = data_service.get_summary_statistics()
        
        if not stats:
            raise HTTPException(status_code=404, detail="No financial data found")
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/ai/query", response_model=NaturalLanguageQueryResponse, tags=["AI Features"])
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query financial data using natural language.
    
    Examples:
    - "What was the total profit in Q1 2024?"
    - "Show me revenue trends for 2024"
    - "Which expense category had the highest increase this year?"
    - "Compare Q1 and Q2 performance"
    
    Supports follow-up questions through conversation_history.
    """
    try:
        ai_service = AIService(db)
        result = ai_service.query_natural_language(
            question=request.question,
            conversation_history=request.conversation_history
        )
        return result
    except AIServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/ai/insights", response_model=InsightsResponse, tags=["AI Features"])
async def generate_insights(
    request: InsightsRequest = None,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered insights from financial data.
    
    Analyzes financial patterns, trends, and provides actionable recommendations.
    Can filter by date range for focused analysis.
    """
    try:
        ai_service = AIService(db)
        
        period_filter = None
        if request and (request.start_date or request.end_date):
            period_filter = {
                'start_date': request.start_date,
                'end_date': request.end_date
            }
        
        result = ai_service.generate_insights(period_filter=period_filter)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

