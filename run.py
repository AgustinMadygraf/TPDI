"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.shared.config import load_config
from src.infrastructure.shared.displayer_factory import DisplayerFactory
from src.infrastructure.shared.path_validator import PathValidator


def main() -> None:
    "Punto de entrada principal de la aplicación TPDI."
    config = load_config()

    # Crear dependencias
    path_validator = PathValidator(base_path=config.INPUT_DIR)
    loader = CV2ImageLoader(path_validator=path_validator)
    displayer = DisplayerFactory.create(config)

    # Inicializar y ejecutar aplicación
    app = CLIApp(loader, displayer, None, config.COLOR_MODE)
    app.run_color_channel_analysis()


if __name__ == "__main__":
    main()
