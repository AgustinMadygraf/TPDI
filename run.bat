@echo off
chcp 65001 >nul
echo ========================================
echo TPDI - Procesamiento Digital de Imagenes
echo ========================================
echo.
echo Este script mostrara:
echo   [ARRIBA]  Imagen ORIGINAL (color)
echo   [ABAJO]   Imagen ESCALA DE GRISES
echo.
echo La comparacion se muestra en una sola ventana.
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Asegurate de que la carpeta 'venv' existe
    pause
    exit /b 1
)

echo Entorno virtual activado
echo.

REM Ejecutar aplicacion
echo Iniciando TPDI...
echo.
python run.py

REM Desactivar entorno virtual al terminar
call venv\Scripts\deactivate.bat

echo.
echo ========================================
echo TPDI finalizado
echo ========================================
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
