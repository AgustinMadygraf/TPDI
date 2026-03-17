"""
Path: src/use_cases/image_processing.py

Casos de uso para procesamiento de imágenes.
Operaciones de transformación de imágenes del dominio.
"""

from src.entities.image import Image


def apply_grayscale(image: Image) -> Image:
    """Convierte la imagen a escala de grises.
    
    Calcula el promedio de los canales R, G, B y replica el valor
    en los 3 canales para mantener formato RGB.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen en escala de grises (formato RGB con R=G=B).
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


def extract_red_channel(image: Image) -> Image:
    """Extrae el canal rojo de la imagen.
    
    Elimina los canales verde y azul, manteniendo solo el rojo.
    Resultado: imagen RGB donde G=0 y B=0.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen con solo el canal rojo (R, 0, 0).
    """
    if image.channels == 1:
        # Si es grayscale, no hay canal rojo que extraer
        return image
    
    red_data = []
    for i in range(0, len(image.data), 3):
        r = image.data[i]
        # Mantener R, eliminar G y B
        red_data.extend([r, 0, 0])
    
    return Image(
        name=f"{image.name}_red_channel",
        width=image.width,
        height=image.height,
        channels=3,
        data=red_data,
        path=image.path
    )


def red_to_grayscale(image: Image) -> Image:
    """Convierte el canal rojo a escala de grises.
    
    Toma solo el valor del canal R y lo replica en los 3 canales
    para crear una imagen en escala de grises basada únicamente
    en la intensidad del canal rojo.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen en escala de grises basada en el canal rojo (R, R, R).
    """
    if image.channels == 1:
        return image
    
    red_gray_data = []
    for i in range(0, len(image.data), 3):
        r = image.data[i]
        # Replicar el valor R en los 3 canales
        red_gray_data.extend([r, r, r])
    
    return Image(
        name=f"{image.name}_red_grayscale",
        width=image.width,
        height=image.height,
        channels=3,
        data=red_gray_data,
        path=image.path
    )


def extract_green_channel(image: Image) -> Image:
    """Extrae el canal verde de la imagen.
    
    Elimina los canales rojo y azul, manteniendo solo el verde.
    Resultado: imagen RGB donde R=0 y B=0.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen con solo el canal verde (0, G, 0).
    """
    if image.channels == 1:
        return image
    
    green_data = []
    for i in range(0, len(image.data), 3):
        g = image.data[i + 1]
        # Mantener G, eliminar R y B
        green_data.extend([0, g, 0])
    
    return Image(
        name=f"{image.name}_green_channel",
        width=image.width,
        height=image.height,
        channels=3,
        data=green_data,
        path=image.path
    )


def green_to_grayscale(image: Image) -> Image:
    """Convierte el canal verde a escala de grises.
    
    Toma solo el valor del canal G y lo replica en los 3 canales
    para crear una imagen en escala de grises basada únicamente
    en la intensidad del canal verde.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen en escala de grises basada en el canal verde (G, G, G).
    """
    if image.channels == 1:
        return image
    
    green_gray_data = []
    for i in range(0, len(image.data), 3):
        g = image.data[i + 1]
        # Replicar el valor G en los 3 canales
        green_gray_data.extend([g, g, g])
    
    return Image(
        name=f"{image.name}_green_grayscale",
        width=image.width,
        height=image.height,
        channels=3,
        data=green_gray_data,
        path=image.path
    )


def extract_blue_channel(image: Image) -> Image:
    """Extrae el canal azul de la imagen.
    
    Elimina los canales rojo y verde, manteniendo solo el azul.
    Resultado: imagen RGB donde R=0 y G=0.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen con solo el canal azul (0, 0, B).
    """
    if image.channels == 1:
        return image
    
    blue_data = []
    for i in range(0, len(image.data), 3):
        b = image.data[i + 2]
        # Mantener B, eliminar R y G
        blue_data.extend([0, 0, b])
    
    return Image(
        name=f"{image.name}_blue_channel",
        width=image.width,
        height=image.height,
        channels=3,
        data=blue_data,
        path=image.path
    )


def blue_to_grayscale(image: Image) -> Image:
    """Convierte el canal azul a escala de grises.
    
    Toma solo el valor del canal B y lo replica en los 3 canales
    para crear una imagen en escala de grises basada únicamente
    en la intensidad del canal azul.
    
    Args:
        image: Imagen original RGB.
        
    Returns:
        Imagen en escala de grises basada en el canal azul (B, B, B).
    """
    if image.channels == 1:
        return image
    
    blue_gray_data = []
    for i in range(0, len(image.data), 3):
        b = image.data[i + 2]
        # Replicar el valor B en los 3 canales
        blue_gray_data.extend([b, b, b])
    
    return Image(
        name=f"{image.name}_blue_grayscale",
        width=image.width,
        height=image.height,
        channels=3,
        data=blue_gray_data,
        path=image.path
    )
