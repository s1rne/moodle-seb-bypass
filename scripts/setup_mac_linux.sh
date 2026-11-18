#!/usr/bin/env bash
# === moodle-seb-bypass: быстрый старт для macOS / Linux ===
set -euo pipefail

if ! command -v python3 >/dev/null; then
  echo "[!] Python3 не найден. macOS: brew install python | Linux: apt install python3 python3-pip"
  exit 1
fi

python3 -m pip install -e .
python3 -m pip install mitmproxy

python3 -m unittest discover -s tests -v

cat <<'EOF'

Готово! Дальше:
  1. Скопируй cookie MoodleSession из браузера.
  2. seb-bypass config-key --url https://moodle.example.org --cmid 12345 --cookie COOKIE
  3. mitmdump -s seb_bypass/mitm_addon.py --set seb_url=https://moodle.example.org
  4. Запусти Chrome через прокси:  google-chrome --proxy-server="http://127.0.0.1:8080"
     (или настрой системный прокси 127.0.0.1:8080) и открой квиз.
EOF
