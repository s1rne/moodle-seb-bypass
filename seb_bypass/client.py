"""
Moodle client that can open and run SEB-protected quizzes with plain HTTP.

The flow for one quiz attempt:

1. ``GET  /mod/quiz/view.php?id=<cmid>``          — with SEB headers
2. ``POST /mod/quiz/startattempt.php``            — with SEB headers
3. ``GET  /mod/quiz/attempt.php?attempt=<id>&cmid=<cmid>[&page=N]``
4. ``POST /mod/quiz/processattempt.php``          — answers for current page
5. repeat 3-4 for every page
6. ``POST /mod/quiz/processattempt.php`` with ``finishattempt=1``

Important details learned the hard way:

* Every question slot needs ``q<qubaid>:<slot>_:sequencecheck`` and
  ``q<qubaid>:<slot>_:flagged`` submitted, otherwise Moodle silently
  drops the answers.
* Moodle may **re-randomise questions on every attempt**: the internal
  question id (``qubaid``) and even the option order can change between
  attempts. Always parse the fresh attempt page before submitting.
* The session cookie is reused from your normal browser login, so
  log in first with any browser and export the ``MoodleSession``
  cookie, or let :meth:`MoodleClient.login` do a headless login.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from http.cookiejar import CookieJar
from typing import Optional
from urllib.parse import urljoin, urlparse
from urllib.request import (
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
    install_opener,
    urlopen,
)

from .configkey import compute_config_key

try:
    import ssl
except ImportError:  # pragma: no cover
    ssl = None  # type: ignore

__all__ = ["MoodleClient", "SebQuizError"]


class SebQuizError(RuntimeError):
    """Raised when the quiz flow cannot be completed."""


@dataclass
class Question:
    """One parsed question on an attempt page."""

    slot: int
    qubaid: int
    qtype: str
    text: str
    # For multichoice / truefalse: {value: label}
    options: dict[str, str] = field(default_factory=dict)
    # For ddwtos (drag & drop into text): {choice_index: label}
    choices: dict[str, str] = field(default_factory=dict)
    # For ddwtos: {placeholder_number: name}
    places: dict[int, str] = field(default_factory=dict)
    # For multianswer (cloze): {sub_name: {value: label}}
    subs: dict[str, dict[str, str]] = field(default_factory=dict)


class MoodleClient:
    """Small cookie-aware HTTP client with SEB header injection."""

    UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36 SafeExamBrowser/3.7.0"
    )

    def __init__(self, base_url: str, session_cookie: str,
                 config_key: Optional[str] = None, proxy: Optional[str] = None):
        """
        Parameters
        ----------
        base_url:
            Moodle root, e.g. ``https://moodle.example.org``.
        session_cookie:
            Value of the ``MoodleSession`` cookie (from your browser).
        config_key:
            Pre-computed SEB ConfigKey (see :mod:`seb_bypass.configkey`).
            Optional — it will be fetched automatically per-quiz if missing.
        proxy:
            Optional HTTP(S) proxy, e.g. ``http://127.0.0.1:8080``.
        """
        self.base_url = base_url.rstrip("/")
        self.session_cookie = session_cookie
        self.config_key = config_key
        handlers = []
        if proxy:
            handlers.append(ProxyHandler({"http": proxy, "https": proxy}))
        if ssl is not None:
            ctx = ssl.create_default_context()
            handlers.append(HTTPSHandler(context=ctx))
        self.opener = build_opener(CookieJar(), *handlers)
        self._sesskey: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Low-level HTTP
    # ------------------------------------------------------------------ #

    def request(self, path_or_url: str, data: Optional[dict] = None,
                seb: bool = False, follow: bool = False) -> tuple[int, str, str]:
        """Perform a request. Returns ``(status, final_url, body)``."""
        url = urljoin(self.base_url + "/", path_or_url)
        headers = {"User-Agent": self.UA}
        cookie = f"MoodleSession={self.session_cookie}"
        if seb and self.config_key:
            headers["X-SafeExamBrowser-ConfigKeyHash"] = self._hash_for(url)
            cookie += "; SEBKey=1"
        headers["Cookie"] = cookie
        if data is not None:
            from urllib.parse import urlencode
            body = urlencode(data, quote_via=lambda s, *a, **k: s).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = None
        req = Request(url, data=body, headers=headers)
        with urlopen(req) as resp:
            final_url = resp.geturl()
            status = resp.status if hasattr(resp, "status") else resp.getcode()
            content = resp.read().decode("utf-8", "replace")
        return status, final_url, content

    def _hash_for(self, url: str) -> str:
        from .configkey import compute_header_hash
        if not self.config_key:
            raise SebQuizError("config_key is not set")
        # SEB reports the URL without the query string.
        parsed = urlparse(url)
        raw = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return compute_header_hash(raw, self.config_key)

    # ------------------------------------------------------------------ #
    # Session helpers
    # ------------------------------------------------------------------ #

    def login(self, username: str, password: str) -> None:
        """Headless login through ``/login/index.php`` (works on stock Moodle)."""
        _, _, html = self.request("/login/index.php")
        logintoken = ""
        m = re.search(r'name="logintoken" value="([^"]+)"', html)
        if m:
            logintoken = m.group(1)
        status, _, html = self.request(
            "/login/index.php",
            data={"username": username, "password": password, "logintoken": logintoken},
        )
        if "login/index.php" in html and "logout" not in html.lower():
            raise SebQuizError("Login failed — check credentials")
        self._sesskey = self.fetch_sesskey()

    def fetch_sesskey(self) -> str:
        """Extract the current ``sesskey`` from any dashboard page."""
        _, _, html = self.request("/my/")
        m = re.search(r'"sesskey":"([^"]+)"', html) or re.search(
            r'name="sesskey" value="([^"]+)"', html
        )
        if not m:
            raise SebQuizError("Cannot find sesskey — are you logged in?")
        self._sesskey = m.group(1)
        return self._sesskey

    @property
    def sesskey(self) -> str:
        if not self._sesskey:
            return self.fetch_sesskey()
        return self._sesskey

    # ------------------------------------------------------------------ #
    # SEB plumbing
    # ------------------------------------------------------------------ #

    def ensure_config_key(self, cmid: int) -> str:
        """Fetch (and cache) the SEB ConfigKey for a quiz."""
        if self.config_key:
            return self.config_key
        _, _, xml = self.request(
            f"/mod/quiz/accessrule/seb/config.php?cmid={cmid}", seb=False
        )
        if "mod/quiz/view.php" in xml and "<plist" not in xml:
            # Redirected to login — cookie expired.
            raise SebQuizError("Session cookie expired — refresh MoodleSession")
        self.config_key = compute_config_key(xml.encode())
        return self.config_key

    def open_quiz(self, cmid: int) -> None:
        """Hit ``view.php`` with SEB headers so Moodle caches the validation."""
        self.ensure_config_key(cmid)
        self.request(f"/mod/quiz/view.php?id={cmid}", seb=True)

    # ------------------------------------------------------------------ #
    # Attempt flow
    # ------------------------------------------------------------------ #

    def start_attempt(self, cmid: int) -> int:
        """Start a new attempt, return the attempt id."""
        self.open_quiz(cmid)
        status, final_url, _ = self.request(
            "/mod/quiz/startattempt.php",
            data={
                "cmid": cmid,
                "sesskey": self.sesskey,
                "_qf__mod_quiz_form_preflight_check_form": "1",
            },
            seb=True,
        )
        m = re.search(r"attempt=(\d+)", final_url)
        if not m:
            raise SebQuizError(f"startattempt did not redirect to an attempt (status {status})")
        return int(m.group(1))

    def load_page(self, attempt: int, cmid: int, page: int = 0) -> list[Question]:
        """Load one attempt page and parse its questions."""
        url = f"/mod/quiz/attempt.php?attempt={attempt}&cmid={cmid}"
        if page:
            url += f"&page={page}"
        _, _, html = self.request(url)
        return parse_questions(html)

    def submit_page(self, attempt: int, cmid: int, page: int,
                    answers: dict[str, str], last_page: bool) -> None:
        """Submit answers for one page (``answers`` maps field name → value)."""
        # sequencecheck/flagged must come from the live page — the caller
        # obtained them together with :meth:`load_page`.
        data = {k: v for k, v in answers.items()}
        data.update({
            "attempt": attempt,
            "thispage": page,
            "nextpage": -1 if last_page else page + 1,
            "timeup": 0,
            "sesskey": self.sesskey,
            "slots": "",
            "next": "Finish attempt ..." if last_page else "Next page",
        })
        self.request("/mod/quiz/processattempt.php", data=data)

    def finish(self, attempt: int, cmid: int) -> None:
        """Submit the whole attempt."""
        self.request("/mod/quiz/processattempt.php", data={
            "attempt": attempt,
            "finishattempt": 1,
            "timeup": 0,
            "slots": "",
            "cmid": cmid,
            "sesskey": self.sesskey,
        })


# ---------------------------------------------------------------------- #
# HTML parsing helpers (stdlib only)
# ---------------------------------------------------------------------- #

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _clean(html: str) -> str:
    import html as _h
    return _WS.sub(" ", _h.unescape(_TAG.sub(" ", html))).strip()


def parse_questions(html: str) -> list[Question]:
    """Parse all questions from a Moodle attempt page (best effort)."""
    questions: list[Question] = []
    for chunk in re.split(r'(?=id="question-\d+-\d+")', html)[1:]:
        m = re.match(r'id="question-(\d+)-(\d+)" class="que (\w+)', chunk)
        if not m:
            continue
        q = Question(
            qubaid=int(m.group(1)),
            slot=int(m.group(2)),
            qtype=m.group(3),
            text="",
        )
        tm = re.search(r'(?s)<div class="qtext">(.*?)</div>', chunk)
        if tm:
            q.text = _clean(tm.group(1))
        # radio options
        for om in re.finditer(
            r'<input type="radio" name="(q\d+:\d+_\w+)" value="(\d+)"[^>]*/>'
            r'<label for="\1\2"[^>]*>(.*?)</label>', chunk
        ):
            q.options[om.group(2)] = _clean(om.group(3))
        # ddwtos drag choices
        for dm in re.finditer(
            r'(?s)<[^>]*class="draghome[^"]*choice(\d+)[^"]*"[^>]*>(.*?)</',
            chunk
        ):
            q.choices[dm.group(1)] = _clean(dm.group(2))
        # ddwtos placeholders
        for pm in re.finditer(r'class="placeinput[^"]*" name="([^"]+)"', chunk):
            slot_num = re.search(r"_p(\d+)$", pm.group(1))
            if slot_num:
                q.places[int(slot_num.group(1))] = pm.group(1)
        # multianswer selects
        for sm in re.finditer(r'(?s)<select[^>]*name="(q\d+:\d+_\w+)"[^>]*>(.*?)</select>', chunk):
            opts = {
                v: _clean(o)
                for v, o in re.findall(r'<option value="([^"]*)"[^>]*>([^<]*)</option>', sm.group(2))
                if v != ""
            }
            q.subs[sm.group(1)] = opts
        questions.append(q)
    return questions


def sequencecheck_fields(html: str) -> dict[str, str]:
    """Extract the hidden ``_:sequencecheck`` / ``_:flagged`` fields."""
    out: dict[str, str] = {}
    for name, value in re.findall(
        r'name="(q\d+:\d+_):(sequencecheck|flagged)" value="([^"]*)"', html
    ):
        out[f"{name}_{value.split(':')[0] if False else ''}"] = value
    # simpler: rebuild exact names
    out = {}
    for full in re.findall(r'name="(q\d+:\d+_:(?:sequencecheck|flagged))" value="([^"]*)"', html):
        out[full[0]] = full[1]
    return out
