"""
Path: run.py

Punto de entrada principal de TPDI.
Muestra la primera imagen del directorio data/input:
  - Arriba: Imagen ORIGINAL (color)
  - Abajo: Imagen en ESCALA DE GRISES
"""

from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
from src.infrastructure.shared.path_validator import PathValidator
from src.interface_adapters.controllers.main_controller import MainController
from src.use_cases.load_images import LoadImagesFromDirectory
from src.entities.image import Image


def apply_grayscale(image: Image) -> Image:
    """Convierte la imagen a escala de grises.
    
    Args:
        image: Imagen original.
        
    Returns:
        Imagen en escala de grises.
    """
    if image.channels == 1:
        return image
    
    grayscale_data = []
    for i in range(0, len(image.data), 3):
        r, g, b = image.data[i], image.data[i+1], image.data[i+2]
        gray = int((r + g + b) / 3)
        grayscale_data.extend([gray, gray, gray])
    
    return Image(
        name=f"{image.name}_grayscale",
        width=image.width,
        height=image.height,
        channels=3,
        data=grayscale_data,
        path=image.path
    )


def main() -> None:
    """Punto de entrada principal."""
    print("=" * 50)
    print("TPDI - Procesamiento Digital de Imagenes")
    print("=" * 50)
    print()
    
    # Wiring de dependencias
    path_validator = PathValidator(base_path=MainController.DEFAULT_INPUT_DIR)
    loader = CV2ImageLoader(path_validator=path_validator)
    displayer = CV2ImageDisplayer()
    
    # Cargar imagenes
    print(f"Cargando imagenes desde: {MainController.DEFAULT_INPUT_DIR}")
    use_case = LoadImagesFromDirectory(loader)
    images = use_case.execute(MainController.DEFAULT_INPUT_DIR)
    
    if not images:
        print(f"ERROR: No se encontraron imagenes en: {MainController.DEFAULT_INPUT_DIR}")
        print("Agrega imagenes PNG/JPG a la carpeta data/input/")
        print()
        input("Presiona Enter para salir...")
        return
    
    print(f"Cargadas {len(images)} imagen(es)")
    print()
    
    # Tomar la primera imagen
    original = images[0]
    print(f"Imagen seleccionada: {original.name}")
    print(f"  Dimensiones: {original.width}x{original.height}")
    print(f"  Canales: {original.channels}")
    print()
    
    # Convertir a escala de grises
    print("Convirtiendo a escala de grises...")
    grayscale = apply_grayscale(original)
    print(f"  Original: {original.name}")
    print(f"  Grayscale: {grayscale.name}")
    print()
    
    # Mostrar comparacion (arriba: original, abajo: grayscale)
    print("Mostrando comparacion:")
    print("  [ARRIBA]  ORIGINAL (color)")
    print("  [ABAJO]   ESCALA DE GRISES")
    print()
    print("Presiona cualquier tecla en la ventana para cerrar...")
    print()
    
    # Layout vertical: original arriba, grayscale abajo
    displayer.display(original, grayscale, layout="vertical")
    
    print()
    print("Aplicacion finalizada.")


if __name__ == "__main__":
    main()
