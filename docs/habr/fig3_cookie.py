import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

W, H = 11.6, 6.2
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 116)
ax.set_ylim(0, 62)
ax.axis("off")
INK, MUT, ACC, BG = "#1a1a2e", "#666a75", "#e76f51", "#ffffff"

ax.text(58, 58.5, "Всё, что нужно от браузера: одна cookie и DevTools",
        ha="center", fontsize=13.5, fontweight="bold", color=INK)

# ---------- browser window ----------
bx, by, bw, bh = 5, 4, 62, 50
ax.add_patch(FancyBboxPatch((bx, by), bw, bh,
             boxstyle="round,pad=0.6,rounding_size=1.5",
             fc="#fbfbfd", ec="#c8ccd4", lw=1.5))
for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    ax.add_patch(Circle((bx + 5 + i*4.0, by + bh - 3.6), 1.4, fc=c, ec="none"))
ax.add_patch(FancyBboxPatch((bx + 20, by + bh - 6.2), bw - 26, 5.0,
             boxstyle="round,pad=0.3,rounding_size=2.4",
             fc="#eef0f4", ec="none"))
ax.text(bx + 20 + (bw - 26)/2, by + bh - 3.7, "moodle.example.org",
        ha="center", va="center", fontsize=8.5, color=MUT, family="monospace")

# devtools panel
dx, dy, dw, dh = bx + 3, by + 4, bw - 6, bh - 14
ax.add_patch(Rectangle((dx, dy), dw, dh, fc="white", ec="#d8dce2", lw=1))
# tab bar
ax.add_patch(Rectangle((dx, dy + dh - 5), dw, 5, fc="#e8f4f8", ec="#d8dce2", lw=1))
ax.text(dx + 2.5, dy + dh - 2.5, "Application ▸ Cookies ▸ https://moodle.example.org",
        fontsize=8.3, color=INK, va="center")

# table header
ty = dy + dh - 9.5
ax.text(dx + 3, ty, "Name", fontsize=8.5, fontweight="bold", color=MUT)
ax.text(dx + 22, ty, "Value", fontsize=8.5, fontweight="bold", color=MUT)
ax.add_patch(Rectangle((dx + 1.5, ty - 3.6), dw - 3, 4.8, fc="#fff3e9", ec="none"))
ax.text(dx + 3, ty - 1.3, "MoodleSession", fontsize=9, family="monospace",
        color=ACC, fontweight="bold")
ax.text(dx + 22, ty - 1.3, "f8hkq3u7v2…", fontsize=9, family="monospace", color=ACC)
ax.text(dx + 3, ty - 7.0, "MoodleBlast", fontsize=9, family="monospace", color=MUT)
ax.text(dx + 22, ty - 7.0, "—", fontsize=9, family="monospace", color=MUT)

# ---------- terminal ----------
tx, ty2, tw, th = 82, 20, 30, 20
ax.add_patch(FancyBboxPatch((tx, ty2), tw, th,
             boxstyle="round,pad=0.6,rounding_size=1.2",
             fc="#10141f", ec="none"))
ax.text(tx + 2.5, ty2 + th - 4.0, "$ export MOODLE_COOKIE=\\",
        fontsize=8.3, family="monospace", color="#7ee787", va="center")
ax.text(tx + 5.0, ty2 + th - 8.0, '"f8hkq3u7v2…"', fontsize=8.3,
        family="monospace", color="#7ee787", va="center")
ax.text(tx + 2.5, ty2 + th - 12.5, "$ seb-bypass config-key \\",
        fontsize=8.3, family="monospace", color="#79c0ff", va="center")
ax.text(tx + 5.0, ty2 + th - 16.5, "--url … --cmid 42",
        fontsize=8.3, family="monospace", color="#79c0ff", va="center")

# arrow cookie -> terminal
ax.add_patch(FancyArrowPatch((bx + bw + 1, 30), (tx - 1.5, 30),
             arrowstyle="-|>", mutation_scale=20, lw=2.2, color=ACC))
ax.text((bx + bw + tx)/2, 33.6, "копируем значение",
        fontsize=9.5, color=ACC, ha="center", fontweight="bold")
ax.text((bx + bw + tx)/2, 25.8, "MoodleSession",
        fontsize=9.5, color=ACC, ha="center", fontweight="bold",
        family="monospace")

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig3_cookie.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
