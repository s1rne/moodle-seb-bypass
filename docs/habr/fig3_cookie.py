import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

W, H = 11.0, 6.4
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, 110)
ax.set_ylim(0, 64)
ax.axis("off")
INK, MUT, ACC, BG = "#1a1a2e", "#666a75", "#e76f51", "#ffffff"

# --- browser window mock ---
ax.add_patch(FancyBboxPatch((4, 6), 62, 52,
             boxstyle="round,pad=0.6,rounding_size=1.5",
             fc="#fbfbfd", ec="#c8ccd4", lw=1.5))
# traffic lights
for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    ax.add_patch(plt.Circle((10 + i*4.2, 53.5), 1.5, fc=c, ec="none"))
ax.add_patch(FancyBboxPatch((26, 51), 36, 5,
             boxstyle="round,pad=0.3,rounding_size=2.5",
             fc="#eef0f4", ec="none"))
ax.text(44, 53.5, "moodle.example.org  •  devtools", ha="center", va="center",
        fontsize=9, color=MUT, family="monospace")

# devtools split
ax.add_patch(Rectangle((7, 9), 56, 38, fc="white", ec="#d8dce2", lw=1))
ax.add_patch(Rectangle((7, 38), 56, 9, fc="#e8f4f8", ec="#d8dce2", lw=1))
ax.text(10, 42.5, "F12 → Application → Cookies → https://moodle.example.org",
        fontsize=9.5, color=INK, va="center")

# cookie table
ax.add_patch(Rectangle((7, 9), 56, 29, fc="white", ec="none"))
hdr = ["Name", "Value", ""]
rows = [
    ("MoodleSession", "f8hkq3u7…", True),
    ("MoodleBlast",    "——",      False),
]
y = 34.5
ax.text(11, y, "Name", fontsize=9, fontweight="bold", color=MUT)
ax.text(33, y, "Value", fontsize=9, fontweight="bold", color=MUT)
y -= 4.5
for name, val, hot in rows:
    if hot:
        ax.add_patch(Rectangle((8, y - 3.2), 54, 4.4, fc="#fff3e9", ec="none"))
    ax.text(11, y, name, fontsize=9.5, family="monospace",
            color=ACC if hot else INK, fontweight="bold" if hot else "normal")
    ax.text(33, y, val, fontsize=9.5, family="monospace",
            color=ACC if hot else MUT)
    y -= 5.2

ax.add_patch(FancyArrowPatch((26.5, 26.8), (30, 26.8), arrowstyle="-",
             mutation_scale=0, lw=0))  # spacer no-op

# arrow from cookie row to terminal
ax.add_patch(FancyArrowPatch((63.5, 27.5), (78, 20), arrowstyle="-|>",
             mutation_scale=20, lw=2.2, color=ACC,
             connectionstyle="arc3,rad=-0.25"))
ax.text(71.5, 29.5, "копируем значение\nMoodleSession", fontsize=10,
        color=ACC, ha="center", fontweight="bold")

# terminal mock
ax.add_patch(FancyBboxPatch((70, 8), 36, 16,
             boxstyle="round,pad=0.6,rounding_size=1.2",
             fc="#10141f", ec="none"))
ax.text(73.5, 20.5, "$ export MOODLE_COOKIE=\"f8hkq3u7…\"",
        fontsize=9, family="monospace", color="#7ee787", va="center")
ax.text(73.5, 15.5, "$ seb-bypass config-key --url … --cmid 42",
        fontsize=9, family="monospace", color="#79c0ff", va="center")
ax.text(73.5, 11.0, "ConfigKey: 9a78a7ab9c92…", fontsize=9,
        family="monospace", color="#e6edf3", va="center")

ax.text(55, 61.5, "Всё, что нужно от браузера: одна cookie и DevTools",
        ha="center", fontsize=13, fontweight="bold", color=INK)

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig3_cookie.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
