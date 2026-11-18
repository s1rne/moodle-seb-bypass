import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, H = 13.2, 6.8
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 132)
ax.set_ylim(0, 68)
ax.axis("off")

INK, MUT, ACC, BG = "#1a1a2e", "#666a75", "#e76f51", "#ffffff"

ax.text(66, 63, "От XML-конфига до ConfigKey: четыре шага", ha="center",
        fontsize=14, fontweight="bold", color=INK)
ax.text(66, 58.5, "если хоть один шаг сделать иначе, Moodle ответит «не тот браузер»",
        ha="center", fontsize=10.5, color=MUT)

stages = [
    ("XML PList", [
        "<plist>",
        "  <dict>",
        "    <key>allowWlan</key>",
        "    <true/>",
        "    …",
        "    <key>originatorVersion</key>",
        "    <string>SEB_3.7.0</string>",
    ], "#f1faee", "#adb5bd", INK),
    ("Убрать originatorVersion", [
        "SEB вписывает в конфиг",
        "свою версию, но в хеш",
        "она не входит:",
        "плагин выбрасывает",
        "ключ перед подсчётом",
    ], "#fff3e9", ACC, INK),
    ("Отсортировать ключи", [
        "рекурсивно, каждый",
        "словарь, без учёта",
        "регистра (casefold):",
        "порядок ключей не",
        "должен влиять на хеш",
    ], "#fff3e9", ACC, INK),
    ("Сериализовать в JSON", [
        "компактно, без пробелов",
        'и \\u-экранирования:',
        '{"allowWlan":true,…}',
        "одна строка",
    ], "#fff3e9", ACC, INK),
    ("ConfigKey", [
        "SHA256(json)",
        "= 9a78a7ab9c92…",
        "64 hex-символа —",
        "«паспорт» квиза",
    ], "#264653", "#264653", "white"),
]

bw, bh, gap = 22.0, 34, 4.0
x = 5
for i, (title, lines, fc, ec, tc) in enumerate(stages):
    ax.add_patch(FancyBboxPatch((x, 12), bw, bh,
                 boxstyle="round,pad=0.5,rounding_size=1.0",
                 fc=fc, ec=ec, lw=1.6))
    ax.text(x + bw/2, 12 + bh - 3.0, title, ha="center", va="top",
            fontsize=10.2, fontweight="bold", color=tc)
    body = "\n".join(lines)
    fam = "monospace" if i == 0 else None
    ax.text(x + bw/2, 12 + bh - 8.0, body, ha="center", va="top",
            fontsize=7.6 if i == 0 else 8.2, color=tc,
            family=fam, linespacing=1.65)
    if i < len(stages) - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.8, 29), (x + bw + gap - 0.8, 29),
                     arrowstyle="-|>", mutation_scale=17, lw=2, color=MUT))
    x += bw + gap

ax.add_patch(FancyBboxPatch((16, 2), 100, 6.5,
             boxstyle="round,pad=0.4,rounding_size=0.8",
             fc="#eaf4f4", ec="#2a9d8f", lw=1.4))
ax.text(66, 5.2, "в заголовок идёт ещё один хеш:   SHA256( URL_без_query + ConfigKey )",
        ha="center", fontsize=10.5, family="monospace", color=INK)

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig2_configkey.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
