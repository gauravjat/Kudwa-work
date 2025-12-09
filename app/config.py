"""
Application configuration.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings."""
    
    # Database
    DATABASE_URL = "sqlite:///./financial_data.db"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective model
    
    # Data files
    QUICKBOOKS_DATA_FILE = "data_ser-1.json"
    ROOTFI_DATA_FILE = "data_set-2.json"

settings = Settings()

