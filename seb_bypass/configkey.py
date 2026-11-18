"""
Safe Exam Browser ConfigKey computation.

Moodle's `quizaccess_seb` plugin validates a browser by checking an
`X-SafeExamBrowser-ConfigKeyHash` HTTP header. The header value is:

    SHA256( raw_url + ConfigKey )

where ``raw_url`` is the full request URL **without query string** as SEB
sees it, and ``ConfigKey`` is a SHA256 hash of a canonicalised version of
the SEB configuration PList that the quiz exposes at

    /mod/quiz/accessrule/seb/config.php?cmid=<cmid>

Canonicalisation (must match SEB's own algorithm exactly):

1. Remove the ``originatorVersion`` key from the root dictionary.
2. Recursively sort every dictionary by key, case-insensitively
   (Unicode case-fold, culture-invariant), falling back to a plain byte
   comparison for keys that only differ in case.
3. Serialize to compact JSON: no spaces, unescaped slashes and unicode
   (``ensure_ascii=False``, ``separators=(',', ':')``).
4. ``ConfigKey = SHA256(json_bytes)`` (lower-case hex).

The resulting hash is cached by Moodle inside the PHP session after the
first successful check, so the header only needs to be present on the
requests that open the attempt (``view.php`` / ``startattempt.php``).
"""

from __future__ import annotations

import hashlib
import json
import plistlib
from typing import Union

__all__ = ["compute_config_key", "compute_header_hash", "seb_header_for"]


def _sort_recursively(obj):
    """Sort every dict in the structure by (casefolded key, raw key)."""
    if isinstance(obj, dict):
        return {
            k: _sort_recursively(v)
            for k, v in sorted(obj.items(), key=lambda kv: (kv[0].casefold(), kv[0]))
        }
    if isinstance(obj, list):
        return [_sort_recursively(item) for item in obj]
    return obj


def compute_config_key(seb_config: bytes) -> str:
    """Compute the SEB ConfigKey from the raw ``config.php`` response.

    Parameters
    ----------
    seb_config:
        Raw bytes of the XML property list served by
        ``/mod/quiz/accessrule/seb/config.php?cmid=<cmid>``.

    Returns
    -------
    str
        64-character lower-case hex SHA256 digest — the ConfigKey.
    """
    plist = plistlib.loads(seb_config)
    if not isinstance(plist, dict):
        raise ValueError("SEB config root must be a <dict> plist")

    # 1. SEB strips its own version marker before hashing.
    plist.pop("originatorVersion", None)

    # 2-3. Canonicalise and serialize to compact JSON.
    canonical = json.dumps(
        _sort_recursively(plist),
        separators=(",", ":"),
        ensure_ascii=False,
    )

    # 4. Hash.
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_header_hash(raw_url: str, config_key: str) -> str:
    """Compute ``SHA256(raw_url + config_key)`` — the value of
    ``X-SafeExamBrowser-ConfigKeyHash``.

    Parameters
    ----------
    raw_url:
        The URL as SEB would report it: scheme + host + path,
        **without** query string and **without** trailing fragment.
        Example: ``https://moodle.example.org/mod/quiz/view.php?id=42``
    config_key:
        ConfigKey as returned by :func:`compute_config_key`.
    """
    return hashlib.sha256((raw_url + config_key).encode("utf-8")).hexdigest()


def seb_header_for(raw_url: str, seb_config: bytes) -> dict[str, str]:
    """One-shot helper: return the exact headers SEB would send for ``raw_url``.

    >>> headers = seb_header_for(
    ...     "https://moodle.example.org/mod/quiz/view.php?id=42",
    ...     open("seb_config.xml", "rb").read(),
    ... )
    """
    config_key = compute_config_key(seb_config)
    return {"X-SafeExamBrowser-ConfigKeyHash": compute_header_hash(raw_url, config_key)}
