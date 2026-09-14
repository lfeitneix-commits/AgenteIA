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
permisos que se pueda resolver desde acá. Opciones reales:
1. El usuario pega el CSV actualizado en el chat cuando haga falta (lo que se
   viene haciendo).
2. El usuario sube/actualiza un archivo `centro-costos/matriz_gastos.csv` en
   el repo (a mano, o con algo automático de su lado tipo Apps Script + API de
   GitHub) — si ese archivo existe, usarlo en vez de `matriz.py` y avisar con
   qué fecha de commit se está trabajando.

Snapshot actual (última vez que el usuario lo pasó): `matriz.py`, con
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

| Área de staff | Mesa | FAs+Mza | Banca Corp. | Banca Priv. | Criterio |
|---|---|---|---|---|---|
| Back Office | 60% | 30% | 5% | 5% | Operaciones del área / Operaciones totales |
| RRHH | 58% | 14% | 17% | 11% | Headcount del área / Headcount total |
| IT | 58% | 14% | 17% | 11% | Headcount del área / Headcount total |
| Administración | 58% | 14% | 17% | 11% | Headcount del área / Headcount total |
| MKTG | 16% | 59% | 12% | 14% | 75% área comercial + 25% headcount |
| Performance | 8% | 57% | 16% | 19% | 75% equipo comercial + 25% desarrollos del área |
| General | — | — | — | — | **Sin fila propia**, default headcount (58/14/17/11) |

Fuente de los % de headcount (36 empleados en las 4 áreas de negocio): Mesa 21,
FAs+Mza 5, Banca Corporativa 6, Banca Privada 4 → 21/36=58%, 5/36=14%,
6/36=17%, 4/36=11%. Comitentes activos (para las filas "Comitentes del
área/Comitentes totales"): Mesa 22, FAs+Mza 1.205, Banca Corporativa 159, Banca
Privada 235 → 1%/74%/10%/14%. Facturación promedio Ene-Jul (para filas de
Impuestos): Mesa 60%, FAs 34%, BC 4%, BP 2%. **Estos números vienen de la hoja
"CÁLCULOS AUX" al pie de la Matriz de gastos — si el usuario manda una Matriz
nueva, recalcular estos % de ahí, no asumir que siguen iguales.**

⚠️ Estos son los valores del snapshot de `matriz.py` (`SNAPSHOT_DATE`), no un
dato en vivo — ver §2.2.

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
- [ ] Preguntarle al usuario si quiere armar alguna forma de sincronizar
      `matriz_gastos.csv` al repo automáticamente (Apps Script + API de
      GitHub, o similar) para no depender de pegar el CSV a mano cada vez —
      ver §2.2.

Actualizar este checklist a medida que se resuelva o aparezca algo nuevo — no
dejarlo desactualizado.
