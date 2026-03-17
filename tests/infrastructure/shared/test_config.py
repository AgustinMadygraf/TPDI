"""Tests for application configuration."""

from pathlib import Path

from src.infrastructure.shared.config import AppConfig, load_config


class TestAppConfig:
    """Test suite for AppConfig and load_config."""

    def test_app_config_defaults_to_rgb(self):
        """Default configuration should use RGB mode."""
        config = AppConfig()

        assert config.COLOR_MODE == "RGB"

    def test_load_config_accepts_color_mode(self):
        """Custom configuration should override color mode."""
        config = load_config(color_mode="CMY")

        assert config.COLOR_MODE == "CMY"

    def test_load_config_converts_input_dir_to_path(self):
        """Input directory should still be normalized to Path."""
        config = load_config(input_dir="data/input")

        assert config.INPUT_DIR == Path("data/input")