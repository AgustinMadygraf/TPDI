"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
from src.infrastructure.settings.logger import setup_logging, get_logger
from src.interface_adapters.controllers.main_controller import MainController
from src.interface_adapters.gateways.image_gateway import ImageGateway
from src.use_cases.load_images import ImageLoaderPort
from src.entities.image import Image

class CLIApp:
    "Aplicación de línea de comandos para TPDI."
    def __init__(self, adapter: ImageLoaderPort):
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        self._gateway = ImageGateway(
            adapter=adapter,
            base_path=MainController.DEFAULT_INPUT_DIR,
            on_load_error=self._on_load_error
        )
        self._controller = MainController(
            image_loader=self._gateway,
            on_load_error=self._on_load_error
        )

    def _on_load_error(self, path: Path, exc: Exception) -> None:
        """Callback para manejar errores de carga de imágenes."""
        self._logger.warning("No se pudo cargar imagen %s: %s", path, exc)

    def run(self) -> None:
        "Ejecuta la aplicación CLI."
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
        "Muestra una imagen usando el adaptador."
        self._logger.info("Mostrando imagen: %s", image.name)
        self._gateway.display(image)
