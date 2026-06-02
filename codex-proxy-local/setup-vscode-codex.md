# Cấu hình Codex Extension / VS Code sử dụng codex-proxy-local

Repo `codex-proxy-local` đã có sẵn proxy chuyển `gpt-5.5` sang `cx/gpt-5.5` và cho phép đổi provider API.

## 1. Chạy proxy local

Trong thư mục `codex-proxy-local`, chạy Node với provider của bạn:

```bash
cd d:/ANTIGRAVITY/check_api/codex-proxy-local
set PROXY_TARGET=https://provider-cua-ban.com
set PROXY_PORT=18080
node model-proxy.js
```

Hoặc nếu dùng PowerShell:

```powershell
$env:PROXY_TARGET = 'https://provider-cua-ban.com'
$env:PROXY_PORT = '18080'
node .\model-proxy.js
```

Proxy sẽ chạy tại:

- `http://127.0.0.1:18080`

## 2. Cập nhật cấu hình Codex

Thêm hoặc sửa file `~/.codex/config.toml` như sau:

```toml
model_provider = "maivangia"
model = "cx/gpt-5.5"
model_reasoning_effort = "medium"

[model_providers.maivangia]
name = "Mai Van Gia Provider"
base_url = "http://127.0.0.1:18080/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

## 3. Đặt biến môi trường

Trong Windows, thiết lập biến cho VS Code và Codex CLI:

```powershell
setx OPENAI_BASE_URL "http://127.0.0.1:18080/v1"
setx OPENAI_API_KEY "YOUR_API_KEY"
```

Sau đó khởi động lại VS Code.

### Script hỗ trợ cấu hình nhanh

Nếu muốn cấu hình tự động, dùng script PowerShell sau:

```powershell
cd d:/ANTIGRAVITY/check_api/codex-proxy-local
.\configure-codex-provider.ps1 -ProviderUrl "https://provider-cua-ban.com" -ApiKey "YOUR_API_KEY" -Model "cx/gpt-5.5"
```

Script sẽ:
- tạo hoặc cập nhật `~/.codex/config.toml`
- đặt `OPENAI_BASE_URL` và `OPENAI_API_KEY` cho Windows user
- giữ model mặc định `cx/gpt-5.5`

## 4. Model mặc định là `gpt-5.5`

Repo đã cấu hình alias mặc định trong `model-proxy.js`:

```js
const MODEL_ALIASES = {
  "gpt-5.5": "cx/gpt-5.5",
  "gpt-5.4": "cx/gpt-5.4",
  "gpt-5.3-codex": "cx/gpt-5.3-codex",
};
```

Vì vậy khi codex extension chọn `GPT-5.5`, proxy sẽ tự động remap đến `cx/gpt-5.5`.

## 5. Nếu muốn đổi provider API

Chỉ cần thay `PROXY_TARGET` thành URL provider của bạn, ví dụ:

```powershell
$env:PROXY_TARGET = 'https://api-cua-nguon-moi.com'
node .\model-proxy.js
```

Hoặc chỉnh `PROXY_TARGET` trong `install.sh` nếu cài bằng script.

## 6. Khởi động lại

- Restart proxy local nếu đổi `PROXY_TARGET` hoặc `PROXY_PORT`
- Reload VS Code: `Ctrl+Shift+P` -> `Reload Window`

---

Nếu bạn muốn, tôi cũng có thể sửa thẳng `model-proxy.js` để mặc định dùng provider của bạn và gán model `gpt-5.5` ngay trong source code.