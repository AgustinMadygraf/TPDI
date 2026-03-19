"""
Path: src/infrastructure/opencv/cv2_image_displayer.py
"""

from typing import List, Optional, Tuple
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

    def _get_screen_size(self) -> tuple[int, int]:
        """Retorna (ancho, alto) de pantalla con fallback seguro."""
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            width = int(root.winfo_screenwidth())
            height = int(root.winfo_screenheight())
            root.destroy()
            if width > 0 and height > 0:
                return width, height
        except Exception:
            pass
        return (1920, 1080)

    def _fit_image_to_screen(self, image, margin_ratio: float = 0.9):
        """Escala la imagen para que no exceda la pantalla."""
        screen_width, screen_height = self._get_screen_size()
        max_width = int(screen_width * margin_ratio)
        max_height = int(screen_height * margin_ratio)

        height, width = image.shape[:2]
        if width <= max_width and height <= max_height:
            return image

        scale = min(max_width / width, max_height / height)
        target_width = max(1, int(width * scale))
        target_height = max(1, int(height * scale))
        return cv2.resize(
            image,
            (target_width, target_height),
            interpolation=cv2.INTER_AREA,
        )

    def display(
        self,
        image: Image,
        comparison: Image = None,
        layout: str = "vertical",
        comparison_labels: Optional[Tuple[str, str]] = None,
    ) -> None:
        data = self._numpy_adapter.to_numpy(image)

        if comparison:
            main_label, comparison_label = comparison_labels or (
                "ORIGINAL",
                "ESCALA DE GRISES",
            )
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
                main_label,
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                label_modified,
                comparison_label,
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
        wait_ms: int = 0,
        close_on_exit: bool = True,
        quit_key: str | None = None,
    ) -> bool:
        "Muestra un grid de imagenes con etiquetas usando OpenCV."
        rows, cols = grid_size
        label_height = 30

        # Preparar todas las imagenes con sus etiquetas
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

        # Determinar tamano de celda (usar el maximo para uniformidad)
        if not cells:
            self._logger.warning("No hay imagenes para mostrar en grid")
            return True

        max_height = max(cell.shape[0] for cell in cells)
        max_width = max(cell.shape[1] for cell in cells)

        # Normalizar todas las celdas al mismo tamano
        normalized_cells = []
        for cell in cells:
            if cell.shape[0] != max_height or cell.shape[1] != max_width:
                normalized = self._numpy_adapter.resize(cell, (max_width, max_height))
            else:
                normalized = cell
            normalized_cells.append(normalized)

        # Rellenar celdas vacias si es necesario
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

            if row_cells:
                row_img = self._numpy_adapter.hstack(row_cells)
                grid_rows.append(row_img)

        if grid_rows:
            grid_img = self._numpy_adapter.vstack(grid_rows)
            grid_img = self._fit_image_to_screen(grid_img)
            cv2.imshow(title, grid_img)
            self._logger.info("Mostrando grid %dx%d: %s", rows, cols, title)

        should_continue = True
        key_code = cv2.waitKey(wait_ms if wait_ms > 0 else 0)
        if quit_key and key_code != -1:
            try:
                pressed_key = chr(key_code & 0xFF).lower()
                if pressed_key == quit_key.lower():
                    should_continue = False
            except ValueError:
                pass

        if close_on_exit:
            cv2.destroyAllWindows()

        return should_continue

    def close_windows(self) -> None:
        "Cierra todas las ventanas abiertas de OpenCV."
        cv2.destroyAllWindows()
