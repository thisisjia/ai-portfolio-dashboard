"""Configuration management for the resume dashboard."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:////Users/jia/Personal/resume-dashboard/resume_dashboard.db"
    
    # Authentication
    token_file: str = "data/tokens.json"
    
    # API Keys
    openai_api_key: str = ""
    tavily_api_key: str = ""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    model_config = {"extra": "ignore", "env_file": ".env"}


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()