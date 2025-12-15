# backend/app/core/logging_config.py
"""
Structured logging configuration with JSON formatting.

Provides:
- JSON-formatted logs for easy parsing
- Multiple log handlers (console, file, error-specific)
- Rotating file handlers to manage log file sizes
- Request-specific logging with context
- Configurable log levels and formats

Log files:
- app.log: General application logs (rotating by size, 10MB max)
- error.log: Error-level logs only (rotating daily)
- api_requests.log: API request logs (50MB max)
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom log formatter that outputs logs in JSON format.
    
    JSON logs are easier to parse by log aggregation tools like
    Elasticsearch, Splunk, or CloudWatch.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record (logging.LogRecord): Log record to format
            
        Returns:
            str: JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra context information if available
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(
    log_level: str = "INFO",
    log_dir = "logs",
    enable_file_logging: bool = True,
    enable_json: bool = True
):
    """
    Configure the logging system with multiple handlers.
    
    Args:
        log_level (str): Minimum log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_dir (str): Directory for log files
        enable_file_logging (bool): Enable file-based logging
        enable_json (bool): Use JSON formatting for logs
        
    Returns:
        logging.Logger: Configured root logger
    """
    
    # Convert to Path and create log directory
    from pathlib import Path
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler (always enabled for stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    if enable_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handlers (optional)
    if enable_file_logging:
        # General application log (rotates by size)
        general_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB max file size
            backupCount=5  # Keep 5 backup files
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        root_logger.addHandler(general_handler)
        
        # Error-specific log (rotates daily at midnight)
        error_handler = TimedRotatingFileHandler(
            log_dir / "error.log",
            when="midnight",  # Rotate at midnight
            interval=1,  # Every day
            backupCount=30  # Keep 30 days of error logs
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        root_logger.addHandler(error_handler)
        
        # API requests log (larger size limit for high-traffic endpoints)
        api_handler = RotatingFileHandler(
            log_dir / "api_requests.log",
            maxBytes=50 * 1024 * 1024,  # 50MB max file size
            backupCount=10  # Keep 10 backup files
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        
        # Create dedicated logger for API requests
        api_logger = logging.getLogger("api")
        api_logger.addHandler(api_handler)
    
    return root_logger


class RequestLogger:
    \"""
    Specialized logger for API request tracking.
    
    Logs detailed information about each API request including:
    - Request ID for tracing
    - HTTP method and path
    - Client IP address
    - User ID (if authenticated)
    - Response status code
    - Response time in milliseconds
    - Error details (if any)
    \"""
    
    def __init__(self):
        self.logger = logging.getLogger("api")
    
    def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        ip_address: str,
        user_id: str = None,
        status_code: int = None,
        response_time: float = None,
        error: str = None
    ):
        \"""
        Log a complete API request with all relevant details.
        
        Args:
            request_id (str): Unique identifier for this request
            method (str): HTTP method (GET, POST, etc.)
            path (str): Request path/endpoint
            ip_address (str): Client IP address
            user_id (str): User ID if authenticated
            status_code (int): HTTP response status code
            response_time (float): Processing time in seconds
            error (str): Error message if request failed
        \"""
        # Build log data dictionary
        log_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add optional fields if provided
        if user_id:
            log_data["user_id"] = user_id
        if status_code:
            log_data["status_code"] = status_code
        if response_time:
            # Convert seconds to milliseconds for readability
            log_data["response_time_ms"] = round(response_time * 1000, 2)
        if error:
            log_data["error"] = error
        
        # Log as JSON string
        self.logger.info(json.dumps(log_data))


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================
# Create global instance for easy import and use throughout the application
request_logger = RequestLogger()
