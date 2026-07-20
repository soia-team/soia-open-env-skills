#!/usr/bin/env python3
"""Read-only HTTPS probe with secret-free, machine-readable output."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse


def probe(url: str, timeout: float) -> dict[str, object]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
        return {"url": url, "ok": False, "category": "invalid_url"}
    started = time.monotonic()
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "soia-env-tools-probe/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            return {"url": url, "ok": 200 <= status < 400, "category": "reachable", "status": status, "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "category": "http_error", "status": exc.code, "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except urllib.error.URLError as exc:
        reason = str(exc.reason).lower()
        category = "tls_failed" if any(word in reason for word in ("certificate", "ssl", "tls")) else "dns_failed" if "name or service" in reason or "nodename" in reason else "unreachable"
        return {"url": url, "ok": False, "category": category, "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except TimeoutError:
        return {"url": url, "ok": False, "category": "timeout", "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except OSError as exc:
        message = str(exc).lower()
        category = "timeout" if "timed out" in message else "unreachable"
        return {"url": url, "ok": False, "category": category, "elapsed_ms": round((time.monotonic() - started) * 1000)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe HTTPS endpoints without saving response bodies")
    parser.add_argument("--url", action="append", required=True, help="HTTP(S) URL; may be repeated")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()
    results = [probe(url, max(0.1, args.timeout)) for url in args.url]
    if args.json:
        print(json.dumps(results, ensure_ascii=False))
    else:
        for result in results:
            print(f"{result['category']}: {result['url']}")
    return 0 if all(bool(result.get("ok")) for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
