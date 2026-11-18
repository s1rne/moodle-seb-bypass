import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, H = 12.8, 6.2
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 128)
ax.set_ylim(0, 62)
ax.axis("off")

INK = "#1a1a2e"
MUT = "#666a75"
ACC = "#e76f51"
BG = "#ffffff"

stages = [
    ("XML PList", '<plist>\n  <dict>\n    <key>allowWlan</key>\n    <true/>\n    ...\n    <key>originatorVersion</key>\n    <string>SEB_3.7.0</string>', "#f1faee", "#adb5bd", INK),
    ("Шаг 1. Убрать originatorVersion", 'SEB кладёт в конфиг свою версию,\nно в хеш она не входит —\nплагин её выкидывает перед подсчётом', "#fff3e9", ACC, INK),
    ("Шаг 2. Отсортировать ключи", 'рекурсивно, каждый словарь,\nбез учёта регистра (casefold),\nпорядок не должен зависеть ни от чего', "#fff3e9", ACC, INK),
    ("Шаг 3. Сериализовать в JSON", 'без пробелов, без \\u-экранирования:\n{"allowWlan":true,...}\nодна строка, компактно', "#fff3e9", ACC, INK),
    ("ConfigKey", 'SHA256(json)\n= 9a78a7ab9c92…\n64 hex-символа — это и есть "паспорт" квиза', "#264653", "#264653", "white"),
]

bw, bh, gap = 22.4, 34, 2.5
x = 3
for i, (title, body, fc, ec, tc) in enumerate(stages):
    ax.add_patch(FancyBboxPatch((x, 14), bw, bh,
                 boxstyle="round,pad=0.5,rounding_size=1.0",
                 fc=fc, ec=ec, lw=1.6))
    ax.text(x + bw/2, 14 + bh - 2.2, title, ha="center", va="top",
            fontsize=10.6, fontweight="bold", color=tc)
    ax.text(x + bw/2, 14 + bh - 7.5, body, ha="center", va="top",
            fontsize=8.4, color=tc, family="monospace", linespacing=1.5)
    if i < len(stages) - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.4, 31), (x + bw + gap - 0.4, 31),
                     arrowstyle="-|>", mutation_scale=18, lw=2, color=MUT))
    x += bw + gap

ax.text(64, 56, "От XML-конфига до ConfigKey: четыре шага, которые нельзя перепутать",
        ha="center", fontsize=13.5, fontweight="bold", color=INK)
ax.text(64, 51.5, "если хоть один шаг отличается — Moodle ответит «не тот браузер»",
        ha="center", fontsize=10.5, color=MUT)

# bottom annotation: what the header hash is
ax.add_patch(FancyBboxPatch((14, 2.5), 100, 7.5,
             boxstyle="round,pad=0.4,rounding_size=0.8",
             fc="#eaf4f4", ec="#2a9d8f", lw=1.4))
ax.text(64, 6.2, "А в заголовок идёт ещё один хеш:  X-SafeExamBrowser-ConfigKeyHash = SHA256( URL_без_query + ConfigKey )",
        ha="center", fontsize=10.5, family="monospace", color=INK)

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig2_configkey.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
