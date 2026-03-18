"""Politicas de separacion de color para procesos de impresion."""

from dataclasses import dataclass
from typing import Protocol


class CmykSeparationPolicy(Protocol):
    """Contrato para conversion y visualizacion de separaciones CMYK."""

    def rgb_to_cmyk(self, red: int, green: int, blue: int) -> tuple[int, int, int, int]:
        """Convierte un pixel RGB a CMYK en rango 0..255."""

    def channel_to_display_rgb(self, channel_index: int, intensity: int) -> tuple[int, int, int]:
        """Mapea un canal CMYK a una representacion RGB visible."""

    def cmyk_to_display_gray(
        self, cyan: int, magenta: int, yellow: int, black: int
    ) -> int:
        """Calcula un nivel de gris visible (0..255) desde CMYK."""


@dataclass(frozen=True)
class SpotInk:
    """Define una tinta plana por nombre y color de referencia en sustrato blanco."""

    name: str
    rgb: tuple[int, int, int]


@dataclass(frozen=True)
class FlexoSpotPalette:
    """Paleta de 2 tintas para separacion flexografica basica."""

    name: str
    first_ink: SpotInk
    second_ink: SpotInk


class FlexoTwoSpotSeparationPolicy(Protocol):
    """Contrato para separar una imagen RGB en 2 canales de tinta plana."""

    def rgb_to_spot_channels(
        self,
        red: int,
        green: int,
        blue: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int]:
        """Convierte RGB a intensidades de 2 tintas en rango 0..255."""

    def channel_to_display_rgb(
        self,
        channel_index: int,
        intensity: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int, int]:
        """Mapea un canal de tinta plana a RGB visible en monitor."""

    def channels_to_display_rgb(
        self,
        first_intensity: int,
        second_intensity: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int, int]:
        """Combina ambas tintas para simulacion visible en monitor."""


def default_flexo_spot_palettes() -> dict[str, FlexoSpotPalette]:
    """Retorna paletas base para iniciar flujos flexo de 2 plenos."""
    cyan = SpotInk(name="CYAN", rgb=(0, 174, 239))
    magenta = SpotInk(name="MAGENTA", rgb=(236, 0, 140))
    black = SpotInk(name="BLACK", rgb=(20, 20, 20))
    yellow = SpotInk(name="YELLOW", rgb=(255, 242, 0))

    return {
        "CYAN_MAGENTA": FlexoSpotPalette(
            name="CYAN_MAGENTA",
            first_ink=cyan,
            second_ink=magenta,
        ),
        "BLACK_YELLOW": FlexoSpotPalette(
            name="BLACK_YELLOW",
            first_ink=black,
            second_ink=yellow,
        ),
    }


class GenericCmykSeparationPolicy:
    """Politica CMYK generica para analisis y simulacion de impresion."""

    def __init__(
        self,
        dot_gain: float = 0.0,
        total_ink_limit: int = 1020,
    ) -> None:
        self._dot_gain = dot_gain
        self._total_ink_limit = total_ink_limit

    def rgb_to_cmyk(self, red: int, green: int, blue: int) -> tuple[int, int, int, int]:
        red_norm = red / 255.0
        green_norm = green / 255.0
        blue_norm = blue / 255.0

        key = 1.0 - max(red_norm, green_norm, blue_norm)
        if key >= 1.0:
            return (0, 0, 0, 255)

        cyan = (1.0 - red_norm - key) / (1.0 - key)
        magenta = (1.0 - green_norm - key) / (1.0 - key)
        yellow = (1.0 - blue_norm - key) / (1.0 - key)

        channels = [
            int(round(cyan * 255)),
            int(round(magenta * 255)),
            int(round(yellow * 255)),
            int(round(key * 255)),
        ]

        if self._dot_gain > 0:
            channels = [
                min(255, int(round(value * (1.0 + self._dot_gain))))
                for value in channels
            ]

        total_ink = sum(channels)
        if total_ink > self._total_ink_limit:
            scale = self._total_ink_limit / total_ink
            channels = [int(round(value * scale)) for value in channels]

        return (channels[0], channels[1], channels[2], channels[3])

    def channel_to_display_rgb(self, channel_index: int, intensity: int) -> tuple[int, int, int]:
        if channel_index == 0:
            return (255 - intensity, 255, 255)
        if channel_index == 1:
            return (255, 255 - intensity, 255)
        if channel_index == 2:
            return (255, 255, 255 - intensity)

        value = 255 - intensity
        return (value, value, value)

    def cmyk_to_display_gray(self, cyan: int, magenta: int, yellow: int, black: int) -> int:
        return 255 - int((cyan + magenta + yellow + black) / 4)


class BasicFlexoTwoSpotSeparationPolicy:
    """Separacion baseline para flexo 2 plenos usando mezcla lineal acotada."""

    def rgb_to_spot_channels(
        self,
        red: int,
        green: int,
        blue: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int]:
        # Modelo sustractivo simplificado en absorbancia: A = 1 - R.
        target = (
            1.0 - (red / 255.0),
            1.0 - (green / 255.0),
            1.0 - (blue / 255.0),
        )
        first_abs = self._ink_absorbance(palette.first_ink)
        second_abs = self._ink_absorbance(palette.second_ink)

        w1, w2 = self._solve_two_channel_mix(target, first_abs, second_abs)
        return (int(round(w1 * 255)), int(round(w2 * 255)))

    def channel_to_display_rgb(
        self,
        channel_index: int,
        intensity: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int, int]:
        ink = palette.first_ink if channel_index == 0 else palette.second_ink
        return self._single_ink_display(ink, intensity)

    def channels_to_display_rgb(
        self,
        first_intensity: int,
        second_intensity: int,
        palette: FlexoSpotPalette,
    ) -> tuple[int, int, int]:
        first_abs = self._ink_absorbance(palette.first_ink)
        second_abs = self._ink_absorbance(palette.second_ink)
        w1 = max(0.0, min(1.0, first_intensity / 255.0))
        w2 = max(0.0, min(1.0, second_intensity / 255.0))

        mixed_abs = [
            max(0.0, min(1.0, w1 * first_abs[idx] + w2 * second_abs[idx]))
            for idx in range(3)
        ]
        return tuple(int(round((1.0 - value) * 255)) for value in mixed_abs)

    def _ink_absorbance(self, ink: SpotInk) -> tuple[float, float, float]:
        return tuple(1.0 - (channel / 255.0) for channel in ink.rgb)

    def _single_ink_display(self, ink: SpotInk, intensity: int) -> tuple[int, int, int]:
        weight = max(0.0, min(1.0, intensity / 255.0))
        absorbance = self._ink_absorbance(ink)
        return tuple(
            int(round((1.0 - (weight * channel_abs)) * 255))
            for channel_abs in absorbance
        )

    def _solve_two_channel_mix(
        self,
        target: tuple[float, float, float],
        first_abs: tuple[float, float, float],
        second_abs: tuple[float, float, float],
    ) -> tuple[float, float]:
        # Resuelve min ||w1*A + w2*B - T|| por ecuaciones normales 2x2.
        aa = sum(value * value for value in first_abs)
        bb = sum(value * value for value in second_abs)
        ab = sum(first_abs[idx] * second_abs[idx] for idx in range(3))
        at = sum(first_abs[idx] * target[idx] for idx in range(3))
        bt = sum(second_abs[idx] * target[idx] for idx in range(3))

        determinant = (aa * bb) - (ab * ab)
        if determinant <= 1e-9:
            w1 = at / aa if aa > 1e-9 else 0.0
            return (max(0.0, min(1.0, w1)), 0.0)

        w1 = ((at * bb) - (bt * ab)) / determinant
        w2 = ((bt * aa) - (at * ab)) / determinant
        return (max(0.0, min(1.0, w1)), max(0.0, min(1.0, w2)))
