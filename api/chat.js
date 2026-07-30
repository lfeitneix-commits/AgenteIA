// Proxy serverless para la API de Claude (Vercel Node function).
// Mantiene la API key del lado del servidor: el navegador nunca la ve.
// El cliente (index.html) manda { system, messages, tools } y este endpoint
// solo reenvía la llamada a Anthropic con la API key tomada de las env vars de Vercel.

const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';
const DEFAULT_MODEL = 'claude-sonnet-5';
const MAX_TOKENS = 1536;

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    res.status(500).json({
      error: 'ANTHROPIC_API_KEY no está configurada en el proyecto de Vercel. Agregala en Settings > Environment Variables y volvé a deployar.',
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

  const { system, messages, tools, model } = body || {};

  if (!Array.isArray(messages) || messages.length === 0) {
    res.status(400).json({ error: 'Falta el array de "messages".' });
    return;
  }

  try {
    const upstream = await fetch(ANTHROPIC_API_URL, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: model || DEFAULT_MODEL,
        max_tokens: MAX_TOKENS,
        system,
        messages,
        tools,
      }),
    });

    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({
      error: 'No se pudo contactar a la API de Claude.',
      detail: String(err && err.message ? err.message : err),
    });
  }
};
