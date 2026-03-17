"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
from typing import List, Tuple

from src.infrastructure.settings.logger import setup_logging, get_logger
from src.interface_adapters.controllers.main_controller import MainController
from src.interface_adapters.gateways.image_gateway import ImageGateway
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.image_processing import (
    apply_grayscale,
    extract_red_channel,
    extract_green_channel,
    extract_blue_channel,
    red_to_grayscale,
    green_to_grayscale,
    blue_to_grayscale
)
from src.entities.image import Image


class CLIApp:
    """Aplicación de línea de comandos para TPDI."""

    def __init__(
        self,
        loader: ImageLoaderPort,
        displayer: ImageDisplayPort,
        base_path: Path = None
    ):
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        self._displayer = displayer
        self._loader = loader
        self._base_path = base_path or MainController.DEFAULT_INPUT_DIR

    def _on_load_error(self, path: Path, exc: Exception) -> None:
        """Callback para manejar errores de carga de imágenes."""
        self._logger.warning("No se pudo cargar imagen %s: %s", path, exc)

    def load_images(self) -> List[Image]:
        """Carga todas las imágenes del directorio base."""
        use_case = LoadImagesFromDirectory(self._loader, on_error=self._on_load_error)
        return use_case.execute(self._base_path)

    def run_color_channel_analysis(self) -> bool:
        """Ejecuta análisis de canales de color en grid 2x3.
        
        Returns:
            True si se ejecutó correctamente, False si no hay imágenes.
        """
        print("=" * 50)
        print("TPDI - Analisis de Canales de Color")
        print("=" * 50)
        print()
        
        # Cargar imágenes
        print(f"Cargando imagenes desde: {self._base_path}")
        images = self.load_images()
        
        if not images:
            print(f"ERROR: No se encontraron imagenes en: {self._base_path}")
            print("Agrega imagenes PNG/JPG a la carpeta data/input/")
            print()
            return False
        
        print(f"Cargadas {len(images)} imagen(es)")
        print()
        
        # Tomar la primera imagen
        original = images[0]
        print(f"Imagen seleccionada: {original.name}")
        print(f"  Dimensiones: {original.width}x{original.height}")
        print(f"  Canales: {original.channels}")
        print()
        
        # Procesar variantes
        print("Procesando canales de color...")
        variants = self._process_color_variants(original)
        print(f"  Original: {original.name}")
        for name, img in variants:
            print(f"  {name}: {img.name}")
        print()
        
        # Mostrar grid 2x4
        self._display_grid_2x4(original, variants)
        
        print()
        print("Aplicacion finalizada.")
        return True

    def _process_color_variants(self, original: Image) -> List[Tuple[str, Image]]:
        """Procesa las variantes de canales de color RGB.
        
        Args:
            original: Imagen original.
            
        Returns:
            Lista de tuplas (nombre_descriptivo, imagen_procesada).
        """
        return [
            ("Canal Rojo (R,0,0)", extract_red_channel(original)),
            ("Canal Verde (0,G,0)", extract_green_channel(original)),
            ("Canal Azul (0,0,B)", extract_blue_channel(original)),
            ("Escala de grises", apply_grayscale(original)),
            ("Rojo -> Gris", red_to_grayscale(original)),
            ("Verde -> Gris", green_to_grayscale(original)),
            ("Azul -> Gris", blue_to_grayscale(original))
        ]

    def _display_grid_2x4(self, original: Image, variants: List[Tuple[str, Image]]) -> None:
        """Muestra el grid 2x4 con la imagen original y variantes RGB.
        
        Args:
            original: Imagen original.
            variants: Lista de variantes procesadas.
        """
        print("Mostrando grid de analisis 2x4:")
        print("  [FILA 1] ORIGINAL | ROJO (R,0,0) | VERDE (0,G,0) | AZUL (0,0,B)")
        print("  [FILA 2] GRIS (promedio) | R->GRIS (R,R,R) | V->GRIS (G,G,G) | A->GRIS (B,B,B)")
        print()
        print("Presiona cualquier tecla en la ventana para cerrar...")
        print()
        
        # Grid 2x4: 2 filas, 4 columnas
        red_channel = variants[0][1]
        green_channel = variants[1][1]
        blue_channel = variants[2][1]
        full_grayscale = variants[3][1]
        red_grayscale = variants[4][1]
        green_grayscale = variants[5][1]
        blue_grayscale = variants[6][1]
        
        grid_images = [
            # Fila 1
            (original, "ORIGINAL"),
            (red_channel, "CANAL ROJO"),
            (green_channel, "CANAL VERDE"),
            (blue_channel, "CANAL AZUL"),
            # Fila 2
            (full_grayscale, "ESCALA DE GRISES"),
            (red_grayscale, "ROJO -> GRIS"),
            (green_grayscale, "VERDE -> GRIS"),
            (blue_grayscale, "AZUL -> GRIS")
        ]
        
        self._displayer.display_grid(
            images=grid_images,
            grid_size=(2, 4),
            title=f"Analisis RGB: {original.name}"
        )

    def run(self) -> None:
        """Ejecuta la aplicación CLI estándar (carga y muestra imágenes)."""
        self._logger.info("=" * 50)
        self._logger.info("TPDI - Procesamiento Digital de Imagenes")
        self._logger.info("=" * 50)

        self._logger.info("Cargando imagenes desde: %s", self._base_path)
        images = self.load_images()

        if not images:
            self._logger.warning("No se encontraron imagenes en: %s", self._base_path)
            return

        self._logger.info("Cargadas %d imagen(es)", len(images))

        for img in images:
            self._logger.info("  [%s] %dx%d px, %d canal(es)",
                            img.name,
                            img.width,
                            img.height,
                            img.channels)

        # Mostrar primera imagen
        if images:
            self._display_image(images[0])

        self._logger.info("Visor cerrado. Aplicacion finalizada.")

    def _display_image(self, image: Image) -> None:
        """Muestra una imagen usando el displayer."""
        self._logger.info("Mostrando imagen: %s", image.name)
        self._displayer.display(image)

    def _display_comparison(self, original: Image, modified: Image) -> None:
        """Muestra comparación lado a lado de dos imágenes."""
        self._logger.info("Mostrando comparacion: %s", original.name)
        self._displayer.display(original, modified)
