# Parametros iniciales - 2026-06-26

## Contexto

Se avanzo con los primeros cuatro pendientes definidos en el plan inicial:

1. Elegir valores base definitivos para `M/M/1`.
2. Definir la politica exacta del modelo de inventario.
3. Crear la estructura inicial de carpetas del proyecto.
4. Implementar un primer simulador Python para `M/M/1`.

## Decisiones para `M/M/1`

Se usara como unidad base la hora.

Parametros iniciales:

- Tasa de servicio: `mu = 10 clientes/hora`.
- Factores de tasa de arribo respecto de `mu`: `0.25`, `0.50`, `0.75`, `1.00`, `1.25`.
- Tasas de arribo resultantes: `2.5`, `5.0`, `7.5`, `10.0`, `12.5` clientes/hora.
- Horizonte inicial de simulacion: `10000 horas`.
- Corridas minimas por experimento: `10`.
- Semilla base: `20260626`.
- Capacidades de cola: infinita para validacion clasica y finitas `0`, `2`, `5`, `10`, `50` para estudiar denegacion.

Justificacion:

- `mu = 10` permite interpretar facilmente los porcentajes pedidos en el enunciado.
- `10000 horas` da un horizonte suficientemente largo para que las metricas de los casos estables se acerquen a los valores teoricos.
- Se mantiene `10` corridas porque es el minimo obligatorio del TP; mas adelante puede aumentarse si los intervalos de confianza quedan amplios.
- La semilla base queda registrada para reproducibilidad.

## Decisiones para inventario

Se usara como unidad base el dia.

Politica elegida:

- Revision continua `(Q, r)`.
- Cuando la posicion de inventario cae a `r`, se emite una orden de cantidad fija `Q`.
- La orden llega luego de un lead time fijo inicial de `3 dias`.

Parametros iniciales:

- Horizonte: `365 dias`.
- Corridas minimas por experimento: `10`.
- Distribucion de demanda: Poisson.
- Demanda media diaria: `20 unidades/dia`.
- Inventario inicial: `120 unidades`.
- Costo fijo de orden: `120`.
- Costo de mantenimiento: `0.35` por unidad por dia.
- Costo de faltante: `8` por unidad faltante.

Politicas iniciales para comparar:

| Politica | Q | r | Intencion |
| --- | ---: | ---: | --- |
| `low_inventory` | 80 | 45 | Menor inventario promedio, mayor riesgo de faltantes |
| `balanced` | 120 | 70 | Punto medio entre mantenimiento y faltantes |
| `high_service` | 160 | 95 | Mayor nivel de servicio, mayor costo de mantenimiento |

Justificacion:

- La demanda Poisson es razonable para representar pedidos discretos diarios.
- El lead time de `3 dias` fuerza a que el punto de reorden sea relevante.
- Las tres politicas permiten observar el trade-off central del modelo: mantener stock cuesta, pero quedarse sin stock tambien.

## Estructura creada

```text
config/
data/
  anylogic/
  processed/
docs/
figures/
  inventory/
  mm1/
report/
  figures/
  sections/
  tables/
results/
  inventory/
  mm1/
src/
  common/
  inventory/
  mm1/
```

## Archivos creados

- `config/default_parameters.json`: parametros iniciales de `M/M/1` e inventario.
- `src/mm1/theory.py`: formulas teoricas para `M/M/1` infinito y `M/M/1/K`.
- `src/mm1/simulator.py`: simulador de eventos discretos para `M/M/1`.
- `src/mm1/run_single.py`: runner de una simulacion individual con salida CSV.

## Como ejecutar la primera simulacion

Desde la raiz del proyecto:

```bash
python -m src.mm1.run_single
```

Este comando usa por defecto:

- `lambda = 0.75 * mu = 7.5`.
- `mu = 10`.
- Cola infinita.
- Horizonte `10000`.
- Semilla `20260626`.

Salidas esperadas:

```text
results/mm1/mm1_single_metrics.csv
results/mm1/mm1_single_queue_probabilities.csv
results/mm1/mm1_single_timeseries.csv
```

Si solo se quieren metricas finales y probabilidades de longitud de cola, sin serie temporal:

```bash
python -m src.mm1.run_single --no-time-series
```

## Validacion inicial ejecutada

Se verifico que los modulos compilan correctamente con Python `3.12.13`.

Comando de validacion principal:

```bash
python -m src.mm1.run_single --no-time-series
```

Parametros:

- `lambda = 7.5`.
- `mu = 10`.
- `rho = 0.75`.
- Cola infinita.
- Horizonte `10000`.
- Semilla `20260626`.

Resultados de simulacion:

| Metrica | Simulacion | Teoria |
| --- | ---: | ---: |
| Clientes promedio en sistema | 2.8834 | 3.0000 |
| Clientes promedio en cola | 2.1420 | 2.2500 |
| Tiempo promedio en sistema | 0.3865 | 0.4000 |
| Tiempo promedio en cola | 0.2872 | 0.3000 |
| Utilizacion del servidor | 0.7414 | 0.7500 |
| Probabilidad de denegacion | 0.0000 | 0.0000 |

La diferencia es razonable para una corrida individual. La comparacion formal debera hacerse luego con al menos 10 corridas e intervalos de confianza.

Tambien se ejecuto una prueba corta con serie temporal:

```bash
python -m src.mm1.run_single --simulation-time 100 --output-dir results/mm1/smoke_timeseries
```

Archivos generados:

- `results/mm1/smoke_timeseries/mm1_single_metrics.csv`
- `results/mm1/smoke_timeseries/mm1_single_queue_probabilities.csv`
- `results/mm1/smoke_timeseries/mm1_single_timeseries.csv`

Y una prueba de cola finita con rechazos:

```bash
python -m src.mm1.run_single --arrival-factor 1.25 --queue-capacity 2 --simulation-time 1000 --output-dir results/mm1/smoke_finite --no-time-series
```

Parametros:

- `lambda = 12.5`.
- `mu = 10`.
- `rho = 1.25`.
- Capacidad de cola `2`.
- Capacidad total del sistema `3`.

Resultados principales:

| Metrica | Simulacion | Teoria |
| --- | ---: | ---: |
| Clientes promedio en sistema | 1.8182 | 1.7751 |
| Clientes promedio en cola | 0.9787 | 0.9485 |
| Tiempo promedio en sistema | 0.2226 | 0.2148 |
| Tiempo promedio en cola | 0.1198 | 0.1148 |
| Utilizacion del servidor | 0.8395 | 0.8266 |
| Probabilidad de denegacion | 0.3515 | 0.3388 |

Esta prueba confirma que la rama de cola finita calcula rechazos y que el modelo puede analizar casos con `rho >= 1` cuando existe capacidad limitada.

## Pendientes inmediatos

1. Revisar visualmente los graficos SVG generados para `M/M/1`.
2. Preparar tablas LaTeX a partir de `results/mm1/experiments/mm1_summary_long.csv`.
3. Empezar a preparar la seccion LaTeX de marco teorico `M/M/1`.
4. Empezar la implementacion del modelo de inventario.
