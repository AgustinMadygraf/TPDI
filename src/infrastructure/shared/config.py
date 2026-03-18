"""
Path: src/infrastructure/shared/config.py
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from src.use_cases.display_image import ImageDisplayPort

@dataclass(frozen=True)
class AppConfigDefaults:
    gui_backend: str = "cv2"
    color_mode: str = "CMYK"
    input_dir: Path = Path("data/input")
    log_level: str = "INFO"

APP_CONFIG_DEFAULTS = AppConfigDefaults()

DisplayerRegistry = dict[str, type[ImageDisplayPort]]
MODE_CHOICES: tuple[str, str, str] = ("RGB", "CMY", "CMYK")

def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TPDI - Analisis de canales de color")
    parser.add_argument(
        "--mode",
        choices=list(MODE_CHOICES),
        help="Modo de color para el analisis (si se omite usa el default de config)",
    )
    return parser.parse_args(argv)

@dataclass(frozen=True)
class AppConfig:
    _displayers: ClassVar[dict[str, type[ImageDisplayPort]]] = {}

    gui_backend: str = APP_CONFIG_DEFAULTS.gui_backend
    color_mode: str = APP_CONFIG_DEFAULTS.color_mode
    input_dir: Path = APP_CONFIG_DEFAULTS.input_dir
    log_level: str = APP_CONFIG_DEFAULTS.log_level

    def __post_init__(self):
        # Validar que input_dir sea un Path valido.
        if isinstance(self.input_dir, str):
            object.__setattr__(self, "input_dir", Path(self.input_dir))

        # Permite recibir strings (CLI/tests) y normaliza a enum tipado.
        if self.color_mode not in MODE_CHOICES:
            valid_modes = ", ".join(MODE_CHOICES)
            raise ValueError(
                f"color_mode invalido: '{self.color_mode}'. "
                f"Valores permitidos: {valid_modes}"
            )



        # Se elimina la validación de flexo_spot_palettes vacía para simplificar el modelo.

    @classmethod
    def register_displayer(
        cls, backend: str, displayer_class: type[ImageDisplayPort]
    ) -> None:
        cls._displayers[backend] = displayer_class

    @classmethod
    def register_displayers(cls, displayers: DisplayerRegistry) -> None:
        for backend, displayer_class in displayers.items():
            cls.register_displayer(backend, displayer_class)

    @classmethod
    def available_backends(cls) -> list[str]:
        # Asegurar que cv2 este registrado para exponer al menos un backend.
        if "cv2" not in cls._displayers:
            try:
                from src.infrastructure.opencv.cv2_image_displayer import (
                    CV2ImageDisplayer,
                )

                cls.register_displayer("cv2", CV2ImageDisplayer)
            except ImportError:
                pass
        return list(cls._displayers.keys())

    def create_displayer(self) -> ImageDisplayPort:
        backend = self.gui_backend

        if backend not in self._displayers:
            # Lazy loading de displayers built-in.
            if backend == "cv2":
                from src.infrastructure.opencv.cv2_image_displayer import (
                    CV2ImageDisplayer,
                )

                self.register_displayer("cv2", CV2ImageDisplayer)
            elif backend == "matplotlib":
                raise NotImplementedError(
                    f"Backend '{backend}' no implementado aun. "
                    f"Disponibles: {list(self._displayers.keys()) or ['cv2']}"
                )
            else:
                raise ValueError(
                    f"Backend de GUI desconocido: '{backend}'. "
                    f"Disponibles: {list(self._displayers.keys())}"
                )

        displayer_class = self._displayers[backend]
        return displayer_class()

    @classmethod
    def from_overrides(
        cls,
        gui_backend: str = None,
        color_mode: str = None,
        gui_displayers: DisplayerRegistry = None,
        input_dir: str | Path = None,
        log_level: str = None,
    ) -> "AppConfig":
        kwargs = {}
        if gui_backend is not None:
            kwargs["gui_backend"] = gui_backend
        if color_mode is not None:
            kwargs["color_mode"] = color_mode
        if input_dir is not None:
            kwargs["input_dir"] = input_dir
        if log_level is not None:
            kwargs["log_level"] = log_level

        config = cls(**kwargs)
        if gui_displayers:
            cls.register_displayers(gui_displayers)

        return config
