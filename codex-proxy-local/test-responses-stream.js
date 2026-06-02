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
        stream: true,
      }),
    });
    console.log('STATUS', res.status);
    if (!res.body) {
      console.log('No response body');
      return;
    }
    const reader = res.body.getReader();
    let decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('STREAM done');
        break;
      }
      process.stdout.write(decoder.decode(value));
    }
  } catch (err) {
    console.error('ERROR', err);
    process.exit(1);
  }
})();
