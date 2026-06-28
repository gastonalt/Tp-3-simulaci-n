# Inventario Python e informe - 2026-06-28

## Contexto

Se implemento el modelo de inventario del TP y se integro al informe LaTeX existente sin reescribir el bloque `M/M/1`.

Antes de trabajar se leyo `AGENTS.md` y todos los documentos existentes en `docs/`, con especial atencion a `docs/2026-06-27-handoff-inventario.md`.

## Decisiones de modelado

- Se uso una politica de revision continua `(Q, r)`.
- La unidad de tiempo es el dia.
- La simulacion avanza por periodos diarios.
- En cada dia se reciben pedidos, se genera demanda, se satisface demanda, se registran faltantes, se acumulan costos, se revisa posicion de inventario y se emite una orden si corresponde.
- El criterio de faltantes es ventas perdidas: la demanda no satisfecha genera costo y no queda pendiente para dias futuros.
- La posicion de inventario se calcula como inventario disponible mas unidades en pedido.
- El inventario promedio se calcula con el inventario disponible al cierre de cada dia, que es el mismo estado sobre el que se cobra mantenimiento diario.
- Para codigo nuevo se usaron nombres en espanol cuando fue razonable. Se conservaron `Q` y `r` por ser simbolos tecnicos de la politica.
- Las claves estructurales en ingles de `config/default_parameters.json` se conservaron porque ya funcionan como contrato de configuracion del proyecto; los nombres visibles de politicas ya estaban en espanol.

## Parametros usados

- Horizonte: `365 dias`.
- Replicas: `10` por politica.
- Semilla base: `20260626`.
- Demanda diaria: Poisson con media `20 unidades/dia`.
- Inventario inicial: `120 unidades`.
- Tiempo de entrega: `3 dias`.
- Costo fijo de orden: `120`.
- Costo de mantenimiento: `0.35` por unidad por dia.
- Costo de faltante: `8` por unidad faltante.

Politicas:

| Politica | Q | r |
| --- | ---: | ---: |
| `bajo_inventario` | 80 | 45 |
| `balanceada` | 120 | 70 |
| `alto_servicio` | 160 | 95 |

## Codigo agregado

- `src/inventory/__init__.py`
- `src/inventory/simulador.py`
- `src/inventory/experimentos.py`
- `src/inventory/ejecutar_experimentos.py`
- `src/inventory/graficar_resultados.py`
- `src/inventory/exportar_tablas_latex.py`

## Resultados generados

CSV:

- `results/inventory/experiments/inventario_corridas.csv`: 30 corridas mas encabezado.
- `results/inventory/experiments/inventario_resumen.csv`: 3 politicas mas encabezado.
- `results/inventory/experiments/inventario_series.csv`: 10950 dias-politica-replica mas encabezado.

Figuras SVG:

- `figures/inventory/inventario_disponible.svg`
- `figures/inventory/demanda_diaria.svg`
- `figures/inventory/costos_acumulados.svg`
- `figures/inventory/costo_total_por_politica.svg`
- `figures/inventory/nivel_servicio_por_politica.svg`

Copias PDF para el informe:

- `report/figures/inventory/inventario_disponible.pdf`
- `report/figures/inventory/demanda_diaria.pdf`
- `report/figures/inventory/costos_acumulados.pdf`
- `report/figures/inventory/costo_total_por_politica.pdf`
- `report/figures/inventory/nivel_servicio_por_politica.pdf`

Tablas LaTeX:

- `report/tables/inventario_resumen_politicas.tex`
- `report/tables/inventario_costos.tex`

Secciones LaTeX:

- `report/sections/05-marco-teorico-inventario.tex`
- `report/sections/06-metodologia-inventario.tex`
- `report/sections/07-resultados-inventario.tex`

Tambien se actualizo `report/main.tex` para incluir las secciones y el directorio `report/figures/inventory/`.

## Resultados principales

Promedios sobre 10 replicas:

| Politica | Costo total | Nivel de servicio | Faltantes |
| --- | ---: | ---: | ---: |
| `bajo_inventario` | 17998.25 | 93.37% | 485.80 |
| `balanceada` | 16304.39 | 99.96% | 2.70 |
| `alto_servicio` | 20235.96 | 100.00% | 0.00 |

La politica recomendada por menor costo total promedio es `balanceada`. `alto_servicio` elimina faltantes, pero el costo de mantenimiento aumenta demasiado. `bajo_inventario` reduce inventario, pero el costo de faltantes vuelve menos conveniente la politica.

## Validaciones ejecutadas

Se ejecutaron los comandos pedidos:

```bash
python -m compileall src
python -m src.inventory.ejecutar_experimentos
python -m src.inventory.graficar_resultados
python -m src.inventory.exportar_tablas_latex
git diff --check
```

Resultado: todos finalizaron sin errores. El comando de graficos con el Python del sistema aviso que `reportlab` no estaba disponible, por lo que no genero PDFs en esa ejecucion. Los SVG se generaron correctamente. Para dejar las copias PDF del informe se ejecuto el mismo generador con el Python empaquetado de Codex, donde `reportlab` si esta disponible.

Tambien se reviso textualmente que los nuevos `\input{...}` y `\includegraphics{...}` del informe apunten a archivos existentes.

## Pendientes

1. Compilar `report/main.tex` en Overleaf o en una instalacion local de LaTeX para revisar el PDF final.
2. Si se desea que cualquier Python local genere PDFs del informe, agregar `reportlab` como dependencia documentada o dejar la conversion PDF como paso opcional.
3. Implementar el modelo de inventario en AnyLogic solo cuando el usuario lo pida.
4. Mas adelante, integrar comparaciones con AnyLogic cuando existan esos resultados.

