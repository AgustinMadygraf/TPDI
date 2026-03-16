"""
Path: src/infrastructure/cli/app.py
"""

from src.entities.image import Image
from src.infrastructure.opencv import CV2ImageAdapter
from src.infrastructure.settings.logger import setup_logging, get_logger
from src.interface_adapters.controllers.main_controller import MainController
from src.interface_adapters.gateways import ImageGateway


class CLIApp:
    "Aplicación de línea de comandos para TPDI."
    def __init__(self):
        # Configurar logging una vez al inicio
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        # Crear adapter (infrastructure) e inyectarlo al gateway (interface_adapters)
        adapter = CV2ImageAdapter()
        self._gateway = ImageGateway(adapter=adapter, base_path=MainController.DEFAULT_INPUT_DIR)
        self._controller = MainController(image_loader=self._gateway)

    def run(self) -> None:
        """Ejecuta la aplicación CLI."""
        self._logger.info("=" * 50)
        self._logger.info("TPDI - Procesamiento Digital de Imágenes")
        self._logger.info("=" * 50)

        input_dir = MainController.DEFAULT_INPUT_DIR
        self._logger.info("Cargando imágenes desde: %s", input_dir)

        summary = self._controller.load_default_images()

        if summary["count"] == 0:
            self._logger.warning("No se encontraron imágenes en: %s", input_dir.absolute())
            return

        self._logger.info("Cargadas %d imagen(es)", summary["count"])

        for img_info in summary["images"]:
            self._logger.info("  [%s] %dx%d px, %d canal(es)",
                            img_info["name"],
                            img_info["width"],
                            img_info["height"],
                            img_info["channels"])

        first_image = self._controller.get_image(0)
        if first_image:
            self._display_image(first_image)

        self._logger.info("Visor cerrado. Aplicación finalizada.")

    def _display_image(self, image: Image) -> None:
        """Muestra una imagen usando el adaptador."""
        self._logger.info("Mostrando imagen: %s", image.name)
        self._gateway.display(image)
