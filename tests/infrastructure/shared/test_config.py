"""Tests for application configuration."""

from pathlib import Path

import pytest

from src.infrastructure.shared.config import AppConfig
from src.use_cases.color_separation import (
    FlexoSpotPalette,
    SpotInk,
    default_flexo_spot_palettes,
)


class DummyDisplayer:
    """Minimal displayer used to validate plugin registration."""

    def display(
        self,
        _image,
        _comparison=None,
        _layout="vertical",
        _comparison_labels=None,
    ):
        return None

    def display_grid(self, _images, _grid_size=(2, 2), _title="Grid"):
        return None


class TestAppConfig:
    """Test suite for AppConfig and AppConfig.from_overrides."""

    def test_app_config_defaults_to_rgb(self):
        """Default configuration should use RGB mode."""
        config = AppConfig()

        assert config.color_mode == "RGB"
        assert config.cmyk_dot_gain == 0.0
        assert config.cmyk_total_ink_limit == 1020
        assert config.flexo_active_palette == "CYAN_MAGENTA"
        assert "CYAN_MAGENTA" in config.flexo_spot_palettes

    def test_load_config_accepts_color_mode(self):
        """Custom configuration should override color mode."""
        config = AppConfig.from_overrides(color_mode="CMY")

        assert config.color_mode == "CMY"

    def test_load_config_accepts_cmyk_color_mode(self):
        """Configuration should allow selecting CMYK mode."""
        config = AppConfig.from_overrides(color_mode="CMYK")

        assert config.color_mode == "CMYK"

    def test_load_config_accepts_cmyk_print_parameters(self):
        """Configuration should allow overriding CMYK print-process parameters."""
        config = AppConfig.from_overrides(
            cmyk_dot_gain=0.12, cmyk_total_ink_limit=840
        )

        assert config.cmyk_dot_gain == 0.12
        assert config.cmyk_total_ink_limit == 840

    def test_load_config_accepts_flexo_palette_configuration(self):
        """Configuration should allow selecting active palette."""
        palettes = default_flexo_spot_palettes()
        config = AppConfig.from_overrides(
            flexo_active_palette="BLACK_YELLOW",
            flexo_spot_palettes=palettes,
        )

        assert config.flexo_active_palette == "BLACK_YELLOW"
        assert config.flexo_spot_palettes["BLACK_YELLOW"].name == "BLACK_YELLOW"

    def test_app_config_rejects_invalid_dot_gain(self):
        """Dot gain must stay in the expected range."""
        with pytest.raises(ValueError):
            AppConfig(cmyk_dot_gain=1.5)

    def test_app_config_rejects_invalid_total_ink_limit(self):
        """Total ink limit must stay in the expected range."""
        with pytest.raises(ValueError):
            AppConfig(cmyk_total_ink_limit=0)

    def test_app_config_rejects_unknown_active_flexo_palette(self):
        """Active flexo palette must exist in configured palette map."""
        palettes = {
            "CUSTOM": FlexoSpotPalette(
                name="CUSTOM",
                first_ink=SpotInk(name="A", rgb=(10, 20, 30)),
                second_ink=SpotInk(name="B", rgb=(40, 50, 60)),
            )
        }

        with pytest.raises(ValueError):
            AppConfig(
                flexo_active_palette="MISSING",
                flexo_spot_palettes=palettes,
            )

    def test_load_config_converts_input_dir_to_path(self):
        """Input directory should still be normalized to Path."""
        config = AppConfig.from_overrides(input_dir="data/input")

        assert config.input_dir == Path("data/input")

    def test_available_backends_includes_cv2(self):
        """Available backends should expose cv2 when OpenCV displayer is available."""
        backends = AppConfig.available_backends()

        assert "cv2" in backends

    def test_create_displayer_returns_cv2_displayer_by_default(self):
        """Default configuration should instantiate the cv2 displayer."""
        config = AppConfig()

        displayer = config.create_displayer()

        assert displayer.__class__.__name__ == "CV2ImageDisplayer"

    def test_create_displayer_rejects_unknown_backend(self):
        """Unknown GUI backend should fail with a clear validation error."""
        config = AppConfig(gui_backend="unknown")

        with pytest.raises(ValueError):
            config.create_displayer()

    def test_create_displayer_matplotlib_not_implemented(self):
        """Matplotlib backend should currently be marked as not implemented."""
        config = AppConfig(gui_backend="matplotlib")

        with pytest.raises(NotImplementedError):
            config.create_displayer()

    def test_load_config_registers_custom_displayer_backend(self):
        """Bootstrap should allow registering custom GUI backends."""
        backend = "dummy_plugin_backend"
        config = AppConfig.from_overrides(
            gui_backend=backend,
            gui_displayers={backend: DummyDisplayer},
        )

        displayer = config.create_displayer()

        assert isinstance(displayer, DummyDisplayer)