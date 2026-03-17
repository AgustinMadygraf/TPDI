"""
Path: src/infrastructure/shared/config.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class AppConfig:
    GUI_BACKEND: Literal["cv2", "matplotlib"] = "cv2"
    INPUT_DIR: Path = field(default_factory=lambda: Path("data/input"))
    LOG_LEVEL: str = "INFO"

    def __post_init__(self):
        # Validar que INPUT_DIR sea un Path válido
        if isinstance(self.INPUT_DIR, str):
            object.__setattr__(self, 'INPUT_DIR', Path(self.INPUT_DIR))


def load_config(
    gui_backend: Literal["cv2", "matplotlib"] = None,
    input_dir: str | Path = None,
    log_level: str = None
) -> AppConfig:
    kwargs = {}    
    if gui_backend is not None:
        kwargs['GUI_BACKEND'] = gui_backend
    if input_dir is not None:
        kwargs['INPUT_DIR'] = input_dir
    if log_level is not None:
        kwargs['LOG_LEVEL'] = log_level

    return AppConfig(**kwargs)
