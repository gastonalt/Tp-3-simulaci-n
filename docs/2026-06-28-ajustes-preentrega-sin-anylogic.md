# Ajustes preentrega sin AnyLogic - 2026-06-28

## Contexto

El usuario indico que AnyLogic se esta trabajando en paralelo y que luego se
integrara manualmente. Se pidio corregir los demas hallazgos de la revision
evaluadora:

- Agregar comparacion esperada para inventario.
- Actualizar la introduccion desactualizada.
- Agregar evolucion temporal explicita para `M/M/1`.
- Actualizar el README.

Antes de editar se leyeron todos los documentos existentes en `docs/`.

## Cambios realizados

### Inventario

Se agrego una referencia esperada simplificada para inventario. La aproximacion
usa:

- demanda esperada del horizonte `D_T = lambda_D T`;
- ciclos esperados `N_Q = D_T / Q`;
- inventario medio aproximado `Q/2 + max(r - lambda_D L, 0)`;
- faltante esperado durante el tiempo de entrega `E[(D_L-r)^+]`, con
  `D_L ~ Poisson(lambda_D L)`;
- costo esperado total de orden, mantenimiento y faltante.

Archivos modificados:

- `src/inventory/exportar_tablas_latex.py`
- `report/sections/05-marco-teorico-inventario.tex`
- `report/sections/07-resultados-inventario.tex`

Archivo generado:

- `report/tables/inventario_comparacion_esperada.tex`

### M/M/1

Se agrego una figura temporal para una corrida representativa de `rho=0.75` y
100 horas, usando la serie `results/mm1/smoke_timeseries/mm1_single_timeseries.csv`.
La figura muestra clientes en sistema y clientes en cola a lo largo del tiempo.

Archivos modificados:

- `src/mm1/plot_results.py`
- `report/sections/04-resultados-mm1.tex`

Archivos generados:

- `figures/mm1/mm1_temporal_clientes_rho_075.svg`
- `report/figures/mm1/mm1_temporal_clientes_rho_075.pdf`

### Informe y README

Se actualizo:

- `report/main.tex`: resumen actualizado y aclaracion de AnyLogic en paralelo.
- `report/sections/01-introduccion.tex`: ya no dice que inventario se agregara despues.
- `README.md`: ahora refleja que `M/M/1` e inventario estan implementados en Python y que AnyLogic queda pendiente de resultados.

## Resultados destacados

La nueva tabla esperada de inventario muestra:

| Politica | Costo esperado | Python | Diferencia |
| --- | ---: | ---: | ---: |
| `bajo_inventario` | 27052.20 | 17998.25 | -33.47% |
| `balanceada` | 16434.40 | 16304.39 | -0.79% |
| `alto_servicio` | 20166.26 | 20235.96 | 0.35% |

La discrepancia de `bajo_inventario` queda explicada en el informe: la
referencia simplificada es conservadora porque resume el riesgo por ciclo y no
modela con todo detalle la superposicion diaria de pedidos pendientes.

## Validaciones realizadas

- Se regeneraron tablas de inventario con `python -m src.inventory.exportar_tablas_latex`.
- Se regeneraron figuras `M/M/1` con el Python empaquetado de Codex para contar
  con `reportlab`.
- Se renderizo el PDF temporal `mm1_temporal_clientes_rho_075.pdf` a PNG con
  Poppler y se reviso visualmente: grafico legible, no blanco, con ejes y
  leyenda correctos.

## Pendientes

- Integrar resultados reales de AnyLogic cuando esten disponibles.
- Compilar `report/main.tex` en Overleaf o en una instalacion local de LaTeX
  para revisar el PDF completo.
