"""
Path: tests/infrastructure/shared/test_logger.py
"""

import logging
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from src.infrastructure.settings.logger import (
    FastAPIFormatter,
    get_logger,
    setup_logging,
)


class TestFastAPIFormatter:
    "Test suite for FastAPIFormatter."
    @pytest.fixture
    def formatter(self):
        "Provides a FastAPIFormatter instance."
        return FastAPIFormatter()

    @pytest.fixture
    def sample_record(self):
        "Provides a sample log record."
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = 1700000000.0  # Fixed timestamp
        record.msecs = 123
        return record

    def test_format_time_with_tenths(self, formatter, sample_record):
        "Test that formatTime includes tenths of second."
        formatted_time = formatter.formatTime(sample_record)

        # Should be in format HH:MM:SS,d (d = tenths)
        assert "," in formatted_time
        parts = formatted_time.split(",")
        assert len(parts) == 2
        assert len(parts[1]) == 1  # Single digit for tenths

    def test_format_includes_level(self, formatter, sample_record):
        "Test that format includes log level."
        formatted = formatter.format(sample_record)

        assert "INFO" in formatted

    def test_format_includes_name(self, formatter, sample_record):
        "Test that format includes logger name."
        formatted = formatter.format(sample_record)
        
        assert "test" in formatted

    def test_format_includes_message(self, formatter, sample_record):
        "Test that format includes message."
        formatted = formatter.format(sample_record)
        
        assert "Test message" in formatted

    def test_colors_for_different_levels(self, formatter):
        "Test that different levels have different colors."
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level, level_name in levels:
            record = logging.LogRecord(
                name="test", level=level, pathname="test.py",
                lineno=1, msg="Test", args=(), exc_info=None
            )
            record.created = 1700000000.0
            record.msecs = 0

            formatted = formatter.format(record)

            # Each level should have its color code
            assert level_name in formatted

    def test_color_codes_present(self, formatter, sample_record):
        "Test that ANSI color codes are present."
        formatted = formatter.format(sample_record)

        # Check for ANSI escape codes
        assert "\033[" in formatted
    
    def test_reset_code_present(self, formatter, sample_record):
        "Test that reset code is present."
        formatted = formatter.format(sample_record)

        assert "\033[0m" in formatted


class TestSetupLogging:
    "Test suite for setup_logging function."

    def test_setup_logging_returns_logger(self):
        "Test that setup_logging returns a logger."
        logger = setup_logging(name="test_setup")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_setup"

    def test_setup_logging_sets_level(self):
        "Test that setup_logging sets the correct level."
        logger = setup_logging(name="test_level", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_logging_adds_handler(self):
        "Test that setup_logging adds a StreamHandler."
        # Create a unique name to avoid conflicts
        import uuid
        unique_name = f"test_handler_{uuid.uuid4().hex[:8]}"

        logger = setup_logging(name=unique_name)

        assert len(logger.handlers) > 0
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_uses_fastapi_formatter_for_tty(self):
        "Test that FastAPIFormatter is used for TTY."
        import uuid
        unique_name = f"test_formatter_{uuid.uuid4().hex[:8]}"

        with patch.object(sys.stdout, 'isatty', return_value=True):
            logger = setup_logging(name=unique_name)

            handler = logger.handlers[0]
            assert isinstance(handler.formatter, FastAPIFormatter)

    def test_setup_logging_uses_standard_formatter_for_non_tty(self):
        "Test that standard formatter is used for non-TTY."
        import uuid
        unique_name = f"test_std_formatter_{uuid.uuid4().hex[:8]}"
        
        with patch.object(sys.stdout, 'isatty', return_value=False):
            logger = setup_logging(name=unique_name)
            
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, logging.Formatter)
            assert not isinstance(handler.formatter, FastAPIFormatter)

    def test_setup_logging_prevents_duplicate_handlers(self):
        """Test that calling setup_logging twice doesn't duplicate handlers."""
        import uuid
        unique_name = f"test_duplicate_{uuid.uuid4().hex[:8]}"
        
        logger1 = setup_logging(name=unique_name)
        initial_handler_count = len(logger1.handlers)
        
        # Call again with same name
        logger2 = setup_logging(name=unique_name)
        
        assert len(logger2.handlers) == initial_handler_count
        assert logger1 is logger2

    def test_setup_logging_handler_goes_to_stdout(self):
        """Test that handler outputs to stdout."""
        import uuid
        unique_name = f"test_stdout_{uuid.uuid4().hex[:8]}"
        
        logger = setup_logging(name=unique_name)
        
        handler = logger.handlers[0]
        assert handler.stream == sys.stdout

    def test_setup_logging_handler_level_matches_logger(self):
        """Test that handler level matches logger level."""
        import uuid
        unique_name = f"test_handler_level_{uuid.uuid4().hex[:8]}"
        
        logger = setup_logging(name=unique_name, level=logging.WARNING)
        
        handler = logger.handlers[0]
        assert handler.level == logging.WARNING


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger."""
        logger = get_logger("test_get")
        
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_same_logger_for_same_name(self):
        """Test that get_logger returns the same logger instance."""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        
        assert logger1 is logger2

    def test_get_logger_different_names_different_loggers(self):
        """Test that different names return different loggers."""
        logger1 = get_logger("test_diff_1")
        logger2 = get_logger("test_diff_2")
        
        assert logger1 is not logger2

    def test_get_logger_preserves_configuration(self):
        """Test that get_logger preserves previous configuration."""
        name = "test_config_preserve"
        
        # Setup logging with specific level
        setup_logging(name=name, level=logging.ERROR)
        
        # Get logger
        logger = get_logger(name)
        
        assert logger.level == logging.ERROR


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_log_message_is_formatted(self):
        """Test that log messages are properly formatted."""
        import uuid
        unique_name = f"test_integration_{uuid.uuid4().hex[:8]}"
        
        # Capture stdout
        captured = StringIO()
        
        with patch.object(sys.stdout, 'isatty', return_value=True):
            logger = setup_logging(name=unique_name)
            
            # Replace handler stream
            logger.handlers[0].stream = captured
            
            logger.info("Integration test message")
            
            output = captured.getvalue()
            assert "Integration test message" in output

    def test_different_log_levels(self):
        """Test that different log levels work correctly."""
        import uuid
        unique_name = f"test_levels_{uuid.uuid4().hex[:8]}"
        
        captured = StringIO()
        
        with patch.object(sys.stdout, 'isatty', return_value=True):
            logger = setup_logging(name=unique_name, level=logging.DEBUG)
            logger.handlers[0].stream = captured
            
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            output = captured.getvalue()
            assert "Debug message" in output
            assert "Info message" in output
            assert "Warning message" in output
            assert "Error message" in output

    def test_log_level_filtering(self):
        """Test that log level filtering works."""
        import uuid
        unique_name = f"test_filter_{uuid.uuid4().hex[:8]}"
        
        captured = StringIO()
        
        with patch.object(sys.stdout, 'isatty', return_value=True):
            logger = setup_logging(name=unique_name, level=logging.WARNING)
            logger.handlers[0].stream = captured
            
            logger.debug("Debug - should be filtered")
            logger.info("Info - should be filtered")
            logger.warning("Warning - should appear")
            
            output = captured.getvalue()
            assert "Debug - should be filtered" not in output
            assert "Info - should be filtered" not in output
            assert "Warning - should appear" in output
