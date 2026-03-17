"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_adapter import CV2ImageAdapter
from src.interface_adapters.controllers.main_controller import MainController

def main() -> None:
    "Punto de entrada principal."
    adapter = CV2ImageAdapter(base_path=MainController.DEFAULT_INPUT_DIR)
    app = CLIApp(adapter=adapter)
    app.run()

if __name__ == "__main__":
    main()
