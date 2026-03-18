"""Tests for application configuration."""

from pathlib import Path

from src.infrastructure.shared.config import AppConfig, load_config


class TestAppConfig:
    """Test suite for AppConfig and load_config."""

    def test_app_config_defaults_to_rgb(self):
        """Default configuration should use RGB mode."""
        config = AppConfig()

        assert config.COLOR_MODE == "RGB"
        assert config.CMYK_DOT_GAIN == 0.0
        assert config.CMYK_TOTAL_INK_LIMIT == 1020

    def test_load_config_accepts_color_mode(self):
        """Custom configuration should override color mode."""
        config = load_config(color_mode="CMY")

        assert config.COLOR_MODE == "CMY"

    def test_load_config_accepts_cmyk_color_mode(self):
        """Configuration should allow selecting CMYK mode."""
        config = load_config(color_mode="CMYK")

        assert config.COLOR_MODE == "CMYK"

    def test_load_config_accepts_cmyk_print_parameters(self):
        """Configuration should allow overriding CMYK print-process parameters."""
        config = load_config(cmyk_dot_gain=0.12, cmyk_total_ink_limit=840)

        assert config.CMYK_DOT_GAIN == 0.12
        assert config.CMYK_TOTAL_INK_LIMIT == 840

    def test_app_config_rejects_invalid_dot_gain(self):
        """Dot gain must stay in the expected range."""
        try:
            AppConfig(CMYK_DOT_GAIN=1.5)
            assert False, "Expected ValueError for invalid dot gain"
        except ValueError:
            assert True

    def test_app_config_rejects_invalid_total_ink_limit(self):
        """Total ink limit must stay in the expected range."""
        try:
            AppConfig(CMYK_TOTAL_INK_LIMIT=0)
            assert False, "Expected ValueError for invalid total ink limit"
        except ValueError:
            assert True

    def test_load_config_converts_input_dir_to_path(self):
        """Input directory should still be normalized to Path."""
        config = load_config(input_dir="data/input")

        assert config.INPUT_DIR == Path("data/input")