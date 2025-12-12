"""
AI service for natural language querying and insights generation using LangChain.
"""
import json
from typing import Dict, Any, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from sqlalchemy.orm import Session

from app.config import settings
from app.services.data_service import DataService
from app.exceptions import AIServiceError
from app.models import FinancialPeriod
from app.prompts.prompt_loader import prompt_loader


class AIService:
    """Service for AI-powered financial data analysis using LangChain."""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
        
        # Initialize LangChain ChatOpenAI model
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # Lower temperature for more factual responses
            openai_api_key=settings.OPENAI_API_KEY,
            max_tokens=1000
        )
        
        # Initialize insight generation LLM with different settings
        self.insights_llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.5,  # Slightly higher for more creative insights
            openai_api_key=settings.OPENAI_API_KEY,
            max_tokens=1500
        )
    
    def query_natural_language(self, question: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process natural language query about financial data using LangChain.
        
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
            
            # Build messages for LangChain
            messages = self._build_langchain_messages(
                question,
                financial_context,
                self._sanitize_history(conversation_history)
            )
            
            # Invoke LangChain
            response = self.llm.invoke(messages)
            answer = response.content
            
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
        Generate AI-powered insights from financial data using LangChain.
        
        Args:
            period_filter: Optional filter for specific periods
            
        Returns:
            Dictionary with insights and narratives
        """
        # Get financial data
        if period_filter:
            start_date = period_filter.get('start_date')
            end_date = period_filter.get('end_date')
            if not start_date or not end_date:
                raise AIServiceError("Both start_date and end_date are required when filtering insights")
            periods = self.data_service.get_period_range(start_date, end_date)
        else:
            periods = self.data_service.get_all_periods()
        
        if not periods:
            raise AIServiceError("No financial data available to generate insights")
        
        # Prepare data summary
        data_summary = self._prepare_data_summary(periods)
        
        # Build prompt context for Jinja2 template
        prompt_context = {
            'period_count': len(periods),
            'date_range_start': str(periods[0].period_start),
            'date_range_end': str(periods[-1].period_end),
            'total_revenue': data_summary['totals']['revenue'],
            'total_expenses': data_summary['totals']['expenses'],
            'total_profit': data_summary['totals']['profit'],
            'profit_margin': (data_summary['totals']['profit'] / data_summary['totals']['revenue'] * 100) if data_summary['totals']['revenue'] > 0 else 0,
            'avg_revenue': data_summary['averages']['revenue'],
            'avg_expenses': data_summary['averages']['expenses'],
            'avg_profit': data_summary['averages']['profit'],
            'revenue_trend': data_summary['trends']['revenue_trend'],
            'profit_trend': data_summary['trends']['profit_trend']
        }
        
        # Generate insights using LangChain with Jinja2 prompt
        system_prompt = prompt_loader.get_system_prompt()
        insights_prompt = prompt_loader.get_insights_prompt(prompt_context)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=insights_prompt)
        ]
        
        response = self.insights_llm.invoke(messages)
        insights = response.content
        
        return {
            'insights': insights,
            'period_count': len(periods),
            'data_summary': data_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_financial_context(self) -> str:
        """Prepare financial data context for AI using Jinja2 templates."""
        # Get summary statistics
        stats = self.data_service.get_summary_statistics()
        
        # Get recent periods for context
        recent_periods = self.data_service.get_all_periods()[-12:]  # Last 12 months
        
        # Build context using Jinja2 template
        context = {
            'total_periods': stats.get('total_periods', 0),
            'date_range_start': stats.get('date_range', {}).get('start', 'N/A'),
            'date_range_end': stats.get('date_range', {}).get('end', 'N/A'),
            'total_revenue': stats.get('total_revenue', 0),
            'total_expenses': stats.get('total_expenses', 0),
            'total_profit': stats.get('total_profit', 0),
            'recent_periods': recent_periods
        }
        
        return prompt_loader.get_financial_context(context)
    
    def _build_langchain_messages(
        self, 
        question: str, 
        context: str, 
        history: List[Dict] = None
    ) -> List:
        """Build messages for LangChain."""
        # System message with instructions
        system_prompt = prompt_loader.get_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=context)  # Financial context as system message
        ]
        
        # Add conversation history if provided
        if history:
            for msg in history:
                role = msg.get('role')
                content = msg.get('content')
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    messages.append(AIMessage(content=content))
        
        # Add current question
        messages.append(HumanMessage(content=question))
        
        return messages

    def _sanitize_history(self, history: List[Dict] | None) -> List[Dict]:
        """Ensure conversation history is well-formed and safe to forward."""
        if not history:
            return []
        
        allowed_roles = {"user", "assistant", "system"}
        sanitized: List[Dict] = []
        for msg in history:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content")
            if role not in allowed_roles or not isinstance(content, str):
                continue
            sanitized.append({"role": role, "content": content})
        
        # Keep recent context only to avoid unbounded growth
        return sanitized[-10:]
    
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
        elif 'q3' in question_lower or 'quarter 3' in question_lower or 'third quarter' in question_lower:
            supporting_data['periods'] = self._get_quarter_data(3)
        elif 'q4' in question_lower or 'quarter 4' in question_lower or 'fourth quarter' in question_lower:
            supporting_data['periods'] = self._get_quarter_data(4)
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
        revenue_trend = [float(p.revenue) for p in periods]
        profit_trend = [float(p.net_profit) for p in periods]
        
        return {
            'period_count': len(periods),
            'date_range': {
                'start': str(periods[0].period_start),
                'end': str(periods[-1].period_end)
            },
            'totals': {
                'revenue': float(total_revenue),
                'expenses': float(total_expenses),
                'profit': float(total_profit)
            },
            'averages': {
                'revenue': float(total_revenue) / len(periods),
                'expenses': float(total_expenses) / len(periods),
                'profit': float(total_profit) / len(periods)
            },
            'trends': {
                'revenue_trend': revenue_trend[-6:],  # Last 6 months
                'profit_trend': profit_trend[-6:]
            }
        }
