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

    assert config.color_mode == "RGB"
