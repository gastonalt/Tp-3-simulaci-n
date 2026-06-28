# Guias AnyLogic - 2026-06-28

## Contexto

Se generaron dos documentos explicativos para construir en AnyLogic los modelos
del TP:

- `docs/2026-06-28-guia-anylogic-mm1.md`
- `docs/2026-06-28-guia-anylogic-inventario.md`

Antes de escribirlos se leyo la memoria completa del proyecto en `docs/`, el
enunciado, la configuracion vigente, las secciones teoricas del informe y el
codigo Python de ambos modelos.

## Criterios usados

- Se mantuvieron los parametros de `config/default_parameters.json`.
- Se respeto la convencion del proyecto: textos en espanol y notacion tecnica
  estandar para `lambda`, `mu`, `rho`, `Q`, `r`, `M/M/1` y `M/M/1/K`.
- Se verifico la documentacion oficial de AnyLogic para la version 8.9.x y la
  edicion Personal Learning Edition.
- Se documento la diferencia encontrada entre la pagina de descargas
  (`8.9.8`) y las release notes oficiales (`8.9.9`, 2026-06-18).
- Se incluyeron diagramas Mermaid para explicar el flujo de cada modelo.
- Se agregaron checklists de validacion y referencias a resultados/figuras del
  proyecto para facilitar la comparacion.

## Validacion

Se ejecuto:

```bash
git diff --check
```

Resultado: sin problemas de whitespace.

## Pendientes

1. Implementar efectivamente los modelos en AnyLogic.
2. Exportar o registrar resultados de AnyLogic en `data/anylogic/`.
3. Comparar AnyLogic contra Python y teoria en el informe final.
4. Agregar capturas reales de AnyLogic cuando existan los modelos.
