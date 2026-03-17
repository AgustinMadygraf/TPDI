"""
Path: src/infrastructure/opencv/cv2_image_displayer.py
"""

from typing import List, Tuple
import cv2
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.shared.logger import get_logger
from src.use_cases.display_image import ImageDisplayPort
from src.entities.image import Image


class CV2ImageDisplayer(ImageDisplayPort):
    "Muestra imágenes usando OpenCV."

    def __init__(self):
        "Inicializa el displayer."
        self._logger = get_logger(__name__)
        self._numpy_adapter = NumPyImageAdapter()

    def _prepare_for_display(self, data):
        "Prepara los datos de la imagen para su visualización con OpenCV."
        if len(data.shape) == 2:
            data = cv2.cvtColor(data, cv2.COLOR_GRAY2BGR)
        elif len(data.shape) == 3 and data.shape[2] == 3:
            data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        return data

    def display(
        self, image: Image, comparison: Image = None, layout: str = "vertical"
    ) -> None:
        data = self._numpy_adapter.to_numpy(image)

        if comparison:
            comp_data = self._numpy_adapter.to_numpy(comparison)
            if data.shape[:2] != comp_data.shape[:2]:
                comp_data = self._numpy_adapter.resize(
                    comp_data, (data.shape[1], data.shape[0])
                )
            data_display = self._prepare_for_display(data)
            comp_display = self._prepare_for_display(comp_data)
            _height = data_display.shape[0]
            width = data_display.shape[1]
            label_height = 30
            label_original = self._numpy_adapter.zeros((label_height, width, 3))
            label_modified = self._numpy_adapter.zeros((label_height, width, 3))

            cv2.putText(
                label_original,
                "ORIGINAL",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                label_modified,
                "ESCALA DE GRISES",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )
            if layout == "vertical":
                top = self._numpy_adapter.vstack([label_original, data_display])
                bottom = self._numpy_adapter.vstack([label_modified, comp_display])
                display_data = self._numpy_adapter.vstack([top, bottom])
            else:
                left = self._numpy_adapter.vstack([label_original, data_display])
                right = self._numpy_adapter.vstack([label_modified, comp_display])
                display_data = self._numpy_adapter.hstack([left, right])

            cv2.imshow(f"Comparacion: {image.name}", display_data)
            self._logger.info("Mostrando comparacion: %s (%s)", image.name, layout)
        else:
            display_data = self._prepare_for_display(data)
            cv2.imshow(image.name, display_data)
            self._logger.info("Mostrando: %s", image.name)

        self._logger.info("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def display_grid(
        self,
        images: List[Tuple[Image, str]],
        grid_size: Tuple[int, int] = (2, 2),
        title: str = "Grid",
    ) -> None:
        "Muestra un grid de imágenes con etiquetas usando OpenCV."
        rows, cols = grid_size
        label_height = 30

        # Preparar todas las imágenes con sus etiquetas
        cells = []
        for img, label in images:
            data = self._numpy_adapter.to_numpy(img)
            display_data = self._prepare_for_display(data)

            # Crear etiqueta
            _height, width = display_data.shape[:2]
            label_img = self._numpy_adapter.zeros((label_height, width, 3))
            cv2.putText(
                label_img,
                label,
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # Combinar etiqueta + imagen
            cell = self._numpy_adapter.vstack([label_img, display_data])
            cells.append(cell)

        # Determinar tamaño de celda (usar el máximo para uniformidad)
        if not cells:
            self._logger.warning("No hay imágenes para mostrar en grid")
            return

        max_height = max(cell.shape[0] for cell in cells)
        max_width = max(cell.shape[1] for cell in cells)

        # Normalizar todas las celdas al mismo tamaño
        normalized_cells = []
        for cell in cells:
            if cell.shape[0] != max_height or cell.shape[1] != max_width:
                normalized = self._numpy_adapter.resize(cell, (max_width, max_height))
            else:
                normalized = cell
            normalized_cells.append(normalized)

        # Rellenar celdas vacías si es necesario
        total_cells = rows * cols
        while len(normalized_cells) < total_cells:
            empty_cell = self._numpy_adapter.zeros((max_height, max_width, 3))
            normalized_cells.append(empty_cell)

        # Construir el grid fila por fila
        grid_rows = []
        for row_idx in range(rows):
            start_idx = row_idx * cols
            end_idx = start_idx + cols
            row_cells = normalized_cells[start_idx:end_idx]

            # Concatenar horizontalmente
            if row_cells:
                row_img = self._numpy_adapter.hstack(row_cells)
                grid_rows.append(row_img)

        # Concatenar verticalmente todas las filas
        if grid_rows:
            grid_img = self._numpy_adapter.vstack(grid_rows)
            cv2.imshow(title, grid_img)
            self._logger.info("Mostrando grid %dx%d: %s", rows, cols, title)

        self._logger.info("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
