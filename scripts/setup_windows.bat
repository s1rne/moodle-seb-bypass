@echo off
REM === moodle-seb-bypass: быстрый старт для Windows (PowerShell не требуется) ===
REM 1) Проверяем Python
where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python не найден. Установи с https://www.python.org/downloads/ ^(галочка "Add to PATH"^).
    pause
    exit /b 1
)

REM 2) Зависимости
python -m pip install -e . || (pause & exit /b 1)
python -m pip install mitmproxy || (pause & exit /b 1)

REM 3) Тесты
python -m unittest discover -s tests -v

echo.
echo Готово! Дальше:
echo   1. Скопируй cookie MoodleSession из браузера.
echo   2. seb-bypass config-key --url https://moodle.example.org --cmid 12345 --cookie COOKIE
echo   3. mitmdump -s seb_bypass/mitm_addon.py --set seb_url=https://moodle.example.org
echo   4. Пропиши в браузере прокси 127.0.0.1:8080 и открой квиз.
pause
