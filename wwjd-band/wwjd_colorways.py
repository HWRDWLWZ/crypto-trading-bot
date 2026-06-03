#!/usr/bin/env python3
"""WWJD バンドのカラーウェイ一覧(コンタクトシート)を1枚に生成。
写真のような複数色のバリエーションを並べて確認・配布用に使う。
    python3 wwjd_colorways.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wwjd_alpha_pattern import build_grid

# (文字色, 地色, ラベル)
COLORWAYS = [
    ("#1f4fb0", "#ffffff", "blue/white"),
    ("#ffffff", "#ff5aa0", "white/pink"),
    ("#ffffff", "#111111", "white/black"),
    ("#ffffff", "#c0322b", "white/red"),
    ("#ffffff", "#1f7a44", "white/green"),
    ("#ffffff", "#7a4fc0", "white/purple"),
    ("#ffffff", "#ff7a1a", "white/orange"),
    ("#ffffff", "#f2c200", "white/yellow"),
    ("#111111", "#ffffff", "black/white"),
    ("#ffffff", "#7f7f7f", "white/gray"),
]

grid = build_grid("W.W.J.D")
nrows, ncols = len(grid), len(grid[0])
gap = 3  # バンド間の余白(列)

fig, ax = plt.subplots(figsize=(len(COLORWAYS) * (ncols + gap) * 0.16, nrows * 0.16))
for b, (fg, bg, label) in enumerate(COLORWAYS):
    x0 = b * (ncols + gap)
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            ax.add_patch(plt.Rectangle((x0 + c, nrows - 1 - r), 1, 1,
                         facecolor=fg if v else bg, edgecolor="#dddddd", lw=0.3))
    ax.text(x0 + ncols / 2, -2, label, ha="center", va="top", fontsize=7)

ax.set_xlim(-1, len(COLORWAYS) * (ncols + gap))
ax.set_ylim(-6, nrows + 1)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("WWJD band — colorways", fontsize=11)
plt.tight_layout()
plt.savefig("wwjd_colorways.png", dpi=150)
print("wrote wwjd_colorways.png")
