# moodle-seb-bypass

**Take Moodle quizzes that are locked behind [Safe Exam Browser](https://safeexambrowser.org/) (SEB) from your regular browser — no VM, no admin rights, no SEB installed.**

Pure Python. Works on **macOS**, **Windows** and **Linux**.

```
┌──────────────┐    SEB headers injected     ┌─────────────────┐
│ Your browser │ ──────────────────────────► │ Moodle + SEB    │
│ (Chrome etc.)│ ◄────────────────────────── │ plugin          │
└──────────────┘      looks like real SEB     └─────────────────┘
        ▲
        │  mitmproxy sits between them and signs every request
```

## How it works

Moodle's [`quizaccess_seb`](https://docs.moodle.org/en/Safe_Exam_Browser) plugin doesn't
actually talk to the SEB application. It just checks one HTTP header:

```
X-SafeExamBrowser-ConfigKeyHash: SHA256( <url-without-query> + <ConfigKey> )
```

The `ConfigKey` is `SHA256` of a canonicalised version of the quiz's SEB configuration,
which Moodle publicly serves at:

```
/mod/quiz/accessrule/seb/config.php?cmid=<quiz_id>
```

Canonicalisation = remove `originatorVersion` key → sort every dict by key
(case-insensitive) → compact JSON → SHA256. That's the whole "encryption".

After the first validated request Moodle **caches the check inside your PHP session**,
so you can even keep answering after turning the proxy off.

## Quick start

### 0. Requirements

* Python **3.9+** (`python --version`)
* [mitmproxy](https://mitmproxy.org/) (only for the transparent-proxy mode)
* A Moodle account that is allowed to take the quiz

### 1. Install

```bash
git clone https://github.com/s1rne/moodle-seb-bypass.git
cd moodle-seb-bypass
python -m pip install -e .
python -m pip install mitmproxy      # only needed for proxy mode
```

<details>
<summary>Windows one-liners (PowerShell)</summary>

```powershell
git clone https://github.com/s1rne/moodle-seb-bypass.git
cd moodle-seb-bypass
python -m pip install -e .
python -m pip install mitmproxy
```

If `python` is not found, install it from [python.org](https://www.python.org/downloads/)
and tick **Add python.exe to PATH** during setup.
</details>

### 2. Get your session cookie

1. Log into Moodle in your normal browser.
2. Press `F12` → *Application* (Chrome) / *Storage* (Firefox) → *Cookies* → your Moodle host.
3. Copy the value of the **`MoodleSession`** cookie.

### 3. Compute the key (sanity check)

```bash
seb-bypass config-key --url https://moodle.example.org --cmid 12345 --cookie "<MoodleSession>"
```

You should see:

```
ConfigKey:                       9a78a7ab9c929416c953cb05b9a6f51d43f77399074515243c42826307914468
Raw URL:                         https://moodle.example.org/mod/quiz/view.php?id=12345
X-SafeExamBrowser-ConfigKeyHash: 0589724ba8da52bff0476dc2c5cc6bc5c4911247ce76e83dfb5529d22fd38dcd
```

### 4. Run the proxy and take the quiz

```bash
mitmdump -s seb_bypass/mitm_addon.py --set seb_url=https://moodle.example.org
```

* **macOS / Linux:** run your browser through the proxy:

  ```bash
  # Chrome / Edge / Brave
  google-chrome --proxy-server="http://127.0.0.1:8080"
  ```

  or set *System Settings → Network → Proxies → Web Proxy (HTTP & HTTPS)* to
  `127.0.0.1:8080` (remember to turn it off afterwards).

* **Windows:** *Settings → Network & Internet → Proxy → Manual proxy setup* →
  `127.0.0.1`, port `8080`. Accept mitmproxy's certificate once:
  visit <http://mitm.it> through the proxy and follow the OS instructions.

Then open the quiz page in your browser as usual and press **Attempt quiz**.
Every request is signed, Moodle believes you are inside SEB. Solving the
questions is, of course, up to you 🙂.

> **Tip.** Once the attempt has started you can close the proxy — Moodle keeps
> the SEB session until the attempt is submitted.

## Using it from Python (no proxy)

```python
from seb_bypass.client import MoodleClient
from seb_bypass.configkey import compute_config_key
from urllib.request import urlopen, Request

BASE = "https://moodle.example.org"
COOKIE = "<MoodleSession>"
CMID = 12345

# 1. ConfigKey for this quiz
xml = urlopen(Request(f"{BASE}/mod/quiz/accessrule/seb/config.php?cmid={CMID}",
                      headers={"Cookie": f"MoodleSession={COOKIE}"})).read()
key = compute_config_key(xml)

# 2. Client
cl = MoodleClient(BASE, COOKIE, config_key=key)
attempt = cl.start_attempt(CMID)             # opens view.php + startattempt.php
questions = cl.load_page(attempt, CMID)      # parse page 0
for q in questions:
    print(q.slot, q.qtype, q.text[:80])
# ... fill answers dict {field_name: value} ...
# cl.submit_page(attempt, CMID, page=0, answers=..., last_page=True)
# cl.finish(attempt, CMID)
```

## Answers cheat-sheet (field formats)

Moodle expects answers POSTed to `mod/quiz/processattempt.php`.
Field names and values by question type:

| Question type | Fields | Values |
|---|---|---|
| `multichoice` (radio) | `q<qubaid>:<slot>_answer` | option index (`0`, `1`, …) |
| `multichoice` (checkboxes) | `q<qubaid>:<slot>_choice<N>` | `1` for each selected |
| `truefalse` | `q<qubaid>:<slot>_answer` | `0` = True, `1` = False |
| `shortanswer` | `q<qubaid>:<slot>_answer` | URL-encoded text |
| `ddwtos` (drag into text) | `q<qubaid>:<slot>_p<N>` | **choice number as shown in the drag list (1-based)** |
| `multianswer` (cloze) | `q<qubaid>:<slot>_sub<N>_answer` | option index of that dropdown |

Plus, for **every** question slot on the page (this is what everyone gets wrong):

```
q<qubaid>:<slot>_:sequencecheck = <value from the hidden input>
q<qubaid>:<slot>_:flagged       = 0
```

And the page-level params: `attempt`, `thispage`, `nextpage` (`page+1`, or `-1` on the
last page), `timeup=0`, `sesskey`, `slots`, `next=Next page` / `Finish attempt ...`.

> ⚠️ Moodle often **re-randomises questions between attempts**: the internal
> `qubaid` and the option order can change. Always re-parse the attempt page
> before submitting instead of replaying an old answer sheet.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Quiz still says "requires SEB" | Wrong `--url` host in `seb_url`, or the proxy is not actually used by the browser. Check `mitmdump` console — you should see your requests. |
| `config-key` prints HTML instead of a hash | Session cookie expired or quiz ID wrong. Re-copy `MoodleSession`. |
| Answers don't register (attempt ends with everything empty) | Missing `_:sequencecheck` fields — see the cheat-sheet above. |
| Browser complains about certificates | Trust mitmproxy's CA from <http://mitm.it> (only needed in proxy mode). |
| `startattempt` redirects to the quiz start page | Attempt limit reached, or the quiz has a password / time window. |

## Project layout

```
seb_bypass/
  configkey.py    # ConfigKey + header-hash maths (the whole "crypto")
  mitm_addon.py   # mitmproxy add-on — transparent SEB patcher
  client.py       # headless Moodle client + question parser
  cli.py          # `seb-bypass` console command
tests/
  test_configkey.py
```

## Legal / ethics

This project reproduces the SEB handshake protocol; it does not hack anything.
Use it for quizzes where *you* are allowed to use your own environment, and
always follow your institution's academic-integrity policy.

## License

MIT
