# Centro de Costos Neix

Motor de asignación de gastos por área, construido a partir de 3 fuentes: el
export de contabilidad ("Tablero_Gastos_NEIX"), la Matriz de gastos (Google
Sheet), y el roster de empleados + detalle de sueldos que pasa RRHH.

**Empezar por [`MANUAL.md`](./MANUAL.md)** — ahí está todo el criterio de
asignación, los gaps conocidos, y las reglas para cada cuenta. Este README es
solo un índice de archivos.

- `roster.py` — empleados por área + matching de nombres (tolera apodos/nombres truncados).
- `matriz.py` — % reales de la Matriz de gastos.
- `rrhh_sueldos.py` — Sueldos y CS por área y mes (RRHH).
- `allocation_final.py` — motor principal. Lee `quant_accounting.json` (no
  versionado — son datos reales de sueldos/proveedores, se genera aparte
  parseando el export de contabilidad) y calcula el gasto final por área.

No se versiona ningún archivo con datos de proveedores/sueldos en el detalle
transaccional (`quant_accounting.json`) — solo los criterios y los totales
agregados por área que ya están en `rrhh_sueldos.py`.
