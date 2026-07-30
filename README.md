# Asistente de Gastos — Neix S.A.

Chatbot interno que responde preguntas sobre los gastos de Neix consultando en vivo el Google Sheet "Resultados por área 2026". El modelo de IA corre **100% en el navegador** (vía [WebLLM](https://github.com/mlc-ai/web-llm) + WebGPU): no hay API externa, no hay backend, no hay API key que configurar ni cuenta que crear. El modelo interpreta la pregunta e invoca funciones que corren en el propio navegador contra los datos ya parseados del CSV (nunca se le manda el Excel completo en el prompt).

## Estructura

```
index.html      → toda la app (HTML+CSS+JS, un solo archivo, sin build ni backend)
```

No hay carpeta `api/` ni variables de entorno: es un sitio 100% estático. Se puede servir desde cualquier hosting estático (Vercel, Netlify, GitHub Pages) o abrir localmente.

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

## 3. El modelo de IA (WebLLM, sin API)

No hace falta ninguna key ni cuenta. `index.html` carga [WebLLM](https://github.com/mlc-ai/web-llm) desde un CDN (`https://esm.run/@mlc-ai/web-llm`) con `import()` dinámico, y corre el modelo `Llama-3.2-3B-Instruct-q4f32_1-MLC` enteramente en el navegador vía WebGPU.

- **Requiere un navegador con WebGPU** (Chrome/Edge recientes; Safari/Firefox tienen soporte parcial o nulo según versión).
- **La primera vez** que se abre la página, el navegador descarga los pesos del modelo (unos ~2 GB) desde Hugging Face — se ve una barra de progreso arriba del chat mientras tanto. Después queda cacheado por el navegador y las siguientes visitas arrancan rápido.
- **Toda la inferencia es local**: nada de lo que se pregunta ni de los datos financieros sale de la computadora de quien lo usa.
- Para cambiar de modelo (uno más grande/preciso pero más pesado, o más chico/liviano pero menos preciso), basta con cambiar el valor de `WEBLLM_MODEL_ID` en `index.html` por otro id de la lista de modelos soportados por WebLLM (`prebuiltAppConfig.model_list` en su repo).

### Cómo se invocan las tools sin function calling nativo

A diferencia de Gemini/Claude, no hay una API de "tool use" estructurada para modelos corriendo localmente en WebLLM del tamaño que usamos acá. En su lugar se usa un esquema tipo ReAct por prompt:

1. El system prompt le describe al modelo las 6 tools disponibles (`buscar_gasto`, `buscar_resultado`, `buscar_rubro_mensual`, `buscar_sueldos`, `buscar_en_hoja_cruda`, `meses_disponibles`) y le pide que, si necesita una, responda con un JSON de una sola línea: `{"tool": "...", "args": {...}}`.
2. El frontend detecta ese JSON en la respuesta del modelo (`parseToolCall`), ejecuta la función real correspondiente contra los datos ya cargados, y le manda el resultado de vuelta al modelo como un mensaje de usuario que arranca con `Resultado de la tool "...":`.
3. El modelo responde entonces en texto plano con la respuesta final. Ese ida y vuelta interno (el JSON pedido y el resultado) se guarda en el historial pero se marca `hidden: true` para no mostrarlo en el chat — solo se ve la pregunta y la respuesta final.
4. Se acotan los rounds de tool-use a 4 por turno (`MAX_TOOL_ROUNDS`) para no quedar en loop si el modelo insiste en pedir tools.

Este esquema es más frágil que el function calling nativo de un modelo grande en la nube: un modelo de 3B parámetros puede a veces no respetar el formato JSON exacto, inventar un nombre de tool que no existe, o directamente no darse cuenta de que necesita una tool. El código tolera bastante (busca cualquier `{...}` en el texto, no exige que sea *todo* el mensaje), pero no es infalible — si el chat responde raro, probá reformular la pregunta de forma más directa (ej. "buscá gastos de Tanoira en mayo" en vez de una pregunta larga y ambigua).

## Deploy

Es un archivo estático, ninguna configuración especial:

- **Vercel / Netlify**: conectar el repo, listo.
- **GitHub Pages**: activarlo apuntando a `index.html`.
- **Local**: abrir el archivo directo, o `python3 -m http.server` y entrar a `localhost:8000`.

## Cómo funciona

1. Al cargar la página, `index.html` hace fetch de cada CSV publicado (los 17 gids de `CONFIG`) y los parsea con PapaParse (vía CDN) en memoria.
2. En paralelo, descarga (o recupera de caché) el modelo WebLLM y lo inicializa — se ve el progreso en una barra arriba del chat. Hasta que esto termina, la caja de texto queda deshabilitada.
3. El usuario escribe una pregunta. Se manda todo el historial + el system prompt al modelo local (`engine.chat.completions.create`).
4. Si el modelo pide una tool (JSON `{"tool": ..., "args": ...}`), se ejecuta la función real (`buscar_gasto`, etc.) contra los datos ya cargados, y el resultado se le devuelve al modelo para que arme la respuesta final.
5. La respuesta final se muestra en el chat. El historial se guarda en `localStorage` (clave `neix-gastos-chat-history-v3`, sin login, uso personal).

**Nota:** este entorno no tiene salida de red hacia el CDN de WebLLM ni GPU, así que no se pudo probar la carga real del modelo ni la calidad de sus respuestas — se verificó toda la lógica (el loop de tool-use, el parseo del JSON, qué se guarda/oculta en el historial, que la UI no tire errores) con un motor simulado que imita la forma de la respuesta real de WebLLM. Antes de darlo por andando, abrilo en Chrome o Edge, esperá a que la barra de progreso termine, y probá una pregunta simple.
