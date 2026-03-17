"""
Unit tests for ImageDisplayPort protocol.
Path: tests/use_cases/test_display_image.py
"""

from src.entities.image import Image
from src.use_cases.display_image import ImageDisplayPort


class MockImageDisplayer(ImageDisplayPort):
    """Mock implementation of ImageDisplayPort for testing."""
    
    def __init__(self):
        self.displayed_images = []
    
    def display(self, image: Image) -> None:
        self.displayed_images.append(image)


class TestImageDisplayPort:
    """Test suite for ImageDisplayPort protocol."""

    def test_protocol_can_be_implemented(self):
        """Test that the protocol can be properly implemented."""
        displayer = MockImageDisplayer()
        
        image = Image(
            name="test.png",
            width=100,
            height=100,
            channels=3,
            data=[0] * 30000,
            path="/tmp/test.png"
        )
        
        # Should be able to call display
        displayer.display(image)
        
        assert len(displayer.displayed_images) == 1
        assert displayer.displayed_images[0] == image

    def test_multiple_displays(self):
        """Test that multiple images can be displayed."""
        displayer = MockImageDisplayer()
        
        images = [
            Image(name=f"img{i}.png", width=100, height=100, channels=3, data=[0]*30000, path=f"/tmp/img{i}.png")
            for i in range(5)
        ]
        
        for img in images:
            displayer.display(img)
        
        assert len(displayer.displayed_images) == 5

    def test_protocol_structure(self):
        """Test that the protocol has the expected structure."""
        import inspect
        
        # Check that display method exists
        assert hasattr(ImageDisplayPort, 'display')
        
        # Get method signature
        sig = inspect.signature(ImageDisplayPort.display)
        params = list(sig.parameters.keys())
        
        # Should have 'self' and 'image' parameters
        assert 'image' in params
