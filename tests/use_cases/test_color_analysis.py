"""Tests for configurable color analysis use case."""

from src.entities.image import Image
from src.use_cases.color_analysis import ColorChannelAnalyzer


class TestColorChannelAnalyzer:
    """Test suite for RGB/CMY configurable analysis."""

    def test_execute_rgb_returns_expected_labels(self):
        """RGB mode should preserve current channel labels."""
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 128, 64],
            path="/tmp/test.png",
        )

        result = analyzer.execute(image, "RGB")

        assert result.mode == "RGB"
        assert result.debug_title == "DEPURACION DE CANALES RGB"
        assert [variant.label for variant in result.variants[:3]] == [
            "CANAL ROJO",
            "CANAL VERDE",
            "CANAL AZUL",
        ]

    def test_execute_cmy_returns_expected_labels(self):
        """CMY mode should expose CMY labels and title."""
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 128, 64],
            path="/tmp/test.png",
        )

        result = analyzer.execute(image, "CMY")

        assert result.mode == "CMY"
        assert result.debug_title == "DEPURACION DE CANALES CMY"
        assert result.analysis_title == "Analisis CMY: test.png"
        assert [variant.label for variant in result.variants[:3]] == [
            "CANAL CIAN",
            "CANAL MAGENTA",
            "CANAL AMARILLO",
        ]

    def test_execute_cmy_converts_rgb_to_visible_cmy_channels(self):
        """CMY mode should derive visible additive representations from RGB input."""
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[10, 20, 30],
            path="/tmp/test.png",
        )

        result = analyzer.execute(image, "CMY")

        cyan_channel = result.variants[0].image
        magenta_channel = result.variants[1].image
        yellow_channel = result.variants[2].image
        grayscale = result.variants[3].image

        assert cyan_channel.data == [0, 245, 245]
        assert magenta_channel.data == [235, 0, 235]
        assert yellow_channel.data == [225, 225, 0]
        assert grayscale.data == [235, 235, 235]

    def test_execute_cmyk_returns_expected_labels(self):
        """CMYK mode should expose CMYK labels and title."""
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[10, 20, 30],
            path="/tmp/test.png",
        )

        result = analyzer.execute(image, "CMYK")

        assert result.mode == "CMYK"
        assert result.debug_title == "DEPURACION DE CANALES CMYK"
        assert result.analysis_title == "Analisis CMYK: test.png"
        assert len(result.variants) == 5
        assert [variant.label for variant in result.variants[:4]] == [
            "CANAL CIAN",
            "CANAL MAGENTA",
            "CANAL AMARILLO",
            "CANAL NEGRO",
        ]
        assert result.variants[4].label == "ESCALA DE GRISES"

    def test_execute_cmyk_converts_rgb_to_visible_cmyk_channels(self):
        """CMYK mode should derive expected visible channels from RGB input."""
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[10, 20, 30],
            path="/tmp/test.png",
        )

        result = analyzer.execute(image, "CMYK")

        cyan_channel = result.variants[0].image
        magenta_channel = result.variants[1].image
        yellow_channel = result.variants[2].image
        black_channel = result.variants[3].image
        grayscale = result.variants[4].image

        assert cyan_channel.data == [85, 255, 255]
        assert magenta_channel.data == [255, 170, 255]
        assert yellow_channel.data == [255, 255, 255]
        assert black_channel.data == [30, 30, 30]
        assert grayscale.data == [135, 135, 135]