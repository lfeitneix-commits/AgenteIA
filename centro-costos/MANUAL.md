# Centro de Costos Neix — Manual de referencia

Este documento es la fuente de verdad para el proceso de asignación de gastos por
área de Neix. Está pensado para que **Claude lo lea al retomar este trabajo en
cualquier sesión futura** y sepa exactamente qué hacer cuando el usuario dice
cosas como "te paso el dato de los sueldos" o "actualicé la matriz" — sin tener
que re-derivar el criterio desde cero.

Si el usuario pega datos nuevos (sueldos, roster, Matriz de gastos, export de
contabilidad), la tarea por defecto es: **actualizar los archivos de este
directorio** (`roster.py`, `matriz.py`, `rrhh_sueldos.py`) con el dato nuevo,
re-correr `allocation_final.py`, y actualizar este `MANUAL.md` si el dato nuevo
cambia algún criterio (no solo un número).

> ⚠️ **Los % de la Matriz, el roster y los sueldos NO son datos en vivo.**
> Este entorno no tiene salida de red a Google Sheets (confirmado con curl y
> con la tool de fetch web — bloqueado por política de red de la
> organización), así que todo lo que está en `matriz.py`/`roster.py`/
> `rrhh_sueldos.py` es una **foto de un momento dado** (ver `SNAPSHOT_DATE` en
> cada archivo), no la fuente viva. **Antes de usar estos números para
> cualquier cálculo que le importe al usuario de verdad (no una prueba),
> preguntar explícitamente si siguen vigentes o si hay una versión más
> nueva.** No asumir nunca que "como ya lo tengo cargado, ya está" — la Matriz
> es una hoja que el usuario edita directamente y puede haber cambiado sin que
> nadie me avise.

## 1. Objetivo

Reproducir el proceso manual que el usuario hace en Excel: tomar los gastos
reales de contabilidad de un período y repartirlos entre las 4 áreas de negocio
(**Mesa, Banca Corporativa, Banca Privada, FAs** — FAs incluye Productores y
Mendoza), pasando primero por las áreas internas de staff cuando corresponde
(**Back Office, IT, RRHH, Administración, Marketing, Performance**).

## 2. Las 3 fuentes de datos

### 2.1 Export de contabilidad ("Tablero_Gastos_NEIX")
HTML que la contadora exporta y se vuelve a subir cada tanto. Contiene
`var D = {...}` con una entrada por cuenta contable. Extraer con
`re.search(r'var D=(\{.*?\});', content, re.DOTALL)` y guardar como JSON
(`quant_accounting.json` en el scratchpad de la sesión — no se commitea al repo
por ser datos reales de proveedores/sueldos; si el usuario sube un export nuevo,
volver a generarlo ahí).

Campos por cuenta: `n` (nombre), `r` (rubro), `s` (sector — puede venir
tageado, o "Sin asignar"/"Oficina Neix"/"Oficina Mendoza"), `e` (Erogable /
"No erogable contable" / "Valuación..." — ver §5), `f` (Fijo/Variable,
borrador), `m` (totales por mes, `{"1": monto, ...}`, 1=enero), `d` (detalle
transaccional: `[fecha, comprobante, descripción, monto]`).

Convención de sufijos en el código contable: `.01`=Mesa, `.02`=BC, `.04`=BP,
`.05`=Back, `.06`=IT, `.07`=Adm, `.08`=RRHH, `.09`=MKTG, `.10`="Neix" (catch-all
sin discriminar), `.11`=Mendoza.

### 2.2 Matriz de gastos (Google Sheet, gid `44234235`)
El mismo gid que ya usa `dashboard-rentabilidad` (`MATRIZ_GID` en su
`index.html`). Una fila por cuenta, % por columna (Mesa, FAs+Mza, Banca
Corporativa, Banca Privada) + TOTAL + Detalle (explica el criterio). Es la
fuente de verdad para todo lo que no viene ya separado por área en la cuenta
contable.

**URL exacta de la pestaña** (mismo `BASE` + gid que usa `dashboard-rentabilidad`
en su `index.html`, pestaña "Matriz de gastos" del Google Sheet "Resultados por
área 2026"):
```
https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4gdsYZTOZlI1jllNuQ2mBWBjabHVL5vJ9dPGVso5lnUVOOuRsQ_xhKVfa0XYDlKpPGr61FUnO3kvy/pub?output=csv&gid=44234235
```
Esta es LA fuente — siempre que se pueda, leer de acá (o de un archivo que se
haya generado a partir de acá), nunca de una copia vieja porque "ya la
tenemos cargada".

**No se puede leer en vivo desde este entorno.** Se probó fetch directo (curl) y con la tool de
fetch web — las dos veces bloqueado por la política de red de la
organización (`EGRESS_BLOCKED` a `docs.google.com`). No es un límite de
permisos que se pueda resolver desde acá.

**Solución implementada:** el usuario tiene un script de Google Apps Script
(`sync_matriz_to_github.gs`, entregado por chat, no vive en este repo porque
corre del lado de Google Sheets) que sincroniza la pestaña "Matriz de gastos"
a `centro-costos/matriz_gastos.csv` en este repo cada vez que edita la hoja.
`allocation_final.py` (vía `load_matriz_csv.py`) **prefiere siempre ese
archivo si existe** — solo cae al snapshot hardcodeado de `matriz.py` si
`matriz_gastos.csv` todavía no existe en el repo. El script imprime cuál de
los dos usó en cada corrida.

Aun así, **`matriz_gastos.csv` sigue siendo un archivo del repo, no la hoja en
vivo** — se actualiza recién cuando el usuario edita el Sheet Y el Apps
Script corre. Si pasó mucho tiempo sin commits nuevos en ese archivo, o el
usuario dice que cambió algo y el archivo no refleja eso, sospechar que el
Apps Script no está andando y confirmar con el usuario en vez de asumir que
está al día.

Snapshot de respaldo (si `matriz_gastos.csv` no existe): `matriz.py`, con
`SNAPSHOT_DATE` al principio del archivo. **Tratarlo como desactualizado por
default** — confirmar con el usuario antes de usarlo para algo real.

### 2.3 Roster de empleados + Sueldos y CS (RRHH)
El roster (`roster.py`) mapea nombre de persona → área. Sirve para triagear
transacciones de las cuentas "*Neix" que mencionan a alguien por nombre. Los
nombres en las descripciones de contabilidad vienen **truncados/apodados**
("CUOTA GERMAN JURA" = Germán Jurado, "PILAR BOTAZ" = Pilar Bottazzi, "FACU
LINA" = Facundo Linares) — el matching exacto de nombre completo no alcanza,
hace falta normalizar (sin acentos, lower) y matchear por apellido/prefijo
(ver `roster.py::name_variants`).

`rrhh_sueldos.py` trae el total mensual por área que pasa RRHH para Sueldos y
CS — porque en contabilidad las cuentas "Sueldos", "Cargas Sociales" y
"Vacaciones" vienen **100% sin discriminar** (confirmado por el usuario: "no lo
vamos a discriminar, va todo junto como un globo"). Se reparten aplicando el %
real de RRHH mes a mes.

⚠️ El roster y los sueldos también son snapshots (mismo problema de §2.2: sin
acceso a la fuente viva). El roster puede quedar desactualizado por altas/
bajas/cambios de área (ya pasó con Pedro Perez Marexiano — ver `roster.py`), y
`rrhh_sueldos.py` solo tiene Enero-Junio. Confirmar con el usuario antes de
asumir que están al día.

## 3. Reglas de asignación por cuenta

Regla general de resolución, en este orden:

1. **No erogable** (§5) → excluir.
2. **Mesa-neto** (§6) → 100% Mesa.
3. **Sector ya tageado a un área de negocio** (Mesa/Banca Corporativa/Banca
   Privada/Productores/Oficina Mendoza) → directo a esa área (Productores y
   Oficina Mendoza → FAs).
4. **Sufijo de área interna** (Back/IT/Adm/RRHH/MKTG/Performance/General) en
   una cuenta de la familia Suscripciones/Sueldos y CS/Hardware/Viáticos/Serv.
   Contratados/Representación/Honorarios/Capacitación → aplicar la fila de esa
   área interna en la "primera matriz" (§4). "General" no tiene fila propia →
   usar el default de headcount (58/14/17/11) y flaggear como supuesto.
5. **Cuenta con fila propia en la Matriz de gastos** (por nombre, normalizado)
   → aplicar ese %.
6. **Cuenta catch-all "*Neix"** → triage especial, ver §7.
7. Si nada de lo anterior aplica → **gap real**, no asignar, preguntar al
   usuario (ver §8 para los gaps ya conocidos).

## 4. "Primera matriz" — reparto por área interna (staff)

Cada área de staff (Back Office, RRHH, IT, Administración, MKTG, Performance)
tiene su propia fila en la Matriz de gastos con el % de reparto hacia las 4
áreas de negocio — algunas por headcount, otras por operaciones/comitentes/
facturación (ver el Detalle de cada fila en la hoja). "General" no tiene fila
propia: usar el default de headcount como supuesto y flaggearlo.

**Los valores puntuales viven solo en `matriz.py` (`PRIMERA_MATRIZ`), no acá.**
Los números concretos no se repiten en este manual a propósito — son un
snapshot (§2.2) y escribirlos en un documento pensado para durar los deja
leerse como un hecho fijo. Para saber el % vigente de cada área, abrir
`matriz.py` y confirmar la fecha de `SNAPSHOT_DATE` antes de usarlo.

## 5. Cuentas NO erogables — excluir siempre

Confirmado por el usuario ("NO VAN"): **RECPAM**, **Amortizaciones**,
**Diferencia cambio u$s (Pesos)**, **D/C por Cambio**, **Diferencia de
Redondeo**. Son ajustes contables/valuación, no salida de caja real (`e` ≠
"Erogable" en el JSON). También **"Impuesto a las ganancias"** — aunque viene
marcada "Erogable", el usuario confirmó que es una provisión y se excluye.

## 6. Cuentas 100% Mesa, netas de facturación

`Gastos Caja de Valores`, `Gastos A3 Mercados`, `Gastos Byma`, `Gastos Mae`,
`Gastos Caja de Valores Exento`, `Gastos Byma Op. fuera Horario`, `Gtos Alq
Comitentes`, `Intereses Pagados`. Ya vienen descontadas de la facturación de la
mesa (nota "Valor de este mes: x… ya descontado de la facturación de la
mesa").

## 7. Triage de las cuentas catch-all "*Neix"

| Cuenta | Regla | Notas |
|---|---|---|
| Suscripciones Neix | Tecnología y Software (adobe/microsoft/nss/github/slack/digital ocean/lanbot/mailchimp) · Membresías/Regulatorio (byma/cámara de agentes/bolsa de comercio/cfa institute) · resto → default headcount | "Cuota EG"/"Cuota LM" (Esteban Goyheneix, Lucas Mieres — socios/directores) caen acá, en Membresías/Regulatorio |
| Serv. Contratados Neix | Servicios de Oficina (limpieza/alarma/isikawa/star servicios) → % de "Gtos Mant de Oficina" · Administración/Consultoría (interbanking/consultora/gimenez ezequiel) · Petracchi → 100% FAs (viaje, no servicio) · **NUBI/NUBY → excluir, ya está contado en Sueldos** · resto → default headcount | Gimenez Ezequiel confirmado "con dudas" por el usuario — revisar si aparece de nuevo |
| Gtos Hardw y Comp Neix | Sin depto propio → default headcount | — |
| Viaticos y Mov. Neix / Gastos de Viajes Neix | Directo si el roster identifica a la persona (o si la descripción dice "MDZ"/"Mendoza" → FAs) · resto → % de "Movilidad y viajes" (headcount) | "Bauti Lin" = hijo de Facundo Linares → Banca Corporativa |
| Capacit. y Cursos Neix | Directo si el roster identifica a un empleado de área de **negocio** · si es de área de **staff**, por su fila de "primera matriz" · sin persona → default headcount | Agustín Frers (ex-empleado) → Banca Corporativa aunque ya no trabaje ahí |
| Gastos Representacion Neix | Directo si el roster identifica a la persona y es de área de negocio · resto (eventos genéricos) → % de "Representación" (comitentes) | — |
| Hon. Profesionales Neix | % de la fila "Honorarios Profesionales" (headcount) | — |
| Eventos Empresariales | Mismo criterio que Gastos Representacion Neix | — |

## 8. Gaps reales (sin regla en ningún lado, a confirmar con el usuario)

- **Honorarios x Serv Diversos** — la cuenta más grande sin resolver (~$453M
  en Ene-Ago 2026). Preguntar antes de asumir nada.
- **Artículos de Limpieza** (~$2,4M).
- **Telefonia Movil** (~$1,8M) — distinta de "Telefonia e Internet", que sí
  tiene regla.

## 9. Bug de matching a evitar — nombres que no coinciden por texto exacto

Nunca comparar nombres de cuenta entre contabilidad/Matriz/roster con `==`
literal. Normalizar (sin acentos, lower, trim) como mínimo — `allocation_final.py::norm()`
ya lo hace. Además hay diferencias de fondo, no solo de formato, que necesitan
alias explícito (ver `ALIAS_CUENTA` en `allocation_final.py`):

| Contabilidad | Matriz | Motivo |
|---|---|---|
| Telefonia e Internet | Telefonía e Internet | acento |
| Impuestos Municipales, Tasas | Impuestos Municiaples, Tasas | typo en la Matriz |
| Impuestos a los Sellos | Impuesto a los Sellos | singular/plural |
| Gastos Director Titular Autóno... | Gastos Director Titular Autónomo | nombre truncado en el export |
| Merchandising / Pagina Web/Publicidad | Página Web/Publicidad/Merchandising | cuentas separadas vs. fila combinada |
| Gastos Bancarios / Gastos Bancarios 10,5% / Gastos Bancarios Exentos / Int. Desc Bcario | Gastos bancarios | mayúscula + nombres hijos distintos |

## 10. Último resultado calculado (Ene–Ago 2026, referencia)

| Área | Monto | % |
|---|---|---|
| Mesa | $7.054,5M | 58,6% |
| FAs + Mza | $3.530,9M | 29,3% |
| Banca Corporativa | $850,0M | 7,1% |
| Banca Privada | $601,6M | 5,0% |
| **Total** | **$12.037,1M** | 100% |

(No incluye los ~$457M de gaps del §8 ni las cuentas no erogables del §5.)
Sirve como número de referencia — si se vuelve a correr `allocation_final.py`
con datos nuevos y el total se dispara sin explicación, algo cambió en las
fuentes (Matriz, roster, o el export) que hay que revisar antes de confiar en
el resultado nuevo.

Calculado con los snapshots de Matriz/roster/RRHH vigentes en ese momento
(§2.2, §2.3) — no lo presentes como el número "actual" sin antes confirmar que
esos snapshots siguen valiendo.

## 11. Cómo correr esto

```
cd centro-costos/
# 1. Poner el export de contabilidad parseado en quant_accounting.json
#    (parsear el HTML: re.search(r'var D=(\{.*?\});', html, re.DOTALL))
python3 allocation_final.py
```

Imprime el resultado final por área, lo excluido, y todos los flags/supuestos
aplicados (con el monto de cada uno) para poder auditar cualquier número.

## 12. Pendiente de recibir / confirmar (checklist vivo)

- [ ] Sueldos y CS de Julio y Agosto (RRHH) — hoy usan el promedio Ene-Jun.
- [ ] Operaciones por área de Julio/Agosto (el usuario avisó que las va a
      mandar) — para afinar el % de Back Office / Gastos Corresp. Ext. u$s
      (hoy 60/30/5/5, un valor fijo de la Matriz).
- [ ] Definir Honorarios x Serv Diversos, Artículos de Limpieza, Telefonia
      Movil (§8).
- [ ] Confirmar el criterio de "General" en la primera matriz (§4).
- [ ] Confirmar que el usuario instaló y activó `sync_matriz_to_github.gs` en
      el Google Sheet — mientras no esté instalado, `matriz_gastos.csv` no va
      a existir y el motor sigue usando el snapshot de `matriz.py` (ver §2.2).

Actualizar este checklist a medida que se resuelva o aparezca algo nuevo — no
dejarlo desactualizado.
