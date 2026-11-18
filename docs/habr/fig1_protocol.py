import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

W, H = 12.8, 7.0
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 128)
ax.set_ylim(0, 70)
ax.axis("off")

INK, MUT = "#1a1a2e", "#666a75"
SEB, CLIENT, BG = "#e76f51", "#2a9d8f", "#ffffff"


def box(x, y, w, h, fc, ec, tc, title, lines, fs=10, tfs=12.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.5,rounding_size=1.0",
                 fc=fc, ec=ec, lw=1.6))
    ax.text(x + w/2, y + h - 3.6, title, ha="center", va="top",
            fontsize=tfs, fontweight="bold", color=tc)
    for i, ln in enumerate(lines):
        ax.text(x + w/2, y + h - 9.0 - i*3.8, ln, ha="center", va="top",
                fontsize=fs, color=tc, alpha=0.95)


# ---- three actors: w=30, gaps ~13 units ----
box(6, 42, 30, 20, CLIENT, CLIENT, "white", "Обычный браузер",
    ("Chrome / Firefox,", "ничего не установлено,", "заголовки подставляет", "mitmproxy на лету"))
box(49, 42, 30, 20, "#8ecae6", "#219ebc", INK, "mitmproxy",
    ("локальный прокси", "127.0.0.1:8080,", "считает SHA256 и", "вставляет заголовок"))
box(92, 42, 30, 20, "#264653", "#264653", "white", "Moodle",
    ("плагин quizaccess_seb", "сверяет заголовок", "X-…ConfigKeyHash", "и кэширует успех в сессию"))

for x0, x1, label, sub in [(37.3, 48.7, "HTTPS", "через прокси"),
                           (80.3, 91.7, "HTTPS", "уже как SEB")]:
    ax.add_patch(FancyArrowPatch((x0, 52), (x1, 52),
                 arrowstyle="-|>", mutation_scale=20, lw=2, color=INK))
    ax.text((x0+x1)/2, 55.0, label, ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.text((x0+x1)/2, 49.2, sub, ha="center", fontsize=8.5, color=MUT)

ax.text(64, 34.8, "Как Moodle решает, пускать ли вас на тест", ha="center",
        fontsize=13, fontweight="bold", color=INK)

# ---- five steps: w=20, spacing 25.2, clearance 4.2 ----
steps = [
    ("1", "Сервер отдаёт\nконфиг SEB", "GET …/seb/config.php\n?cmid=…"),
    ("2", "Считаем\nConfigKey", "SHA256(PList →\nкомпактный JSON)"),
    ("3", "Считаем хеш\nзаголовка", "SHA256(URL +\nConfigKey)"),
    ("4", "Шлём с каждым\nзапросом", "X-SafeExamBrowser-\nConfigKeyHash"),
    ("5", "Moodle сверяет\nи кэширует", "успех живёт в\nPHP-сессии"),
]
x = 6
for n, t, s in steps:
    ax.add_patch(FancyBboxPatch((x, 5), 20, 20,
                 boxstyle="round,pad=0.5,rounding_size=1.0",
                 fc="#f1faee", ec="#adb5bd", lw=1.2))
    ax.add_patch(Circle((x+10, 21.3), 2.0, fc=SEB, ec="none"))
    ax.text(x+10, 21.3, n, ha="center", va="center", fontsize=11,
            fontweight="bold", color="white")
    ax.text(x+10, 17.0, t, ha="center", va="top", fontsize=9,
            fontweight="bold", color=INK, linespacing=1.35)
    ax.text(x+10, 8.2, s, ha="center", va="top", fontsize=7.2,
            color=MUT, family="monospace", linespacing=1.45)
    if n != "5":
        ax.add_patch(FancyArrowPatch((x+21.2, 15), (x+24.2, 15),
                     arrowstyle="-|>", mutation_scale=13, lw=1.5, color=MUT))
    x += 25.2

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig1_protocol.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
