#!/usr/bin/env python3
"""kArmasDatr — fetch Instagram/Facebook datr and persist it.

datr is the anonymous browser id Meta sets on first hit. finds it all sessionid, tokens, etc,
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener

UA = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
)

TARGETS = {
    "ig": "https://www.instagram.com/",
    "fb": "https://www.facebook.com/",
    "ig-login": "https://www.instagram.com/accounts/login/",
}

DATR_RE = re.compile(
    r'"(?:_js_)?datr"\s*:\s*(?:\{\s*"value"\s*:\s*)?"([A-Za-z0-9_\-]{8,})"',
)
SET_COOKIE_RE = re.compile(r"(?i)(?:^|,\s*)datr=([A-Za-z0-9_\-]{8,})")


def fetch(url: str, timeout: int) -> tuple[str, dict[str, str], list[str]]:
    jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    req = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    with opener.open(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "replace")
        headers = {k.lower(): v for k, v in resp.headers.items()}
        raw_set = resp.headers.get_all("Set-Cookie") or []
    cookies = {c.name: c.value for c in jar}
    return body, cookies, raw_set if isinstance(raw_set, list) else [raw_set]


def extract(body: str, cookies: dict[str, str], set_cookie: list[str]) -> dict[str, str]:
    found: dict[str, str] = {}
    if cookies.get("datr"):
        found["cookiejar"] = cookies["datr"]
    for line in set_cookie:
        m = SET_COOKIE_RE.search(line.replace("\n", " "))
        if m:
            found["set-cookie"] = m.group(1)
            break
    embedded = DATR_RE.findall(body)
    if embedded:
        found["html"] = embedded[0]
    return found


def pick(found: dict[str, str]) -> str | None:
    for key in ("set-cookie", "cookiejar", "html"):
        if found.get(key):
            return found[key]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch and save a fresh datr")
    ap.add_argument("--target", choices=sorted(TARGETS), default="ig")
    ap.add_argument("--url", help="Override target URL")
    ap.add_argument("-o", "--out", default="datr.json", help="Output path")
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    url = args.url or TARGETS[args.target]
    last_err = ""
    for attempt in range(1, args.retries + 1):
        try:
            body, cookies, set_cookie = fetch(url, args.timeout)
            found = extract(body, cookies, set_cookie)
            value = pick(found)
            if not value:
                last_err = f"no datr in response ({len(body)} bytes, cookies={list(cookies)})"
                print(f"[{attempt}/{args.retries}] {last_err}", file=sys.stderr)
                time.sleep(1.2 * attempt)
                continue
            record = {
                "datr": value,
                "sources": found,
                "url": url,
                "fetched_at": int(time.time()),
                "other_cookies": sorted(k for k in cookies if k != "datr"),
            }
            path = Path(args.out)
            path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            print(value)
            print(f"saved {path.resolve()}", file=sys.stderr)
            return 0
        except HTTPError as exc:
            last_err = f"HTTP {exc.code}"
            print(f"[{attempt}/{args.retries}] {last_err}", file=sys.stderr)
        except URLError as exc:
            last_err = f"URL error: {exc.reason}"
            print(f"[{attempt}/{args.retries}] {last_err}", file=sys.stderr)
        except TimeoutError:
            last_err = "timeout"
            print(f"[{attempt}/{args.retries}] timeout", file=sys.stderr)
        time.sleep(1.2 * attempt)

    print(f"failed: {last_err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
