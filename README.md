# Asistente de Gastos — Neix S.A.

Chatbot interno que responde preguntas sobre los gastos de Neix consultando en vivo el Google Sheet "Resultados por área 2026". Usa la API de Claude con tool use: el modelo interpreta la pregunta e invoca funciones que corren en el navegador contra los datos ya parseados del CSV (nunca se le manda el Excel completo en el prompt).

## Estructura

```
index.html      → interfaz de chat completa (HTML+CSS+JS, un solo archivo)
api/chat.js      → función serverless de Vercel que hace de proxy a la API de Claude
                   (guarda la API key del lado del servidor, nunca en el browser)
```

## Fuente de datos: "Resultados por área 2026"

El archivo es un Google Sheet con varias familias de hojas (confirmado inspeccionando el archivo real vía Google Drive, no una suposición):

- **"Gastos MM,26"** (una por mes, ej. "Gastos 05,26" para mayo). Mayor contable: cada cuenta arranca con una fila `Cta: <código> <nombre>` con su saldo inicial, sigue con los movimientos del período (columnas **CUENTA, FECHA, ORDEN, CONCEPTO, DEBE, HABER, SALDO** — el proveedor viene como parte del texto libre de CONCEPTO, ej. "COMPRAS TANOIRA CASSAGN 2-42311 SERV PROFESIONALE") y termina con una fila "TOTALES DEL PERIODO".
- **Resultados/rentabilidad por área** (una por mes: ENERO..MAYO) y una hoja **CONSOLIDADO** con el acumulado del período. Una fila por rubro (Facturación Bruta, Gastos Directos, Gastos Indirectos, y decenas de sub-rubros como "Sueldos Mesa" o "Comisiones Productores") y una columna por área: **Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N**, más columnas de Total y Notas.
- **Tablas mensuales de gastos**: "Gastos fijos" (proveedores recurrentes como estudios contables/legales), "Clasificación de gastos" (gastos etiquetados Fijo/Variable) y "Capital N" (facturación/gastos/resultado de Cap N). Una fila por rubro/proveedor y una columna por mes (Enero..Mayo).
- **"Sueldos y CS"**: un mini-bloque por mes (ENERO, FEBRERO, ...) con sueldo bruto, costo laboral, plus, total y % por departamento (Mesa, Banca Privada, Banca Corporativa, Middle Office, Operaciones, Administración, RRHH, Tecnología, General, Marketing, Performance).
- **"Resultados"** (matriz anual por cuenta contable, Enero a Diciembre) y **"Matriz de gastos"**: su estructura interna no está completamente mapeada, así que se cargan como grilla genérica (header + filas) para poder buscarlas por texto sin forzar un parseo específico.

El asistente no le impone una clasificación fija a las hojas de resultados (no calcula "ingresos/egresos/resultado" como categorías cerradas): guarda cada fila tal cual está en el sheet para poder buscar por rubro y devolver el dato exacto con su fuente.

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
  apiEndpoint: '/api/chat',
  model: 'claude-sonnet-5',
};
```

Estos gids no pudieron verificarse en vivo (el entorno donde se armó/actualizó esta app no tiene salida de red hacia `docs.google.com`) — antes de usar en producción, abrí la app, mandá una pregunta simple ("¿qué meses hay disponibles?") y confirmá que los montos coinciden con el sheet real.

- `gids.resultados.consolidado` es la hoja con los totales acumulados del período completo (no es un mes puntual) — el asistente la expone como el pseudo-mes especial **"CONSOLIDADO"** (también acepta "acumulado" o "total").
- A medida que se agreguen meses nuevos (Junio, Julio, ...), agregar una entrada más en `gids.gastos` y en `gids.resultados` con el gid de esa pestaña, y publicarla igual que las demás.
- Si un gid queda con el placeholder (`REEMPLAZAR_...`), el asistente simplemente no va a cargar esa hoja y lo va a mostrar en el tooltip del estado — no rompe nada, pero esa hoja no estará disponible hasta completarla.

### Sobre el parseo

Los parsers dentro de `index.html` son adaptativos (detectan encabezados por nombre de columna, no por posición fija) y fueron probados contra datos sintéticos que imitan la estructura real:

- `parseGastosLedger`: detecta CUENTA/CONCEPTO (tolera encabezados espaciados letra por letra, ej. "C U E N T A"), sigue el contexto de cuenta a través de las filas "Cta: ...", ignora saldo inicial y "TOTALES DEL PERIODO".
- `parseResultadosHoja`: detecta ≥2 columnas de área (Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N) y guarda cada fila con su label, valores por área, total y notas.
- `parseTablaMensual`: detecta ≥2 columnas de mes; usa la primera columna como label y cualquier columna intermedia (antes del primer mes) como tag (ej. Fijo/Variable en "Clasificación de gastos").
- `parseSueldosPorMes`: detecta bloques que arrancan con una fila "<MES> | SUELDO BRUTO | COSTO LABORAL | PLUS | TOTAL | %" y acumula las filas de departamento hasta el próximo bloque.
- `parseHojaCruda`: fallback genérico para "Resultados" y "Matriz de gastos" — toma la primera fila no vacía como encabezado y arma un objeto por fila, sin imponer semántica.

Si la estructura real de alguna pestaña difiere de esto, estas funciones son las únicas que dependen del layout exacto del sheet.

## 3. Configurar la API key de Claude

El navegador **nunca** llama directo a `api.anthropic.com` — llama a `/api/chat`, que corre en el servidor de Vercel y ahí sí usa la key. Esto evita exponer la API key en el código fuente que cualquiera puede ver en el navegador.

En Vercel: **Project Settings → Environment Variables** → agregar:

```
ANTHROPIC_API_KEY = sk-ant-...
```

Redeployar después de agregarla.

## 4. Deploy en Vercel

Igual que tus otros proyectos: conectar el repo a Vercel (o `vercel --prod` desde la CLI). No hace falta configuración adicional — Vercel detecta automáticamente `index.html` como estático y `api/chat.js` como función serverless.

Para probar en local con `vercel dev` (requiere `vercel login` y tener `ANTHROPIC_API_KEY` en un `.env.local`):

```bash
npm i -g vercel
vercel dev
```

## Cómo funciona

1. Al cargar la página, `index.html` hace fetch de cada CSV publicado y los parsea con PapaParse (vía CDN) en memoria — no hay backend de datos, todo vive en el navegador de cada sesión.
2. El usuario escribe una pregunta. El frontend manda el historial de la conversación + la lista de tools a `/api/chat`.
3. `/api/chat` reenvía la llamada a `api.anthropic.com/v1/messages` con el modelo `claude-sonnet-5`, agregando la API key del servidor.
4. Si Claude decide invocar una tool (`buscar_gasto`, `buscar_resultado`, `buscar_rubro_mensual`, `buscar_sueldos`, `buscar_en_hoja_cruda`, `meses_disponibles`), la función correspondiente corre **en el navegador** contra los datos ya cargados, y el resultado se le manda de vuelta a Claude como `tool_result`.
5. Este loop se repite hasta que Claude responde con texto final, que se muestra en el chat.
6. El historial de la conversación se guarda en `localStorage` del navegador (sin login, uso personal).

El system prompt le exige a Claude que solo responda con datos verificables por las tools, que use la tool más específica para cada tipo de consulta (y `buscar_en_hoja_cruda` solo como último recurso), que cite siempre la hoja y el mes de cada dato, y que diga explícitamente cuando no encuentra algo, en vez de inventar montos.
