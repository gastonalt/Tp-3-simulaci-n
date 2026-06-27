# Traduccion al espanol del TP - 2026-06-27

## Contexto

Se realizo una pasada de nomenclatura para dejar en espanol los terminos visibles del bloque `M/M/1`: salidas por consola, encabezados CSV, estados teoricos, graficos SVG/PDF, tablas LaTeX, configuracion visible y documentacion.

Antes de modificar se leyeron las bitacoras existentes en `docs/`, incluyendo las bitacoras agregadas durante el trabajo:

- `2026-06-26-plan-tp3.md`
- `2026-06-26-parametros-iniciales.md`
- `2026-06-26-experimentos-mm1.md`
- `2026-06-27-informe-mm1.md`
- `2026-06-27-template-arxiv-figuras-mm1.md`
- `2026-06-27-handoff-inventario.md`

## Criterio de traduccion

- Se tradujeron artefactos visibles para el usuario o el informe.
- En una segunda pasada se tradujeron tambien nombres internos de funciones, clases, atributos y helpers propios del proyecto para que el codigo resulte mas legible para el equipo.
- Se agregaron alias CLI en espanol, conservando las banderas anteriores en ingles para compatibilidad.
- Se mantuvieron los simbolos y notaciones tecnicas estandar: `lambda`, `mu`, `rho`, `L`, `L_q`, `W`, `W_q`, `M/M/1` y `M/M/1/K`.
- Se mantuvieron nombres de archivos generados ya usados por el informe para no romper rutas LaTeX, pero se tradujo su contenido visible.

## Terminos traducidos

Columnas y valores de resultados:

- `queue_capacity` -> `capacidad_cola`
- `infinite` -> `infinita`
- `theoretical_status` -> `estado_teorico`
- `infinite_capacity_steady_state` -> `capacidad_infinita_regimen_estacionario`
- `infinite_capacity_unstable_no_steady_state` -> `capacidad_infinita_sin_regimen_estacionario`
- `finite_capacity_steady_state` -> `capacidad_finita_regimen_estacionario`
- `mean`, `stdev`, `ci95_half_width`, `theory`, `error_percent` -> `media`, `desvio_estandar`, `semiancho_ic95`, `teoria`, `error_porcentual`
- metricas como `average_number_in_system`, `server_utilization` y `denial_probability` -> `promedio_clientes_sistema`, `utilizacion_servidor`, `probabilidad_denegacion`
- eventos de serie temporal como `start`, `departure`, `arrival_queue` -> `inicio`, `salida`, `llegada_a_cola`

Textos visibles:

- Titulos, ejes y leyendas de graficos SVG/PDF.
- Mensajes de consola de `run_single`, `run_experiments`, `plot_results` y `export_latex_tables`.
- Comentarios generados en fragmentos LaTeX.
- Nombres visibles de politicas de inventario en `config/default_parameters.json`: `bajo_inventario`, `balanceada`, `alto_servicio`.
- Referencias documentales a `lead time` se pasaron a `tiempo de entrega`.

## Terminos conservados

- Claves estructurales de `config/default_parameters.json` como `service_rate`, `arrival_rate_factors`, `simulation_time` y `lead_time_days`. Se mantuvieron porque forman el contrato de lectura de configuracion.
- `Queue`, `Service`, `Source` y `Sink` en el plan AnyLogic, cuando se refieren a nombres de bloques de la herramienta.
- Nombres de archivos como `mm1_summary.csv` o `mm1_infinite_average_number_in_system.svg`, para mantener compatibilidad con rutas existentes.
- Nombres de modulos existentes como `run_single.py`, `run_experiments.py`, `plot_results.py` y `export_latex_tables.py`, para no romper los comandos documentados con `python -m`.

## Archivos modificados

- `src/mm1/simulator.py`
- `src/mm1/experiments.py`
- `src/mm1/run_single.py`
- `src/mm1/run_experiments.py`
- `src/mm1/plot_results.py`
- `src/mm1/export_latex_tables.py`
- `src/mm1/theory.py`
- `src/common/statistics.py`
- `src/common/csv_utils.py`
- `src/__init__.py`
- `src/mm1/__init__.py`
- `config/default_parameters.json`
- `results/mm1/**/*.csv`
- `figures/mm1/*.svg`
- `report/tables/*.tex`
- `report/figures/mm1/*.pdf`
- `docs/2026-06-26-plan-tp3.md`
- `docs/2026-06-26-parametros-iniciales.md`
- `docs/2026-06-26-experimentos-mm1.md`
- `docs/2026-06-27-handoff-inventario.md`

## Regeneraciones

Se regeneraron:

```bash
python -m src.mm1.run_experiments
python -m src.mm1.run_single --sin-serie-temporal
python -m src.mm1.run_single --tiempo-simulacion 100 --directorio-salida results/mm1/smoke_timeseries
python -m src.mm1.run_single --factor-arribo 1.25 --capacidad-cola 2 --tiempo-simulacion 1000 --directorio-salida results/mm1/smoke_finite --sin-serie-temporal
python -m src.mm1.export_latex_tables
python -m src.mm1.plot_results
```

Tambien se convirtieron nuevamente los seis SVG de `figures/mm1/` a PDF en `report/figures/mm1/` usando `reportlab`.

## Validaciones realizadas

- `python -m compileall src`: sin errores.
- `python -m src.mm1.run_experiments`: genera 300 corridas y marca los casos de cola infinita con `rho >= 1` como `capacidad_infinita_sin_regimen_estacionario`.
- `python -m src.mm1.run_single --sin-serie-temporal`: salida CLI y CSV en espanol.
- `python -m src.mm1.export_latex_tables`: tablas regeneradas desde CSV traducidos.
- `python -m src.mm1.plot_results`: SVG regenerados con titulos, ejes y leyendas en espanol.
- Conversion SVG -> PDF con `reportlab`: seis PDF generados en `report/figures/mm1/`.
- Verificacion con `pypdf`: seis PDF de `960 x 560` puntos y texto extraido en espanol.
- Render con `pdftoppm`: PNG temporales generados; se revisaron visualmente la figura de clientes en sistema y la de probabilidad de denegacion. Luego se eliminaron los PNG temporales.
- Chequeo LaTeX de `\input`, `\includegraphics`, `\ref` y `\label`: sin faltantes.
- Busqueda de etiquetas visibles viejas en `docs`, `report`, `figures` y `results`: sin restos relevantes.
- `git diff --check`: sin problemas de whitespace.

No se pudo compilar el PDF LaTeX localmente porque `latexmk`, `pdflatex` y `tectonic` no estan disponibles en `PATH`.

## Nota conceptual conservada

Se mantuvo explicita la decision importante del TP: para `M/M/1` con cola infinita, los casos `rho >= 1` no tienen regimen estacionario. En los resultados traducidos quedan marcados como `capacidad_infinita_sin_regimen_estacionario` y no se comparan contra formulas estacionarias.
