"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.shared.config import AppConfig, parse_cli_args
from src.infrastructure.shared.path_validator import PathValidator


class AppBootstrap:
    def __init__(self, mode: str | None = None):
        self._mode = mode

    def run(self) -> None:
        config = AppConfig.from_overrides(color_mode=self._mode)

        # Crear dependencias
        path_validator = PathValidator(base_path=config.input_dir)
        loader = CV2ImageLoader(path_validator=path_validator)
        displayer = config.create_displayer()

        # Inicializar y ejecutar aplicacion
        app = CLIApp(
            loader,
            displayer,
            None,
            config.color_mode,
            config.cmyk_dot_gain,
            config.cmyk_total_ink_limit,
        )
        app.run_color_channel_analysis()


def main() -> None:
    "Punto de entrada principal de la aplicacion TPDI."
    args = parse_cli_args()
    AppBootstrap(mode=args.mode).run()


if __name__ == "__main__":
    main()
