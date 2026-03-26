"""Tests for application configuration."""

from pathlib import Path

import pytest

from src.infrastructure.settings.config import AppConfig


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

    def display_grid(
        self,
        _images,
        _grid_size=(2, 2),
        _title="Grid",
        _wait_ms=0,
        _close_on_exit=True,
        _quit_key=None,
    ):
        return True


class TestAppConfig:
    """Test suite for AppConfig and AppConfig.from_overrides."""

    def test_app_config_defaults_to_cmyk(self):
        """Default configuration should use CMYK mode."""
        config = AppConfig()

        assert config.color_mode == "CMYK"

    def test_load_config_accepts_color_mode(self):
        """Custom configuration should override color mode."""
        config = AppConfig.from_overrides(color_mode="CMY")

        assert config.color_mode == "CMY"

    def test_load_config_accepts_cmyk_color_mode(self):
        """Configuration should allow selecting CMYK mode."""
        config = AppConfig.from_overrides(color_mode="CMYK")

        assert config.color_mode == "CMYK"

    def test_app_config_defaults_to_file_source_and_index_zero(self):
        """Default input source should be file and camera index 0."""
        config = AppConfig()

        assert config.image_source == "file"
        assert config.camera_index == 0
        assert config.fps == 10.0
        assert config.grid == "2x2"

    def test_load_config_accepts_camera_source_and_index(self):
        """Configuration should allow overriding image source and camera index."""
        config = AppConfig.from_overrides(image_source="camera", camera_index=2)

        assert config.image_source == "camera"
        assert config.camera_index == 2

    def test_load_config_accepts_fps(self):
        """Configuration should allow overriding camera FPS."""
        config = AppConfig.from_overrides(fps=30)

        assert config.fps == 30

    def test_load_config_accepts_grid(self):
        """Configuration should allow overriding CMYK grid layout."""
        config = AppConfig.from_overrides(grid="2x3")

        assert config.grid == "2x3"

    def test_load_config_accepts_camera_mode_and_resolution(self):
        """Camera mode and requested resolution should be configurable."""
        config = AppConfig.from_overrides(
            camera_mode="stream",
            frame_width=1280,
            frame_height=720,
        )

        assert config.camera_mode == "stream"
        assert config.frame_width == 1280
        assert config.frame_height == 720

    def test_load_config_accepts_perf_debug_options(self):
        """Performance debug options should be configurable."""
        config = AppConfig.from_overrides(perf_debug=True, perf_every=12)

        assert config.perf_debug is True
        assert config.perf_every == 12

    def test_load_config_rejects_negative_camera_index(self):
        """Camera index must be zero or positive."""
        with pytest.raises(ValueError, match="camera_index invalido"):
            AppConfig.from_overrides(camera_index=-1)

    def test_load_config_rejects_zero_fps(self):
        """FPS must be greater than zero."""
        with pytest.raises(ValueError, match="fps invalido"):
            AppConfig.from_overrides(fps=0)

    def test_load_config_rejects_unknown_grid(self):
        """Grid must be one of the known layout options."""
        with pytest.raises(ValueError, match="grid invalido"):
            AppConfig.from_overrides(grid="4x4")

    def test_load_config_rejects_unknown_camera_mode(self):
        """Camera mode must be one of the known options."""
        with pytest.raises(ValueError, match="camera_mode invalido"):
            AppConfig.from_overrides(camera_mode="realtime")

    def test_load_config_rejects_invalid_frame_dimensions(self):
        """Frame dimensions must be greater than zero when provided."""
        with pytest.raises(ValueError, match="frame_width invalido"):
            AppConfig.from_overrides(frame_width=0)
        with pytest.raises(ValueError, match="frame_height invalido"):
            AppConfig.from_overrides(frame_height=-1)

    def test_load_config_rejects_invalid_perf_every(self):
        """Perf report interval must be greater than zero."""
        with pytest.raises(ValueError, match="perf_every invalido"):
            AppConfig.from_overrides(perf_every=0)







    def test_app_config_rejects_unknown_active_flexo_palette(self):
        """Active flexo palette must exist in configured palette map."""
        # flexo_active_palette eliminado, ya no se valida existencia

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
