# Preguntas de Arquitectura Pendientes

> Archivo de inbox para decisiones arquitectonicas activas.
> Solo mantiene preguntas pendientes; las resueltas viven en `docs/decisions/ADR-*.md`.

---

### [2026-03-19] Definir modelo de color explicito en la entidad Image
- **Contexto**: El backlog tecnico identifica que `Image` solo expresa cantidad de canales y no el modelo de color.
- **Pregunta**: ¿Debe `src/entities/image.py` incorporar metadata explicita de espacio de color (RGB/CMY/CMYK/GRAY) como parte del contrato de dominio?
- **Opciones consideradas**:
  - Mantener modelo actual (channels) y delegar semantica de color a politicas externas.
  - Agregar `color_space` a la entidad `Image` y adaptar use cases/adapters.
  - Introducir una entidad/VO separada para metadatos de color sin acoplar conversiones.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Estrategia inicial de reduccion a 2 canales para flexografia
- **Contexto**: El plan de evolucion a flexo 2 plenos requiere una primera estrategia operativa de separacion.
- **Pregunta**: ¿Que algoritmo inicial se adopta para reducir CMYK/RGB a 2 tintas planas (fidelidad vs simplicidad vs costo computacional)?
- **Opciones consideradas**:
  - Umbralizado y asignacion heuristica por canal dominante.
  - Cuantizacion/palette mapping con optimizacion por error perceptual.
  - Politica configurable por perfil de impresion y sustrato.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Validaciones de cobertura total para proceso flexografico
- **Contexto**: Se requiere limitar cobertura de tinta total en salida de 2 plenos para evitar problemas de impresion.
- **Pregunta**: ¿Que regla formal de cobertura total (TAC) se adopta y en que capa se impone (dominio, use case o infraestructura)?
- **Opciones consideradas**:
  - Validacion fija global (limite unico por defecto).
  - Validacion configurable por perfil de maquina/sustrato.
  - Validacion mixta con hard limits + soft warnings.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Estrategia de pruebas de regresion para escenarios de 2 plenos
- **Contexto**: Falta definir como garantizar estabilidad visual/tecnica del pipeline de separacion a 2 canales.
- **Pregunta**: ¿Que suite de regresion se adopta como baseline (metricas, dataset patron, tolerancias, entorno de ejecucion)?
- **Opciones consideradas**:
  - Baseline de snapshots de imagen con tolerancia por pixel.
  - Metricas perceptuales (SSIM/DeltaE) con umbrales por caso.
  - Combinacion de snapshots + metricas + casos sinteticos.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Hardening de carga de imagenes: limites de dimension y memoria
- **Contexto**: Auditoria backend detecto ausencia de limites explicitos al cargar archivos con OpenCV.
- **Pregunta**: ¿Cuales deben ser los limites oficiales (megapixeles/bytes/canales) y donde se configuran para balancear seguridad y usabilidad?
- **Opciones consideradas**:
  - Limites fijos en infraestructura (`cv2_image_loader`).
  - Limites en `AppConfig` con defaults seguros y override CLI.
  - Politica de seguridad separada inyectable por entorno.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Optimizacion del stream de camara evitando conversion masiva a list[int]
- **Contexto**: Auditoria backend detecto overhead por `flatten().tolist()` en cada frame de stream.
- **Pregunta**: ¿Debe evolucionar el contrato de `Image`/adaptadores para soportar buffers NumPy sin conversion eager en la ruta caliente?
- **Opciones consideradas**:
  - Mantener contrato actual y optimizar solo microdetalles.
  - Extender `Image` para aceptar buffer estructurado ademas de lista.
  - Introducir DTO interno para pipeline de stream y convertir solo al borde.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)

### [2026-03-19] Optimizacion de analisis CMYK en una pasada/vectorizacion
- **Contexto**: Auditoria backend detecto multiples pasadas O(n) sobre pixeles en `color_analysis.py`.
- **Pregunta**: ¿Se prioriza una refactorizacion vectorizada con NumPy o una optimizacion incremental manteniendo la API actual?
- **Opciones consideradas**:
  - Refactorizacion completa vectorizada para rendimiento.
  - Fusion de pasadas en una implementacion imperativa controlada.
  - Mantener implementacion actual y diferir optimizacion.
- **Decision**: (pendiente - escalado desde `docs/todo.md` por `todo-workflow`)
- **ADR resultante**: (pendiente)
