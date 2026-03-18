# ADR-003: Priorizar Fidelidad de Impresion (Cuatricromia) y Ruta a Flexo 2 Plenos

## Estado
- **Fecha**: 2026-03-17
- **Estado**: Aceptada
- **Decisores**: Usuario + Agente (GitHub Copilot)

## Contexto

Se definio que el criterio principal de diseno para color en TPDI debe ser la **fidelidad de impresion real**.

En paralelo, el producto debe prepararse para evolucionar desde analisis de cuatricromia (CMYK) hacia escenarios de **flexografia con 2 colores plenos**.

Estado base relevante:

1. El pipeline interno carga en RGB canónico y analiza CMY/CMYK como politica externa.
2. Ya existe visualizacion CMYK y pruebas base de comportamiento.
3. Aun no existe gestion de color de impresion (perfiles, parametros de prensa/sustrato, estrategia de separacion configurable).

## Decision

Se establece la fidelidad de impresion real como objetivo principal para los flujos CMYK y se define una ruta de arquitectura hacia flexo de 2 plenos.

### Alcance inmediato

1. Mantener el enfoque de politica externa para color (sin mover color_mode a la entidad Image por ahora).
2. Introducir una capa de politicas de conversion/separacion de color configurable por perfil de impresion.
3. Tratar la visualizacion en pantalla como simulacion de impresion, no como verdad colorimetrica absoluta.

### Alcance de mediano plazo (flexo 2 plenos)

1. Incorporar modelos de separacion para 2 tintas planas (spot colors).
2. Permitir definir bibliotecas de tintas y reglas de asignacion a 2 canales de impresion.
3. Conservar trazabilidad entre la imagen de entrada, separaciones generadas y parametros usados.

## Justificacion

1. El objetivo de TPDI deja de ser solo didactico y pasa a priorizar decisiones tecnicas cercanas a preprensa.
2. CMYK sin reglas de impresion produce resultados consistentes, pero insuficientes para fidelidad real.
3. Definir desde ahora la ruta a flexo evita decisiones locales que bloqueen la evolucion del producto.

## Consecuencias

### Positivas

- ✅ Mayor coherencia entre lo que TPDI muestra y lo que se necesita en flujo de impresion.
- ✅ Base clara para agregar perfiles por proceso (offset/flexo) sin rehacer todo el pipeline.
- ✅ Reduce deuda conceptual al explicitar que la simulacion de color depende de politicas de impresion.

### Costos y Trade-offs

- ⚠️ Aumenta complejidad de configuracion y validacion.
- ⚠️ Requiere ampliar tests con casos de referencia por perfil/proceso.
- ⚠️ Exige documentar limites de fidelidad en visualizacion de monitor.

## Lineamientos Tecnicos

1. Definir una interfaz de politica de separacion de color en casos de uso.
2. Implementar politicas concretas por proceso de impresion (inicial: cuatricromia generica; luego: flexo 2 plenos).
3. Externalizar parametros de impresion en configuracion versionable.
4. Agregar pruebas de regresion con imagenes patron y valores esperados por canal.

## Criterio de Revision

Revisar ADR-003 si ocurre alguno de estos eventos:

1. Se decide volver a enfoque didactico como prioridad principal.
2. Se requiere certificacion colorimetrica formal basada en instrumentos/perfiles externos.
3. El dominio necesita capturar semantica de color de forma persistente en entidades.
