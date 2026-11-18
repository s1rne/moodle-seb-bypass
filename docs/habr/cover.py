import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (FancyBboxPatch, Circle, Rectangle, Arc,
                                FancyBboxPatch as Pill)
from matplotlib.colors import LinearSegmentedColormap

fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
ax.set_xlim(0, 128)
ax.set_ylim(0, 72)
ax.axis("off")

BG      = "#0d1321"
WIN     = "#131b30"
CHROME  = "#182142"
BORDER  = "#2e3a5c"
MUT     = "#7d88a3"
FAINT   = "#56617a"
ORANGE  = "#e76f51"
ORANGE2 = "#f4a261"
GREEN   = "#7ee787"
HASHC   = "#9ecbff"

# ---------- background with two soft glows ----------
X, Y = np.meshgrid(np.linspace(0, 128, 320), np.linspace(0, 72, 180))
g1 = np.exp(-(((X - 44) / 36.0) ** 2 + ((Y - 30) / 24.0) ** 2))
g2 = np.exp(-(((X - 92) / 40.0) ** 2 + ((Y - 44) / 28.0) ** 2))
Z = np.maximum(g1, 0.65 * g2)
cmap = LinearSegmentedColormap.from_list("glow", [BG, "#22335c"])
ax.imshow(Z, extent=(0, 128, 0, 72), origin="lower", aspect="auto",
          cmap=cmap, zorder=0)

# ---------- browser window ----------
wx, wy, ww, wh = 14, 10, 100, 52
ax.add_patch(FancyBboxPatch((wx, wy), ww, wh,
             boxstyle="round,pad=0.6,rounding_size=1.8",
             fc=WIN, ec=BORDER, lw=2, zorder=2))
ax.add_patch(Rectangle((wx, wy + wh - 7), ww, 7, fc=CHROME, ec="none", zorder=3))
ax.plot([wx + 0.5, wx + ww - 0.5], [wy + wh - 7, wy + wh - 7],
        color=BORDER, lw=1.2, zorder=4)

for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    ax.add_patch(Circle((wx + 5 + i * 4.4, wy + wh - 3.6), 1.35,
                 fc=c, ec="none", zorder=5))

# URL bar with mini https-lock
ux, uy, uw, uh = wx + 20, wy + wh - 5.9, 62, 4.2
ax.add_patch(FancyBboxPatch((ux, uy), uw, uh,
             boxstyle="round,pad=0.25,rounding_size=2.1",
             fc="#0f1626", ec="#26314f", lw=1, zorder=5))
lx, ly = ux + 3.2, uy + uh / 2 - 0.6
ax.add_patch(Rectangle((lx, ly), 1.7, 1.3, fc="#4ade80", ec="none", zorder=6))
ax.add_patch(Arc((lx + 0.85, ly + 1.25), 1.5, 1.7, theta1=0, theta2=180,
                 lw=1.4, color="#4ade80", zorder=6))
ax.text(ux + 6.4, uy + uh / 2, "moodle.example.org/mod/quiz/view.php?id=42",
        fontsize=9, family="monospace", color=MUT, va="center", zorder=6)

# ---------- big padlock ----------
cx = 44
ax.add_patch(Arc((cx, 40), 19, 17, theta1=0, theta2=180,
                 lw=6, color=ORANGE2, zorder=5))
ax.add_patch(FancyBboxPatch((cx - 14, 18), 28, 22,
             boxstyle="round,pad=0.4,rounding_size=2.2",
             fc=ORANGE, ec="none", zorder=6))
ax.add_patch(FancyBboxPatch((cx - 12.5, 36.5), 12, 3.2,
             boxstyle="round,pad=0.3,rounding_size=1.4",
             fc="white", ec="none", alpha=0.14, zorder=7))
ax.add_patch(Circle((cx, 31), 2.6, fc="#35160e", ec="none", zorder=7))
ax.add_patch(Rectangle((cx - 1.1, 24.5), 2.2, 5.2, fc="#35160e",
             ec="none", zorder=7))

# ---------- hash block ----------
hx = 66
ax.text(hx, 47.5, "X-SafeExamBrowser-ConfigKeyHash",
        fontsize=11.5, fontweight="bold", family="monospace",
        color=GREEN, zorder=6)
ax.text(hx, 41.5, "9a78a7ab9c929416c953cb05b9a6f51",
        fontsize=10.5, family="monospace", color=HASHC, zorder=6)
ax.text(hx, 36.5, "d43f77399074515243c42826307914468",
        fontsize=10.5, family="monospace", color=HASHC, zorder=6)
ax.text(hx, 30.5, "SHA256 \u2713", fontsize=11, fontweight="bold",
        family="monospace", color=GREEN, zorder=6)
ax.text(hx, 23.5, "сервер думает: это SEB",
        fontsize=10.5, style="italic", color=MUT, zorder=6)

# ---------- badge ----------
ax.add_patch(FancyBboxPatch((14, 64.5), 34, 5.6,
             boxstyle="round,pad=0.35,rounding_size=2.8",
             fc=ORANGE, ec="none", zorder=6))
ax.text(31, 67.3, "PYTHON × MITMPROXY", fontsize=9.5, fontweight="bold",
        color="white", ha="center", va="center", zorder=7)

# ---------- footer ----------
ax.text(114, 4.6, "github.com/s1rne/moodle-seb-bypass",
        fontsize=8, family="monospace", color=FAINT, ha="right", zorder=6)

fig.savefig("/Users/alexander/moodle-seb-bypass/docs/habr/cover.png",
            bbox_inches="tight", facecolor=BG)
print("ok")
