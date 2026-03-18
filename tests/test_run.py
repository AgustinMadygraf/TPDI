"""Tests for run.py CLI argument parsing and config fallback behavior."""

from src.infrastructure.shared.config import AppConfig, parse_cli_args


def test_parse_args_accepts_mode_cmy():
    args = parse_cli_args(["--mode=CMY"])

    assert args.mode == "CMY"


def test_parse_args_defaults_mode_to_none():
    args = parse_cli_args([])

    assert args.mode is None


def test_load_config_uses_hardcoded_default_mode_when_none():
    config = AppConfig.from_overrides(color_mode=None)

    assert config.color_mode == "CMYK"


def test_parse_args_accepts_image_source_and_camera_index():
    args = parse_cli_args(["--image_source=camera", "--camera_index=2"])

    assert args.image_source == "camera"
    assert args.camera_index == 2


def test_parse_args_accepts_fps():
    args = parse_cli_args(["--fps=20"])

    assert args.fps == 20


def test_load_config_defaults_to_file_source_and_index_zero():
    config = AppConfig.from_overrides()

    assert config.image_source == "file"
    assert config.camera_index == 0
    assert config.fps == 10.0


def test_load_config_accepts_image_source_and_camera_index():
    config = AppConfig.from_overrides(image_source="camera", camera_index=3)

    assert config.image_source == "camera"
    assert config.camera_index == 3


def test_load_config_accepts_fps():
    config = AppConfig.from_overrides(fps=12.5)

    assert config.fps == 12.5
