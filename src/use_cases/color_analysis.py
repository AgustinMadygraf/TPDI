"""
Casos de uso para analisis configurable de canales de color.
"""

from dataclasses import dataclass
from typing import List, Literal

from src.entities.image import Image
from src.use_cases.image_processing import (
    apply_grayscale,
    blue_to_grayscale,
    extract_blue_channel,
    extract_green_channel,
    extract_red_channel,
    green_to_grayscale,
    red_to_grayscale,
)


ColorMode = Literal["RGB", "CMY"]


@dataclass(frozen=True)
class ColorAnalysisVariant:
    """Representa una imagen derivada y su etiqueta de presentacion."""

    label: str
    image: Image


@dataclass(frozen=True)
class ColorAnalysisResult:
    """Resultado listo para depuracion y visualizacion."""

    mode: ColorMode
    debug_title: str
    channel_labels: tuple[str, str, str]
    channel_pixel_labels: tuple[str, str, str]
    analysis_title: str
    variants: List[ColorAnalysisVariant]


class ColorChannelAnalyzer:
    """Construye variantes de analisis de color para RGB o CMY."""

    def execute(self, image: Image, color_mode: ColorMode) -> ColorAnalysisResult:
        """Genera variantes y metadatos de analisis para el modo indicado."""
        if image.channels == 1:
            grayscale = apply_grayscale(image)
            return ColorAnalysisResult(
                mode=color_mode,
                debug_title=f"DEPURACION DE CANALES {color_mode}",
                channel_labels=("Canal 1", "Canal 2", "Canal 3"),
                channel_pixel_labels=("Canal 1", "Canal 2", "Canal 3"),
                analysis_title=f"Analisis {color_mode}: {image.name}",
                variants=[ColorAnalysisVariant("ESCALA DE GRISES", grayscale)],
            )

        if color_mode == "CMY":
            return self._build_cmy_analysis(image)

        return self._build_rgb_analysis(image)

    def _build_rgb_analysis(self, image: Image) -> ColorAnalysisResult:
        red_channel = extract_red_channel(image)
        green_channel = extract_green_channel(image)
        blue_channel = extract_blue_channel(image)
        full_grayscale = apply_grayscale(image)
        red_grayscale = red_to_grayscale(image)
        green_grayscale = green_to_grayscale(image)
        blue_grayscale = blue_to_grayscale(image)

        return ColorAnalysisResult(
            mode="RGB",
            debug_title="DEPURACION DE CANALES RGB",
            channel_labels=("Canal Rojo", "Canal Verde", "Canal Azul"),
            channel_pixel_labels=("Rojo", "Verde", "Azul"),
            analysis_title=f"Analisis RGB: {image.name}",
            variants=[
                ColorAnalysisVariant("CANAL ROJO", red_channel),
                ColorAnalysisVariant("CANAL VERDE", green_channel),
                ColorAnalysisVariant("CANAL AZUL", blue_channel),
                ColorAnalysisVariant("ESCALA DE GRISES", full_grayscale),
                ColorAnalysisVariant("ROJO -> GRIS", red_grayscale),
                ColorAnalysisVariant("VERDE -> GRIS", green_grayscale),
                ColorAnalysisVariant("AZUL -> GRIS", blue_grayscale),
            ],
        )

    def _build_cmy_analysis(self, image: Image) -> ColorAnalysisResult:
        cyan_channel = self._extract_cyan_channel(image)
        magenta_channel = self._extract_magenta_channel(image)
        yellow_channel = self._extract_yellow_channel(image)
        full_grayscale = self._apply_cmy_grayscale(image)
        cyan_grayscale = self._cyan_to_grayscale(image)
        magenta_grayscale = self._magenta_to_grayscale(image)
        yellow_grayscale = self._yellow_to_grayscale(image)

        return ColorAnalysisResult(
            mode="CMY",
            debug_title="DEPURACION DE CANALES CMY",
            channel_labels=("Canal Cian", "Canal Magenta", "Canal Amarillo"),
            channel_pixel_labels=("Cian", "Magenta", "Amarillo"),
            analysis_title=f"Analisis CMY: {image.name}",
            variants=[
                ColorAnalysisVariant("CANAL CIAN", cyan_channel),
                ColorAnalysisVariant("CANAL MAGENTA", magenta_channel),
                ColorAnalysisVariant("CANAL AMARILLO", yellow_channel),
                ColorAnalysisVariant("ESCALA DE GRISES", full_grayscale),
                ColorAnalysisVariant("CIAN -> GRIS", cyan_grayscale),
                ColorAnalysisVariant("MAGENTA -> GRIS", magenta_grayscale),
                ColorAnalysisVariant("AMARILLO -> GRIS", yellow_grayscale),
            ],
        )

    def _apply_cmy_grayscale(self, image: Image) -> Image:
        grayscale_data = []
        for i in range(0, len(image.data), 3):
            cyan = 255 - image.data[i]
            magenta = 255 - image.data[i + 1]
            yellow = 255 - image.data[i + 2]
            gray = int((cyan + magenta + yellow) / 3)
            grayscale_data.extend([gray, gray, gray])

        return Image(
            name=f"{image.name}_cmy_grayscale",
            width=image.width,
            height=image.height,
            channels=3,
            data=grayscale_data,
            path=image.path,
        )

    def _extract_cyan_channel(self, image: Image) -> Image:
        return self._build_visible_channel_image(
            image, source_index=0, visible_indexes=(1, 2), suffix="cyan_channel"
        )

    def _extract_magenta_channel(self, image: Image) -> Image:
        return self._build_visible_channel_image(
            image, source_index=1, visible_indexes=(0, 2), suffix="magenta_channel"
        )

    def _extract_yellow_channel(self, image: Image) -> Image:
        return self._build_visible_channel_image(
            image, source_index=2, visible_indexes=(0, 1), suffix="yellow_channel"
        )

    def _cyan_to_grayscale(self, image: Image) -> Image:
        return self._build_channel_grayscale_image(image, 0, suffix="cyan_grayscale")

    def _magenta_to_grayscale(self, image: Image) -> Image:
        return self._build_channel_grayscale_image(image, 1, suffix="magenta_grayscale")

    def _yellow_to_grayscale(self, image: Image) -> Image:
        return self._build_channel_grayscale_image(image, 2, suffix="yellow_grayscale")

    def _build_visible_channel_image(
        self,
        image: Image,
        source_index: int,
        visible_indexes: tuple[int, int],
        suffix: str,
    ) -> Image:
        channel_data = []
        for i in range(0, len(image.data), 3):
            values = [0, 0, 0]
            intensity = 255 - image.data[i + source_index]
            first_visible_index, second_visible_index = visible_indexes
            values[first_visible_index] = intensity
            values[second_visible_index] = intensity
            channel_data.extend(values)

        return Image(
            name=f"{image.name}_{suffix}",
            width=image.width,
            height=image.height,
            channels=3,
            data=channel_data,
            path=image.path,
        )

    def _build_channel_grayscale_image(
        self, image: Image, source_index: int, suffix: str
    ) -> Image:
        grayscale_data = []
        for i in range(0, len(image.data), 3):
            intensity = 255 - image.data[i + source_index]
            grayscale_data.extend([intensity, intensity, intensity])

        return Image(
            name=f"{image.name}_{suffix}",
            width=image.width,
            height=image.height,
            channels=3,
            data=grayscale_data,
            path=image.path,
        )