# Revision evaluador preentrega - 2026-06-28

## Contexto

Se reviso el trabajo practico con mirada de evaluador antes de entrega. La revision cubrio:

- Enunciado del TP.
- Memoria viva en `docs/`.
- Informe LaTeX en `report/`.
- Tablas y resultados exportados.
- Configuracion de parametros.
- Logica principal de los simuladores Python de `M/M/1` e inventario.

## Dictamen general

El bloque `M/M/1` esta conceptualmente solido: las formulas estacionarias son correctas, la condicion `rho < 1` para cola infinita esta bien tratada, y la definicion de cola finita como `B` con capacidad total `K = B + 1` es consistente con el codigo y las tablas.

El bloque de inventario es coherente como simulacion Python con ventas perdidas, demanda Poisson, politica `(Q,r)` y costos de orden, mantenimiento y faltante. Los resultados respaldan la recomendacion de la politica `balanceada`.

Sin embargo, el informe aun no cumple completamente la consigna literal porque faltan comparaciones con AnyLogic y una fuente teorica/esperada para inventario. Tambien falta una evolucion temporal explicita para las metricas de rendimiento del modelo `M/M/1` dentro del informe.

## Hallazgos principales

1. Falta AnyLogic en el informe.
   - El enunciado pide comparar tres fuentes: valor teorico esperado, Python y AnyLogic.
   - El informe actual solo compara teoria y Python para `M/M/1`, y solo politicas Python para inventario.
   - Esto deberia resolverse antes de una entrega final si la catedra exige estrictamente ese punto.

2. Falta valor teorico o esperado para inventario.
   - El informe presenta formulas de costo y resultados simulados, pero no una referencia teorica o aproximada para contrastar las politicas.
   - Si no se calcula una referencia cerrada, conviene justificar explicitamente que el modelo de inventario con ventas perdidas y lead time se evalua por simulacion, o agregar una aproximacion esperada simple.

3. La introduccion esta desactualizada.
   - `report/sections/01-introduccion.tex` todavia dice que en una etapa posterior se agregara inventario y AnyLogic.
   - Inventario ya esta incluido en el informe, por lo que esa frase contradice el documento.

4. Falta evolucion temporal `M/M/1` en el informe.
   - La consigna pide medidas finales y en relacion al tiempo de simulacion.
   - El informe muestra resultados finales y graficos contra `rho`, pero no una serie temporal de clientes en sistema, clientes en cola, utilizacion u otra metrica `M/M/1`.

5. La seccion `Resultados preliminares M/M/1` deberia dejar de decir "preliminares" si esta version se entrega como final.

6. El README esta desactualizado.
   - Todavia indica que inventario esta pendiente, aunque ya existen codigo, resultados y secciones de inventario.
   - Si se entrega el repositorio o el enlace de GitHub, esto puede confundir al evaluador.

7. Falta una conclusion final integradora.
   - Hay interpretacion local en resultados, pero no una seccion de cierre que resuma cumplimiento de objetivos, hallazgos principales, limitaciones y pendientes.

## Validaciones realizadas

- Se verifico que no hay herramientas LaTeX locales disponibles en `PATH` (`latexmk`, `pdflatex`, `tectonic`), por lo que no se pudo compilar el PDF localmente.
- Se ejecuto `git diff --check` sin errores.
- Se reviso que el codigo de `M/M/1` e inventario coincida con las decisiones declaradas en el informe.

## Recomendacion de prioridad

Antes de entregar, priorizar:

1. Agregar o documentar AnyLogic.
2. Agregar comparacion teorica/esperada o justificacion explicita para inventario.
3. Corregir la introduccion desactualizada.
4. Agregar al menos un grafico temporal `M/M/1`.
5. Agregar conclusiones finales.
6. Actualizar README si se entrega el repositorio.
