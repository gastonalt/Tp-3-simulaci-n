# Convencion de codigo en espanol - 2026-06-27

## Decision

A partir de esta fecha, el codigo nuevo del TP debe escribirse en espanol siempre que sea razonable:

- Nombres de funciones y metodos.
- Nombres de clases y dataclasses.
- Nombres de atributos propios del proyecto.
- Variables locales.
- Helpers privados.
- Mensajes de consola.
- Encabezados CSV y textos visibles.

Se pueden conservar terminos tecnicos estandar cuando mejoran la claridad o son notacion universal: `lambda`, `mu`, `rho`, `M/M/1`, `M/M/1/K`, `Q`, `r`, `FIFO`, nombres de bloques de AnyLogic como `Source`, `Queue`, `Service` y `Sink`, y claves de APIs externas.

Tambien se pueden conservar nombres de archivos o modulos ya documentados si renombrarlos rompe comandos existentes o rutas usadas por el informe.

## Cambios aplicados al bloque M/M/1

Se tradujeron identificadores internos del codigo Python:

- `MM1Parameters` -> `ParametrosMM1`
- `MM1Result` -> `ResultadoMM1`
- `simulate_mm1` -> `simular_mm1`
- `metrics_row` -> `fila_metricas`
- `write_metrics_csv` -> `escribir_metricas_csv`
- `write_queue_probabilities_csv` -> `escribir_probabilidades_cola_csv`
- `write_time_series_csv` -> `escribir_serie_temporal_csv`
- `ExperimentConfig` -> `ConfiguracionExperimentos`
- `load_experiment_config` -> `cargar_configuracion_experimentos`
- `run_experiments` -> `ejecutar_experimentos`
- `write_experiment_outputs` -> `escribir_salidas_experimentos`
- `mm1_infinite_theory` -> `teoria_mm1_infinita`
- `mm1k_theory` -> `teoria_mm1k`
- `mean`, `sample_stdev`, `confidence_interval_half_width`, `percent_error` -> `media`, `desvio_estandar_muestral`, `semiancho_intervalo_confianza`, `error_porcentual`
- `read_rows_csv`, `write_rows_csv` -> `leer_filas_csv`, `escribir_filas_csv`

Los scripts ejecutables mantienen los nombres de modulo existentes:

```bash
python -m src.mm1.run_single
python -m src.mm1.run_experiments
python -m src.mm1.plot_results
python -m src.mm1.export_latex_tables
```

pero internamente usan `principal()` y helpers en espanol.

## Validaciones realizadas

- `python -m compileall src`: sin errores.
- `python -m src.mm1.run_single --sin-serie-temporal`: sin errores.
- `python -m src.mm1.run_experiments`: sin errores; 300 corridas.
- `python -m src.mm1.export_latex_tables`: sin errores.
- `python -m src.mm1.plot_results`: sin errores.

## Nota para futuras IAs

No volver a generar codigo del proyecto con nombres internos en ingles salvo que se trate de una API externa, una convencion tecnica fuerte o una ruta/comando ya documentado que convenga preservar.
