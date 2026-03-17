"""
Unit tests for CLIApp.
Path: tests/infrastructure/cli/test_app.py
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.entities.image import Image
from src.infrastructure.cli.app import CLIApp


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
                
                app = CLIApp(loader=mock_loader, displayer=mock_displayer)
                app._logger = mock_logger
                return app

    def test_initialization(self, mock_loader, mock_displayer):
        """Test CLIApp initialization."""
        with patch('src.infrastructure.cli.app.setup_logging'):
            with patch('src.infrastructure.cli.app.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                app = CLIApp(loader=mock_loader, displayer=mock_displayer)
                
                assert app._displayer == mock_displayer
                assert app._gateway is not None
                assert app._controller is not None

    def test_on_load_error_logs_warning(self, app):
        """Test that load error logs warning."""
        test_path = Path("/tmp/test.png")
        test_error = ValueError("Test error")
        
        app._on_load_error(test_path, test_error)
        
        app._logger.warning.assert_called_once_with(
            "No se pudo cargar imagen %s: %s", test_path, test_error
        )

    @patch.object(CLIApp, '_display_image')
    def test_run_with_images(self, mock_display, app, mock_loader):
        """Test run when images are found."""
        # Mock controller to return summary with images
        test_images = [
            Image(name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png")
        ]
        
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {
                "count": 1,
                "images": [{"name": "test.png", "width": 100, "height": 100, "channels": 3}]
            }
            with patch.object(app._controller, 'get_image') as mock_get:
                mock_get.return_value = test_images[0]
                
                app.run()
                
                # Should display the first image
                mock_display.assert_called_once()

    @patch.object(CLIApp, '_display_image')
    def test_run_no_images(self, mock_display, app):
        """Test run when no images are found."""
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {"count": 0, "images": []}
            
            app.run()
            
            # Should log warning and not display anything
            app._logger.warning.assert_called_with(
                "No se encontraron imágenes en: %s", 
                app._gateway._base_path.absolute()
            )
            mock_display.assert_not_called()

    def test_display_image(self, app, mock_displayer):
        """Test _display_image method."""
        test_image = Image(
            name="test.png", 
            width=100, 
            height=100, 
            channels=3, 
            data=[0]*30000, 
            path="/tmp/test.png"
        )
        
        app._display_image(test_image)
        
        mock_displayer.display.assert_called_once_with(test_image)
        app._logger.info.assert_any_call("Mostrando imagen: %s", "test.png")

    def test_run_logs_startup_info(self, app):
        """Test that run logs startup information."""
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {"count": 0, "images": []}
            
            app.run()
            
            # Should log app startup
            app._logger.info.assert_any_call("=" * 50)
            app._logger.info.assert_any_call("TPDI - Procesamiento Digital de Imágenes")

    def test_run_logs_image_info(self, app):
        """Test that run logs image information."""
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {
                "count": 2,
                "images": [
                    {"name": "img1.png", "width": 100, "height": 200, "channels": 3},
                    {"name": "img2.png", "width": 300, "height": 400, "channels": 1}
                ]
            }
            with patch.object(app._controller, 'get_image') as mock_get:
                mock_get.return_value = Image(
                    name="img1.png", width=100, height=200, channels=3, data=[0]*60000, path="/tmp/img1.png"
                )
                
                app.run()
                
                # Should log each image info
                app._logger.info.assert_any_call(
                    "  [%s] %dx%d px, %d canal(es)",
                    "img1.png", 100, 200, 3
                )

    def test_run_logs_completion(self, app):
        """Test that run logs completion message."""
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {
                "count": 1,
                "images": [{"name": "test.png", "width": 100, "height": 100, "channels": 3}]
            }
            with patch.object(app._controller, 'get_image') as mock_get:
                mock_get.return_value = Image(
                    name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png"
                )
                
                app.run()
                
                app._logger.info.assert_any_call("Visor cerrado. Aplicación finalizada.")

    def test_run_handles_no_first_image(self, app):
        """Test run when get_image returns None."""
        with patch.object(app._controller, 'load_default_images') as mock_load:
            mock_load.return_value = {
                "count": 1,
                "images": [{"name": "test.png", "width": 100, "height": 100, "channels": 3}]
            }
            with patch.object(app._controller, 'get_image') as mock_get:
                mock_get.return_value = None
                
                with patch.object(app, '_display_image') as mock_display:
                    app.run()
                    
                    mock_display.assert_not_called()
