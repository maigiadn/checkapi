const fetch = globalThis.fetch || require('node-fetch');
const url = 'http://127.0.0.1:18080/v1/chat/completions';
const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) {
  console.error('Missing OPENAI_API_KEY');
  process.exit(1);
}
const body = {
  model: 'gpt-5.5',
  messages: [{ role: 'user', content: 'hi' }],
};

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    });
    console.log('STATUS', res.status);
    const text = await res.text();
    console.log(text.slice(0, 1200));
  } catch (err) {
    console.error('ERROR', err.message);
    process.exit(1);
  }
})();
