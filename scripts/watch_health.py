#!/usr/bin/env python3
"""Local health watcher for CI/CD ДЗ шаг 6 (G2=C — no public URL yet).

Usage:
  python scripts/watch_health.py
  HEALTH_URL=http://127.0.0.1:5001/api/health INTERVAL_SEC=30 python scripts/watch_health.py

Exit codes: 0 = ok/degraded process up; 1 = HTTP/network fail or status=fail.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request


def once(url: str, timeout: float) -> tuple[int, dict | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, None, raw[:200]
            return resp.status, body, ""
    except urllib.error.HTTPError as exc:
        return exc.code, None, str(exc)
    except urllib.error.URLError as exc:
        return 0, None, str(exc.reason)


def main() -> int:
    url = os.getenv("HEALTH_URL", "http://127.0.0.1:5001/api/health").strip()
    interval = float(os.getenv("INTERVAL_SEC", "0") or "0")
    timeout = float(os.getenv("HEALTH_TIMEOUT_SEC", "5") or "5")
    loops = int(os.getenv("WATCH_LOOPS", "1") or "1")

    exit_code = 0
    i = 0
    while True:
        i += 1
        status, body, err = once(url, timeout)
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        if body is None:
            print(f"{ts} FAIL http={status} err={err}")
            exit_code = 1
        else:
            overall = body.get("status", "?")
            checks = body.get("checks") or {}
            print(
                f"{ts} status={overall} http={status} "
                f"db={checks.get('db', {}).get('ok')} "
                f"ai={checks.get('ai', {}).get('configured')} "
                f"disk={checks.get('disk', {}).get('ok')}"
            )
            if overall == "fail" or status != 200:
                exit_code = 1
        if interval <= 0 or (loops > 0 and i >= loops):
            break
        time.sleep(interval)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
