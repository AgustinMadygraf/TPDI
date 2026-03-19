"""
Unit tests for CV2ImageDisplayer.
Path: tests/infrastructure/opencv/test_cv2_image_displayer.py

Note: These tests mock cv2 to avoid actual GUI display during testing.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.entities.image import Image
from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer


def setup_cv2_mock(mock_cv2, shape=(100, 100, 3)):
    """Setup cv2 mock to return proper numpy arrays."""
    # Configure cvtColor to return an array with proper shape
    def cvtColor_side_effect(img, code):
        if len(img.shape) == 2:
            # Grayscale to BGR
            return np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        return np.zeros(shape, dtype=np.uint8)
    
    mock_cv2.cvtColor.side_effect = cvtColor_side_effect
    mock_cv2.COLOR_GRAY2BGR = 8
    mock_cv2.COLOR_RGB2BGR = 4
    mock_cv2.FONT_HERSHEY_SIMPLEX = 0
    
    # Configure resize to return proper shape
    def resize_side_effect(img, size, **_kwargs):
        return np.zeros((size[1], size[0], 3) if len(img.shape) == 3 else (size[1], size[0]), dtype=np.uint8)
    mock_cv2.resize.side_effect = resize_side_effect


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
        setup_cv2_mock(mock_cv2)
        
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
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image)
        
        # cvtColor should be called for RGB conversion
        assert mock_cv2.cvtColor.called

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_converts_grayscale_to_bgr(self, mock_get_logger, mock_cv2, displayer, sample_grayscale_image):
        """Test that grayscale images are converted to BGR."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_grayscale_image)
        
        # cvtColor should be called for grayscale conversion
        assert mock_cv2.cvtColor.called

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_calls_waitkey(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display waits for key press."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image)
        
        mock_cv2.waitKey.assert_called_once_with(0)

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_calls_destroyallwindows(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display cleans up windows."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image)
        
        mock_cv2.destroyAllWindows.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_display_logs_info(self, mock_cv2, displayer, sample_rgb_image):
        """Test that display logs information."""
        setup_cv2_mock(mock_cv2)
        with patch.object(displayer._logger, 'info') as mock_info:
            displayer.display(sample_rgb_image)
            
            # Should log image name
            mock_info.assert_any_call("Mostrando: %s", "test.png")
            mock_info.assert_any_call("Presiona cualquier tecla para cerrar...")


class TestCV2ImageDisplayerComparison:
    """Test suite for comparison mode."""

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
    def grayscale_image(self):
        """Provides a grayscale version of the image."""
        return Image(
            name="test_grayscale.png",
            width=100,
            height=100,
            channels=1,
            data=[128] * 10000,  # Grayscale values
            path="/tmp/test_grayscale.png"
        )

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_comparison_vertical_shows_two_images(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, grayscale_image):
        """Test that vertical comparison mode shows two images stacked."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image, grayscale_image, layout="vertical")
        
        # Should create window with comparison title
        mock_cv2.imshow.assert_called_once()
        call_args = mock_cv2.imshow.call_args
        assert "Comparacion" in call_args[0][0]

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_comparison_horizontal_shows_two_images(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, grayscale_image):
        """Test that horizontal comparison mode shows two images side by side."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image, grayscale_image, layout="horizontal")
        
        # Should create window with comparison title
        mock_cv2.imshow.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_comparison_vertical_logs_layout(self, mock_cv2, displayer, sample_rgb_image, grayscale_image):
        """Test that vertical comparison logs the layout."""
        setup_cv2_mock(mock_cv2)
        with patch.object(displayer._logger, 'info') as mock_info:
            displayer.display(sample_rgb_image, grayscale_image, layout="vertical")
            
            mock_info.assert_any_call("Mostrando comparacion: %s (%s)", "test.png", "vertical")

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_comparison_uses_puttext_for_labels(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, grayscale_image):
        """Test that comparison adds text labels."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        displayer.display(sample_rgb_image, grayscale_image, layout="vertical")
        
        # Should use putText for labels
        assert mock_cv2.putText.called
        # Check that labels contain ORIGINAL and ESCALA DE GRISES
        calls = mock_cv2.putText.call_args_list
        texts = [str(call) for call in calls]
        assert any("ORIGINAL" in text for text in texts)
        assert any("ESCALA DE GRISES" in text for text in texts)

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_comparison_accepts_custom_labels(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, grayscale_image):
        """Test that comparison allows overriding default labels."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)

        displayer.display(
            sample_rgb_image,
            grayscale_image,
            layout="vertical",
            comparison_labels=("BASE", "VARIANTE"),
        )

        calls = mock_cv2.putText.call_args_list
        texts = [str(call) for call in calls]
        assert any("BASE" in text for text in texts)
        assert any("VARIANTE" in text for text in texts)

    def test_initialization(self):
        """Test displayer initialization."""
        with patch('src.infrastructure.opencv.cv2_image_displayer.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            displayer = CV2ImageDisplayer()
            
            assert displayer._numpy_adapter is not None


class TestCV2ImageDisplayerGrid:
    """Test suite for grid display mode."""

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
    def sample_image_2(self):
        """Provides another sample image."""
        return Image(
            name="test2.png",
            width=100,
            height=100,
            channels=3,
            data=[128] * 30000,
            path="/tmp/test2.png"
        )

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_grid_calls_imshow(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, sample_image_2):
        """Test that display_grid calls cv2.imshow."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        images = [
            (sample_rgb_image, "Label 1"),
            (sample_image_2, "Label 2")
        ]
        
        displayer.display_grid(images, grid_size=(1, 2), title="Test Grid")
        
        mock_cv2.imshow.assert_called_once()
        call_args = mock_cv2.imshow.call_args
        assert call_args[0][0] == "Test Grid"

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_grid_uses_puttext_for_labels(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image, sample_image_2):
        """Test that display_grid adds text labels to cells."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        images = [
            (sample_rgb_image, "ORIGINAL"),
            (sample_image_2, "CANAL ROJO")
        ]
        
        displayer.display_grid(images, grid_size=(1, 2))
        
        # Should use putText for labels
        assert mock_cv2.putText.called
        calls = mock_cv2.putText.call_args_list
        texts = [str(call) for call in calls]
        assert any("ORIGINAL" in text for text in texts)
        assert any("CANAL ROJO" in text for text in texts)

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_display_grid_logs_info(self, mock_cv2, displayer, sample_rgb_image):
        """Test that display_grid logs grid information."""
        setup_cv2_mock(mock_cv2)
        with patch.object(displayer._logger, 'info') as mock_info:
            images = [(sample_rgb_image, "Test")]
            displayer.display_grid(images, grid_size=(1, 1), title="Grid Test")
            
            mock_info.assert_any_call("Mostrando grid %dx%d: %s", 1, 1, "Grid Test")

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_display_grid_empty_list_warns(self, mock_cv2, displayer):
        """Test that display_grid warns when given empty list."""
        setup_cv2_mock(mock_cv2)
        with patch.object(displayer._logger, 'warning') as mock_warning:
            displayer.display_grid([], grid_size=(2, 2))
            
            # Check that warning was called (avoiding encoding issues with accents)
            mock_warning.assert_called_once()
            assert "No hay" in str(mock_warning.call_args)

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_grid_2x2_layout(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display_grid creates correct 2x2 layout."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        # Create 4 images for a 2x2 grid
        images = [
            (sample_rgb_image, "TL"),
            (sample_rgb_image, "TR"),
            (sample_rgb_image, "BL"),
            (sample_rgb_image, "BR")
        ]
        
        displayer.display_grid(images, grid_size=(2, 2))
        
        # Should call imshow once with the combined grid
        mock_cv2.imshow.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_grid_fills_empty_cells(self, mock_get_logger, mock_cv2, displayer, sample_rgb_image):
        """Test that display_grid fills empty cells with zeros."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)
        
        # Only 2 images for a 2x2 grid (4 cells)
        images = [
            (sample_rgb_image, "Img 1"),
            (sample_rgb_image, "Img 2")
        ]
        
        displayer.display_grid(images, grid_size=(2, 2))
        
        # Should still call imshow (filling remaining cells with empty images)
        mock_cv2.imshow.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    def test_display_grid_calls_waitkey_and_destroy(self, mock_cv2, displayer, sample_rgb_image):
        """Test that display_grid waits for key and cleans up."""
        setup_cv2_mock(mock_cv2)
        
        images = [(sample_rgb_image, "Test")]
        displayer.display_grid(images, grid_size=(1, 1))
        
        mock_cv2.waitKey.assert_called_once_with(0)
        mock_cv2.destroyAllWindows.assert_called_once()

    @patch('src.infrastructure.opencv.cv2_image_displayer.cv2')
    @patch('src.infrastructure.opencv.cv2_image_displayer.get_logger')
    def test_display_grid_scales_down_when_larger_than_screen(
        self, mock_get_logger, mock_cv2, displayer, sample_rgb_image
    ):
        """Grid should be resized to fit within screen bounds."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        setup_cv2_mock(mock_cv2)

        with patch.object(displayer, "_get_screen_size", return_value=(120, 120)):
            images = [
                (sample_rgb_image, "A"),
                (sample_rgb_image, "B"),
                (sample_rgb_image, "C"),
                (sample_rgb_image, "D"),
            ]
            displayer.display_grid(images, grid_size=(2, 2))

        assert mock_cv2.resize.called
