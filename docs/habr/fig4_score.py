import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

INK, MUT, ACC, GREEN = "#1a1a2e", "#666a75", "#e76f51", "#2a9d8f"
BG = "#ffffff"

quizzes = [
    ("7.1 Vocab",      20.0, 20.0),
    ("7.2 Grammar",    20.0, 20.0),
    ("8.1 Vocab",      20.0, 20.0),
    ("8.2 Grammar",    20.0, 20.0),
    ("9.1 Vocab",      20.0, 20.0),
    ("9.2 Grammar",    20.0, 20.0),
    ("10.1 Vocab",     20.0, 20.0),
    ("10.2 Grammar",   20.0, 20.0),
    ("Midterm (SEB)",  20.0, 20.0),
    ("11.1 Vocab",     20.0, 20.0),
    ("11.2 Grammar",   20.0, 18.33),
    ("11.4 Listen",    20.0, 16.0),
    ("11.4 Read",      20.0, 20.0),
    ("12.1 Vocab",     20.0, 19.0),
    ("12.2 Vocab",     20.0, 20.0),
    ("12.4 Listen",    20.0, 20.0),
    ("Final (SEB)",    10.0,  9.5),
]
labels  = [q[0] for q in quizzes]
full    = np.array([q[1] for q in quizzes])
got     = np.array([q[2] for q in quizzes])

y = np.arange(len(quizzes))
fig, ax = plt.subplots(figsize=(10.5, 8.2), dpi=150)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.barh(y, full, height=0.62, color="#e9ecef", edgecolor="none", zorder=1)
colors = [GREEN if g == f else ACC for g, f in zip(got, full)]
ax.barh(y, got, height=0.62, color=colors, edgecolor="none", zorder=2)

for yi, (g, f) in enumerate(zip(got, full)):
    if g == f:
        ax.text(g + 0.25, yi, f"{g:.0f}", va="center", fontsize=9,
                color=GREEN, fontweight="bold")
    else:
        ax.text(g + 0.25, yi, f"{g:g}", va="center", fontsize=9,
                color=ACC, fontweight="bold")

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10)
ax.invert_yaxis()
ax.set_xlim(0, 22.5)
ax.set_xticks([0, 5, 10, 15, 20])
ax.tick_params(axis="x", colors=MUT, labelsize=9)
ax.tick_params(axis="y", colors=INK)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8dce2")
ax.grid(axis="x", color="#eef0f4", zorder=0)
ax.set_axisbelow(True)

ax.set_title("Квизы курса, решённые скриптом: 772 из 780 баллов (98.71%)",
             fontsize=13.5, fontweight="bold", color=INK, pad=14, loc="left")
from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(fc=GREEN, label="максимальный балл"),
    Patch(fc=ACC,  label="потеряны баллы"),
], loc="lower right", frameon=False, fontsize=10)

ax.text(0, -1.6, "серая полоса — максимально возможный балл квиза",
        fontsize=9, color=MUT)

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/fig4_score.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
