# ADR-002: Modelar Color como Política Externa para CMYK

## Estado
- **Fecha**: 2026-03-17
- **Estado**: Aceptada / Pendiente de implementación
- **Decisores**: Usuario + Agente (GitHub Copilot)

## Contexto

Tras implementar análisis configurable RGB/CMY, quedó pendiente la decisión para extender a CMYK.

La duda era si el modelo de color debía pasar a ser parte explícita del dominio (por ejemplo, en la entidad `Image`) o mantenerse como una política externa de análisis/configuración.

Estado actual relevante:

1. La carga de imágenes normaliza a RGB canónico en infraestructura.
2. El análisis de color está desacoplado en un caso de uso específico.
3. El dominio central sigue simple y estable (`Image` no conoce modo de color).

## Decisión

Se elige mantener el modelo de color como **política externa** para la próxima iteración (incluyendo CMYK), evitando por ahora introducir `color_mode` dentro de la entidad `Image`.

### Alcance de la decisión

1. `Image` permanece como contenedor de datos de imagen y metadatos básicos (ancho, alto, canales, path).
2. La elección de espacio o modo de análisis de color se define en configuración y se ejecuta en casos de uso.
3. Las conversiones de color permanecen fuera del dominio central, en capas de aplicación/infrastructura según corresponda.

## Justificación

1. **Respeta Clean Architecture**: la entidad no absorbe reglas de representación de cada experimento de color.
2. **Menor costo de cambio inmediato**: CMYK puede incorporarse extendiendo el caso de uso de análisis sin romper contratos de dominio ya probados.
3. **Evolución incremental segura**: permite validar el flujo CMYK primero, antes de introducir complejidad estructural permanente.
4. **Consistencia con el estado actual**: RGB/CMY ya funcionan con esta estrategia y la suite de tests está estable.

## Consecuencias

### Positivas

- ✅ Menor impacto transversal para habilitar CMYK.
- ✅ Menos riesgo de regresiones en entidades y adaptadores existentes.
- ✅ Mantiene la estrategia de extensión por casos de uso.

### Negativas / Trade-offs

- ⚠️ El dominio no expresa explícitamente semántica de color.
- ⚠️ A largo plazo, si aparecen más modelos/perfiles (LAB, HSV, ICC), puede crecer la complejidad en aplicación.
- ⚠️ Se requiere disciplina para que las conversiones no se dispersen fuera del caso de uso dedicado.

## Alternativas Rechazadas

### Opción A: Incorporar `color_mode` en `Image` ahora

**Por qué se rechazó**: agrega acoplamiento y alcance prematuro sin validar primero el flujo CMYK real del producto.

### Opción B: Crear jerarquía de entidades por espacio de color

**Por qué se rechazó**: sobrediseño para la etapa actual; incrementa complejidad accidental y costo de mantenimiento.

## Implementación

1. Mantener la entidad `Image` sin cambios de modelo de color.
2. Extender el caso de uso de análisis configurable para soportar CMYK.
3. Añadir pruebas de comportamiento CMYK en use_cases, CLI y display.
4. Revisar esta decisión si se incorporan múltiples espacios con necesidades de semántica persistente.

## Criterio de Revisión

Reevaluar ADR-002 si ocurre alguno de estos eventos:

1. Más de un flujo de negocio requiere semántica de color persistente en dominio.
2. Se incorporan conversiones entre múltiples perfiles avanzados (no solo análisis visual).
3. El costo de mantener política externa supera el costo de explicitar el modelo en entidades.
