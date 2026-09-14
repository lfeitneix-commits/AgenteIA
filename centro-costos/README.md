# Centro de Costos Neix

Motor de asignación de gastos por área, construido a partir de 3 fuentes: el
export de contabilidad ("Tablero_Gastos_NEIX"), la Matriz de gastos (Google
Sheet), y el roster de empleados + detalle de sueldos que pasa RRHH.

**Empezar por [`MANUAL.md`](./MANUAL.md)** — ahí está todo el criterio de
asignación, los gaps conocidos, y las reglas para cada cuenta. Este README es
solo un índice de archivos.

- `roster.py` — empleados por área + matching de nombres (tolera apodos/nombres truncados).
- `matriz.py` — % de respaldo de la Matriz de gastos (snapshot hardcodeado, solo se usa si no existe `matriz_gastos.csv`).
- `matriz_gastos.csv` — **no versionado a mano**, lo sube solo el Apps Script de Google Sheets (`sync_matriz_to_github.gs`, entregado por chat) cada vez que se edita la Matriz. Si existe, tiene prioridad sobre `matriz.py`.
- `load_matriz_csv.py` — parsea `matriz_gastos.csv` cuando existe.
- `rrhh_sueldos.py` — Sueldos y CS por área y mes (RRHH).
- `allocation_final.py` — motor principal. Lee `quant_accounting.json` (no
  versionado — son datos reales de sueldos/proveedores, se genera aparte
  parseando el export de contabilidad) y calcula el gasto final por área.
- `quant_inversion.py` — **aparte del motor de asignación** (no se reparte
  por área). Datos del informe de IT sobre la inversión en hardware/servicios
  de Quant (Ene-Ago 2026) — se actualiza reemplazando el archivo entero cada
  vez que IT pasa un informe nuevo, no hay fuente en vivo para esto.

No se versiona ningún archivo con datos de proveedores/sueldos en el detalle
transaccional (`quant_accounting.json`) — solo los criterios y los totales
agregados por área que ya están en `rrhh_sueldos.py`.
