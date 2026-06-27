# Template arXiv y figuras MM1 - 2026-06-27

## Contexto

Se ordeno el informe LaTeX ubicado en `report/` para que sea facil de subir a Overleaf y use el template sencillo estilo Cornell/arXiv indicado por el usuario:

```text
https://es.overleaf.com/latex/templates/style-and-template-for-preprints-arxiv-bio-arxiv/
codigo/template: pkzcrhzcdxmc
```

El alcance se mantuvo en el modelo `M/M/1`. No se inicio la parte de inventario.

## Cambios en LaTeX

- Se adapto `report/main.tex` para usar `\documentclass[11pt]{article}` y `\usepackage{arxiv}`.
- Se agrego un resumen inicial con la advertencia clave: en cola infinita, los casos con `rho >= 1` no tienen regimen estacionario y no se comparan contra teoria estacionaria.
- Se mantuvieron las secciones existentes:
  - `report/sections/01-introduccion.tex`
  - `report/sections/02-marco-teorico-mm1.tex`
  - `report/sections/03-metodologia-mm1.tex`
  - `report/sections/04-resultados-mm1.tex`
- Se actualizaron los resultados para incluir las figuras ya convertidas, cada una con `caption` y `label`.
- Se conservaron las tablas existentes en `report/tables/` sin regenerarlas.

## Archivos del template agregados

Se agrego:

```text
report/arxiv.sty
```

No se trajeron archivos de ejemplo del template de Overleaf, para evitar contenido innecesario y mantener el paquete `report/` limpio.

## Figuras

Los SVG originales estan en:

```text
figures/mm1/
```

Se convirtieron a PDF y se guardaron en:

```text
report/figures/mm1/
```

Archivos generados:

- `report/figures/mm1/mm1_infinite_average_number_in_system.pdf`
- `report/figures/mm1/mm1_infinite_average_number_in_queue.pdf`
- `report/figures/mm1/mm1_infinite_average_time_in_system.pdf`
- `report/figures/mm1/mm1_infinite_average_time_in_queue.pdf`
- `report/figures/mm1/mm1_infinite_server_utilization.pdf`
- `report/figures/mm1/mm1_denial_probability_by_capacity.pdf`

La conversion se hizo localmente con `reportlab` desde el Python empaquetado de Codex, porque no habia `cairosvg`, `svglib` ni conversores externos detectados. Los SVG eran simples y solo usaban elementos basicos: `rect`, `text`, `line`, `polyline` y `circle`.

## Como compilar o subir a Overleaf

Para Overleaf, subir la carpeta `report/` completa. La estructura relevante queda:

```text
report/
|-- arxiv.sty
|-- main.tex
|-- figures/
|   |-- mm1/
|       |-- *.pdf
|-- sections/
|   |-- *.tex
|-- tables/
|   |-- *.tex
```

El archivo principal es:

```text
main.tex
```

Como las figuras estan en PDF y se incluyen con `graphicx`, no hace falta activar `shell-escape` ni instalar soporte SVG en Overleaf.

## Validaciones realizadas

- Se verifico que `latexmk`, `pdflatex` y `tectonic` no estan disponibles localmente en `PATH`, por lo que no se pudo compilar el PDF en esta maquina.
- Se valido textualmente que los `\input{...}` usados por `report/main.tex` y por las secciones existen dentro de `report/`.
- Se valido que todos los `\includegraphics{...}` apuntan a archivos existentes bajo `report/figures/mm1/`.
- Se valido que no hay referencias `\ref{...}` apuntando a labels inexistentes.
- Se abrieron los seis PDF generados con `pypdf`; cada uno tiene una pagina de `960 x 560` puntos.
- Se ejecuto `git diff --check` sin errores de whitespace.

## Pendientes

1. Compilar en Overleaf o en una instalacion local de LaTeX para revisar el PDF final visualmente.
2. Completar datos reales de autores/integrantes si corresponde.
3. Cuando se avance con inventario, agregar nuevas secciones sin mezclar resultados aun no generados.
