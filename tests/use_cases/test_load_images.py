"""
Unit tests for LoadImagesFromDirectory use case.
Path: tests/use_cases/test_load_images.py
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock

import pytest

from src.entities.image import Image
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory


class MockImageLoader(ImageLoaderPort):
    """Mock implementation of ImageLoaderPort for testing."""
    
    def __init__(self, should_fail_for: List[str] = None):
        self.should_fail_for = should_fail_for or []
        self.load_calls = []
    
    def load(self, path: Path) -> Image:
        self.load_calls.append(path)
        
        if path.name in self.should_fail_for:
            raise ValueError(f"Failed to load: {path}")
        
        return Image(
            name=path.name,
            width=100,
            height=100,
            channels=3,
            data=[0] * 30000,
            path=str(path)
        )


class TestLoadImagesFromDirectory:
    """Test suite for LoadImagesFromDirectory use case."""

    def test_execute_empty_directory(self, temp_directory):
        """Test loading from an empty directory."""
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert result == []
        assert loader.load_calls == []

    def test_execute_loads_supported_extensions(self, temp_directory):
        """Test loading files with supported extensions."""
        # Create test files
        (temp_directory / "image1.png").touch()
        (temp_directory / "image2.jpg").touch()
        (temp_directory / "document.txt").touch()  # Should be ignored
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == 2
        assert result[0].name == "image1.png"
        assert result[1].name == "image2.jpg"
        assert len(loader.load_calls) == 2

    def test_execute_case_insensitive_extensions(self, temp_directory):
        """Test that extensions are matched case-insensitively."""
        (temp_directory / "image.PNG").touch()
        (temp_directory / "image.JpG").touch()
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == 2

    def test_execute_skips_directories(self, temp_directory):
        """Test that subdirectories are skipped."""
        (temp_directory / "image.png").touch()
        (temp_directory / "subdir").mkdir()
        (temp_directory / "subdir" / "nested.png").touch()
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == 1
        assert result[0].name == "image.png"

    def test_execute_handles_load_errors(self, temp_directory):
        """Test that load errors are handled gracefully."""
        (temp_directory / "good.png").touch()
        (temp_directory / "bad.png").touch()
        
        loader = MockImageLoader(should_fail_for=["bad.png"])
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == 1
        assert result[0].name == "good.png"

    def test_execute_calls_error_callback(self, temp_directory):
        """Test that error callback is called on load failure."""
        (temp_directory / "bad.png").touch()
        
        loader = MockImageLoader(should_fail_for=["bad.png"])
        error_callback = Mock()
        use_case = LoadImagesFromDirectory(loader, on_error=error_callback)
        
        use_case.execute(temp_directory)
        
        error_callback.assert_called_once()
        call_args = error_callback.call_args[0]
        assert call_args[0].name == "bad.png"
        assert isinstance(call_args[1], ValueError)

    def test_execute_returns_sorted_results(self, temp_directory):
        """Test that results are sorted alphabetically."""
        (temp_directory / "z.png").touch()
        (temp_directory / "a.png").touch()
        (temp_directory / "m.png").touch()
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        names = [img.name for img in result]
        assert names == ["a.png", "m.png", "z.png"]

    def test_execute_nonexistent_directory(self, temp_directory):
        """Test loading from a non-existent directory."""
        nonexistent = temp_directory / "does_not_exist"
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(nonexistent)
        
        assert result == []

    def test_default_extensions(self):
        """Test that default extensions are defined."""
        expected = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
        assert LoadImagesFromDirectory.DEFAULT_EXTENSIONS == expected

    def test_custom_extensions(self, temp_directory):
        """Test using custom supported extensions."""
        (temp_directory / "image.raw").touch()
        (temp_directory / "image.png").touch()
        
        loader = MockImageLoader()
        custom_extensions = {'.raw'}
        use_case = LoadImagesFromDirectory(loader, supported_extensions=custom_extensions)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == 1
        assert result[0].name == "image.raw"

    def test_all_supported_extensions(self, temp_directory):
        """Test that all default extensions are loaded."""
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp']
        for ext in extensions:
            (temp_directory / f"image{ext}").touch()
        
        loader = MockImageLoader()
        use_case = LoadImagesFromDirectory(loader)
        
        result = use_case.execute(temp_directory)
        
        assert len(result) == len(extensions)
