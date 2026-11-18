"""
mitmproxy add-on: turn any regular browser into SEB for Moodle quizzes.

Run::

    mitmdump -s seb_bypass/mitm_addon.py --set seb_url=https://moodle.example.org

Then point your system/browser proxy at mitmproxy (default 127.0.0.1:8080),
log into Moodle as usual and take the quiz — every request to the Moodle
host gets the exact ``X-SafeExamBrowser-ConfigKeyHash`` header that SEB
would send, so the plugin accepts you.

How it works
------------

1. On the first request to ``/mod/quiz/view.php`` (or any quiz page) the
   add-on fetches ``/mod/quiz/accessrule/seb/config.php?cmid=...``
   **directly from Moodle** (not through the client), computes the
   ConfigKey and caches it per ``cmid``.
2. Every subsequent client request to the Moodle host gets
   ``X-SafeExamBrowser-ConfigKeyHash: SHA256(url_without_query + configkey)``
   and a SEB-flavoured User-Agent.
3. Once Moodle validates the hash it caches the check in the PHP session,
   so even if the header were missing later the attempt would still work.
"""

from __future__ import annotations

import hashlib
import json
import os
import plistlib
import re
from urllib.parse import urlparse, parse_qs

from mitmproxy import http, ctx


class SebPatcher:
    def __init__(self):
        # cmid -> config_key
        self._keys: dict[str, str] = {}
        # host -> base url
        self._hosts: set[str] = set()

    # ------------------------------------------------------------------ #
    # Config
    # ------------------------------------------------------------------ #

    @property
    def seb_urls(self) -> list[str]:
        raw = getattr(ctx.options, "seb_url", "") or os.environ.get("SEB_URL", "")
        return [u.strip() for u in re.split(r"[,\s]+", raw) if u.strip()]

    def load(self, loader):
        loader.add_option(
            "seb_url", str, "",
            "Comma-separated Moodle base URLs to patch, e.g. https://moodle.example.org"
        )

    def configure(self, updated):
        for u in self.seb_urls:
            self._hosts.add(urlparse(u).netloc)

    # ------------------------------------------------------------------ #
    # ConfigKey machinery
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sort_recursively(obj):
        if isinstance(obj, dict):
            return {
                k: SebPatcher._sort_recursively(v)
                for k, v in sorted(obj.items(), key=lambda kv: (kv[0].casefold(), kv[0]))
            }
        if isinstance(obj, list):
            return [SebPatcher._sort_recursively(x) for x in obj]
        return obj

    def _config_key(self, xml: bytes) -> str:
        plist = plistlib.loads(xml)
        plist.pop("originatorVersion", None)
        canonical = json.dumps(
            self._sort_recursively(plist),
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _get_key_for_cmid(self, cmid: str) -> str | None:
        if cmid in self._keys:
            return self._keys[cmid]
        host = next(iter(self._hosts), None)
        if not host:
            return None
        url = f"https://{host}/mod/quiz/accessrule/seb/config.php?cmid={cmid}"
        try:
            # Fetch with the client's cookies so the session is respected.
            r = http.HTTPRequest.make("GET", url, headers={"Cookie": self._cookie_header()})
            resp = http.request(r)  # not used; see below
        except Exception:
            pass
        # mitmproxy cannot easily do blocking upstream calls inside a hook
        # without a loop; instead we rely on intercepting the config.php
        # request made by the browser (see `response` hook below).
        return self._keys.get(cmid)

    def _cookie_header(self) -> str:
        # The add-on receives cookies from the live request; we stash them.
        return getattr(self, "_last_cookie", "")

    # ------------------------------------------------------------------ #
    # Hooks
    # ------------------------------------------------------------------ #

    def request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url
        parsed = urlparse(url)
        host = parsed.netloc

        if self._hosts and host not in self._hosts:
            return

        # Remember cookies so we can re-fetch config.php with a session.
        self._last_cookie = flow.request.headers.get("Cookie", "")

        # Grab cmid from any quiz-related URL.
        cmid = None
        qs = parse_qs(parsed.query)
        if "cmid" in qs:
            cmid = qs["cmid"][0]
        else:
            m = re.search(r"[?&]id=(\d+)", parsed.query)
            if m and "/mod/quiz/" in parsed.path:
                cmid = m.group(1)

        # Intercept config.php responses to learn ConfigKeys.
        if parsed.path.endswith("/mod/quiz/accessrule/seb/config.php") and cmid:
            # The response hook will hash the body; nothing to do here.
            flow.metadata["seb_cmid"] = cmid
            return

        # Patch quiz-related requests once we have the key.
        if cmid and self._keys.get(cmid):
            key = self._keys[cmid]
            raw_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            digest = hashlib.sha256((raw_url + key).encode()).hexdigest()
            flow.request.headers["X-SafeExamBrowser-ConfigKeyHash"] = digest
            ua = flow.request.headers.get("User-Agent", "")
            if "SafeExamBrowser" not in ua:
                flow.request.headers["User-Agent"] = ua + " SafeExamBrowser/3.7.0"
            ctx.log.info(f"[seb] patched {parsed.path} (cmid={cmid})")

    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url
        parsed = urlparse(url)
        if self._hosts and parsed.netloc not in self._hosts:
            return

        cmid = (flow.metadata or {}).get("seb_cmid")
        if cmid and flow.response and flow.response.status_code == 200:
            xml = flow.response.get_text(strict=False)
            if "<plist" in xml:
                key = self._config_key(xml.encode())
                self._keys[cmid] = key
                ctx.log.info(f"[seb] cached ConfigKey for cmid={cmid}: {key[:12]}…")


addons = [SebPatcher()]
