"""
moodle-seb-bypass — Take Moodle SEB-locked quizzes from your regular browser.

Pure-Python implementation of the Safe Exam Browser handshake that the
Moodle `quizaccess_seb` plugin expects, plus a mitmproxy add-on that
injects the right headers into your normal browser traffic.

Works on macOS, Windows and Linux. No admin rights required.
"""

__version__ = "1.0.0"
__all__ = ["configkey", "mitm_addon", "cli", "client"]
