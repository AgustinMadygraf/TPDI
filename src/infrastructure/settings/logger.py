"""
Path: src/infrastructure/settings/logger.py
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter con colores estilo uvicorn."""
    
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
        "DIM": "\033[2m",
    }
    
    def __init__(self, fmt: Optional[str] = None, *args, **kwargs):
        self.default_fmt = fmt or "%(dim)s%(asctime)s%(reset)s | %(levelname)s | %(name)s: %(message)s"
        super().__init__(self.default_fmt, *args, **kwargs)
        self.default_time_format = "%H:%M:%S"
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        ct = datetime.fromtimestamp(record.created)
        tenths = int((record.msecs // 100) % 10)
        return f"{ct.strftime('%H:%M:%S')},{tenths}"
    
    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        dim = self.COLORS["DIM"]
        
        record.levelname = f"{color}{level_name:8}{reset}"
        record.dim = dim
        record.reset = reset
        record.color = color
        
        result = super().format(record)
        record.levelname = original_levelname
        
        return result


class NonColoredFormatter(logging.Formatter):
    """Formatter sin colores para archivos."""
    
    def __init__(self, detailed: bool = False):
        self.detailed = detailed
        if detailed:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d - %(message)s"
        else:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s: %(message)s"
        super().__init__(fmt=fmt)
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        ct = datetime.fromtimestamp(record.created)
        tenths = int((record.msecs // 100) % 10)
        return f"{ct.strftime('%H:%M:%S')},{tenths}"


def setup_logging(
    name: str = "tpdi",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    colored: bool = True
) -> logging.Logger:
    """
    Configura y retorna el logger estilo FastAPI.
    
    Args:
        name: Nombre del logger root.
        level: Nivel de logging.
        log_file: Archivo opcional para guardar logs.
        colored: Usar colores en consola.
        
    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    use_colors = colored and sys.stdout.isatty()
    
    if use_colors:
        formatter = ColoredFormatter()
    else:
        formatter = NonColoredFormatter(detailed=False)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(NonColoredFormatter(detailed=True))
        logger.addHandler(file_handler)
    
    # Configurar el logger root para que los hijos hereden
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(console_handler)
    root.setLevel(level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Helper para obtener un logger configurado.
    Asegura que el logging esté configurado con nivel INFO.
    
    Uso:
        from src.infrastructure.settings.logger import get_logger
        logger = get_logger(__name__)
        logger.info("mensaje")
    """
    logger = logging.getLogger(name)
    
    # Si no hay handlers en el root o en este logger, configurar
    if not logging.getLogger().handlers and not logger.handlers:
        setup_logging(level=logging.INFO)
    
    return logger
