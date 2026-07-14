// =============================================================
//  WWJD x Fitbit Air  band with sensor sleeve  (parametric)
// =============================================================
//  Fitbit Air のセンサーペブルを「スリーブ」で保持する WWJD 柄バンド。
//  TPU(フレキシブル)での 3D プリントを想定。OpenSCAD で開き F6 -> STL。
//
//  寸法は Google 公式 Fitbit Air ブループリント(図番 D-0001799540)由来。
//  確定仕様:
//    ペブル   : 長さ 33.5 ±0.1 / 幅 14.36 ±0.08(最大膨らみ)/ くびれ溝あり
//    スリーブ : 内開口 長さ 32.76 +0.07 / 幅 13.77 +0.06/-0.15(リップ部)
//    着脱力   : 装着 10-25N / 取り外し 12-45N(テンション式スナップイン)
//    センサー : PPG/SpO2 を塞がない・肌に均一接触(約 35 mmHg)・肌安全素材
//
//  >>> 嵌合の原理 <<<
//    スリーブ開口(32.76 x 13.77)< ペブル最大(33.5 x 14.36)。
//    柔軟な TPU がペブルの膨らみを乗り越え、くびれ溝にリップが噛んで保持。
//    => clr / lip / 壁厚と TPU の硬度で着脱力を 10-25N/12-45N に追い込む。
//       必ず試作プリントでフォースゲージ or 体感で実測しながら調整すること。
//
//  >>> 未確定(要実測)<<<
//    ペブル高さ(厚み)とくびれ溝の Z 位置は図面の該当シートに数値が無い。
//    実機をノギスで測って peb_h / groove_z を入れること。
// =============================================================

$fn = 96;

// ---------- ペブル(センサーモジュール)= 公式値 ----------
peb_l   = 33.5;    // 長さ(長軸)  ±0.1
peb_w   = 14.36;   // 幅(短軸・最大膨らみ) ±0.08
peb_h   = 7.0;     // ★高さ(要実測。仮 7.0)
peb_h_tol = 0;     //  参考

// ---------- スリーブ内開口(保持リップの内寸)= 公式値 ----------
sl_open_l = 32.76; // 開口 長さ  +0.07
sl_open_w = 13.77; // 開口 幅(リップ部 section B-B) +0.06/-0.15

// ---------- スリーブ構造 ----------
wall    = 2.0;     // 側壁厚(TPU)
floor_t = 0.8;     // 肌側の縁(センサー窓の受け)
lip_h   = 0.65;    // リップ高さ(図面 0.65 ±0.15)
pocket_clr = 0.10; // ペブル膨らみとポケットのクリアランス

// センサー窓(肌側開口。PPG/SpO2 を塞がない)
win_l   = 28.0;    // 窓 長さ(内開口より少し小)
win_w   = 10.5;    // 窓 幅

// ---------- バンド(WWJD柄)----------
band_w     = 16.0;   // バンド幅(ペブル幅14.36前後に合わせる)
band_t     = 2.6;    // バンド厚み(TPUは2.2-3.0)
band_taper = 13.0;   // 先端幅
len_a      = 80.0;   // 穴側長さ(手首実測で調整)
len_b      = 72.0;   // バックル側長さ(closureは別途)
edge_r     = 2.0;

// WWJD 彫り込み
logo_text  = "WWJD";
logo_size  = 5.0;
logo_depth = 0.6;
logo_font  = "Liberation Sans:style=Bold";

// 穴(長さ調整)
hole_dia   = 2.2;
hole_n     = 6;
hole_pitch = 6.0;
hole_from_end = 16.0;

// ---------- 派生値 ----------
pocket_l = peb_l + 2*pocket_clr;   // 膨らみを収めるポケット内寸
pocket_w = peb_w + 2*pocket_clr;
out_l = pocket_l + 2*wall;         // スリーブ外形
out_w = pocket_w + 2*wall;
sleeve_h = floor_t + peb_h;        // スリーブ高さ(肌側 z=0)

// =============================================================
//  基本形状: レーストラック(長円)断面
// =============================================================
module racetrack(l, w, h) {
    r = w/2;
    hull() for (sx=[-1,1])
        translate([sx*(l/2 - r), 0, 0]) cylinder(h=h, r=r);
}

// =============================================================
//  センサースリーブ
// =============================================================
module sleeve() {
    difference() {
        racetrack(out_l, out_w, sleeve_h);                 // 外形ソリッド
        // ペブル収納ポケット(floor_t より上を中空に)
        translate([0,0,floor_t]) racetrack(pocket_l, pocket_w, sleeve_h);
        // 肌側センサー窓(底貫通)
        translate([0,0,-1]) racetrack(win_l, win_w, floor_t+2);
    }
    // 上端の保持リップ:開口を 32.76 x 13.77 に絞る(=スナップの噛み)
    translate([0,0, sleeve_h - lip_h])
        difference() {
            racetrack(out_l, out_w, lip_h);
            translate([0,0,-1]) racetrack(sl_open_l, sl_open_w, lip_h+2);
        }
}

// =============================================================
//  バンド(WWJD柄)
// =============================================================
module strap(length, w_root, w_tip) {
    hull() {
        translate([0,      -w_root/2+edge_r, 0]) cylinder(h=band_t, r=edge_r);
        translate([0,       w_root/2-edge_r, 0]) cylinder(h=band_t, r=edge_r);
        translate([length, -w_tip/2 +edge_r, 0]) cylinder(h=band_t, r=edge_r);
        translate([length,  w_tip/2 -edge_r, 0]) cylinder(h=band_t, r=edge_r);
    }
}
module logo_on(length) {
    translate([length*0.45, 0, band_t - logo_depth])
        linear_extrude(height = logo_depth + 1)
        text(logo_text, size=logo_size, font=logo_font,
             halign="center", valign="center");
}
module strap_holes(length) {
    for (i=[0:hole_n-1])
        translate([length - hole_from_end - i*hole_pitch, 0, -1])
            cylinder(h=band_t+2, r=hole_dia/2);
}

// =============================================================
//  組み立て(スリーブ + 両側 WWJD バンド)
// =============================================================
module assembly() {
    sleeve();
    // +X 側(調整穴つき)
    translate([out_l/2 - 0.5, 0, sleeve_h - band_t])
        difference() {
            strap(len_a, band_w, band_taper);
            logo_on(len_a);
            strap_holes(len_a);
        }
    // -X 側(バックル取付側。closure は別途)
    mirror([1,0,0])
    translate([out_l/2 - 0.5, 0, sleeve_h - band_t])
        difference() {
            strap(len_b, band_w, band_taper);
            logo_on(len_b);
        }
}

assembly();

// -------------------------------------------------------------
//  調整の順番:
//   1) sleeve() だけを TPU で印刷し、実機ペブルで着脱力を確認
//      (緩い=lip 大 / sl_open を小さく、固い=逆)。10-25N/12-45N を狙う
//   2) peb_h を実測して入れ、ポケット深さを合わせる
//   3) 確定後に len_a/len_b を手首実測であわせ、closure(バックル)を追加
// -------------------------------------------------------------
