# Experimentos MM1 - 2026-06-26

## Contexto

Se completo el siguiente bloque de trabajo para el modelo `M/M/1`:

1. Runner completo de experimentos para todas las tasas y capacidades.
2. Resumen estadistico de 10 corridas por experimento.
3. Tablas CSV consolidadas.
4. Graficos iniciales en SVG.
5. Tratamiento explicito de la trampa de estabilidad para `rho >= 1`.

## La trampa de las tasas `1.00` y `1.25`

El enunciado pide variar la tasa de arribo al `25%`, `50%`, `75%`, `100%` y `125%` respecto de la tasa de servicio. Eso significa:

```text
rho = lambda / mu
rho = 0.25, 0.50, 0.75, 1.00, 1.25
```

La trampa es que el modelo `M/M/1` con cola infinita solo tiene regimen estacionario si:

```text
rho < 1
```

Entonces:

- Para `rho = 0.25`, `0.50` y `0.75`, la cola infinita tiene valores teoricos estacionarios.
- Para `rho = 1.00` y `1.25`, la cola infinita no tiene valores teoricos estacionarios finitos.
- Esos casos igual pueden simularse por horizonte finito, pero no deben compararse contra formulas estacionarias.
- En cola finita `M/M/1/K`, los casos `rho = 1.00` y `1.25` si tienen estado estacionario, porque la capacidad limitada bloquea arribos y evita crecimiento infinito.

El workaround adoptado en el codigo es mantener todos los casos pedidos por el enunciado, pero etiquetar cada experimento con una columna `theoretical_status`:

- `infinite_capacity_steady_state`
- `infinite_capacity_unstable_no_steady_state`
- `finite_capacity_steady_state`

De esta forma no se oculta el problema: queda visible en los CSV, en la documentacion y en la futura interpretacion del informe.

## Codigo agregado

Archivos nuevos:

- `src/common/csv_utils.py`: lectura y escritura CSV con finales de linea consistentes.
- `src/common/statistics.py`: media, desvio estandar, intervalo de confianza 95% y error porcentual.
- `src/mm1/experiments.py`: matriz experimental, referencias teoricas y resumenes.
- `src/mm1/run_experiments.py`: CLI para correr todos los experimentos `M/M/1`.
- `src/mm1/plot_results.py`: generador de graficos SVG sin dependencias externas.

Archivo actualizado:

- `config/default_parameters.json`: se agrego `max_queue_probability_length = 20`.

## Comandos ejecutados

Compilacion:

```bash
python -m compileall src
```

Ejecucion de matriz completa:

```bash
python -m src.mm1.run_experiments
```

Generacion de graficos:

```bash
python -m src.mm1.plot_results
```

## Matriz experimental ejecutada

Parametros:

- `mu = 10 clientes/hora`.
- `lambda = 2.5`, `5.0`, `7.5`, `10.0`, `12.5`.
- `rho = 0.25`, `0.50`, `0.75`, `1.00`, `1.25`.
- Capacidades de cola: infinita, `0`, `2`, `5`, `10`, `50`.
- Corridas por experimento: `10`.
- Horizonte por corrida: `10000 horas`.

Cantidad total de corridas:

```text
5 tasas * 6 capacidades * 10 corridas = 300 corridas
```

Se verifico que `results/mm1/experiments/mm1_runs.csv` contiene `301` lineas: encabezado mas `300` corridas.

## Archivos de resultados

Se generaron:

- `results/mm1/experiments/mm1_runs.csv`: una fila por corrida.
- `results/mm1/experiments/mm1_summary.csv`: una fila por experimento con metricas en formato ancho.
- `results/mm1/experiments/mm1_summary_long.csv`: una fila por experimento y metrica, mas util para tablas.
- `results/mm1/experiments/mm1_queue_probabilities.csv`: probabilidades promedio de longitud de cola para `n = 0..20` y cola de probabilidad `>20`.

Columnas importantes:

- `queue_capacity`: `infinite`, `0`, `2`, `5`, `10`, `50`.
- `queue_model`: `M/M/1` o `M/M/1/K`.
- `theoretical_status`: indica si existe referencia teorica estacionaria.
- `mean`: promedio entre corridas.
- `stdev`: desvio estandar entre corridas.
- `ci95_half_width`: semiancho del intervalo de confianza 95%.
- `theory`: valor teorico esperado cuando corresponde.
- `error_percent`: error porcentual contra teoria cuando corresponde.

## Graficos generados

Se generaron graficos SVG en `figures/mm1/`:

- `mm1_infinite_average_number_in_system.svg`
- `mm1_infinite_average_number_in_queue.svg`
- `mm1_infinite_average_time_in_system.svg`
- `mm1_infinite_average_time_in_queue.svg`
- `mm1_infinite_server_utilization.svg`
- `mm1_denial_probability_by_capacity.svg`

Los graficos de cola infinita incluyen solo los casos estables `rho < 1`, porque los casos `rho >= 1` no tienen referencia estacionaria.

## Observaciones de validacion

Para cola infinita estable, los promedios quedan cerca de la teoria. Por ejemplo, para `rho = 0.75`:

| Metrica | Simulacion media | Teoria |
| --- | ---: | ---: |
| Clientes promedio en sistema | 3.0205 | 3.0000 |
| Clientes promedio en cola | 2.2705 | 2.2500 |
| Tiempo promedio en sistema | 0.4025 | 0.4000 |
| Tiempo promedio en cola | 0.3026 | 0.3000 |
| Utilizacion del servidor | 0.7500 | 0.7500 |

Para cola infinita inestable, la simulacion por horizonte finito produce numeros, pero no se comparan contra teoria estacionaria. En `mm1_summary.csv` se observan:

- `rho = 1.00`, cola infinita: `infinite_capacity_unstable_no_steady_state`.
- `rho = 1.25`, cola infinita: `infinite_capacity_unstable_no_steady_state`.

Para cola finita, todos los `rho` tienen referencia teorica estacionaria. Esto es lo que permite analizar probabilidad de denegacion de servicio para capacidades `0`, `2`, `5`, `10` y `50`.

## Pendientes inmediatos

1. Revisar visualmente los SVG y seleccionar cuales entran al informe.
2. Preparar tablas LaTeX a partir de `mm1_summary_long.csv`.
3. Escribir la seccion teorica `M/M/1` en `report/sections/`.
4. Empezar la implementacion del modelo de inventario.
