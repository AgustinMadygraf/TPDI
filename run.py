"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
from src.infrastructure.shared.path_validator import PathValidator
from src.interface_adapters.controllers.main_controller import MainController

def main() -> None:
    "Punto de entrada principal."
    path_validator = PathValidator(base_path=MainController.DEFAULT_INPUT_DIR)
    loader = CV2ImageLoader(path_validator=path_validator)
    displayer = CV2ImageDisplayer()

    app = CLIApp(loader=loader, displayer=displayer)
    app.run_color_channel_analysis()

if __name__ == "__main__":
    main()
