"""Presenter for analysis grid layout decisions."""

from dataclasses import dataclass
import math

from src.entities.image import Image
from src.use_cases.color_analysis import ColorAnalysisResult


@dataclass(frozen=True)
class AnalysisGridPresentation:
    images: list[tuple[Image, str]]
    grid_size: tuple[int, int]
    row_labels: list[list[str]]
    title: str
    layout_label: str


class AnalysisGridPresenter:
    """Builds a grid presentation from color analysis results."""

    def present(
        self, original: Image, analysis: ColorAnalysisResult, grid: str
    ) -> AnalysisGridPresentation:
        if analysis.mode == "CMYK":
            return self._present_cmyk(original=original, analysis=analysis, grid=grid)
        return self._present_default(original=original, analysis=analysis)

    def _present_cmyk(
        self, original: Image, analysis: ColorAnalysisResult, grid: str
    ) -> AnalysisGridPresentation:
        variant_by_label = {variant.label: variant for variant in analysis.variants}
        if grid == "2x3":
            rows, cols = (3, 2)
            ordered_labels = [
                "ORIGINAL",
                "ESCALA DE GRISES",
                "CANAL CIAN",
                "CANAL MAGENTA",
                "CANAL AMARILLO",
                "CANAL NEGRO",
            ]
            images = [(original, "ORIGINAL")]
            images.extend(
                (variant_by_label[label].image, label)
                for label in ordered_labels[1:]
                if label in variant_by_label
            )
            layout_label = "2x3"
        else:
            rows, cols = (2, 2)
            ordered_labels = [
                "CANAL CIAN",
                "CANAL MAGENTA",
                "CANAL AMARILLO",
                "CANAL NEGRO",
            ]
            images = [
                (variant_by_label[label].image, label)
                for label in ordered_labels
                if label in variant_by_label
            ]
            layout_label = "2x2 (CMYK)"

        row_labels: list[list[str]] = []
        for row in range(rows):
            start = row * cols
            end = start + cols
            row_labels.append(ordered_labels[start:end])

        return AnalysisGridPresentation(
            images=images,
            grid_size=(rows, cols),
            row_labels=row_labels,
            title=analysis.analysis_title,
            layout_label=layout_label,
        )

    def _present_default(
        self, original: Image, analysis: ColorAnalysisResult
    ) -> AnalysisGridPresentation:
        grid_labels = [variant.label for variant in analysis.variants]
        total_images = 1 + len(grid_labels)
        cols = 4
        rows = max(2, math.ceil(total_images / cols))

        row_labels: list[list[str]] = []
        for row in range(rows):
            start = row * cols
            end = start + cols
            if row == 0:
                labels = ["ORIGINAL", *grid_labels[: cols - 1]]
            else:
                labels = grid_labels[start - 1 : end - 1]
            row_labels.append(labels)

        images = [(original, "ORIGINAL"), *[(v.image, v.label) for v in analysis.variants]]
        return AnalysisGridPresentation(
            images=images,
            grid_size=(rows, cols),
            row_labels=row_labels,
            title=analysis.analysis_title,
            layout_label="2x4",
        )
