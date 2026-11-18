import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, H = 12.8, 7.0
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 128)
ax.set_ylim(0, 70)
ax.axis("off")

INK = "#1a1a2e"
MUT = "#666a75"
SEB = "#e76f51"
MOODLE = "#264653"
CLIENT = "#2a9d8f"
BG = "#ffffff"

def box(x, y, w, h, fc, ec, title, lines=(), fs=11.5, tfs=13, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.6,rounding_size=1.2",
                 fc=fc, ec=ec, lw=1.6))
    ax.text(x + w/2, y + h - 3.4, title, ha="center", va="top",
            fontsize=tfs, fontweight="bold", color=tc)
    for i, ln in enumerate(lines):
        ax.text(x + w/2, y + h - 8.2 - i*3.6, ln, ha="center", va="top",
                fontsize=fs, color=tc, alpha=0.93)

box(4, 40, 34, 22, CLIENT, CLIENT, "Обычный браузер",
    ("Chrome / Firefox", "ничего не установлено", "SEB-заголовки подставляет", "mitmproxy на лету"), fs=10.5)
box(47, 40, 34, 22, "#8ecae6", "#219ebc", "mitmproxy",
    ("локальный прокси", "127.0.0.1:8080", "считает SHA256", "и вставляет заголовок"), fs=10.5, tc=INK)
box(90, 40, 34, 22, MOODLE, MOODLE, "Moodle",
    ("плагин quizaccess_seb", "сверяет заголовок", "X-…ConfigKeyHash", "кэширует успех в сессию"), fs=10.5)

for x0, x1, label, sub in [
    (38, 47, "HTTPS", "через прокси"),
    (81, 90, "HTTPS", "с SEB-заголовками"),
]:
    ax.add_patch(FancyArrowPatch((x0, 52.5), (x1, 52.5),
                 arrowstyle="-|>", mutation_scale=22, lw=2, color=INK))
    ax.text((x0+x1)/2, 55.2, label, ha="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.text((x0+x1)/2, 49.6, sub, ha="center", fontsize=9.5, color=MUT)

ax.text(64, 34.5, "Как Moodle решает, пускать ли вас на тест", ha="center",
        fontsize=13.5, fontweight="bold", color=INK)

steps = [
    ("1", "Сервер отдаёт конфиг SEB", "GET …/seb/config.php\n?cmid=…"),
    ("2", "Считаем ConfigKey", "SHA256( PList\n→ компактный JSON )"),
    ("3", "Считаем хеш заголовка", "SHA256( URL\n+ ConfigKey )"),
    ("4", "Шлём с каждым запросом", "X-SafeExamBrowser-\nConfigKeyHash: …"),
    ("5", "Moodle сверяет и кэширует", "успех живёт\nв PHP-сессии"),
]
x = 6
for n, t, s in steps:
    ax.add_patch(FancyBboxPatch((x, 8), 23, 17,
                 boxstyle="round,pad=0.5,rounding_size=1.0",
                 fc="#f1faee", ec="#adb5bd", lw=1.2))
    ax.add_patch(plt.Circle((x+3.2, 21.5), 2.1, fc=SEB, ec="none"))
    ax.text(x+3.2, 21.5, n, ha="center", va="center", fontsize=12,
            fontweight="bold", color="white")
    ax.text(x+13.2, 21.8, t, ha="center", va="top", fontsize=9.6,
            fontweight="bold", color=INK)
    ax.text(x+11.5, 15.2, s, ha="center", va="top", fontsize=8.2,
            color=MUT, family="monospace", linespacing=1.45)
    x += 24.4

for x0 in [29.4, 53.8, 78.2, 102.6]:
    ax.add_patch(FancyArrowPatch((x0+0.3, 16.5), (x0+2.1, 16.5),
                 arrowstyle="-|>", mutation_scale=16, lw=1.6, color=MUT))

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig1_protocol.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
