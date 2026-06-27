# TP 3 - Simulacion de un modelo M/M/1 e Inventario

Repositorio del Trabajo Practico 3 de Simulacion. El objetivo general es estudiar dos sistemas mediante simulacion, resultados teoricos cuando existen, graficos e informe:

- Una cola `M/M/1`, ya implementada en Python.
- Un modelo de inventario con politica `(Q, r)`, parametrizado y pendiente de implementacion.
- Una comparacion posterior con AnyLogic, pendiente.

## Estado actual

El bloque `M/M/1` ya contiene simulador, formulas teoricas, matriz experimental, resultados CSV, graficos SVG, tablas LaTeX y una primera version del informe. Los casos de cola infinita con `rho >= 1` se simulan por horizonte finito, pero se marcan como casos sin regimen estacionario y no se comparan contra formulas estacionarias.

El bloque de inventario tiene parametros definidos en `config/default_parameters.json` y una guia de implementacion en `docs/2026-06-27-handoff-inventario.md`, pero todavia no tiene codigo Python versionado.

## Estructura del proyecto

```text
.
|-- AGENTS.md
|-- TP 3 - Simulación de un modelo MM1 e Inventario.md
|-- config/
|   |-- default_parameters.json
|-- docs/
|-- src/
|   |-- common/
|   |-- mm1/
|-- results/
|   |-- mm1/
|-- figures/
|   |-- mm1/
|-- report/
|   |-- main.tex
|   |-- arxiv.sty
|   |-- sections/
|   |-- tables/
|   |-- figures/
|       |-- mm1/
```

### Raiz

- `AGENTS.md`: instrucciones de trabajo para agentes/IA. Indica que antes de modificar el proyecto se deben leer todos los archivos de `docs/`.
- `TP 3 - Simulación de un modelo MM1 e Inventario.md`: enunciado del trabajo practico.
- `108-Simulation-Modeling-and-Analysis-Averill-M.-Law-Edisi-5-2014.pdf` y `The Art of Process-Centric Modeling.pdf`: bibliografia de apoyo.

### `docs/`

Memoria viva del proyecto. Ahi se registran decisiones, parametros, resultados parciales, validaciones y pendientes. Antes de continuar el TP conviene leer todos esos archivos, porque contienen decisiones importantes que no siempre estan repetidas en el codigo.

Documentos clave:

- `2026-06-26-plan-tp3.md`: plan general del TP, fases y riesgos.
- `2026-06-26-parametros-iniciales.md`: parametros base de `M/M/1` e inventario.
- `2026-06-26-experimentos-mm1.md`: matriz experimental y resultados del bloque `M/M/1`.
- `2026-06-27-informe-mm1.md`: armado inicial del informe LaTeX.
- `2026-06-27-template-arxiv-figuras-mm1.md`: adaptacion del informe al template arXiv y conversion de figuras.
- `2026-06-27-convencion-codigo-espanol.md`: convencion de nombres en espanol para codigo nuevo.
- `2026-06-27-handoff-inventario.md`: guia para implementar el modelo de inventario.

### `config/`

`config/default_parameters.json` centraliza los parametros editables.

Para `M/M/1` define:

- unidad de tiempo: horas;
- `mu = 10` clientes/hora;
- factores de arribo: `0.25`, `0.50`, `0.75`, `1.00`, `1.25`;
- capacidades de cola: infinita, `0`, `2`, `5`, `10`, `50`;
- horizonte: `10000` horas;
- replicas: `10`;
- semilla base: `20260626`.

Para inventario define:

- unidad de tiempo: dias;
- politica `(Q, r)`;
- horizonte de `365` dias;
- demanda Poisson media de `20` unidades/dia;
- tiempo de entrega de `3` dias;
- costos de orden, mantenimiento y faltante;
- politicas `bajo_inventario`, `balanceada` y `alto_servicio`.

Algunas claves del JSON estan en ingles porque funcionan como contrato de lectura del codigo.

## Codigo Python

El codigo esta organizado como paquete Python bajo `src/`. Para ejecutar los comandos, ubicarse en la raiz del proyecto.

### `src/common/`

Helpers compartidos:

- `csv_utils.py`
  - `leer_filas_csv(...)`: lee CSV como lista de diccionarios.
  - `escribir_filas_csv(...)`: escribe una lista de diccionarios a CSV, creando directorios si hace falta.
- `statistics.py`
  - `media(...)`;
  - `desvio_estandar_muestral(...)`;
  - `semiancho_intervalo_confianza(...)`;
  - `error_porcentual(...)`;
  - `t_critico_975(...)`.

Estos helpers son usados por los experimentos y generadores de salidas.

### `src/mm1/theory.py`

Contiene las referencias teoricas:

- `teoria_mm1_infinita(tasa_arribo, tasa_servicio, ...)`: calcula las metricas estacionarias de `M/M/1` con cola infinita solo si `rho < 1`. Para `rho >= 1` devuelve metricas en `None` y marca que no hay regimen estacionario.
- `teoria_mm1k(tasa_arribo, tasa_servicio, capacidad_cola)`: calcula las metricas estacionarias de `M/M/1/K`, donde la capacidad total del sistema es `K = capacidad_cola + 1`.

### `src/mm1/simulator.py`

Es el nucleo de simulacion por eventos discretos.

Elementos principales:

- `ParametrosMM1`: dataclass con tasa de arribo, tasa de servicio, horizonte, capacidad de cola y semilla.
- `ResultadoMM1`: dataclass con metricas finales, probabilidades de longitud de cola y serie temporal opcional.
- `simular_mm1(...)`: ejecuta la simulacion. Procesa eventos de llegada y salida, acumula areas temporales para estimar `L`, `Lq` y utilizacion, y mide tiempos promedio de los clientes atendidos.
- `escribir_metricas_csv(...)`, `escribir_probabilidades_cola_csv(...)`, `escribir_serie_temporal_csv(...)`: exportan salidas de una o mas corridas.

La capacidad de cola `None` representa cola infinita. Si la capacidad es un entero, los arribos se rechazan cuando la cola esta llena.

### `src/mm1/experiments.py`

Orquesta la matriz experimental completa.

Flujo principal:

1. `cargar_configuracion_experimentos(...)` lee `config/default_parameters.json`.
2. `ejecutar_experimentos(...)` recorre capacidades, factores de arribo y replicas.
3. Cada combinacion crea un `ParametrosMM1` y llama a `simular_mm1(...)`.
4. `referencia_teorica(...)` conecta cada corrida con `teoria_mm1_infinita(...)` o `teoria_mm1k(...)`.
5. `construir_filas_corridas(...)`, `construir_filas_resumen(...)` y `construir_filas_probabilidades_cola(...)` preparan las tablas de salida.
6. `escribir_salidas_experimentos(...)` genera los CSV consolidados.

Tambien etiqueta cada caso con `estado_teorico`:

- `capacidad_infinita_regimen_estacionario`;
- `capacidad_infinita_sin_regimen_estacionario`;
- `capacidad_finita_regimen_estacionario`.

### Scripts ejecutables

- `src/mm1/run_single.py`: ejecuta una corrida individual y exporta metricas, probabilidades de cola y, si se pide, serie temporal.
- `src/mm1/run_experiments.py`: ejecuta toda la matriz `M/M/1` definida en la configuracion.
- `src/mm1/plot_results.py`: lee `results/mm1/experiments/mm1_summary.csv` y genera graficos SVG en `figures/mm1/`.
- `src/mm1/export_latex_tables.py`: lee `mm1_summary.csv` y genera tablas LaTeX en `report/tables/`.

## Flujo de datos

```text
config/default_parameters.json
        |
        v
src/mm1/run_experiments.py
        |
        v
src/mm1/experiments.py ----> src/mm1/simulator.py
        |                         |
        |                         v
        |                  src/mm1/theory.py
        v
results/mm1/experiments/*.csv
        |
        +--> src/mm1/plot_results.py ---------> figures/mm1/*.svg
        |
        +--> src/mm1/export_latex_tables.py --> report/tables/*.tex
                                             \
                                              v
                                         report/main.tex
```

## Como ejecutar

Requisito minimo: Python 3.10 o superior. El bloque `M/M/1` usa solo biblioteca estandar.

### Corrida individual

```bash
python -m src.mm1.run_single
```

Por defecto usa `rho = 0.75`, cola infinita, horizonte `10000` y semilla base. Genera:

```text
results/mm1/mm1_single_metrics.csv
results/mm1/mm1_single_queue_probabilities.csv
results/mm1/mm1_single_timeseries.csv
```

Para omitir la serie temporal:

```bash
python -m src.mm1.run_single --sin-serie-temporal
```

Ejemplo con cola finita:

```bash
python -m src.mm1.run_single --factor-arribo 1.25 --capacidad-cola 2 --tiempo-simulacion 1000 --directorio-salida results/mm1/smoke_finite --sin-serie-temporal
```

### Matriz completa de experimentos

```bash
python -m src.mm1.run_experiments
```

Genera:

```text
results/mm1/experiments/mm1_runs.csv
results/mm1/experiments/mm1_summary.csv
results/mm1/experiments/mm1_summary_long.csv
results/mm1/experiments/mm1_queue_probabilities.csv
```

Con la configuracion actual se ejecutan:

```text
5 factores de arribo * 6 capacidades de cola * 10 replicas = 300 corridas
```

### Graficos

```bash
python -m src.mm1.plot_results
```

Genera SVG en:

```text
figures/mm1/
```

Figuras actuales:

- `mm1_infinite_average_number_in_system.svg`;
- `mm1_infinite_average_number_in_queue.svg`;
- `mm1_infinite_average_time_in_system.svg`;
- `mm1_infinite_average_time_in_queue.svg`;
- `mm1_infinite_server_utilization.svg`;
- `mm1_denial_probability_by_capacity.svg`.

### Tablas LaTeX

```bash
python -m src.mm1.export_latex_tables
```

Genera:

```text
report/tables/mm1_infinite_steady_state.tex
report/tables/mm1_infinite_unstable.tex
report/tables/mm1_denial_probability.tex
```

## Resultados

Los resultados principales del modelo `M/M/1` estan en `results/mm1/experiments/`.

- `mm1_runs.csv`: una fila por replica.
- `mm1_summary.csv`: una fila por experimento, con metricas en formato ancho.
- `mm1_summary_long.csv`: una fila por experimento y metrica, mas comoda para tablas.
- `mm1_queue_probabilities.csv`: probabilidades promedio de longitud de cola.

Las columnas mas importantes son:

- `rho`;
- `capacidad_cola`;
- `modelo_cola`;
- `estado_teorico`;
- metricas de simulacion: media, desvio estandar e intervalo de confianza;
- valor teorico y error porcentual cuando corresponde.

## Informe LaTeX

El informe esta en `report/` y usa un template simple estilo arXiv:

```text
report/
|-- main.tex
|-- arxiv.sty
|-- sections/
|-- tables/
|-- figures/mm1/
```

Archivo principal:

```text
report/main.tex
```

Secciones actuales:

- `sections/01-introduccion.tex`;
- `sections/02-marco-teorico-mm1.tex`;
- `sections/03-metodologia-mm1.tex`;
- `sections/04-resultados-mm1.tex`.

Para compilar en Overleaf, subir la carpeta `report/` completa y elegir `main.tex` como archivo principal. Las figuras del informe ya estan en PDF dentro de `report/figures/mm1/`, por lo que no hace falta soporte SVG.

## Nota conceptual importante

Para `M/M/1` con cola infinita:

- si `rho < 1`, existe regimen estacionario y se comparan simulacion y teoria;
- si `rho >= 1`, no existe regimen estacionario, por lo que las corridas se informan como resultados de horizonte finito.

Para `M/M/1/K` con capacidad finita, todos los valores de `rho` tienen referencia estacionaria porque los arribos excedentes se rechazan cuando el sistema esta lleno.

## Pendientes

- Implementar el simulador Python de inventario con politica `(Q, r)`.
- Generar resultados, graficos y tablas de inventario.
- Agregar secciones de inventario al informe.
- Replicar `M/M/1` e inventario en AnyLogic.
- Comparar teoria, Python y AnyLogic en el informe final.
- Compilar y revisar visualmente el PDF final del informe.
