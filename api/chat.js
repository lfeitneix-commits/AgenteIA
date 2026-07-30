// Proxy serverless para la API de Google Gemini (Vercel Node function).
// Mantiene la API key del lado del servidor: el navegador nunca la ve.
// El cliente (index.html) manda { systemInstruction, contents, tools, model }
// (formato Gemini) y este endpoint solo reenvía la llamada a
// generativelanguage.googleapis.com con la API key tomada de las env vars de Vercel.

const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models';
const DEFAULT_MODEL = 'gemini-2.5-flash';
const MAX_OUTPUT_TOKENS = 2048;

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    res.status(500).json({
      error: 'GEMINI_API_KEY no está configurada en el proyecto de Vercel. Agregala en Settings > Environment Variables y volvé a deployar.',
    });
    return;
  }

  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch (e) {
      res.status(400).json({ error: 'Body inválido, se esperaba JSON.' });
      return;
    }
  }

  const { systemInstruction, contents, tools, model } = body || {};

  if (!Array.isArray(contents) || contents.length === 0) {
    res.status(400).json({ error: 'Falta el array de "contents".' });
    return;
  }

  const modelName = model || DEFAULT_MODEL;
  const url = GEMINI_API_URL + '/' + encodeURIComponent(modelName) + ':generateContent';

  try {
    const upstream = await fetch(url, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-goog-api-key': apiKey,
      },
      body: JSON.stringify({
        contents,
        tools,
        systemInstruction: systemInstruction ? { parts: [{ text: systemInstruction }] } : undefined,
        generationConfig: { maxOutputTokens: MAX_OUTPUT_TOKENS },
      }),
    });

    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({
      error: 'No se pudo contactar a la API de Gemini.',
      detail: String(err && err.message ? err.message : err),
    });
  }
};
