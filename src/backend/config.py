"""
Configuration globale de l'application.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis les variables d'environnement."""

    # Configuration générale
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # Base de données
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str
    REDIS_PREFIX: str = "mysteres-unil:"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # secondes
    WS_QUEUE_TIMEOUT: int = 300  # secondes
    WS_MAX_CONNECTIONS: int = 1000

    # Sécurité
    CORS_ORIGINS: list[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Chat
    CHAT_MAX_MESSAGE_LENGTH: int = 1000
    CHAT_MIN_DELAY_BETWEEN_MESSAGES: int = 1  # secondes
    CHAT_SESSION_DURATION: int = 600  # secondes
    CHAT_QUEUE_MAX_SIZE: int = 100

    # Modération
    MODERATION_ENABLED: bool = True
    MODERATION_AUTO_BAN_THRESHOLD: int = 3

    # Cache
    CACHE_TTL: int = 3600  # secondes
    CACHE_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Chemins des fichiers
    STATIC_DIR: str = "src/frontend/static"
    TEMPLATES_DIR: str = "src/frontend/templates"
    UPLOAD_DIR: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instance globale des paramètres
settings = Settings() 