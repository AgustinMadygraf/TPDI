"""
Path: src/infrastructure/settings/logger.py

Configuracion de logging.
"""
import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Configura logging basico."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
