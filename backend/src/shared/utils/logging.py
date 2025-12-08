"""Logging utilities for consistent application logging.

This module sets up structured logging that:
1. Outputs both to console and file
2. Includes contextual information
3. Supports different log levels per environment

Lesson: Good logging is crucial for debugging production issues.
Structured logs can be searched and analyzed efficiently.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Format logs as structured JSON for better parsing.
    
    Lesson: Structured logs are much easier to search and analyze
    than traditional text logs. Tools like Elasticsearch can
    index JSON logs efficiently.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "user_token"):
            log_obj["user_token"] = record.user_token
        
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True
) -> logging.Logger:
    """Set up application logging with console and file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        structured: Use structured JSON logging
        
    Returns:
        Configured root logger
        
    Lesson: This function demonstrates the principle of
    "configure once, use everywhere". Set up logging at
    application start and all modules can use it.
    """
    # Remove existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler - human readable
    console_handler = logging.StreamHandler(sys.stdout)
    if structured:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))
    root_logger.addHandler(console_handler)
    
    # File handler - always structured for easier parsing
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Log the configuration
    root_logger.info(
        "Logging configured",
        extra={"log_level": log_level, "log_file": str(log_file) if log_file else None}
    )
    
    return root_logger


def get_logger(name: str, **extra_fields) -> logging.LoggerAdapter:
    """Get a logger with optional extra fields.
    
    Args:
        name: Logger name (usually __name__)
        **extra_fields: Fields to include in all logs from this logger
        
    Returns:
        Logger adapter with extra fields
        
    Example:
        logger = get_logger(__name__, component="chatbot", version="1.0")
        logger.info("Processing message", extra={"user_token": token})
        
    Lesson: LoggerAdapter allows adding context that appears in
    all logs from a specific component. This helps trace issues
    across distributed systems.
    """
    logger = logging.getLogger(name)
    
    if extra_fields:
        # LoggerAdapter adds fields to all logs
        return logging.LoggerAdapter(logger, extra_fields)
    
    return logger


def log_performance(func):
    """Decorator to log function performance.
    
    Lesson: Decorators are powerful for cross-cutting concerns
    like logging, without cluttering business logic.
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"{func.__name__} completed",
                extra={"duration_seconds": duration, "status": "success"}
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{func.__name__} failed",
                extra={"duration_seconds": duration, "status": "error", "error": str(e)}
            )
            raise
    
    return wrapper