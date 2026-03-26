"""Unit tests for AnalysisGridPresenter."""

from unittest.mock import Mock

from src.entities.image import Image
from src.interface_adapters.presenters.analysis_grid_presenter import AnalysisGridPresenter
from src.use_cases.color_analysis import ColorAnalysisResult, ColorAnalysisVariant


def _sample_image() -> Image:
    return Image(
        name="test.png",
        width=100,
        height=100,
        channels=3,
        data=[0] * 30000,
        path="/tmp/test.png",
    )


def test_present_rgb_builds_2x4_layout_with_original_plus_variants() -> None:
    presenter = AnalysisGridPresenter()
    analysis = ColorAnalysisResult(
        mode="RGB",
        debug_title="DEPURACION DE CANALES RGB",
        channel_labels=("Canal Rojo", "Canal Verde", "Canal Azul"),
        channel_pixel_labels=("Rojo", "Verde", "Azul"),
        analysis_title="Analisis RGB: test.png",
        variants=[
            ColorAnalysisVariant("CANAL ROJO", Mock()),
            ColorAnalysisVariant("CANAL VERDE", Mock()),
            ColorAnalysisVariant("CANAL AZUL", Mock()),
            ColorAnalysisVariant("ESCALA DE GRISES", Mock()),
            ColorAnalysisVariant("ROJO -> GRIS", Mock()),
            ColorAnalysisVariant("VERDE -> GRIS", Mock()),
            ColorAnalysisVariant("AZUL -> GRIS", Mock()),
        ],
    )

    presentation = presenter.present(original=_sample_image(), analysis=analysis, grid="2x2")

    assert presentation.grid_size == (2, 4)
    assert presentation.layout_label == "2x4"
    assert len(presentation.images) == 8
    assert presentation.row_labels[0] == [
        "ORIGINAL",
        "CANAL ROJO",
        "CANAL VERDE",
        "CANAL AZUL",
    ]


def test_present_cmyk_2x2_builds_four_channel_grid() -> None:
    presenter = AnalysisGridPresenter()
    analysis = ColorAnalysisResult(
        mode="CMYK",
        debug_title="DEPURACION DE CANALES CMYK",
        channel_labels=("Canal Cian", "Canal Magenta", "Canal Amarillo", "Canal Negro"),
        channel_pixel_labels=("Cian", "Magenta", "Amarillo", "Negro"),
        analysis_title="Analisis CMYK: test.png",
        variants=[
            ColorAnalysisVariant("CANAL CIAN", Mock()),
            ColorAnalysisVariant("CANAL MAGENTA", Mock()),
            ColorAnalysisVariant("CANAL AMARILLO", Mock()),
            ColorAnalysisVariant("CANAL NEGRO", Mock()),
        ],
    )

    presentation = presenter.present(original=_sample_image(), analysis=analysis, grid="2x2")

    assert presentation.grid_size == (2, 2)
    assert presentation.layout_label == "2x2 (CMYK)"
    assert [label for _, label in presentation.images] == [
        "CANAL CIAN",
        "CANAL MAGENTA",
        "CANAL AMARILLO",
        "CANAL NEGRO",
    ]
