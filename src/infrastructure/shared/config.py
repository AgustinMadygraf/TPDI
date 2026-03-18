"""
Path: src/infrastructure/shared/config.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


ColorMode = Literal["RGB", "CMY", "CMYK"]


@dataclass(frozen=True)
class AppConfig:
    GUI_BACKEND: Literal["cv2", "matplotlib"] = "cv2"
    COLOR_MODE: ColorMode = "RGB"
    CMYK_DOT_GAIN: float = 0.0
    CMYK_TOTAL_INK_LIMIT: int = 1020
    INPUT_DIR: Path = field(default_factory=lambda: Path("data/input"))
    LOG_LEVEL: str = "INFO"

    def __post_init__(self):
        # Validar que INPUT_DIR sea un Path válido
        if isinstance(self.INPUT_DIR, str):
            object.__setattr__(self, "INPUT_DIR", Path(self.INPUT_DIR))

        if not (0.0 <= self.CMYK_DOT_GAIN <= 1.0):
            raise ValueError("CMYK_DOT_GAIN debe estar entre 0.0 y 1.0")

        if not (0 < self.CMYK_TOTAL_INK_LIMIT <= 1020):
            raise ValueError(
                "CMYK_TOTAL_INK_LIMIT debe estar entre 1 y 1020"
            )


def load_config(
    gui_backend: Literal["cv2", "matplotlib"] = None,
    color_mode: ColorMode = None,
    cmyk_dot_gain: float = None,
    cmyk_total_ink_limit: int = None,
    input_dir: str | Path = None,
    log_level: str = None,
) -> AppConfig:
    kwargs = {}
    if gui_backend is not None:
        kwargs["GUI_BACKEND"] = gui_backend
    if color_mode is not None:
        kwargs["COLOR_MODE"] = color_mode
    if cmyk_dot_gain is not None:
        kwargs["CMYK_DOT_GAIN"] = cmyk_dot_gain
    if cmyk_total_ink_limit is not None:
        kwargs["CMYK_TOTAL_INK_LIMIT"] = cmyk_total_ink_limit
    if input_dir is not None:
        kwargs["INPUT_DIR"] = input_dir
    if log_level is not None:
        kwargs["LOG_LEVEL"] = log_level

    return AppConfig(**kwargs)
