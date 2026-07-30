# Asistente de Gastos — Neix S.A.

Chatbot interno que responde preguntas sobre los gastos de Neix consultando en vivo los Google Sheets de EERR, Matriz de gastos y Clasificación de gastos. Usa la API de Claude con tool use: el modelo interpreta la pregunta e invoca funciones que corren en el navegador contra los datos ya parseados del CSV (nunca se le manda el Excel completo en el prompt).

## Estructura

```
index.html      → interfaz de chat completa (HTML+CSS+JS, un solo archivo)
api/chat.js      → función serverless de Vercel que hace de proxy a la API de Claude
                   (guarda la API key del lado del servidor, nunca en el browser)
```

## 1. Publicar el Google Sheet como CSV

Para cada hoja que se quiera usar (EERR de cada mes, Matriz de gastos, Clasificación de gastos):

1. En Google Sheets: **Archivo → Compartir → Publicar en la Web**.
2. Elegir la pestaña específica (o "Documento completo") y formato **CSV**.
3. Publicar. Vas a obtener una URL como:

   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/pub?gid=44234235&single=true&output=csv
   ```

4. El `gid` es el identificador de cada pestaña — se puede ver en la URL del navegador al hacer click en la pestaña dentro de Google Sheets normal (no la publicada).

## 2. Configurar `index.html`

Abrir `index.html` y buscar el bloque `CONFIG` (cerca de la línea 260). Completar:

```js
const CONFIG = {
  csvUrlTemplate: 'https://docs.google.com/spreadsheets/d/e/TU_ID_PUBLICADO/pub?gid={GID}&single=true&output=csv',
  gids: {
    matrizGastos: '44234235',
    clasificacionGastos: '2122908998',
    meses: {
      enero: 'GID_DE_ENERO',
      febrero: 'GID_DE_FEBRERO',
      marzo: 'GID_DE_MARZO',
      abril: 'GID_DE_ABRIL',
      mayo: 'GID_DE_MAYO',
      // agregar los meses que se vayan sumando
    },
  },
  apiEndpoint: '/api/chat',
  model: 'claude-sonnet-5',
};
```

- `csvUrlTemplate`: pegar la URL publicada dejando literalmente `{GID}` donde va el número de gid (el código lo reemplaza en cada fetch).
- `gids.matrizGastos` / `gids.clasificacionGastos`: ya vienen con los GID que pasaste (44234235 y 2122908998). Verificar que coincidan con tu sheet.
- `gids.meses`: agregar una entrada por cada hoja mensual de EERR.

Si un gid queda con el placeholder (`REEMPLAZAR_...`), el asistente simplemente no va a cargar esa hoja y lo va a mostrar en el estado de arriba del chat — no rompe nada, pero esa fuente de datos no estará disponible hasta completarla.

### Sobre el formato de las hojas

El parser es adaptativo (detecta encabezados por nombre de columna, no por posición fija), pero asume una estructura razonable:

- **Matriz de gastos**: una columna "Proveedor", opcionalmente "Concepto" y "Área", y o bien columnas "Mes"+"Monto" (formato largo, una fila por pago) o columnas con nombres de mes (Enero, Febrero, ...) con el monto de cada pago en la columna del mes correspondiente (formato ancho).
- **Clasificación de gastos**: filas o columnas con las etiquetas "Fijo"/"Variable"/"Total" cruzadas con los meses.
- **Hojas de EERR**: una fila con label "Ingresos"/"Egresos"/"Resultado" y columnas con los nombres de área (Mesa, Banca Corporativa, Banca Privada, FAs) — o al revés (áreas en filas, ingresos/egresos en columnas se puede adaptar fácilmente, ver `parseEERR` en `index.html`).

Si tu estructura real es distinta, los parsers (`parseMatrizGastos`, `parseClasificacion`, `parseEERR` dentro de `index.html`) están escritos para ser fáciles de ajustar — son las únicas funciones que dependen del layout exacto del sheet.

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
4. Si Claude decide invocar una tool (`buscar_gasto`, `totales_por_area`, `top_proveedores`, `gastos_fijos_variables`, `meses_disponibles`), la función correspondiente corre **en el navegador** contra los datos ya cargados, y el resultado se le manda de vuelta a Claude como `tool_result`.
5. Este loop se repite hasta que Claude responde con texto final, que se muestra en el chat.
6. El historial de la conversación se guarda en `localStorage` del navegador (sin login, uso personal).

El system prompt le exige a Claude que solo responda con datos verificables por las tools y que diga explícitamente cuando no encuentra algo, en vez de inventar montos.

## Botón "Actualizar datos"

Vuelve a hacer fetch de todos los CSV configurados — útil si se acaba de actualizar el Google Sheet y se quiere ver el dato nuevo sin recargar la página.
