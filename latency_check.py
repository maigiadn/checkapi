#!/usr/bin/env python3
import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_PROMPT = "hi"


@dataclass
class RunResult:
    index: int
    ok: bool
    status: Optional[int]
    total_ms: float
    first_token_ms: Optional[float]
    error: Optional[str]


def normalize_base_url(base_url: str) -> str:
    base_url = base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("base url is empty")
    return base_url


def chat_completions_url(base_url: str) -> str:
    base_url = normalize_base_url(base_url)
    if base_url.endswith("/chat/completions"):
        return base_url
    if base_url.endswith("/v1"):
        return f"{base_url}/chat/completions"
    return f"{base_url}/v1/chat/completions"


def build_payload(model: str, prompt: str, max_tokens: int, stream: bool) -> bytes:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": stream,
    }
    return json.dumps(payload).encode("utf-8")


def post_chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: float,
    max_tokens: int,
    stream: bool,
    index: int,
) -> RunResult:
    url = chat_completions_url(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream" if stream else "application/json",
    }
    request = Request(
        url,
        data=build_payload(model, prompt, max_tokens, stream),
        headers=headers,
        method="POST",
    )

    started = time.perf_counter()
    first_token_ms: Optional[float] = None
    status: Optional[int] = None

    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            if stream:
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data:"):
                        if first_token_ms is None:
                            first_token_ms = elapsed_ms(started)
            else:
                response.read()

        return RunResult(
            index=index,
            ok=True,
            status=status,
            total_ms=elapsed_ms(started),
            first_token_ms=first_token_ms,
            error=None,
        )
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return RunResult(
            index=index,
            ok=False,
            status=exc.code,
            total_ms=elapsed_ms(started),
            first_token_ms=first_token_ms,
            error=short_error(body or exc.reason),
        )
    except (URLError, TimeoutError, OSError) as exc:
        return RunResult(
            index=index,
            ok=False,
            status=status,
            total_ms=elapsed_ms(started),
            first_token_ms=first_token_ms,
            error=short_error(str(exc)),
        )


def elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000


def short_error(value: str, limit: int = 300) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def percentile(values: List[float], percent: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percent
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(results: List[RunResult]) -> Dict[str, object]:
    success = [item for item in results if item.ok]
    total_values = [item.total_ms for item in success]
    ttft_values = [
        item.first_token_ms for item in success if item.first_token_ms is not None
    ]

    summary: Dict[str, object] = {
        "runs": len(results),
        "success": len(success),
        "failed": len(results) - len(success),
    }

    if total_values:
        summary["total_ms"] = stats(total_values)
    if ttft_values:
        summary["first_token_ms"] = stats(ttft_values)

    return summary


def stats(values: List[float]) -> Dict[str, float]:
    return {
        "min": round(min(values), 2),
        "avg": round(statistics.mean(values), 2),
        "p50": round(percentile(values, 0.50), 2),
        "p95": round(percentile(values, 0.95), 2),
        "max": round(max(values), 2),
    }


def print_table(results: List[RunResult]) -> None:
    print("run  ok     status  total_ms  first_token_ms  error")
    print("---  -----  ------  --------  --------------  -----")
    for item in results:
        print(
            f"{item.index:<3}  "
            f"{str(item.ok):<5}  "
            f"{str(item.status or '-'):>6}  "
            f"{item.total_ms:>8.2f}  "
            f"{format_optional_ms(item.first_token_ms):>14}  "
            f"{item.error or ''}"
        )


def format_optional_ms(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:.2f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure latency of an OpenAI-compatible chat completion provider."
    )
    parser.add_argument("--base-url", default="https://apikey.maivangia.com", help="Provider base URL")
    parser.add_argument("--api-key", default="sk-e2aa144de4457453-cm1awr-75a68ade", help="Provider API key")
    parser.add_argument("--model", default="cx/gpt-5.4", help="Model name")
    parser.add_argument("--runs", type=int, default=5, help="Number of requests")
    parser.add_argument("--timeout", type=float, default=60, help="Timeout in seconds")
    parser.add_argument("--max-tokens", type=int, default=32, help="Max output tokens")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Benchmark prompt")
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Use streaming and measure time to first streamed chunk",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a table",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 1:
        print("--runs must be at least 1", file=sys.stderr)
        return 2

    results = [
        post_chat_completion(
            base_url=args.base_url,
            api_key=args.api_key,
            model=args.model,
            prompt=args.prompt,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            stream=args.stream,
            index=index,
        )
        for index in range(1, args.runs + 1)
    ]

    output = {
        "target": {
            "base_url": normalize_base_url(args.base_url),
            "model": args.model,
            "stream": args.stream,
        },
        "summary": summarize(results),
        "results": [item.__dict__ for item in results],
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print_table(results)
        print()
        print(json.dumps(output["summary"], indent=2))

    return 0 if all(item.ok for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
