"""Unit tests for the ConfigKey algorithm (no network)."""

import hashlib
import json
import plistlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seb_bypass.configkey import compute_config_key, compute_header_hash


def _roundtrip(plist_dict: dict) -> bytes:
    """Serialize a dict to the same XML form Moodle serves."""
    return plistlib.dumps(plist_dict, fmt=plistlib.FMT_XML)


class TestConfigKey(unittest.TestCase):
    def test_known_vector(self):
        """Reproduce the MISIS Midterm ConfigKey from its real config."""
        xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<plist version="1.0"><dict>'
            b'<key>showTaskBar</key><true/>'
            b'<key>allowWlan</key><true/>'
            b'<key>originatorVersion</key><string>SEB_Windows_3.7.0.429</string>'
            b'<key>startURL</key><string>https://moodle.example.org/mod/quiz/view.php?id=1</string>'
            b'<key>sendBrowserExamKey</key><true/>'
            b'</dict></plist>'
        )
        key = compute_config_key(xml)
        self.assertRegex(key, r"^[0-9a-f]{64}$")
        # originatorVersion must not affect the result
        xml2 = xml.replace(
            b"<key>originatorVersion</key><string>SEB_Windows_3.7.0.429</string>", b""
        )
        self.assertEqual(key, compute_config_key(xml2))

    def test_key_order_does_not_matter(self):
        xml_a = _roundtrip({"showTaskBar": True, "allowWlan": False, "startURL": "https://x"})
        xml_b = _roundtrip({"startURL": "https://x", "allowWlan": False, "showTaskBar": True})
        self.assertEqual(compute_config_key(xml_a), compute_config_key(xml_b))

    def test_nested_dicts_sorted(self):
        xml_a = _roundtrip({"outer": {"b": 1, "a": 2}})
        xml_b = _roundtrip({"outer": {"a": 2, "b": 1}})
        self.assertEqual(compute_config_key(xml_a), compute_config_key(xml_b))

    def test_case_insensitive_key_sort(self):
        xml_a = _roundtrip({"URLFilterEnable": False, "urlFilterEnable2": True})
        xml_b = _roundtrip({"urlFilterEnable2": True, "URLFilterEnable": False})
        self.assertEqual(compute_config_key(xml_a), compute_config_key(xml_b))

    def test_unicode_unescaped(self):
        xml = _roundtrip({"examName": "Экзамен «Тест»"})
        key = compute_config_key(xml)
        # Reproduce manually
        canonical = json.dumps(
            {"examName": "Экзамен «Тест»"}, separators=(",", ":"), ensure_ascii=False
        )
        self.assertEqual(key, hashlib.sha256(canonical.encode()).hexdigest())

    def test_header_hash(self):
        h = compute_header_hash("https://moodle.example.org/mod/quiz/view.php?id=42", "ab" * 32)
        expected = hashlib.sha256(
            ("https://moodle.example.org/mod/quiz/view.php?id=42" + "ab" * 32).encode()
        ).hexdigest()
        self.assertEqual(h, expected)


if __name__ == "__main__":
    unittest.main()
