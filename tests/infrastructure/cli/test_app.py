"""
Unit tests for CLIApp.
Path: tests/infrastructure/cli/test_app.py
"""

# pylint: disable=protected-access

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.entities.image import Image
from src.infrastructure.cli.app import CLIApp
from src.use_cases.color_analysis import ColorAnalysisResult, ColorAnalysisVariant


class TestableCLIApp(CLIApp):
    """Expose internals through public wrappers for testing purposes."""

    @property
    def logger(self):
        return self._logger

    @property
    def displayer(self):
        return self._displayer

    @property
    def loader(self):
        return self._loader

    @property
    def color_mode(self):
        return self._color_mode

    @property
    def base_path(self):
        return self._base_path

    def on_load_error(self, path: Path, exc: Exception) -> None:
        self._on_load_error(path, exc)

    def process_color_variants(self, original: Image) -> ColorAnalysisResult:
        return self._process_color_variants(original)

    def display_grid_analysis(self, original: Image, analysis: ColorAnalysisResult) -> None:
        self._display_grid_2x4(original, analysis)

    def display_image_public(self, image: Image) -> None:
        self._display_image(image)


class TestCLIApp:
    """Test suite for CLIApp."""

    @pytest.fixture
    def mock_loader(self):
        """Provides a mock image loader."""
        return Mock()

    @pytest.fixture
    def mock_displayer(self):
        """Provides a mock image displayer."""
        return Mock()

    @pytest.fixture
    def app(self, mock_loader, mock_displayer):
        """Provides a CLIApp instance with mocked dependencies."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                app = TestableCLIApp(loader=mock_loader, displayer=mock_displayer)
                return app

    def test_initialization(self, mock_loader, mock_displayer):
        """Test CLIApp initialization."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                app = TestableCLIApp(loader=mock_loader, displayer=mock_displayer)
                
                assert app.displayer == mock_displayer
                assert app.loader == mock_loader
                assert app.color_mode == "RGB"

    def test_initialization_accepts_color_mode(self, mock_loader, mock_displayer):
        """Test CLIApp allows overriding the color mode."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                app = TestableCLIApp(
                    loader=mock_loader,
                    displayer=mock_displayer,
                    color_mode="CMY",
                )

                assert app.color_mode == "CMY"

    def test_on_load_error_logs_warning(self, app):
        """Test that load error logs warning."""
        test_path = Path("/tmp/test.png")
        test_error = ValueError("Test error")
        
        app.on_load_error(test_path, test_error)
        
        app.logger.warning.assert_called_once_with(
            "No se pudo cargar imagen %s: %s", test_path, test_error
        )

    def test_load_images(self, app, mock_loader):
        """Test load_images method."""
        test_images = [
            Image(name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png")
        ]
        mock_loader.load.return_value = test_images[0]
        
        with patch('src.infrastructure.cli.app.LoadImagesFromDirectory') as mock_use_case:
            mock_instance = Mock()
            mock_instance.execute.return_value = test_images
            mock_use_case.return_value = mock_instance
            
            result = app.load_images()
            
            assert result == test_images


class TestCLIAppColorChannelAnalysis:
    """Test suite for color channel analysis feature."""

    @pytest.fixture
    def mock_loader(self):
        """Provides a mock image loader."""
        return Mock()

    @pytest.fixture
    def mock_displayer(self):
        """Provides a mock image displayer."""
        return Mock()

    @pytest.fixture
    def app(self, mock_loader, mock_displayer):
        """Provides a CLIApp instance with mocked dependencies."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                app = TestableCLIApp(loader=mock_loader, displayer=mock_displayer)
                return app

    @pytest.fixture
    def sample_image(self):
        """Provides a sample RGB image."""
        return Image(
            name="test.png",
            width=100,
            height=100,
            channels=3,
            data=[255, 128, 64] * 10000,  # Mixed colors
            path="/tmp/test.png"
        )

    def test_run_color_channel_analysis_no_images(self, app):
        """Test analysis when no images are found."""
        with patch.object(app, 'load_images') as mock_load:
            mock_load.return_value = []
            
            result = app.run_color_channel_analysis()
            
            assert result is False

    def test_run_color_channel_analysis_with_images(self, app, sample_image):
        """Test analysis when images are found."""
        with patch.object(app, 'load_images') as mock_load:
            mock_load.return_value = [sample_image]
            
            with patch.object(app, '_process_color_variants') as mock_process:
                mock_process.return_value = ColorAnalysisResult(
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
                
                with patch.object(app, '_display_grid_2x4') as mock_display:
                    result = app.run_color_channel_analysis()
                    
                    assert result is True
                    mock_process.assert_called_once_with(sample_image)
                    mock_display.assert_called_once()

    def test_process_color_variants(self, app, sample_image):
        """Test _process_color_variants creates correct variants."""
        analysis = app.process_color_variants(sample_image)

        assert analysis.mode == "RGB"
        assert len(analysis.variants) == 7

        names = [variant.label for variant in analysis.variants]
        assert "CANAL ROJO" in names
        assert "CANAL VERDE" in names
        assert "CANAL AZUL" in names
        assert "ESCALA DE GRISES" in names
        assert "ROJO -> GRIS" in names
        assert "VERDE -> GRIS" in names
        assert "AZUL -> GRIS" in names

        for variant in analysis.variants:
            assert isinstance(variant.image, Image)

    def test_process_color_variants_cmy(self, mock_loader, mock_displayer, sample_image):
        """Test _process_color_variants creates CMY variants when configured."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                app = TestableCLIApp(
                    loader=mock_loader,
                    displayer=mock_displayer,
                    color_mode="CMY",
                )

        analysis = app.process_color_variants(sample_image)

        assert analysis.mode == "CMY"
        names = [variant.label for variant in analysis.variants]
        assert "CANAL CIAN" in names
        assert "CANAL MAGENTA" in names
        assert "CANAL AMARILLO" in names

    def test_process_color_variants_cmyk(self, mock_loader, mock_displayer, sample_image):
        """Test _process_color_variants creates CMYK variants when configured."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                app = TestableCLIApp(
                    loader=mock_loader,
                    displayer=mock_displayer,
                    color_mode="CMYK",
                )

        analysis = app.process_color_variants(sample_image)

        assert analysis.mode == "CMYK"
        names = [variant.label for variant in analysis.variants]
        assert "CANAL CIAN" in names
        assert "CANAL MAGENTA" in names
        assert "CANAL AMARILLO" in names
        assert "CANAL NEGRO" in names
        assert "ESCALA DE GRISES" in names
        assert len(analysis.variants) == 5

    def test_display_grid_cmyk_uses_2x2_with_four_channel_images(self, app, sample_image):
        """CMYK analysis should show a 2x2 grid with C, M, Y, K only."""
        analysis = ColorAnalysisResult(
            mode="CMYK",
            debug_title="DEPURACION DE CANALES CMYK",
            channel_labels=(
                "Canal Cian",
                "Canal Magenta",
                "Canal Amarillo",
                "Canal Negro",
            ),
            channel_pixel_labels=("Cian", "Magenta", "Amarillo", "Negro"),
            analysis_title="Analisis CMYK: test.png",
            variants=[
                ColorAnalysisVariant("CANAL CIAN", Mock()),
                ColorAnalysisVariant("CANAL MAGENTA", Mock()),
                ColorAnalysisVariant("CANAL AMARILLO", Mock()),
                ColorAnalysisVariant("CANAL NEGRO", Mock()),
            ],
        )

        app.display_grid_analysis(sample_image, analysis)

        call_args = app.displayer.display_grid.call_args
        assert call_args[1]['grid_size'] == (2, 2)
        assert len(call_args[1]['images']) == 4
        labels = [label for _, label in call_args[1]['images']]
        assert labels == [
            "CANAL CIAN",
            "CANAL MAGENTA",
            "CANAL AMARILLO",
            "CANAL NEGRO",
        ]

    def test_display_grid_2x4(self, app, sample_image):
        """Test _display_grid_2x4 calls displayer correctly."""
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

        app.display_grid_analysis(sample_image, analysis)
        
        # Should call display_grid with 8 images
        app.displayer.display_grid.assert_called_once()
        call_args = app.displayer.display_grid.call_args
        
        # Check grid_size is 2x4
        assert call_args[1]['grid_size'] == (2, 4)
        
        # Check 8 images provided
        images = call_args[1]['images']
        assert len(images) == 8
        assert call_args[1]['title'] == 'Analisis RGB: test.png'


class TestCLIAppStandardRun:
    """Test suite for standard run method."""

    @pytest.fixture
    def mock_loader(self):
        """Provides a mock image loader."""
        return Mock()

    @pytest.fixture
    def mock_displayer(self):
        """Provides a mock image displayer."""
        return Mock()

    @pytest.fixture
    def app(self, mock_loader, mock_displayer):
        """Provides a CLIApp instance with mocked dependencies."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                app = TestableCLIApp(loader=mock_loader, displayer=mock_displayer)
                return app

    @pytest.fixture
    def sample_image(self):
        """Provides a sample image."""
        return Image(
            name="test.png",
            width=100,
            height=100,
            channels=3,
            data=[0] * 30000,
            path="/tmp/test.png"
        )

    def test_run_with_images(self, app, sample_image):
        """Test run when images are found."""
        with patch.object(app, 'load_images') as mock_load:
            mock_load.return_value = [sample_image]
            
            with patch.object(app, '_display_image') as mock_display:
                app.run()
                
                mock_display.assert_called_once_with(sample_image)

    def test_run_no_images(self, app):
        """Test run when no images are found."""
        with patch.object(app, 'load_images') as mock_load:
            mock_load.return_value = []
            
            app.run()
            
            app.logger.warning.assert_called_with(
                "No se encontraron imagenes en: %s", 
                app.base_path
            )

    def test_display_image(self, app, mock_displayer, sample_image):
        """Test _display_image method."""
        app.display_image_public(sample_image)
        
        mock_displayer.display.assert_called_once_with(sample_image)
        app.logger.info.assert_any_call("Mostrando imagen: %s", "test.png")
