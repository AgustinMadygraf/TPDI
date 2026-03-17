"""
Unit tests for ImagePresenter.
Path: tests/interface_adapters/presenters/test_image_presenter.py
"""

import pytest

from src.entities.image import Image
from src.interface_adapters.presenters.image_presenter import ImagePresenter


class TestImagePresenter:
    """Test suite for ImagePresenter."""

    @pytest.fixture
    def presenter(self):
        """Provides an ImagePresenter instance."""
        return ImagePresenter()

    @pytest.fixture
    def sample_images(self):
        """Provides a list of sample images."""
        return [
            Image(name="img1.png", width=100, height=200, channels=3, data=[0]*60000, path="/tmp/img1.png"),
            Image(name="img2.jpg", width=300, height=400, channels=1, data=[0]*120000, path="/tmp/img2.jpg"),
        ]

    def test_present_summary_empty_list(self, presenter):
        """Test presenting summary of empty image list."""
        result = presenter.present_summary([])
        
        assert result["count"] == 0
        assert result["images"] == []

    def test_present_summary_single_image(self, presenter):
        """Test presenting summary of single image."""
        image = Image(name="test.png", width=100, height=200, channels=3, data=[0]*60000, path="/tmp/test.png")
        
        result = presenter.present_summary([image])
        
        assert result["count"] == 1
        assert len(result["images"]) == 1
        
        img_data = result["images"][0]
        assert img_data["name"] == "test.png"
        assert img_data["width"] == 100
        assert img_data["height"] == 200
        assert img_data["channels"] == 3
        assert img_data["path"] == "/tmp/test.png"

    def test_present_summary_multiple_images(self, presenter, sample_images):
        """Test presenting summary of multiple images."""
        result = presenter.present_summary(sample_images)
        
        assert result["count"] == 2
        assert len(result["images"]) == 2
        
        # First image
        assert result["images"][0]["name"] == "img1.png"
        assert result["images"][0]["width"] == 100
        assert result["images"][0]["height"] == 200
        
        # Second image
        assert result["images"][1]["name"] == "img2.jpg"
        assert result["images"][1]["channels"] == 1

    def test_present_summary_excludes_data(self, presenter):
        """Test that raw pixel data is excluded from summary."""
        image = Image(name="test.png", width=10, height=10, channels=3, data=[255]*300, path="/tmp/test.png")
        
        result = presenter.present_summary([image])
        
        # Raw data should not be in summary
        assert "data" not in result["images"][0]

    def test_present_for_display(self, presenter):
        """Test presenting image for display."""
        image = Image(name="test.png", width=100, height=200, channels=3, data=[255]*60000, path="/tmp/test.png")
        
        result = presenter.present_for_display(image)
        
        assert result["name"] == "test.png"
        assert result["width"] == 100
        assert result["height"] == 200
        assert result["data"] == image.data

    def test_present_for_display_includes_data(self, presenter):
        """Test that raw data IS included for display."""
        data = list(range(300))
        image = Image(name="test.png", width=10, height=10, channels=3, data=data, path="/tmp/test.png")
        
        result = presenter.present_for_display(image)
        
        assert result["data"] == data

    def test_present_for_display_different_image_sizes(self, presenter):
        """Test presenting images of different sizes."""
        images = [
            Image(name="small.png", width=10, height=10, channels=1, data=[0]*100, path="/tmp/small.png"),
            Image(name="large.png", width=1000, height=1000, channels=3, data=[0]*3000000, path="/tmp/large.png"),
        ]
        
        for img in images:
            result = presenter.present_for_display(img)
            assert result["width"] == img.width
            assert result["height"] == img.height
            assert len(result["data"]) == img.width * img.height * img.channels
