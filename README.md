# OpenAI Provider Latency Check

Chuong trinh CLI nho de do toc do phan hoi cua provider OpenAI-compatible dua tren:

- `base-url`
- `api-key`
- `model`

Mac dinh tool goi endpoint:

```text
{base-url}/v1/chat/completions
```

Neu `base-url` da ket thuc bang `/v1`, tool se khong them `/v1` lan nua.

## Cach chay

```bash
python latency_check.py --base-url https://api.openai.com --api-key YOUR_API_KEY --model gpt-4o-mini
```

Chay nhieu lan de lay thong ke:

```bash
python latency_check.py --base-url https://provider.example.com --api-key YOUR_API_KEY --model MODEL_NAME --runs 10
```

Do streaming va time-to-first-token:

```bash
python latency_check.py --base-url https://provider.example.com --api-key YOUR_API_KEY --model MODEL_NAME --runs 10 --stream
```

Xuat JSON:

```bash
python latency_check.py --base-url https://provider.example.com --api-key YOUR_API_KEY --model MODEL_NAME --json
```

## Chi so

- `total_ms`: tong thoi gian tu luc gui request den khi doc xong response.
- `first_token_ms`: thoi gian den chunk dau tien, chi co khi dung `--stream`.
- `avg`, `p50`, `p95`: trung binh, median, va percentile 95 cua cac lan thanh cong.

## Giao dien web HTML

Mo truc tiep file `index.html` bang trinh duyet, hoac chay server local:

```bash
python -m http.server 8000
```

Sau do mo:

```text
http://localhost:8000
```

Form web ho tro:

- Nhap `base-url`, `api-key`, `model`
- Chon so lan test, timeout, max tokens
- Bat `stream` de do `TTFT`
- Xem bang ket qua va thong ke thanh cong/that bai, avg, p95

Luu y: HTML goi API truc tiep tu trinh duyet, nen provider phai cho phep CORS. Neu bi loi CORS, dung ban CLI `latency_check.py` hoac them backend/proxy local.
