# Buscador de Gastos — Neix S.A.

Buscador interno que responde preguntas sobre los gastos de Neix consultando en vivo el Google Sheet "Resultados por área 2026". Es una página **100% estática, sin backend ni API externa de ningún tipo**: los datos se cargan y se buscan enteramente en el navegador. No hay chat en lenguaje natural — es una interfaz de filtros (elegís qué querés buscar, completás los campos, apretás "Buscar").

## Estructura

```
index.html      → toda la app (HTML+CSS+JS, un solo archivo, sin build ni dependencias propias)
```

No hay carpeta `api/`, ni variables de entorno, ni servicio de terceros que configurar (más allá de las hojas de Google Sheets publicadas como CSV). Se puede abrir `index.html` directo en un navegador, o servirlo desde cualquier hosting estático (Vercel, GitHub Pages, Netlify, o un simple `python -m http.server`).

## Fuente de datos: "Resultados por área 2026"

El archivo es un Google Sheet con varias familias de hojas (confirmado inspeccionando el archivo real vía Google Drive, no una suposición):

- **"Gastos MM,26"** (una por mes, ej. "Gastos 05,26" para mayo). Mayor contable: cada cuenta arranca con una fila `Cta: <código> <nombre>` con su saldo inicial, sigue con los movimientos del período (columnas **CUENTA, FECHA, ORDEN, CONCEPTO, DEBE, HABER, SALDO** — el proveedor viene como parte del texto libre de CONCEPTO, ej. "COMPRAS TANOIRA CASSAGN 2-42311 SERV PROFESIONALE") y termina con una fila "TOTALES DEL PERIODO".
- **Resultados/rentabilidad por área** (una por mes: ENERO..MAYO) y una hoja **CONSOLIDADO** con el acumulado del período. Una fila por rubro (Facturación Bruta, Gastos Directos, Gastos Indirectos, y decenas de sub-rubros como "Sueldos Mesa" o "Comisiones Productores") y una columna por área: **Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N**, más columnas de Total y Notas.
- **Tablas mensuales de gastos**: "Gastos fijos" (proveedores recurrentes como estudios contables/legales), "Clasificación de gastos" (gastos etiquetados Fijo/Variable) y "Capital N" (facturación/gastos/resultado de Cap N). Una fila por rubro/proveedor y una columna por mes (Enero..Mayo).
- **"Sueldos y CS"**: un mini-bloque por mes (ENERO, FEBRERO, ...) con sueldo bruto, costo laboral, plus, total y % por departamento (Mesa, Banca Privada, Banca Corporativa, Middle Office, Operaciones, Administración, RRHH, Tecnología, General, Marketing, Performance).
- **"Resultados"** (matriz anual por cuenta contable, Enero a Diciembre) y **"Matriz de gastos"**: su estructura interna no está completamente mapeada, así que se cargan como grilla genérica (header + filas) para poder buscarlas por texto sin forzar un parseo específico.

La app no le impone una clasificación fija a las hojas de resultados (no calcula "ingresos/egresos/resultado" como categorías cerradas): guarda cada fila tal cual está en el sheet para poder buscar por rubro y devolver el dato exacto con su fuente.

## 1. Publicar las hojas de Google Sheets como CSV

Para cada pestaña que se quiera usar:

1. En Google Sheets: **Archivo → Compartir → Publicar en la Web**.
2. Elegir la pestaña específica y formato **CSV**.
3. Publicar. Vas a obtener una URL como:

   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/pub?gid=44234235&single=true&output=csv
   ```

4. El `gid` es el identificador de cada pestaña — se puede ver en la URL del navegador al hacer click en la pestaña dentro de Google Sheets normal (no la publicada).

## 2. Configuración en `index.html`

El bloque `CONFIG` (cerca de la línea 300) ya tiene los gids reales de las 17 pestañas configuradas:

```js
const CONFIG = {
  csvUrlTemplate: 'https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid={GID}&single=true&output=csv',
  gids: {
    gastos: { '01': '504407038', '02': '1383245355', /* ... */ },
    resultados: { consolidado: '820949426', enero: '226754153', /* ... */ },
    tablasMensuales: { gastosFijos: '1167018877', clasificacionGastos: '2122908998', capitalN: '314640513' },
    sueldosYCS: '987036881',
    hojasCrudas: { resultados: '1908736161', matrizGastos: '44234235' },
  },
};
```

Estos gids no pudieron verificarse en vivo (el entorno donde se armó/actualizó esta app no tiene salida de red hacia `docs.google.com`) — antes de usar en producción, abrí la app, andá a la pestaña **"Hojas cargadas"** y confirmá que los montos coinciden con el sheet real.

- `gids.resultados.consolidado` es la hoja con los totales acumulados del período completo (no es un mes puntual) — se expone como el pseudo-mes especial **"CONSOLIDADO"** (también acepta "acumulado" o "total").
- A medida que se agreguen meses nuevos (Junio, Julio, ...), agregar una entrada más en `gids.gastos` y en `gids.resultados` con el gid de esa pestaña, y publicarla igual que las demás. También conviene sumar la opción correspondiente en los `<select>` de mes de `index.html` (buscar `<option value="enero">Enero</option>` y agregar una línea al lado por cada `<select>`).
- Si un gid queda con el placeholder (`REEMPLAZAR_...`), la app simplemente no va a cargar esa hoja y lo va a mostrar en el tooltip del estado (arriba a la derecha) — no rompe nada, pero esa hoja no estará disponible hasta completarla.

### Sobre el parseo

Los parsers dentro de `index.html` son adaptativos (detectan encabezados por nombre de columna, no por posición fija) y fueron probados contra datos sintéticos que imitan la estructura real:

- `parseGastosLedger`: detecta CUENTA/CONCEPTO (tolera encabezados espaciados letra por letra, ej. "C U E N T A"), sigue el contexto de cuenta a través de las filas "Cta: ...", ignora saldo inicial y "TOTALES DEL PERIODO".
- `parseResultadosHoja`: detecta ≥2 columnas de área (Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N) y guarda cada fila con su label, valores por área, total y notas.
- `parseTablaMensual`: detecta ≥2 columnas de mes; usa la primera columna como label y cualquier columna intermedia (antes del primer mes) como tag (ej. Fijo/Variable en "Clasificación de gastos").
- `parseSueldosPorMes`: detecta bloques que arrancan con una fila "<MES> | SUELDO BRUTO | COSTO LABORAL | PLUS | TOTAL | %" y acumula las filas de departamento hasta el próximo bloque.
- `parseHojaCruda`: fallback genérico para "Resultados" y "Matriz de gastos" — toma la primera fila no vacía como encabezado y arma un objeto por fila, sin imponer semántica.

Si la estructura real de alguna pestaña difiere de esto, estas funciones son las únicas que dependen del layout exacto del sheet.

## 3. Deploy

No hace falta nada especial: es un único archivo HTML estático. Algunas opciones:

- **Vercel / Netlify**: conectar el repo, listo — detectan `index.html` automáticamente, no hace falta configurar nada más (no hay funciones serverless ni variables de entorno).
- **GitHub Pages**: activarlo en la configuración del repo apuntando a la rama/carpeta donde está `index.html`.
- **Local**: `open index.html` directo, o `python3 -m http.server` y entrar a `localhost:8000`.

Cualquiera de estas opciones funciona igual porque no hay nada del lado del servidor — todo el fetch de los CSVs y toda la búsqueda pasan en el navegador de quien lo abre.

## Cómo funciona

1. Al cargar la página, `index.html` hace fetch de cada CSV publicado (los 17 gids de `CONFIG`) y los parsea con PapaParse (vía CDN) en memoria — no hay backend de datos, todo vive en el navegador de cada sesión.
2. La interfaz tiene 6 pestañas, una por tipo de búsqueda: **Gastos** (mayor contable), **Resultados por área**, **Rubros mensuales** (Gastos fijos/Clasificación/Capital N), **Sueldos y CS**, **Búsqueda general** (fallback sobre las hojas "Resultados" y "Matriz de gastos") y **Hojas cargadas** (qué se cargó realmente).
3. Cada pestaña tiene un formulario simple (texto a buscar +, según el caso, un `<select>` de mes/hoja). Al enviarlo, se llama directo a la función de búsqueda correspondiente (`toolBuscarGasto`, `toolBuscarResultado`, `toolBuscarRubroMensual`, `toolBuscarSueldos`, `toolBuscarEnHojaCruda`) — coincidencia de texto parcial, sin distinguir mayúsculas/acentos.
4. El resultado se muestra como una lista de "cards" (una por coincidencia) con todos los campos relevantes ya formateados en pesos argentinos, más el total cuando corresponde. Si no hay coincidencias, se muestra un mensaje explícito en vez de inventar un dato.

## Historial

Este proyecto reemplazó una versión anterior con chat en lenguaje natural (primero con la API de Claude, después con la de Google Gemini como alternativa gratuita). Se sacó el LLM del medio por completo para no depender de ninguna API key ni de configuración de facturación — toda la lógica de búsqueda que antes usaban esas tools quedó intacta, solo cambió cómo se invoca (formularios en vez de una IA interpretando la pregunta).
