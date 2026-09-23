"""S03: 口のループ + Mirror（動画 07:45〜09:30）。

動画の操作: 頂点1個を選び Shift+D で複製 → E を6回で「口の周りを囲う」半分のループ(7頂点) → Mirror 追加（Clipping ON で中心に吸着）
            → 横から見て GY で前へ、口の斜めのラインに合わせて傾ける → E→S で外側にもう1ループ → 外側ループも斜めに合わせる。
ここでは同じ構造（内側7頂点＋外側7頂点の半分ループ、6四角面、X=0 の頂点は中心に吸着）を、下絵の測定値から bmesh で構築する。

入力: out/face_s02b.blend   出力: out/face_s03_gen.blend, out/s03_report.json, out/s03_*_overlay.png
実行: blender --background --factory-startup --python steps/s03_mouth_mirror.py

座標の決め方（正面=高さの正。LEARNINGS.md の方針。口は3視点で高さが食い違うため、ユーザーが補正する前提）:
  X,Z : 正面下絵の口の線を測定（端点・中心の深さ）。半ループは -X 側（目と同じ側）
  Y   : 側面下絵の輪郭（最右の黒画素）からその高さでの顔表面の前後位置を取り、頬の丸み X²/(2R) だけ後ろへ
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s03"
gates = C.Gates(STEP)

N_HALF = 7            # 動画: E を6回 → 半分のループは 7 頂点（両端が X=0 に吸着）
INNER_B_PX = 8        # 内輪の縦の半径（口の線の上下）
BAND_PX = 9           # 外輪の帯の太さ（動画は E→S で目分量。人間が補正する前提の初期値）
SETBACK_R = 0.2       # 頬の丸み: Y の後退量 = X²/(2R)
SIL_INSET_PX = 3      # 輪郭線の太さの半分ぶん内側を顔表面とする


def measure_front_mouth():
    """正面下絵の口の線（r<200 の画素）から、端の位置・中心の深さ・端の高さを測る。"""
    px = overlay._load_top_origin(C.BP_DIR / C.BLUEPRINTS["front"]["file"]) * 255
    reg = px[690:740, 420:610, 0] < 200
    vv, uu = np.where(reg)
    u0, u1 = int(uu.min()) + 420, int(uu.max()) + 420

    def col_center(u):
        w = np.where(reg[:, u - 420])[0]
        return (w.min() + w.max()) / 2 + 690

    uc = (u0 + u1) / 2
    # 線の中央は薄く途切れる（r>=200）ので、画素のある列のうち中心に最も近い6列の平均を中心の高さとする
    cols = sorted((u for u in range(u0, u1 + 1) if reg[:, u - 420].any()), key=lambda u: abs(u - uc))[:6]
    v_c = float(np.mean([col_center(u) for u in cols]))
    v_e = float(np.mean([col_center(u0 + 1), col_center(u1 - 1)]))
    return dict(u0=u0, u1=u1, uc=uc, v_center=v_c, v_corner=v_e)


def measure_side_sil():
    """側面下絵の各行の顔の輪郭（最右の黒画素）の u。"""
    px = overlay._load_top_origin(C.BP_DIR / C.BLUEPRINTS["side"]["file"]) * 255
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    return {v: int(np.where(dark[v, 700:900])[0].max()) + 700 for v in range(600, 800) if dark[v, 700:900].any()}


def build_half(bm, m, sil):
    a = (m["u1"] - m["u0"]) / 2.0          # 口の半幅(px)
    rise = m["v_center"] - m["v_corner"]   # 端が中心より上がる量(px)

    def v_line(x_px):                      # 口の線（笑った形。中心が最も低い）。測定: 上がり量 ∝ (|x|/a)^3
        return m["v_center"] - rise * (abs(x_px) / a) ** 3

    def make_chain(half_w, half_h):
        vs = []
        for k in range(N_HALF):
            t = math.radians(90 + 30 * k)  # 90°(上の中心)→180°(端)→270°(下の中心)
            x_px = half_w * math.cos(t)
            v_px = v_line(x_px) - half_h * math.sin(t)
            X = 0.0 if abs(x_px) < 1e-9 else x_px * C.K
            Z = (C.ROW0 - v_px) * C.K
            u_sil = sil[int(round(v_px))] - SIL_INSET_PX
            Y = -(u_sil - C.COL0) * C.K + X * X / (2 * SETBACK_R)
            vs.append(bm.verts.new((X, Y, Z)))
        return vs

    inner = make_chain(a, INNER_B_PX)
    outer = make_chain(a + BAND_PX, INNER_B_PX + BAND_PX)
    for k in range(N_HALF - 1):
        bm.faces.new((inner[k], outer[k], outer[k + 1], inner[k + 1]))  # 目と同じ巻き順（法線 -Y）
    return inner, outer


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s02b.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    eye_before = [v.co.copy() for v in mesh.vertices]
    n_eye_faces = len(mesh.polygons)

    m = measure_front_mouth()
    sil = measure_side_sil()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    inner, outer = build_half(bm, m, sil)
    bm.verts.index_update()
    inner, outer = [v.index for v in inner], [v.index for v in outer]  # free() 後は BMVert を参照できない
    bm.to_mesh(mesh)
    bm.free()

    mod = obj.modifiers.new("Mirror", "MIRROR")
    mod.use_axis = (True, False, False)
    mod.use_clip = True
    mod.use_mirror_merge = True
    mod.merge_threshold = 0.001

    # --- ソース（半分）のトポロジー ---
    gates.check("目の頂点26個は動いていない", all((a.co - b).length == 0 for a, b in zip(mesh.vertices, eye_before)))
    gates.check("口の頂点14個（内7＋外7）を追加", len(mesh.vertices) == 26 + 14, len(mesh.vertices))
    gates.check("口の面6枚（すべて四角形）を追加",
                len(mesh.polygons) == n_eye_faces + 6 and all(len(p.vertices) == 4 for p in mesh.polygons))
    centers = [v for v in mesh.vertices[26:] if abs(v.co.x) < 1e-12]
    gates.check("X=0 の頂点が4つ（内外の上下の中心）で、X が厳密に 0", len(centers) == 4, len(centers))
    gates.check("口の頂点はすべて X<=0（-X 側の半分）", all(v.co.x <= 0 for v in mesh.vertices[26:]))
    gates.check("モディファイアは Mirror のみ・X軸・Clipping ON・Merge ON・Apply なし",
                [x.type for x in obj.modifiers] == ["MIRROR"] and tuple(mod.use_axis) == (True, False, False)
                and mod.use_clip and mod.use_mirror_merge)

    # --- Mirror 後（評価済みメッシュ）---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    V, E, F = len(ev.vertices), len(ev.edges), len(ev.polygons)
    gates.check("Mirror 後: 頂点76・辺114・面38（目2つ＋口の閉ループ）", (V, E, F) == (76, 114, 38), (V, E, F))
    gates.check("Mirror 後: オイラー数 0（輪が3つ）", V - E + F == 0, V - E + F)
    gates.check("Mirror 後: 全面が四角形", all(len(p.vertices) == 4 for p in ev.polygons))
    gates.check("Mirror 後: 面法線がすべて -Y（前）向き", all(p.normal.y < 0 for p in ev.polygons))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    mouth_ev = [v.co for v in ev.vertices if abs(v.co.x) < 0.07 and v.co.z < -0.15]
    gates.check("Mirror 後: 口は左右対称", all((round(-x, 6), round(y, 6), round(z, 6)) in coords
                                              for (x, y, z) in [tuple(round(c, 6) for c in p) for p in mouth_ev]))
    gates.check("Mirror 後: 中心で頂点が重複していない（結合済み）", len(coords) == V, f"{len(coords)} unique / {V}")

    # --- 下絵との一致 ---
    ring_in = [C.project(mesh.vertices[i].co, 0) for i in inner]
    gates.check("内輪の端が正面の口の線の端と一致 ±1.5px（左）", abs(min(p[0] for p in ring_in) - m["u0"]) <= 1.5,
                f"{min(p[0] for p in ring_in):.2f} vs {m['u0']}")
    gates.check("内輪の端の高さ（線の端の上がり）が測定値と一致 ±1.5px",
                abs(min(ring_in, key=lambda p: p[0])[1] - m["v_corner"]) <= 1.5,
                f"{min(ring_in, key=lambda p: p[0])[1]:.2f} vs {m['v_corner']:.2f}")
    top_c, bot_c = C.project(mesh.vertices[inner[0]].co, 0), C.project(mesh.vertices[inner[-1]].co, 0)
    gates.check("内輪の上下の中心が口の線の中心を挟む（上<線<下）", top_c[1] < m["v_center"] < bot_c[1],
                f"{top_c[1]:.1f} < {m['v_center']:.1f} < {bot_c[1]:.1f}")
    over = []
    for i in inner + outer:
        u, v = C.project(mesh.vertices[i].co, 90)
        if u > sil[int(round(v))] + 1:
            over.append(i)
    gates.check("口の頂点がすべて側面の輪郭の内側（顔からはみ出さない）", not over, over)

    # --- 下絵どうしの食い違い（参考情報。ユーザーが基準を決める）---
    gates.note("口の高さ（線の中心の行）: 正面723 / 45° 709 / 側面 約677。今回は正面を採用",
               f"front v_center={m['v_center']:.1f}")
    gates.note("口の前後位置: 側面の輪郭から Y=%.4f m。45°の下絵の口は約 -0.163 m と食い違う（45°は形の参考のみ）"
               % (mesh.vertices[inner[3]].co.y))

    # --- レビュー画像 ---
    for ang, tag, crop in [(0, "front", (400, 640, 630, 770)), (45, "a45", (580, 640, 780, 760)),
                           (90, "side", (730, 620, 880, 760))]:
        overlay.write_overlay(ev, ang, C.OUT / f"s03_{tag}_overlay.png", crop=crop, zoom=4)
    gates.check("レビュー画像3枚を出力", all((C.OUT / f"s03_{t}_overlay.png").exists() for t in ("front", "a45", "side")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s03_gen.blend"), compress=False)
    gates.finish()


main()
