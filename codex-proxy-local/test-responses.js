const fetch = globalThis.fetch || require('node-fetch');
const url = 'http://127.0.0.1:18080/v1/responses';
const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) {
  console.error('Missing OPENAI_API_KEY');
  process.exit(1);
}

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-5.5',
        input: 'hi',
        stream: false,
      }),
    });
    console.log('STATUS', res.status);
    const text = await res.text();
    console.log(text.slice(0, 2000));
  } catch (err) {
    console.error('ERROR', err);
    process.exit(1);
  }
})();
