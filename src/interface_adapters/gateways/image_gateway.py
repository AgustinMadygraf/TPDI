"""Gateway para acceso a imágenes desde múltiples fuentes."""
from pathlib import Path
from typing import Optional

from src.entities.image import Image
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory


class ImageGateway:
    """
    Gateway que unifica el acceso a imágenes.
    
    Recibe un adapter inyectado que implementa ImageLoaderPort,
    permitiendo cambiar la fuente sin modificar el gateway.
    """
    
    def __init__(
        self,
        adapter: ImageLoaderPort,
        base_path: Optional[Path] = None
    ):
        """
        Inicializa el gateway con un adapter inyectado.
        
        Args:
            adapter: Implementación de ImageLoaderPort (ej: CV2ImageAdapter)
            base_path: Ruta base para búsqueda de archivos
        """
        self._adapter = adapter
        self._base_path = base_path or Path("data/input")
    
    def load(self, path: Path) -> Image:
        """
        Carga una imagen desde la ruta especificada.
        
        Args:
            path: Ruta relativa o absoluta a la imagen
            
        Returns:
            Entidad Image cargada
        """
        if not path.is_absolute():
            try:
                path.relative_to(self._base_path)
            except ValueError:
                path = self._base_path / path
        
        return self._adapter.load(path)
    
    def load_all(self) -> list[Image]:
        """
        Carga todas las imágenes del directorio base.
        
        Returns:
            Lista de imágenes cargadas
        """
        use_case = LoadImagesFromDirectory(self._adapter)
        return use_case.execute(self._base_path)
    
    def display(self, image: Image) -> None:
        """
        Muestra una imagen usando el adapter.
        
        Args:
            image: Imagen a visualizar
        """
        self._adapter.display(image)
