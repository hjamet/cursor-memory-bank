"""
Configuration du système de logging.
"""
import logging
import sys
from typing import Any, Dict

from src.backend.config import settings

# Format du logging
log_format = settings.LOG_FORMAT

# Configuration de base
logging_config: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": log_format,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "app": {  # Logger principal de l'application
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {  # Logger du serveur
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy": {  # Logger SQLAlchemy
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

def setup_logging() -> None:
    """Configure le système de logging."""
    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger configuré.
    
    Args:
        name: Nom du logger (généralement __name__)
    
    Returns:
        Logger configuré
    """
    return logging.getLogger(f"app.{name}")

# Logger par défaut
logger = get_logger(__name__) 