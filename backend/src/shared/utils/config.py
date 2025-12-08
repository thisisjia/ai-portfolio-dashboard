"""Configuration management utilities.

This module demonstrates a robust configuration system that:
1. Loads from multiple sources (files, environment, defaults)
2. Validates configuration completeness
3. Provides type safety

Lesson: Configuration is critical for maintainable applications.
Never hardcode values that might change between environments.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(
    config_path: Optional[Path] = None,
    env_prefix: str = "RESUME_",
    required_fields: Optional[list] = None
) -> Dict[str, Any]:
    """Load configuration from multiple sources with precedence.
    
    Precedence order (highest to lowest):
    1. Environment variables (with prefix)
    2. Config file (YAML)
    3. Default values
    
    Args:
        config_path: Path to YAML config file
        env_prefix: Prefix for environment variables
        required_fields: List of required configuration keys
        
    Returns:
        Merged configuration dictionary
        
    Lesson: This pattern allows different config per environment
    without changing code. Production can use env vars while
    development uses a config file.
    """
    # Load .env file if it exists (for local development)
    load_dotenv()
    
    config = {}
    
    # 1. Load defaults (lowest precedence)
    defaults = {
        "app_name": "Resume Dashboard",
        "debug": False,
        "log_level": "INFO",
        "token_expiry_days": 30,
        "rate_limit_requests": 100,
        "rate_limit_period": 3600,
    }
    config.update(defaults)
    
    # 2. Load from config file if provided
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f) or {}
            config.update(file_config)
    
    # 3. Override with environment variables (highest precedence)
    # This allows secrets to stay out of config files
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # Convert RESUME_API_KEY to api_key
            config_key = key[len(env_prefix):].lower()
            config[config_key] = value
    
    # Special handling for boolean environment variables
    for bool_key in ["debug", "use_local_llm"]:
        if bool_key in config and isinstance(config[bool_key], str):
            config[bool_key] = config[bool_key].lower() in ("true", "1", "yes")
    
    # Validate required fields
    if required_fields:
        missing = [field for field in required_fields if field not in config]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
    
    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration values and types.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Validated configuration
        
    Raises:
        ValueError: If configuration is invalid
        
    Lesson: Always validate configuration early. It's better to
    fail fast with a clear error than to have mysterious bugs later.
    """
    # Check critical API keys
    api_keys = ["openai_api_key", "tavily_api_key"]
    missing_keys = []
    
    for key in api_keys:
        if key in config and config[key] in [None, "", "your_" + key + "_here"]:
            missing_keys.append(key)
    
    if missing_keys and not config.get("use_local_llm", False):
        raise ValueError(
            f"Missing API keys: {missing_keys}. "
            "Set them in .env or enable use_local_llm."
        )
    
    # Validate numeric ranges
    if config.get("rate_limit_requests", 0) < 0:
        raise ValueError("rate_limit_requests must be non-negative")
    
    if config.get("token_expiry_days", 0) < 1:
        raise ValueError("token_expiry_days must be at least 1")
    
    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.get("log_level", "INFO").upper() not in valid_log_levels:
        raise ValueError(f"Invalid log_level. Must be one of: {valid_log_levels}")
    
    return config