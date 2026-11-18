# Минимальный пример: открыть SEB-квиз и вывести вопросы.
# Перед запуском:
#   export MOODLE_URL="https://moodle.example.org"
#   export MOODLE_COOKIE="<значение MoodleSession из браузера>"
#   export MOODLE_CMID="12345"
import os
import sys
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seb_bypass.client import MoodleClient
from seb_bypass.configkey import compute_config_key

BASE = os.environ["MOODLE_URL"]
COOKIE = os.environ["MOODLE_COOKIE"]
CMID = os.environ["MOODLE_CMID"]

xml = urlopen(
    Request(f"{BASE}/mod/quiz/accessrule/seb/config.php?cmid={CMID}",
            headers={"Cookie": f"MoodleSession={COOKIE}"})
).read()
key = compute_config_key(xml)
print(f"ConfigKey: {key}")

cl = MoodleClient(BASE, COOKIE, config_key=key)
attempt = cl.start_attempt(int(CMID))
print(f"Attempt:   {attempt}")

questions = cl.load_page(attempt, int(CMID))
for q in questions:
    print(f"\n— Q{q.slot} [{q.qtype}] {q.text[:100]}")
    for v, label in list(q.options.items())[:6]:
        print(f"    [{v}] {label[:60]}")
    for n, name in sorted(q.places.items()):
        print(f"    <place {n}> {name}")
    for name, opts in list(q.subs.items())[:3]:
        print(f"    <sub {name}> {list(opts.items())[:3]}")
