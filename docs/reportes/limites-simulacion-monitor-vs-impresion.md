# Limites de Simulacion en Monitor vs Impresion Real

## Objetivo

Documentar limites conocidos al visualizar separaciones CMYK en monitor RGB dentro de TPDI.

## Alcance

- Aplica al flujo CMYK actual de TPDI.
- No reemplaza validacion colorimetrica de preprensa.

## Limites Tecnicos

1. La vista de canales CMYK en pantalla es una simulacion RGB.
2. El resultado depende del monitor, su perfil y calibracion.
3. Sin perfiles ICC de entrada/salida, la equivalencia con prensa es aproximada.
4. Parametros de proceso (ganancia de punto y limite total de tinta) afectan salida numerica, pero no garantizan coincidencia absoluta de color impreso.

## Implicaciones para TPDI

1. TPDI sirve para analisis comparativo y validacion de tendencias de separacion.
2. Las decisiones finales de color para impresion deben corroborarse con flujo de preprensa y pruebas de tiraje.
3. Las regresiones automaticas deben fijar valores esperados por politica y parametros, no por percepcion visual del monitor.

## Recomendaciones Operativas

1. Mantener un set de patrones de regresion con valores esperados por canal.
2. Versionar los parametros CMYK de proceso usados en cada corrida.
3. Si el objetivo crece hacia fidelidad certificable, incorporar gestion de color con perfiles ICC y procesos de calibracion.
