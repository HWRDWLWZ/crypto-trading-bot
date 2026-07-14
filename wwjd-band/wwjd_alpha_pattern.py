#!/usr/bin/env python3
"""WWJD 織りブレスレット用「アルファパターン」図案ジェネレータ。

写真のような布製 WWJD バンド(文字がドット状に織り込まれたタイプ)を
個人で再現するための図案を生成する。手編みミサンガ・ビーズ織り機・
クロスステッチ・工場への入稿用、いずれにも使えるドット図。

使い方:
    python3 wwjd_alpha_pattern.py
    python3 wwjd_alpha_pattern.py "WWJD" "#1f4fb0" "#ffffff"   # 文字色 / 地色
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- 5x7 ピクセルフォント(1=文字, 0=地) ---
FONT = {
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "01010"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
}
GLYPH_W = 5
GLYPH_H = 7


def build_grid(text, pad_x=2, gap=1):
    """文字列を縦に積んだドットグリッド(2次元 0/1 配列)を返す。"""
    cols = GLYPH_W + pad_x * 2
    rows = []
    rows += [[0] * cols for _ in range(pad_x)]            # 上余白
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT["."])
        for line in glyph:
            row = [0] * pad_x + [int(c) for c in line] + [0] * pad_x
            rows.append(row)
        if i != len(text) - 1:
            rows += [[0] * cols for _ in range(gap)]      # 文字間ギャップ
    rows += [[0] * cols for _ in range(pad_x)]            # 下余白
    return rows


def render(text, fg, bg, out):
    grid = build_grid(text)
    nrows, ncols = len(grid), len(grid[0])
    fig, ax = plt.subplots(figsize=(ncols * 0.45, nrows * 0.45))
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            ax.add_patch(plt.Rectangle((c, nrows - 1 - r), 1, 1,
                         facecolor=fg if v else bg,
                         edgecolor="#cccccc", lw=0.6))
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.set_aspect("equal")
    ax.set_xticks(range(ncols + 1))
    ax.set_yticks(range(nrows + 1))
    ax.tick_params(labelbottom=False, labelleft=False, length=0)
    ax.grid(False)
    ax.set_title(f'WWJD band pattern  ({ncols} cols x {nrows} rows)\n'
                 f'text {fg} / bg {bg}', fontsize=9)
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"wrote {out}  ({ncols} 列 x {nrows} 段)")


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "W.W.J.D"
    fg = sys.argv[2] if len(sys.argv) > 2 else "#1f4fb0"   # 文字色(既定: 青)
    bg = sys.argv[3] if len(sys.argv) > 3 else "#ffffff"   # 地色(既定: 白)
    render(text, fg, bg, "wwjd_pattern.png")
