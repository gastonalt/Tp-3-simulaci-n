# Handoff modelo de inventario - 2026-06-27

## Objetivo del proximo bloque

Implementar el segundo modelo del TP: inventario con politica `(Q, r)`, simulacion en Python, resultados, graficos y secciones LaTeX integradas al informe existente.

## Regla de estilo para este bloque

El nuevo trabajo debe usar terminos en espanol en los artefactos visibles y, cuando sea razonable, tambien en el codigo nuevo:

- Titulos de graficos en espanol.
- Ejes y leyendas en espanol.
- Encabezados de tablas en espanol.
- Captions y texto del informe en espanol.
- Mensajes de consola en espanol.
- Nombres de politicas en espanol.
- Nombres de funciones, clases y variables del modulo nuevo en espanol, salvo que convenga mantener una convencion existente del proyecto o una API externa.

Si se mantienen terminos tecnicos por claridad, documentar la decision. Ejemplos razonables para conservar: `Q`, `r`, `stock` si se usa de forma consistente, y simbolos matematicos.

## Parametros iniciales de inventario

Los parametros iniciales ya estan en `config/default_parameters.json` y fueron documentados previamente:

- Unidad de tiempo: dias.
- Politica: revision continua `(Q, r)`.
- Horizonte: `365 dias`.
- Corridas: `10`.
- Semilla base: `20260626`.
- Demanda: Poisson.
- Demanda media diaria: `20 unidades/dia`.
- Inventario inicial: `120 unidades`.
- Tiempo de entrega: `3 dias`.
- Costo fijo de orden: `120`.
- Costo de mantenimiento: `0.35` por unidad por dia.
- Costo de faltante: `8` por unidad faltante.

Politicas propuestas:

| Politica visible | Q | r | Intencion |
| --- | ---: | ---: | --- |
| `bajo_inventario` | 80 | 45 | Menor inventario promedio, mayor riesgo de faltantes |
| `balanceada` | 120 | 70 | Punto medio entre mantenimiento y faltantes |
| `alto_servicio` | 160 | 95 | Mayor nivel de servicio, mayor costo de mantenimiento |

El archivo de configuracion debe usar estos nombres visibles en espanol para las politicas.

## Modelo esperado

Simular por periodos diarios es suficiente y legible para el TP. En cada dia:

1. Recibir pedidos pendientes cuyo dia de llegada sea el actual.
2. Generar demanda diaria con Poisson.
3. Satisfacer demanda con inventario disponible.
4. Registrar unidades faltantes si la demanda supera el inventario disponible.
5. Acumular costo de mantenimiento por inventario disponible.
6. Acumular costo de faltante por unidades no satisfechas.
7. Calcular posicion de inventario: inventario disponible mas pedidos pendientes.
8. Si la posicion de inventario es menor o igual a `r`, emitir una orden de cantidad `Q`.
9. Acumular costo fijo de orden.
10. Registrar series temporales del dia.

La decision sobre faltantes debe quedar explicita:

- Opcion recomendada para mantener simple el TP: ventas perdidas, es decir, la demanda no satisfecha se contabiliza como faltante/costo y no queda pendiente para dias futuros.
- Si se decide usar pedidos atrasados, documentarlo y ajustar metricas.

## Metricas a registrar

Por corrida:

- Politica.
- Numero de replica.
- Semilla.
- Horizonte.
- Demanda total.
- Demanda satisfecha.
- Unidades faltantes.
- Ordenes emitidas.
- Inventario promedio.
- Costo de orden.
- Costo de mantenimiento.
- Costo de faltante.
- Costo total.
- Nivel de servicio: demanda satisfecha / demanda total.

Por politica:

- Media.
- Desvio estandar.
- Intervalo de confianza 95%.
- Comparacion de costo total promedio.
- Politica recomendada segun menor costo total promedio, aclarando trade-off con nivel de servicio.

Series temporales:

- Inventario disponible.
- Demanda diaria.
- Ordenes emitidas.
- Unidades faltantes.
- Costos acumulados por componente.
- Costo total acumulado.

## Salidas esperadas

Codigo sugerido:

- `src/inventory/simulador.py`
- `src/inventory/experimentos.py`
- `src/inventory/ejecutar_experimentos.py`
- `src/inventory/graficar_resultados.py`
- `src/inventory/exportar_tablas_latex.py`

Resultados sugeridos:

- `results/inventory/experiments/inventario_corridas.csv`
- `results/inventory/experiments/inventario_resumen.csv`
- `results/inventory/experiments/inventario_series.csv`

Figuras sugeridas:

- `figures/inventory/inventario_disponible.svg`
- `figures/inventory/demanda_diaria.svg`
- `figures/inventory/costos_acumulados.svg`
- `figures/inventory/costo_total_por_politica.svg`
- `figures/inventory/nivel_servicio_por_politica.svg`

Tablas LaTeX sugeridas:

- `report/tables/inventario_resumen_politicas.tex`
- `report/tables/inventario_costos.tex`

Secciones LaTeX sugeridas:

- `report/sections/05-marco-teorico-inventario.tex`
- `report/sections/06-metodologia-inventario.tex`
- `report/sections/07-resultados-inventario.tex`

Actualizar `report/main.tex` para incluir esas secciones respetando el template arXiv ya agregado.

## Validaciones minimas

Ejecutar, si el entorno lo permite:

```bash
python -m compileall src
python -m src.inventory.ejecutar_experimentos
python -m src.inventory.graficar_resultados
python -m src.inventory.exportar_tablas_latex
git diff --check
```

Si los nombres de modulos quedan en ingles por consistencia con Python existente, ajustar los comandos y documentarlo.

## Documentacion

Al terminar, crear o actualizar una bitacora en `docs/` con:

- Decisiones de modelado.
- Tratamiento de faltantes.
- Parametros usados.
- Archivos generados.
- Resultados principales.
- Validaciones ejecutadas.
- Pendientes para AnyLogic y para el informe final.
