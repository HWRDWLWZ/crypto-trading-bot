#!/usr/bin/env python3
"""Fitbit Air ペブルを保持するスリーブの断面概念図(公式寸法版)。
寸法は Google 公式ブループリント D-0001799540 由来。
    python3 fitbit_sleeve_section.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

# 公式値(短軸断面 = section C-C 相当)
peb_w   = 14.36   # ペブル最大幅(膨らみ)
sl_open = 13.77   # スリーブ内開口(リップ部)
peb_h   = 7.0     # ★高さ:要実測(仮)
wall    = 2.0
floor_t = 0.8
lip_h   = 0.65
win_w   = 10.5
band_t  = 2.6

out_w = peb_w + 2*0.1 + 2*wall

fig, ax = plt.subplots(figsize=(8.5, 5))

# 肌ライン
ax.axhline(0, color="#caa472", lw=3)
ax.text(out_w/2 + 7, -0.7, "skin (sensor side)", color="#a07840", fontsize=9, va="top")

# スリーブ外形(肌側 z=0)
ax.add_patch(Rectangle((-out_w/2, 0), out_w, peb_h + floor_t,
             fc="#9bc1e8", ec="#22314f", lw=1.5))
# ポケット中空
ax.add_patch(Rectangle((-(peb_w/2+0.1), floor_t), peb_w+0.2, peb_h,
             fc="white", ec="none"))
# センサー窓(肌側開口)
ax.plot([-win_w/2, win_w/2], [0, 0], color="white", lw=5)
# 保持リップ(上端で内側に絞る:開口 13.77)
for s in (-1, 1):
    ax.add_patch(Rectangle((s*(peb_w/2+0.1), peb_h+floor_t-lip_h),
                 -s*((peb_w/2+0.1)-sl_open/2), lip_h,
                 fc="#5a8fc7", ec="#22314f", lw=1))

# ペブル:くびれ形状(上下が膨らみ中央が溝)= section の見た目
bw, ww = peb_w/2, (sl_open-1.2)/2   # 膨らみ半幅 / くびれ半幅
y0 = floor_t + 0.1
verts = [(-ww, y0), (-bw, y0+1.6), (-bw, y0+peb_h-2.2),
         (-ww, y0+peb_h-1.0), (-ww, y0+peb_h),
         ( ww, y0+peb_h), ( ww, y0+peb_h-1.0),
         ( bw, y0+peb_h-2.2), ( bw, y0+1.6), ( ww, y0)]
ax.add_patch(Polygon(verts, closed=True, fc="#444b55", ec="#111", lw=1.2))
ax.text(0, y0+peb_h/2+0.5, "pebble", color="white", ha="center", va="center", fontsize=9)
# 露出センサー
ax.add_patch(Rectangle((-win_w/2, y0-0.1), win_w, 0.9, fc="#2ec27e", ec="none"))
ax.annotate("lip snaps into\nwaist groove", xy=(bw, y0+peb_h-2.4),
            xytext=(out_w/2+4, peb_h+2.5), fontsize=8, color="#22314f",
            arrowprops=dict(arrowstyle="->", color="#22314f"))

# バンド
for s in (-1, 1):
    ax.add_patch(Rectangle((s*out_w/2, peb_h+floor_t-band_t), s*22, band_t,
                 fc="#4C72B0", ec="#22314f", lw=1.2))
ax.text( out_w/2+11, peb_h+floor_t-band_t/2, "WWJD band", color="white", ha="center", va="center", fontsize=8)
ax.text(-out_w/2-11, peb_h+floor_t-band_t/2, "WWJD band", color="white", ha="center", va="center", fontsize=8)

# 寸法注記
ax.annotate("", xy=(-peb_w/2, peb_h+floor_t+2.2), xytext=(peb_w/2, peb_h+floor_t+2.2),
            arrowprops=dict(arrowstyle="<->", color="#333"))
ax.text(0, peb_h+floor_t+2.6, "pebble 14.36", ha="center", fontsize=8)
ax.annotate("", xy=(-sl_open/2, peb_h+floor_t+0.4), xytext=(sl_open/2, peb_h+floor_t+0.4),
            arrowprops=dict(arrowstyle="<->", color="#c0322b"))
ax.text(0, peb_h+floor_t+0.9, "open 13.77", ha="center", fontsize=8, color="#c0322b")

notes = ("Google blueprint D-0001799540\n"
         "  pebble 33.5 x 14.36 (waisted)\n"
         "  sleeve open 32.76 x 13.77\n"
         "  attach 10-25N / detach 12-45N\n"
         "  sensor unobstructed, skin-safe TPU\n"
         "  ! pebble height = measure device")
ax.text(-out_w/2 - 17, peb_h + 8, notes, fontsize=8, family="monospace", va="top",
        color="#333", bbox=dict(boxstyle="round", fc="#fff7e6", ec="#d9b25b"))

ax.set_title("WWJD x Fitbit Air — sleeve cross-section (official dims)", fontsize=11)
ax.set_aspect("equal")
ax.set_xlim(-out_w/2 - 19, out_w/2 + 19)
ax.set_ylim(-4, peb_h + 18)
ax.axis("off")
plt.tight_layout()
plt.savefig("fitbit_sleeve_section.png", dpi=140)
print("wrote fitbit_sleeve_section.png")
