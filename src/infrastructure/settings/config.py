"""
Path: src/infrastructure/settings/config.py
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Settings base de la aplicacion."""
    app_name: str = "api"
    app_environment: str = "development"
    app_log_level: str = "INFO"


def load_settings() -> Settings:
    """Carga settings desde variables de entorno."""
    return Settings(
        app_name=os.getenv("APP_NAME", "api"),
        app_environment=os.getenv("APP_ENVIRONMENT", "development"),
        app_log_level=os.getenv("APP_LOG_LEVEL", "INFO"),
    )
