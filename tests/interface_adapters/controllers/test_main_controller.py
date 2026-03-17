"""
Unit tests for MainController.
Path: tests/interface_adapters/controllers/test_main_controller.py
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

import pytest

from src.entities.image import Image
from src.interface_adapters.controllers.main_controller import MainController
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory


class TestMainController:
    """Test suite for MainController."""

    def test_default_input_dir(self):
        """Test default input directory."""
        assert MainController.DEFAULT_INPUT_DIR == Path("data/input")

    @pytest.fixture
    def mock_loader(self):
        """Provides a mock image loader."""
        loader = Mock(spec=ImageLoaderPort)
        return loader

    def test_initialization(self, mock_loader):
        """Test controller initialization."""
        controller = MainController(image_loader=mock_loader)
        
        assert controller._loader == mock_loader
        assert controller._images == []

    def test_initialization_with_error_callback(self, mock_loader):
        """Test initialization with error callback."""
        error_callback = Mock()
        controller = MainController(image_loader=mock_loader, on_load_error=error_callback)
        
        # The callback should be passed to the use case
        assert controller._use_case._on_error == error_callback

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_load_default_images_returns_summary(self, mock_execute, mock_loader):
        """Test that load_default_images returns a summary dict."""
        # Setup mock to return sample images
        mock_execute.return_value = [
            Image(name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png")
        ]
        
        controller = MainController(image_loader=mock_loader)
        result = controller.load_default_images()
        
        assert isinstance(result, dict)
        assert "count" in result
        assert "images" in result
        assert result["count"] == 1

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_load_default_images_populates_images(self, mock_execute, mock_loader):
        """Test that images are loaded into controller."""
        mock_execute.return_value = [
            Image(name="test1.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test1.png"),
            Image(name="test2.png", width=200, height=200, channels=3, data=[0]*120000, path="/tmp/test2.png"),
        ]
        
        controller = MainController(image_loader=mock_loader)
        controller.load_default_images()
        
        assert len(controller.get_images()) == 2

    def test_get_images_returns_list(self, mock_loader):
        """Test get_images returns a list."""
        controller = MainController(image_loader=mock_loader)
        result = controller.get_images()
        
        assert isinstance(result, list)

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_get_image_valid_index(self, mock_execute, mock_loader):
        """Test getting image at valid index."""
        mock_execute.return_value = [
            Image(name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png")
        ]
        
        controller = MainController(image_loader=mock_loader)
        controller.load_default_images()
        
        result = controller.get_image(0)
        assert result is not None
        assert isinstance(result, Image)
        assert result.name == "test.png"

    def test_get_image_invalid_index_negative(self, mock_loader):
        """Test getting image at negative index returns None."""
        controller = MainController(image_loader=mock_loader)
        result = controller.get_image(-1)
        
        assert result is None

    def test_get_image_invalid_index_too_large(self, mock_loader):
        """Test getting image at too large index returns None."""
        controller = MainController(image_loader=mock_loader)
        result = controller.get_image(999)
        
        assert result is None

    def test_get_image_empty_list(self, mock_loader):
        """Test getting image when no images loaded."""
        controller = MainController(image_loader=mock_loader)
        result = controller.get_image(0)
        
        assert result is None

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_set_on_images_loaded_callback(self, mock_execute, mock_loader):
        """Test setting callback for when images are loaded."""
        mock_images = [
            Image(name="test.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test.png")
        ]
        mock_execute.return_value = mock_images
        
        callback = Mock()
        controller = MainController(image_loader=mock_loader)
        controller.set_on_images_loaded_callback(callback)
        
        # Load images, callback should be called
        controller.load_default_images()
        
        # Callback is called after loading
        callback.assert_called_once_with(mock_images)

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_callback_receives_images(self, mock_execute, mock_loader):
        """Test that callback receives the loaded images."""
        mock_images = [
            Image(name="test1.png", width=100, height=100, channels=3, data=[0]*30000, path="/tmp/test1.png"),
            Image(name="test2.png", width=200, height=200, channels=3, data=[0]*120000, path="/tmp/test2.png"),
        ]
        mock_execute.return_value = mock_images
        
        received_images = []
        
        def capture_callback(images):
            received_images.extend(images)
        
        controller = MainController(image_loader=mock_loader)
        controller.set_on_images_loaded_callback(capture_callback)
        controller.load_default_images()
        
        # Received images should match what's in the controller
        assert received_images == mock_images
        assert controller.get_images() == mock_images

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_summary_contains_expected_fields(self, mock_execute, mock_loader):
        """Test that summary contains expected image fields."""
        mock_execute.return_value = [
            Image(name="test.png", width=100, height=200, channels=3, data=[0]*60000, path="/tmp/test.png")
        ]
        
        controller = MainController(image_loader=mock_loader)
        result = controller.load_default_images()
        
        assert result["count"] == 1
        first_image = result["images"][0]
        assert "name" in first_image
        assert "width" in first_image
        assert "height" in first_image
        assert "channels" in first_image
        assert "path" in first_image
        
        assert first_image["name"] == "test.png"
        assert first_image["width"] == 100
        assert first_image["height"] == 200
        assert first_image["channels"] == 3

    @patch.object(LoadImagesFromDirectory, 'execute')
    def test_load_default_images_empty_directory(self, mock_execute, mock_loader):
        """Test loading from empty directory."""
        mock_execute.return_value = []
        
        controller = MainController(image_loader=mock_loader)
        result = controller.load_default_images()
        
        assert result["count"] == 0
        assert result["images"] == []
        assert controller.get_images() == []
