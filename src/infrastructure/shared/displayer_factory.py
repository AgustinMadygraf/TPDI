"""
Path: src/infrastructure/shared/displayer_factory.py
"""

from src.use_cases.display_image import ImageDisplayPort
from src.infrastructure.shared.config import AppConfig


class DisplayerFactory:
    _displayers: dict[str, type[ImageDisplayPort]] = {}
    
    @classmethod
    def register(cls, backend: str, displayer_class: type[ImageDisplayPort]) -> None:
        cls._displayers[backend] = displayer_class
    
    @classmethod
    def create(cls, config: AppConfig) -> ImageDisplayPort:
        backend = config.GUI_BACKEND
        
        if backend not in cls._displayers:
            # Lazy loading de displayers built-in
            if backend == "cv2":
                from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
                cls.register("cv2", CV2ImageDisplayer)
            elif backend == "matplotlib":
                # TODO: Implementar MatplotlibImageDisplayer
                raise NotImplementedError(
                    f"Backend '{backend}' no implementado aún. "
                    f"Disponibles: {list(cls._displayers.keys()) or ['cv2']}"
                )
            else:
                raise ValueError(
                    f"Backend de GUI desconocido: '{backend}'. "
                    f"Disponibles: {list(cls._displayers.keys())}"
                )
        
        displayer_class = cls._displayers[backend]
        return displayer_class()
    
    @classmethod
    def available_backends(cls) -> list[str]:
        # Asegurar que cv2 esté registrado
        if "cv2" not in cls._displayers:
            try:
                from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
                cls.register("cv2", CV2ImageDisplayer)
            except ImportError:
                pass
        return list(cls._displayers.keys())
