"""
Prompt template loader using Jinja2.
"""
import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape


class PromptLoader:
    """Loads and renders Jinja2 prompt templates."""
    
    def __init__(self):
        # Get the directory where prompt templates are stored
        template_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_template(self, template_name: str) -> Any:
        """
        Load a Jinja2 template by name.
        
        Args:
            template_name: Name of the template file (with .j2 extension)
            
        Returns:
            Jinja2 Template object
        """
        return self.env.get_template(template_name)
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file (with .j2 extension)
            context: Dictionary of variables to pass to the template
            
        Returns:
            Rendered template string
        """
        template = self.load_template(template_name)
        return template.render(**context)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for financial analysis."""
        return self.render('system_prompt.j2', {})
    
    def get_financial_context(self, context: Dict[str, Any]) -> str:
        """
        Get the financial context prompt with data.
        
        Args:
            context: Dictionary with financial data context
            
        Returns:
            Rendered financial context string
        """
        return self.render('financial_context.j2', context)
    
    def get_insights_prompt(self, context: Dict[str, Any]) -> str:
        """
        Get the insights generation prompt with data.
        
        Args:
            context: Dictionary with financial summary data
            
        Returns:
            Rendered insights prompt string
        """
        return self.render('insights_prompt.j2', context)


# Global instance
prompt_loader = PromptLoader()

