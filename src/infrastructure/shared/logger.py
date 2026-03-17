"""
Path: src/infrastructure/shared/logger.py
"""
import logging
import sys
from datetime import datetime


class FastAPIFormatter(logging.Formatter):
    "Formatter con colores y formato HH:MM:SS,d (décimas)."    
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        tenths = int((record.msecs // 100) % 10)
        return f"{ct.strftime('%H:%M:%S')},{tenths}"

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        level = f"{level_color}{record.levelname:8}{reset}"

        time = self.formatTime(record)
        return f"{time} | {level} | {record.name}: {record.getMessage()}"


def setup_logging(name: str = "tpdi", level: int = logging.INFO) -> logging.Logger:
    "Configura logging estilo FastAPI."
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if sys.stdout.isatty():
        handler.setFormatter(FastAPIFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        ))

    logger.addHandler(handler)
    return logger

def get_logger(name: str) -> logging.Logger:
    "Obtiene un logger configurado."
    return logging.getLogger(name)
