# Revision informe LaTeX y template arXiv - 2026-06-27

## Contexto

Se reviso el informe LaTeX del bloque `M/M/1` para verificar tres puntos:

1. Que las tablas reportadas coincidan con los CSV generados por el codigo.
2. Que las formulas teoricas usadas por el codigo coincidan con el marco teorico del informe.
3. Que el template local se acerque al template sencillo de Overleaf/Cornell indicado por el usuario:
   `https://es.overleaf.com/latex/templates/style-and-template-for-preprints-arxiv-bio-arxiv/pkzcrhzcdxmc`.

Antes de editar se leyeron todos los documentos existentes en `docs/`.

## Cambios realizados

- Se reemplazo `report/arxiv.sty`, que era una version artesanal minima, por una version local mas cercana al estilo `arxiv` del template de Overleaf/Cornell.
- Se ajusto `report/main.tex` para alinear el preambulo con el template:
  - `\usepackage{arxiv}`
  - `inputenc`
  - `fontenc`
  - `hyperref`
  - `url`
  - `booktabs`
  - `amsfonts`
  - `nicefrac`
  - `microtype`
  - `graphicx`
- Se mantuvo `babel` en espanol y se personalizaron `Resumen` y `Palabras clave`.
- Se agregaron keywords del informe.
- Se extendio `src/mm1/export_latex_tables.py` para exportar tambien una tabla de probabilidades de longitud de cola.
- Se genero `report/tables/mm1_infinite_queue_probabilities.tex` desde `results/mm1/experiments/mm1_queue_probabilities.csv`.
- Se actualizo `report/sections/04-resultados-mm1.tex` para incluir la nueva tabla.
- Se actualizo `report/tp3_mm1_v1.zip` para que el paquete de Overleaf incluya el `arxiv.sty`, el `main.tex`, las secciones, tablas y figuras vigentes.
- Se corrigio el formato de las notas bajo las tablas de probabilidades para que no queden al costado del cuadro. Las notas ahora se emiten como un bloque en `minipage` despues de `\par\smallskip`.

## Revision teorica

La teoria revisada queda consistente:

- Para cola infinita `M/M/1`, solo se comparan valores estacionarios cuando `rho < 1`.
- Para `rho >= 1` con cola infinita, el codigo deja la referencia teorica vacia y el informe lo declara como caso sin regimen estacionario.
- Para cola finita `M/M/1/K`, se usa `B` como capacidad de cola y `K = B + 1` como capacidad total del sistema.
- La probabilidad de denegacion reportada es `P_K`.
- La tasa efectiva usada para tiempos teoricos en cola finita es `lambda_eff = lambda (1 - P_K)`.
- La probabilidad de longitud de cola se calcula con `P(Q=0)=P(N=0)+P(N=1)` y `P(Q=q)=P(N=q+1)` para `q >= 1`.

## Validaciones realizadas

Se regeneraron tablas con:

```bash
python -m src.mm1.export_latex_tables
```

Se ejecuto una validacion cruzada con Python que verifico:

- `results/mm1/experiments/mm1_runs.csv` contiene 300 corridas.
- `results/mm1/experiments/mm1_summary.csv` contiene 30 experimentos.
- `results/mm1/experiments/mm1_queue_probabilities.csv` contiene 660 filas.
- Las columnas `*_teoria` de `mm1_summary.csv` coinciden con `src/mm1/theory.py`.
- Los casos de cola infinita con `rho >= 1` no tienen teoria estacionaria reportada.
- Todos los `\input{...}` del informe apuntan a archivos existentes.
- Todos los `\includegraphics{...}` apuntan a figuras existentes.
- No hay referencias `\ref{...}` sin `\label{...}`.
- El ZIP actualizado contiene `arxiv.sty`, `main.tex`, `sections/`, `tables/` y `figures/`, incluida `tables/mm1_infinite_queue_probabilities.tex`.
- Las notas de `report/tables/mm1_infinite_queue_probabilities.tex` y `report/tables/mm1_denial_probability.tex` quedan debajo del `tabular`, no en la misma linea.

Tambien se ejecuto:

```bash
python -m compileall src
git diff --check
```

Ambos comandos finalizaron sin errores. Los directorios `__pycache__` generados por `compileall` se eliminaron luego de la validacion.

## Limitacion

No se pudo compilar el PDF LaTeX localmente porque `latexmk`, `pdflatex` y `tectonic` no estan disponibles en `PATH`. La compilacion visual final debe hacerse en Overleaf o en una instalacion local de LaTeX.

## Pendientes

1. Compilar `report/main.tex` en Overleaf para revisar visualmente la disposicion final del template.
2. Completar datos reales de autores/integrantes.
3. Agregar resultados de inventario y AnyLogic cuando esten disponibles.
4. Si se exige una entrega final completa, agregar graficos temporales de las medidas de rendimiento, porque el informe actual cubre el bloque `M/M/1` de Python y sigue siendo parcial.
