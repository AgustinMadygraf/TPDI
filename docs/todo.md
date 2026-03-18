# Backlog Técnico - TPDI

> Fecha: 2026-03-17
> Enfoque actual: fidelidad de impresion real (cuatricromia) y preparacion para flexo de 2 colores plenos

---

## Contexto Actual

### Estado verificado

- [x] Configuración centralizada para backend de display en `src/infrastructure/shared/config.py`
- [x] `DisplayerFactory` desacopla creación de displayers en `src/infrastructure/shared/displayer_factory.py`
- [x] `CV2ImageLoader` normaliza BGR -> RGB al cargar desde OpenCV
- [x] Existen puertos claros para carga y display en `src/use_cases/`
- [x] Hay cobertura de tests para loader, displayer, CLI y procesamiento RGB actual

### Hallazgos de auditoría relevantes para RGB -> CMY

- [x] El procesamiento de color estaba acoplado semánticamente a RGB en `src/use_cases/image_processing.py` (mitigado con `src/use_cases/color_analysis.py`)
- [x] La CLI mezclaba orquestación, análisis de color y presentación textual en `src/infrastructure/cli/app.py` (parcialmente mitigado)
- [ ] La entidad `Image` no expresa el modelo de color; solo conoce cantidad de canales
- [x] El comportamiento con imágenes RGBA no está cerrado de forma determinista en tests y contrato de carga (cerrado con normalización BGRA->RGB)
- [x] `CV2ImageDisplayer.display()` mantenía etiquetas fijas para un caso de uso puntual (cerrado con `comparison_labels`)

---

## Objetivo Inmediato

Permitir configurar desde `src/infrastructure/shared/config.py` si el análisis y la visualización de canales se realizan en modo `RGB`, `CMY` o `CMYK`, con valor por defecto `RGB`.

Regla acordada:

- Las imágenes se cargan desde archivo y se normalizan a RGB canónico.
- Si el modo configurado es `CMY` o `CMYK`, la aplicación convierte desde RGB para analizar y mostrar.

---

## Plan de Acción

### Fase 1: Configuración del modo de color

- [x] Agregar `COLOR_MODE: Literal["RGB", "CMY"] = "RGB"` en `src/infrastructure/shared/config.py`
- [x] Extender `load_config()` para aceptar `color_mode`
- [x] Propagar la configuración desde `run.py` hacia la aplicación CLI

### Fase 2: Desacoplar análisis de color de la CLI

- [x] Crear un caso de uso específico para análisis de color configurable por modo
- [x] Mover fuera de `CLIApp` la lógica de variantes, nombres de canales y títulos del análisis
- [x] Mantener `CLIApp` como orquestador y no como contenedor de reglas RGB/CMY

### Fase 3: Soporte mínimo para CMY

- [x] Implementar conversión RGB -> CMY dentro del caso de uso de análisis
- [x] Generar variantes visibles para Cian, Magenta y Amarillo sin mover la conversión al loader de OpenCV
- [x] Adaptar títulos, etiquetas y mensajes de depuración para que dependan del modo de color activo

### Fase 4: Endurecer contratos y pruebas

- [x] Agregar tests unitarios para el análisis en modo `CMY`
- [x] Ajustar tests de CLI para ambos modos de color
- [x] Definir y testear comportamiento esperado para imágenes RGBA cargadas por OpenCV (normalización determinista a RGB de 3 canales)
- [x] Revisar si `CV2ImageDisplayer.display()` debe recibir etiquetas dinámicas para comparaciones futuras

---

## No Hacer en Esta Iteración

- [x] No introducir `CMYK` dentro de la entidad `Image` (mantenerlo como política externa)
- [x] No agregar todavía `color_mode` a la entidad `Image`
- [x] No mover la responsabilidad de decodificación de archivos fuera de `CV2ImageLoader`
- [x] No rediseñar la arquitectura completa si el caso de uso configurable resuelve RGB/CMY con bajo acoplamiento

---

## Criterios de Aceptación

- [x] `AppConfig` permite elegir `RGB` o `CMY`, con default `RGB`
- [x] El loader sigue entregando imágenes RGB canónicas
- [x] La CLI no contiene lógica fija de nombres de canales RGB
- [x] El análisis produce variantes correctas para `RGB` y para `CMY`
- [x] La solución mantiene dependencias hacia adentro y no introduce OpenCV en entidades o use cases
- [x] Los tests cubren el comportamiento configurable sin romper la suite existente

---

## Proximo Paso (Fidelidad de Impresion)

Decisiones de arquitectura tomadas en:

- `docs/decisions/ADR-002-modelar-color-como-politica-externa-para-cmyk.md`
- `docs/decisions/ADR-003-priorizar-fidelidad-de-impresion-cuatricromia-y-ruta-flexo-2-plenos.md`

### Backlog de impresion real (cuatricromia)

- [x] Definir interfaz de politica de separacion de color en casos de uso
- [x] Implementar politica base de cuatricromia orientada a impresion (no solo visualizacion)
- [x] Externalizar parametros de proceso (ganancia de punto, cobertura de tinta, limites de canal)
- [x] Crear set de imagenes patron para regresion de separaciones CMYK
- [x] Documentar limites de simulacion en monitor frente a resultado impreso

### Backlog de evolucion a flexo 2 colores plenos

- [ ] Definir modelo de tinta plana (spot) y configuracion de paletas
- [ ] Implementar primera estrategia de reduccion a 2 canales de impresion
- [ ] Agregar validaciones de cobertura total por proceso flexografico
- [ ] Incorporar pruebas de regresion para escenarios 2 plenos
