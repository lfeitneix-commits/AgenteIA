# Asistente de Gastos — Neix S.A.

Chatbot interno que responde preguntas sobre los gastos de Neix consultando en vivo el Google Sheet "Resultados por área 2026". Usa la API de Claude con tool use: el modelo interpreta la pregunta e invoca funciones que corren en el navegador contra los datos ya parseados del CSV (nunca se le manda el Excel completo en el prompt).

## Estructura

```
index.html      → interfaz de chat completa (HTML+CSS+JS, un solo archivo)
api/chat.js      → función serverless de Vercel que hace de proxy a la API de Claude
                   (guarda la API key del lado del servidor, nunca en el browser)
```

## Fuente de datos: "Resultados por área 2026"

El archivo es un Google Sheet con dos familias de hojas relevantes (confirmado inspeccionando el archivo real, no una suposición):

- **Hojas mensuales de gastos**, llamadas **"Gastos MM,26"** (ej. "Gastos 05,26" para mayo). Son el mayor contable: cada cuenta arranca con una fila `Cta: <código> <nombre>` con su saldo inicial, sigue con los movimientos del período (columnas **CUENTA, FECHA, ORDEN, CONCEPTO, DEBE, HABER, SALDO** — el proveedor viene como parte del texto libre de CONCEPTO, ej. "COMPRAS TANOIRA CASSAGN 2-42311 SERV PROFESIONALE") y termina con una fila "TOTALES DEL PERIODO".
- **Hojas de resultados/rentabilidad por área** (una por mes) y una hoja **CONSOLIDADO** con el acumulado del período. Tienen una fila por rubro (Facturación Bruta, Gastos Directos, Gastos Indirectos, y decenas de sub-rubros como "Sueldos Mesa" o "Comisiones Productores") y una columna por área: **Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N**, más columnas de Total y Notas.

El asistente no le impone una clasificación fija a estas últimas hojas (no calcula "ingresos/egresos/resultado" como categorías cerradas): guarda cada fila tal cual está en el sheet para poder buscar por rubro y devolver el dato exacto con su fuente.

## 1. Publicar las hojas de Google Sheets como CSV

Para cada pestaña que se quiera usar (cada "Gastos MM,26", cada hoja de resultados por área, y CONSOLIDADO):

1. En Google Sheets: **Archivo → Compartir → Publicar en la Web**.
2. Elegir la pestaña específica y formato **CSV**.
3. Publicar. Vas a obtener una URL como:

   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/pub?gid=44234235&single=true&output=csv
   ```

4. El `gid` es el identificador de cada pestaña — se puede ver en la URL del navegador al hacer click en la pestaña dentro de Google Sheets normal (no la publicada).

## 2. Configuración en `index.html`

El bloque `CONFIG` (cerca de la línea 290) tiene esta forma:

```js
const CONFIG = {
  csvUrlTemplate: 'https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid={GID}&single=true&output=csv',
  gids: {
    gastos: {
      '01': 'GID_DE_GASTOS_01,26',
      '02': 'GID_DE_GASTOS_02,26',
      // ... una entrada por cada hoja "Gastos MM,26" publicada
    },
    resultados: {
      consolidado: 'GID_DEL_CONSOLIDADO',
      enero: 'GID_DE_RESULTADOS_ENERO',
      // ... una entrada por cada hoja de resultados/rentabilidad por área
    },
  },
  apiEndpoint: '/api/chat',
  model: 'claude-sonnet-5',
};
```

**Todos los gids de este repo son placeholders (`REEMPLAZAR_...`)** — hay que completarlos a mano publicando cada pestaña real y pegando su gid. No pude verificar gids reales porque el entorno donde armé/actualicé esta app no tiene salida de red hacia `docs.google.com` (solo pude inspeccionar el contenido del archivo vía la integración de Google Drive, no obtener el `gid` de cada pestaña desde ahí).

- `gids.resultados.consolidado` es la hoja con los totales acumulados del período completo (no es un mes puntual) — el asistente la expone como el pseudo-mes especial **"CONSOLIDADO"** (también acepta "acumulado" o "total").
- A medida que se agreguen meses nuevos, agregar una entrada más en `gids.gastos` y en `gids.resultados` con el gid de esa pestaña.
- Si un gid queda con el placeholder (`REEMPLAZAR_...`), el asistente simplemente no va a cargar esa hoja y lo va a mostrar en el tooltip del estado — no rompe nada, pero esa hoja no estará disponible hasta completarla.

### Sobre el parseo

Los parsers (`parseGastosLedger` y `parseResultadosHoja` dentro de `index.html`) son adaptativos (detectan encabezados por nombre de columna, no por posición fija) pero fueron escritos y probados contra la estructura real del archivo:

- `parseGastosLedger`: detecta la fila de encabezado buscando las columnas CUENTA/CONCEPTO (tolera que vengan espaciadas letra por letra, ej. "C U E N T A"), sigue el contexto de cuenta contable a través de las filas "Cta: ...", ignora las filas de saldo inicial y "TOTALES DEL PERIODO", y devuelve solo los movimientos reales.
- `parseResultadosHoja`: detecta la fila de encabezado buscando al menos 2 columnas de área (Mesa, Banca Corporativa, Banca Privada, Middle Office/FAs, Cap N), y guarda cada fila con su label, sus valores por área, el total y las notas.

Si la estructura real de alguna pestaña difiere de esto (headers en otra fila, otras áreas, etc.), estas dos funciones son las únicas que dependen del layout exacto del sheet.

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
4. Si Claude decide invocar una tool (`buscar_gasto`, `buscar_resultado`, `meses_disponibles`), la función correspondiente corre **en el navegador** contra los datos ya cargados, y el resultado se le manda de vuelta a Claude como `tool_result`.
5. Este loop se repite hasta que Claude responde con texto final, que se muestra en el chat.
6. El historial de la conversación se guarda en `localStorage` del navegador (sin login, uso personal).

El system prompt le exige a Claude que solo responda con datos verificables por las tools, que cite siempre la hoja y el mes de cada dato, y que diga explícitamente cuando no encuentra algo, en vez de inventar montos.
