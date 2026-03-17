"""
Unit tests for CV2ImageDisplayer.
Path: tests/infrastructure/opencv/test_cv2_image_displayer.py

Note: These tests mock cv2 to avoid actual GUI display during testing.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.entities.image import Image
from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer


class TestCV2ImageDisplayer:
    """Test suite for CV2ImageDisplayer with mocked cv2."""

    @pytest.fixture
    def displayer(self):
        """Provides a CV2ImageDisplayer instance."""
        return CV2ImageDisplayer()

    @pytest.fixture
    def sample_rgb_image(self):
        """Provides a sample RGB image."""
        return Image(
            name="test.png",
            width=100,
            height=100,
            channels=3,
            data=[255] * 30000,
            path="/tmp/test.png"
        )

    @pytest.fixture
    def sample_grayscale_image(self):
        """Provides a sample grayscale image."""
        return Image(
            name="test_gray.png",
            width=50,
            height=50,
            channels=1,
            data=[128] * 2500,
            path="/tmp/test_gray.png"
        )

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_calls_imshow_rgb(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display calls cv2.imshow for RGB image."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        displayer.display(sample_rgb_image)
        
        mock_cv2.imshow.assert_called_once()
        call_args = mock_cv2.imshow.call_args
        assert call_args[0][0] == "test.png"  # Window name

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_converts_rgb_to_bgr(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that RGB image is converted to BGR for OpenCV."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        displayer.display(sample_rgb_image)
        
        # cv2.cvtColor should be called for RGB images
        mock_cv2.cvtColor.assert_called_once()
        call_args = mock_cv2.cvtColor.call_args
        assert call_args[0][1] == mock_cv2.COLOR_RGB2BGR

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_no_conversion_for_grayscale(self, mock_get_logger, mock_cv2, displayer, sample_grayscale_image):
        """Test that grayscale images don't need color conversion."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        displayer.display(sample_grayscale_image)
        
        # cvtColor should NOT be called for grayscale
        mock_cv2.cvtColor.assert_not_called()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_calls_waitkey(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display waits for key press."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        displayer.display(sample_rgb_image)
        
        mock_cv2.waitKey.assert_called_once_with(0)

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_calls_destroyallwindows(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display cleans up windows."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        displayer.display(sample_rgb_image)
        
        mock_cv2.destroyAllWindows.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_display_logs_info(self, mock_cv2, displayer, sample_rgb_image):
        """Test that display logs information."""
        # The logger is created in __init__, so we need to check it's called during display
        with patch.object(displayer._logger, 'info') as mock_info:
            displayer.display(sample_rgb_image)
            
            # Should log image name
            mock_info.assert_any_call("Mostrando: %s", "test.png")
            mock_info.assert_any_call("Presiona cualquier tecla para cerrar...")

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_with_different_image_sizes(self, mock_get_logger, mock_cv2):
        """Test display with various image sizes."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        sizes = [
            (10, 10, 3, "small.png"),
            (100, 100, 3, "medium.png"),
            (1000, 1000, 1, "large_grayscale.png"),
        ]
        
        for width, height, channels, name in sizes:
            img = Image(
                name=name,
                width=width,
                height=height,
                channels=channels,
                data=[0] * (width * height * channels),
                path=f"/tmp/{name}"
            )
            displayer = CV2ImageDisplayer()
            displayer.display(img)
            
            # Each call should use the image name as window title
            mock_cv2.imshow.assert_any_call(name, mock_cv2.cvtColor.return_value if channels == 3 else mock_cv2.imshow.call_args[0][1])

    def test_initialization(self):
        """Test displayer initialization."""
        with patch('src.infrastructure.opencv.cv2_image_displayer.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            displayer = CV2ImageDisplayer()
            
            assert displayer._numpy_adapter is not None
