"""
Unit tests for ImageGateway.
Path: tests/interface_adapters/gateways/test_image_gateway.py
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock

import pytest

from src.entities.image import Image
from src.interface_adapters.gateways.image_gateway import ImageGateway
from src.use_cases.load_images import ImageLoaderPort


class MockImageLoader(ImageLoaderPort):
    """Mock loader for testing."""
    
    def __init__(self, images_to_return: dict = None, should_fail: List[str] = None):
        self.images_to_return = images_to_return or {}
        self.should_fail = should_fail or []
        self.load_calls = []
    
    def load(self, path: Path) -> Image:
        self.load_calls.append(path)
        
        if path.name in self.should_fail:
            raise ValueError(f"Failed: {path}")
        
        if path.name in self.images_to_return:
            return self.images_to_return[path.name]
        
        return Image(
            name=path.name,
            width=100,
            height=100,
            channels=3,
            data=[0] * 30000,
            path=str(path)
        )


class TestImageGateway:
    """Test suite for ImageGateway."""

    def test_load_delegates_to_loader(self, temp_directory):
        """Test that load delegates to the loader."""
        loader = MockImageLoader()
        gateway = ImageGateway(loader=loader, base_path=temp_directory)
        test_file = temp_directory / "test.png"
        test_file.touch()
        
        result = gateway.load(test_file)
        
        assert len(loader.load_calls) == 1
        assert result.name == "test.png"

    def test_load_all_returns_images(self, temp_directory):
        """Test loading all images from base directory."""
        (temp_directory / "img1.png").touch()
        (temp_directory / "img2.jpg").touch()
        
        loader = MockImageLoader()
        gateway = ImageGateway(loader=loader, base_path=temp_directory)
        
        result = gateway.load_all()
        
        assert len(result) == 2

    def test_load_all_calls_error_callback(self, temp_directory):
        """Test that error callback is called on load failure."""
        (temp_directory / "bad.png").touch()
        
        error_callback = Mock()
        loader = MockImageLoader(should_fail=["bad.png"])
        gateway = ImageGateway(
            loader=loader,
            base_path=temp_directory,
            on_load_error=error_callback
        )
        
        gateway.load_all()
        
        error_callback.assert_called_once()
        call_args = error_callback.call_args[0]
        assert call_args[0].name == "bad.png"

    def test_default_base_path(self):
        """Test default base path is data/input."""
        loader = MockImageLoader()
        gateway = ImageGateway(loader=loader)
        
        assert gateway._base_path == Path("data/input").resolve()

    def test_custom_base_path(self, temp_directory):
        """Test custom base path."""
        loader = MockImageLoader()
        custom_path = temp_directory / "custom"
        custom_path.mkdir()
        
        gateway = ImageGateway(loader=loader, base_path=custom_path)
        
        assert gateway._base_path == custom_path.resolve()

    def test_base_path_is_resolved(self, temp_directory):
        """Test that base path is resolved to absolute."""
        loader = MockImageLoader()
        relative = temp_directory / "subdir"
        relative.mkdir()
        
        gateway = ImageGateway(loader=loader, base_path=relative)
        
        assert gateway._base_path.is_absolute()
