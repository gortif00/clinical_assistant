# backend/app/core/logging_config.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Formatter para logs en formato JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar información extra si existe
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        # Agregar exception info si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(
    log_level: str = "INFO",
    log_dir = "logs",
    enable_file_logging: bool = True,
    enable_json: bool = True
):
    """Configura el sistema de logging"""
    
    # Convertir a Path y crear directorio de logs
    from pathlib import Path
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Console handler (siempre)
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
    
    # File handlers
    if enable_file_logging:
        # General log (rotating por tamaño)
        general_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        root_logger.addHandler(general_handler)
        
        # Error log (rotating por día)
        error_handler = TimedRotatingFileHandler(
            log_dir / "error.log",
            when="midnight",
            interval=1,
            backupCount=30
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        root_logger.addHandler(error_handler)
        
        # API requests log
        api_handler = RotatingFileHandler(
            log_dir / "api_requests.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
        
        # Logger específico para API
        api_logger = logging.getLogger("api")
        api_logger.addHandler(api_handler)
    
    return root_logger

class RequestLogger:
    """Logger específico para requests de API"""
    
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
        """Log de request completo"""
        log_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if user_id:
            log_data["user_id"] = user_id
        if status_code:
            log_data["status_code"] = status_code
        if response_time:
            log_data["response_time_ms"] = round(response_time * 1000, 2)
        if error:
            log_data["error"] = error
        
        self.logger.info(json.dumps(log_data))

# Instancia global
request_logger = RequestLogger()
