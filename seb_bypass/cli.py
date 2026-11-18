"""
Command-line interface.

Examples
--------
Compute the ConfigKey for a quiz and print the SEB headers::

    python -m seb_bypass.cli config-key --url https://moodle.example.org --cmid 135314

Dry-run: verify that a session cookie is valid::

    python -m seb_bypass.cli check --url https://moodle.example.org --cookie "abc123"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .configkey import compute_config_key, compute_header_hash


def _fetch_config(base_url: str, cmid: str, cookie: str) -> bytes:
    url = f"{base_url.rstrip('/')}/mod/quiz/accessrule/seb/config.php?cmid={cmid}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; moodle-seb-bypass)",
        **({"Cookie": f"MoodleSession={cookie}"} if cookie else {}),
    })
    with urlopen(req) as resp:
        return resp.read()


def cmd_config_key(args: argparse.Namespace) -> int:
    xml = _fetch_config(args.url, args.cmid, args.cookie)
    if b"<plist" not in xml:
        print("ERROR: did not get a SEB config (check --cmid and cookie).", file=sys.stderr)
        print("Response start:", xml[:120].decode("utf-8", "replace"), file=sys.stderr)
        return 1
    key = compute_config_key(xml)
    parsed = urlparse(args.url)
    raw = f"{parsed.scheme}://{parsed.netloc}/mod/quiz/view.php?id={args.cmid}"
    digest = compute_header_hash(raw, key)
    if args.json:
        print(json.dumps({
            "config_key": key,
            "raw_url": raw,
            "x_safeexambrowser_configkeyhash": digest,
        }, indent=2))
    else:
        print(f"ConfigKey:                       {key}")
        print(f"Raw URL:                         {raw}")
        print(f"X-SafeExamBrowser-ConfigKeyHash: {digest}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    url = f"{args.url.rstrip('/')}/my/"
    req = Request(url, headers={"Cookie": f"MoodleSession={args.cookie}"})
    with urlopen(req) as resp:
        html = resp.read().decode("utf-8", "replace")
        status = resp.status
    ok = "sesskey" in html
    print(f"HTTP {status} — {'session OK' if ok else 'session INVALID (redirected to login?)'}")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seb-bypass",
        description="Moodle Safe Exam Browser bypass toolkit",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pk = sub.add_parser("config-key", help="compute ConfigKey + header hash for a quiz")
    pk.add_argument("--url", required=True, help="Moodle base URL")
    pk.add_argument("--cmid", required=True, help="course module id of the quiz")
    pk.add_argument("--cookie", default="", help="MoodleSession cookie value")
    pk.add_argument("--json", action="store_true", help="machine-readable output")
    pk.set_defaults(func=cmd_config_key)

    ck = sub.add_parser("check", help="verify a MoodleSession cookie")
    ck.add_argument("--url", required=True)
    ck.add_argument("--cookie", required=True)
    ck.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
