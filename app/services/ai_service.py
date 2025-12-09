"""
AI service for natural language querying and insights generation.
"""
import json
from typing import Dict, Any, List
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.services.data_service import DataService
from app.exceptions import AIServiceError


class AIService:
    """Service for AI-powered financial data analysis."""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def query_natural_language(self, question: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process natural language query about financial data.
        
        Args:
            question: User's natural language question
            conversation_history: Previous conversation messages for context
            
        Returns:
            Dictionary with answer and supporting data
            
        Raises:
            AIServiceError: If AI service fails
        """
        if not question or not question.strip():
            raise AIServiceError("Question cannot be empty")
        
        if not settings.OPENAI_API_KEY:
            raise AIServiceError("OpenAI API key not configured")
        
        try:
            # Get relevant financial data
            financial_context = self._prepare_financial_context()
            
            # Build conversation messages
            messages = self._build_conversation(question, financial_context, conversation_history)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract relevant data based on question
            supporting_data = self._extract_supporting_data(question)
            
            return {
                'answer': answer,
                'supporting_data': supporting_data,
                'question': question,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise AIServiceError(f"Failed to process natural language query: {e}")
    
    def generate_insights(self, period_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate AI-powered insights from financial data.
        
        Args:
            period_filter: Optional filter for specific periods
            
        Returns:
            Dictionary with insights and narratives
        """
        # Get financial data
        if period_filter:
            start_date = period_filter.get('start_date')
            end_date = period_filter.get('end_date')
            periods = self.data_service.get_period_range(start_date, end_date)
        else:
            periods = self.data_service.get_all_periods()
        
        # Prepare data summary
        data_summary = self._prepare_data_summary(periods)
        
        # Generate insights using AI
        prompt = self._build_insights_prompt(data_summary)
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial analyst providing clear, actionable insights from financial data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        insights = response.choices[0].message.content
        
        return {
            'insights': insights,
            'period_count': len(periods),
            'data_summary': data_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_financial_context(self) -> str:
        """Prepare financial data context for AI."""
        # Get summary statistics
        stats = self.data_service.get_summary_statistics()
        
        # Get recent periods for context
        recent_periods = self.data_service.get_all_periods()[-12:]  # Last 12 months
        
        # Format context
        context_parts = [
            f"Dataset Overview:",
            f"- Total Periods: {stats.get('total_periods', 0)}",
            f"- Date Range: {stats.get('date_range', {}).get('start')} to {stats.get('date_range', {}).get('end')}",
            f"- Total Revenue: ${stats.get('total_revenue', 0):,.2f}",
            f"- Total Expenses: ${stats.get('total_expenses', 0):,.2f}",
            f"- Total Net Profit: ${stats.get('total_profit', 0):,.2f}",
            f"\nRecent Monthly Data (Last 12 months):"
        ]
        
        for period in recent_periods:
            context_parts.append(
                f"- {period.period_start} to {period.period_end}: "
                f"Revenue ${period.revenue:,.2f}, "
                f"Expenses ${period.operating_expenses:,.2f}, "
                f"Net Profit ${period.net_profit:,.2f}"
            )
        
        return "\n".join(context_parts)
    
    def _build_conversation(self, question: str, context: str, history: List[Dict] = None) -> List[Dict]:
        """Build conversation messages for OpenAI API."""
        system_message = {
            "role": "system",
            "content": (
                "You are a financial data analyst assistant. You answer questions about financial data "
                "with precision and clarity. Use the provided financial data context to answer questions. "
                "Always include specific numbers and time periods when relevant. "
                "If you cannot find the exact answer in the data, say so clearly."
            )
        }
        
        context_message = {
            "role": "system",
            "content": f"Financial Data Context:\n{context}"
        }
        
        messages = [system_message, context_message]
        
        # Add conversation history if provided
        if history:
            messages.extend(history)
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return messages
    
    def _extract_supporting_data(self, question: str) -> Dict[str, Any]:
        """Extract relevant supporting data based on question."""
        # Simple keyword-based extraction
        question_lower = question.lower()
        
        supporting_data = {}
        
        # Check for specific time periods
        if 'q1' in question_lower or 'quarter 1' in question_lower or 'first quarter' in question_lower:
            supporting_data['periods'] = self._get_quarter_data(1)
        elif 'q2' in question_lower or 'quarter 2' in question_lower or 'second quarter' in question_lower:
            supporting_data['periods'] = self._get_quarter_data(2)
        elif '2024' in question_lower:
            supporting_data['periods'] = self._get_year_data('2024')
        elif 'recent' in question_lower or 'latest' in question_lower:
            supporting_data['periods'] = self._get_recent_periods(3)
        
        return supporting_data
    
    def _get_quarter_data(self, quarter: int, year: int = 2024) -> List[Dict]:
        """Get data for specific quarter."""
        quarter_months = {
            1: [(year, 1), (year, 2), (year, 3)],
            2: [(year, 4), (year, 5), (year, 6)],
            3: [(year, 7), (year, 8), (year, 9)],
            4: [(year, 10), (year, 11), (year, 12)]
        }
        
        periods = self.data_service.get_all_periods()
        quarter_data = []
        
        for period in periods:
            if (period.period_start.year, period.period_start.month) in quarter_months.get(quarter, []):
                quarter_data.append({
                    'period': f"{period.period_start} to {period.period_end}",
                    'revenue': period.revenue,
                    'expenses': period.operating_expenses,
                    'profit': period.net_profit
                })
        
        return quarter_data
    
    def _get_year_data(self, year: str) -> List[Dict]:
        """Get data for specific year."""
        year_int = int(year)
        periods = self.data_service.get_all_periods()
        
        year_data = []
        for period in periods:
            if period.period_start.year == year_int:
                year_data.append({
                    'period': f"{period.period_start} to {period.period_end}",
                    'revenue': period.revenue,
                    'expenses': period.operating_expenses,
                    'profit': period.net_profit
                })
        
        return year_data
    
    def _get_recent_periods(self, count: int = 3) -> List[Dict]:
        """Get most recent periods."""
        periods = self.data_service.get_all_periods()[-count:]
        
        return [{
            'period': f"{p.period_start} to {p.period_end}",
            'revenue': p.revenue,
            'expenses': p.operating_expenses,
            'profit': p.net_profit
        } for p in periods]
    
    def _prepare_data_summary(self, periods: List[FinancialPeriod]) -> Dict[str, Any]:
        """Prepare summary of financial data for insight generation."""
        if not periods:
            return {}
        
        total_revenue = sum(p.revenue for p in periods)
        total_expenses = sum(p.operating_expenses for p in periods)
        total_profit = sum(p.net_profit for p in periods)
        
        # Calculate trends
        revenue_trend = [p.revenue for p in periods]
        profit_trend = [p.net_profit for p in periods]
        
        return {
            'period_count': len(periods),
            'date_range': {
                'start': str(periods[0].period_start),
                'end': str(periods[-1].period_end)
            },
            'totals': {
                'revenue': total_revenue,
                'expenses': total_expenses,
                'profit': total_profit
            },
            'averages': {
                'revenue': total_revenue / len(periods),
                'expenses': total_expenses / len(periods),
                'profit': total_profit / len(periods)
            },
            'trends': {
                'revenue_trend': revenue_trend[-6:],  # Last 6 months
                'profit_trend': profit_trend[-6:]
            }
        }
    
    def _build_insights_prompt(self, data_summary: Dict[str, Any]) -> str:
        """Build prompt for insight generation."""
        return f"""
Analyze the following financial data and provide 3-5 key insights:

Period: {data_summary['date_range']['start']} to {data_summary['date_range']['end']}
Number of Periods: {data_summary['period_count']}

Financial Summary:
- Total Revenue: ${data_summary['totals']['revenue']:,.2f}
- Total Expenses: ${data_summary['totals']['expenses']:,.2f}
- Total Net Profit: ${data_summary['totals']['profit']:,.2f}

Monthly Averages:
- Average Revenue: ${data_summary['averages']['revenue']:,.2f}
- Average Expenses: ${data_summary['averages']['expenses']:,.2f}
- Average Profit: ${data_summary['averages']['profit']:,.2f}

Recent Trends (Last 6 months):
- Revenue Trend: {data_summary['trends']['revenue_trend']}
- Profit Trend: {data_summary['trends']['profit_trend']}

Provide clear, actionable insights about:
1. Overall financial health
2. Revenue and profit trends
3. Expense patterns
4. Any notable observations or concerns
"""

