# Ajuste de seccion de codigo y repositorio - 2026-06-28

## Contexto

Se reviso la ubicacion de la seccion `Codigo y repositorio del proyecto` en el informe LaTeX. Aunque el `\input{sections/99-repositorio-proyecto}` ya estaba al final de `report/main.tex`, las figuras de las secciones anteriores podian flotar y quedar visualmente despues o alrededor de esa seccion al compilar.

## Decision

Se agrego `\clearpage` antes de incluir `sections/99-repositorio-proyecto` en `report/main.tex`.

Esto fuerza a LaTeX a imprimir todas las tablas y figuras pendientes antes de empezar la seccion de codigo y repositorio. De esta manera, el enlace a GitHub queda debajo de todo el contenido de resultados y graficos.

## Archivos modificados

- `report/main.tex`
- `docs/2026-06-28-ajuste-repositorio-informe.md`

## Validacion

Se ejecuto `git diff --check` sin problemas de whitespace.

