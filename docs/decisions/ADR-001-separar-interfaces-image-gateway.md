# ADR-001: Separar Interfaces de Image Gateway

## Estado
- **Fecha**: 2026-03-16
- **Estado**: Aceptada / En implementación
- **Decisores**: Usuario + Agente (decision-helper)

## Contexto

El sistema actual tiene una violación de **Interface Segregation Principle (ISP)**:

1. `ImageLoaderPort` (Protocol) define solo `load()`
2. Pero `CV2ImageAdapter` implementa tanto `load()` como `display()`
3. `ImageGateway` expone ambos métodos, pero `display()` no está en ningún protocolo
4. Validación de paths duplicada en `CV2ImageAdapter` y `ImageGateway`

Además, existe el requerimiento futuro de migrar la visualización de OpenCV a Matplotlib.

## Decisión

**Opción seleccionada**: **A** - Separar en dos Protocols distintos + PathValidator centralizado

### Estructura resultante

```
use_cases/
  ├── load_images.py              → ImageLoaderPort
  └── display_image.py            → ImageDisplayPort (nuevo)

infrastructure/
  ├── opencv/
  │   ├── cv2_image_loader.py     → implementa ImageLoaderPort
  │   └── cv2_image_displayer.py  → implementa ImageDisplayPort
  └── shared/
      └── path_validator.py       → validación centralizada (nuevo)

interface_adapters/
  └── gateways/
      └── image_gateway.py        → usa PathValidator, elimina duplicación
```

### Justificación

1. **Escalabilidad a Matplotlib**: Cambiar el visualizador solo requiere crear `MatplotlibImageDisplayer` e inyectarlo, sin tocar UI
2. **Clean Architecture**: Cada capa depende solo de los protocols que necesita
3. **Testabilidad**: Tests independientes para loader, displayer y validación
4. **Eliminación de duplicación**: PathValidator centralizado reusable
5. **ISP/SRP cumplidos**: Cada clase tiene una sola responsabilidad clara

## Consecuencias

### Positivas
- ✅ Escalable a Matplotlib sin modificar UI
- ✅ Tests independientes y más simples
- ✅ Contratos explícitos mediante protocols
- ✅ Validación de seguridad centralizada
- ✅ Menor acoplamiento entre componentes

### Negativas / Trade-offs
- ⚠️ Más clases y archivos (4 nuevos archivos)
- ⚠️ Más wiring en entry point (run.py)
- ⚠️ Cambio mediano en codebase existente

### Alternativas Rechazadas

#### Opción B: Un adapter, gateways separados
**Por qué se rechazó**: El adapter seguiría violando SRP con dos responsabilidades. No resuelve el problema raíz y complica testing.

#### Opción C: Mover display a UI
**Por qué se rechazó**: Acoplaría la UI a OpenCV, dificultando la migración a Matplotlib. La UI debería depender de abstracciones, no de implementaciones.

## Implementación

**Plan de acción**: Ver `docs/todo.md` (tareas generadas por decision-helper)

**Fecha estimada**: 2026-03-16 (implementación inmediata)

**Responsable**: Agente (todo-workflow)

## Notas

- PathValidator debe ser agnóstico al dominio (solo trabajar con Path)
- ImageDisplayPort debe recibir Image (entidad), no datos crudos
- Los nuevos adapters deben mantener la misma interfaz pero separada
- run.py será responsable de crear e inyectar ambos adapters

## Referencias

- Pregunta original: `docs/decisions/preguntas-arquitectura.md` (se eliminó tras decisión)
- Skill: decision-helper v1.0.0
- Relacionado con: code-audit findings sobre ISP/SRP
