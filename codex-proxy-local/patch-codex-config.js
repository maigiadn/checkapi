const fs = require('fs');
const path = require('path');

const home = process.env.USERPROFILE || process.env.HOME;
if (!home) {
  throw new Error('Home directory not found');
}

const cfgPath = path.join(home, '.codex', 'config.toml');
if (!fs.existsSync(cfgPath)) {
  throw new Error(`Config not found: ${cfgPath}`);
}
const backup = `${cfgPath}.backup.${Date.now()}`;
fs.copyFileSync(cfgPath, backup);
console.log('Backup created', backup);

let text = fs.readFileSync(cfgPath, 'utf8');
text = text.replace(/^\s*model_provider\s*=.*\r?\n?/m, '');
text = text.replace(/^\s*model\s*=.*\r?\n?/m, '');
text = text.replace(/^\s*model_reasoning_effort\s*=.*\r?\n?/m, '');
text = text.replace(/^\s*\[model_providers\.maivangia\][\s\S]*?(?=^\[|\z)/m, '');

const header = [
  'model_provider = "maivangia"',
  'model = "cx/gpt-5.5"',
  'model_reasoning_effort = "medium"',
  '',
  '[model_providers.maivangia]',
  'name = "Mai Van Gia Provider"',
  'base_url = "http://127.0.0.1:18080/v1"',
  'env_key = "OPENAI_API_KEY"',
  'wire_api = "responses"',
  ''
].join('\n');

fs.writeFileSync(cfgPath, header + text, 'utf8');
console.log('Updated', cfgPath);
