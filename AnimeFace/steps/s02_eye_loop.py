"""S02: 目の初期ループ（動画 05:30〜07:41 相当）。

動画の操作: Circle(頂点数8) → RX90 → 目の位置にS/G → 目尻をGYで後退 → Alt+クリックでループ選択 → E→S で外側にもう1ループ。
ここでは同じ結果（8頂点の内輪 + 拡大した外輪 = 16頂点・8四角面）を、下絵の測定値から bmesh で構築する。

入力: out/face_s01.blend   出力: out/face_s02_gen.blend, out/s02_report.json, out/s02_*_overlay.png
実行: blender --background --factory-startup --python steps/s02_eye_loop.py

数値の出典（2026-09-21 に下絵1024²を色閾値で測定。DESIGN.md §3 と同じ手法）:
  正面 目の開口(白目+虹彩) bbox : u 262..420, v 467..585
  側面 目の開口(白目の左端..虹彩の右端): u 672..768（顔が右向き。u が大きい=前=-Y）
  ※ 初回は白目だけの連結成分を測って 671..740 と誤った（虹彩の黒縁で分断）。目視で気付き修正
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s02"
gates = C.Gates(STEP)

FRONT_OPEN = dict(u0=262, u1=420, v0=467, v1=585)   # 正面（下絵の左側の目 = -X 側）
SIDE_OPEN = dict(u0=672, u1=768)                    # 側面での目の奥行き範囲
OUTER_SCALE = 1.3                                   # 動画の E→S。外輪は内輪を重心中心に一律拡大
TOL_PX = 1.0


def measure_side_iris_right():
    """側面下絵から虹彩の右端(u)を毎回測り直す（定数との比較ではなく画像から）。行 500..560 の黒画素の最右端。"""
    px = overlay._load_top_origin(C.BP_DIR / C.BLUEPRINTS["side"]["file"])
    dark = (px[..., 0] < 75 / 255) & (px[..., 1] < 75 / 255) & (px[..., 2] < 75 / 255)
    return max(int(np.where(dark[v, 700:800])[0].max()) + 700 for v in range(500, 561, 2))


def measure_side_white_left():
    """側面下絵から白目の左端(u)を測る（行 505..535 の灰白画素の最左端。肌色は |R-B|>=30 で除外）。"""
    px = overlay._load_top_origin(C.BP_DIR / C.BLUEPRINTS["side"]["file"])
    r, b = px[..., 0] * 255, px[..., 2] * 255
    greyw = (np.abs(r - b) < 30) & (r > 100)
    # 黒線の縁のアンチエイリアス画素を拾わないよう、連続4画素以上の灰白だけを数える
    run4 = greyw[:, :-3] & greyw[:, 1:-2] & greyw[:, 2:-1] & greyw[:, 3:]
    return min(int(np.where(run4[v, 640:800])[0].min()) + 640 for v in range(505, 536, 2))


def build():
    f = FRONT_OPEN
    cx = ((f["u0"] + f["u1"]) / 2 - C.COL0) * C.K
    cz = (C.ROW0 - (f["v0"] + f["v1"]) / 2) * C.K
    rx = (f["u1"] - f["u0"]) / 2 * C.K
    rz = (f["v1"] - f["v0"]) / 2 * C.K
    x_out, x_in = cx - rx, cx + rx            # 目尻(外側, -X)・目頭(鼻側)
    y_out = -(SIDE_OPEN["u0"] - C.COL0) * C.K  # 目尻は後ろ
    y_in = -(SIDE_OPEN["u1"] - C.COL0) * C.K   # 目頭は前

    def plane_y(x):  # 目の面は目頭→目尻で前→後ろに傾く1枚の平面（動画 06:26 の GY 後退に相当）
        return y_out + (x - x_out) / (x_in - x_out) * (y_in - y_out)

    inner = []
    for k in range(8):                      # Blender の Circle と同じく角度0(+X方向)から45°刻み
        t = k * math.pi / 4
        x, z = cx + rx * math.cos(t), cz + rz * math.sin(t)
        inner.append(Vector((x, plane_y(x), z)))
    med = sum(inner, Vector()) / 8
    outer = [med + OUTER_SCALE * (p - med) for p in inner]

    bm = bmesh.new()
    vi = [bm.verts.new(p) for p in inner]
    vo = [bm.verts.new(p) for p in outer]
    for k in range(8):
        j = (k + 1) % 8
        bm.faces.new((vi[k], vo[k], vo[j], vi[j]))  # 法線が -Y(顔の前)を向く巻き順
    bm.normal_update()
    mesh = bpy.data.meshes.new("Face")
    bm.to_mesh(mesh)
    bm.free()
    return mesh, med


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s01.blend"))
    scene = bpy.context.scene
    mesh, med = build()
    obj = bpy.data.objects.new("Face", mesh)
    coll = bpy.data.collections.new("MODEL")
    scene.collection.children.link(coll)
    coll.objects.link(obj)

    verts = [v.co.copy() for v in mesh.vertices]
    inner, outer = verts[:8], verts[8:]

    # --- トポロジー ---
    gates.check("頂点数 16（内輪8 + 外輪8）", len(mesh.vertices) == 16, len(mesh.vertices))
    gates.check("エッジ数 24", len(mesh.edges) == 24, len(mesh.edges))
    gates.check("面は8枚すべて四角形", len(mesh.polygons) == 8 and all(len(p.vertices) == 4 for p in mesh.polygons),
                f"{len(mesh.polygons)}面")
    bm = bmesh.new()
    bm.from_mesh(mesh)
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    interior = [e for e in bm.edges if len(e.link_faces) == 2]
    bad = [e for e in bm.edges if len(e.link_faces) not in (1, 2)]
    bm.free()
    gates.check("境界エッジ16（内輪の穴8 + 外周8）・内部エッジ8・非多様体0",
                (len(boundary), len(interior), len(bad)) == (16, 8, 0), (len(boundary), len(interior), len(bad)))
    gates.check("面法線がすべて -Y（前）向き", all(p.normal.y < -0.5 for p in mesh.polygons),
                [round(p.normal.y, 2) for p in mesh.polygons])
    gates.check("モディファイアなし（Apply 済みを作らない）", len(obj.modifiers) == 0)
    gates.check("下絵エンプティ3枚が残っている", len([o for o in bpy.data.objects if o.type == "EMPTY"]) == 3)

    # --- 下絵との一致（内輪 = 目の開口）---
    us = [C.project(p, 0)[0] for p in inner]
    vs = [C.project(p, 0)[1] for p in inner]
    f = FRONT_OPEN
    for name, got, want in [("正面 u 最小", min(us), f["u0"]), ("正面 u 最大", max(us), f["u1"]),
                            ("正面 v 最小", min(vs), f["v0"]), ("正面 v 最大", max(vs), f["v1"])]:
        gates.check(f"内輪 {name} = 測定値 ±{TOL_PX}px", abs(got - want) <= TOL_PX, f"{got:.2f} vs {want}")
    su = [C.project(p, 90)[0] for p in inner]
    iris_r, white_l = measure_side_iris_right(), measure_side_white_left()
    gates.check("内輪の側面 前端(u最大) = 画像から再測定した虹彩右端 ±2px", abs(max(su) - iris_r) <= 2, f"{max(su):.2f} vs {iris_r}")
    gates.check("内輪の側面 後端(u最小) = 画像から再測定した白目左端 ±2px", abs(min(su) - white_l) <= 2, f"{min(su):.2f} vs {white_l}")

    # --- 動画どおりの構造: 外輪 = 内輪の重心中心の一律拡大(E→S) ---
    err = max((o - (med + OUTER_SCALE * (i - med))).length for i, o in zip(inner, outer))
    gates.check(f"外輪 = 内輪の {OUTER_SCALE} 倍拡大（重心中心）", err < 1e-6, f"max err={err:.2e}")
    # 目の面が前後に傾いている（目頭が前・目尻が後ろ）
    gates.check("目頭が前(-Y)・目尻が後ろ(+Y)", min(inner, key=lambda p: p.x).y > max(inner, key=lambda p: p.x).y,
                f"目尻Y={min(inner, key=lambda p: p.x).y:.4f} 目頭Y={max(inner, key=lambda p: p.x).y:.4f}")

    # --- レビュー画像（目の周りを3倍拡大。3視点）---
    crop = (180, 400, 480, 640)
    for ang, tag in [(0, "front"), (45, "a45"), (90, "side")]:
        c = crop if ang != 90 else (560, 400, 860, 640)
        if ang == 45:
            c = (380, 400, 680, 640)
        overlay.write_overlay(mesh, ang, C.OUT / f"s02_{tag}_overlay.png", crop=c, zoom=3)
    gates.check("レビュー画像3枚を出力", all((C.OUT / f"s02_{t}_overlay.png").exists() for t in ("front", "a45", "side")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s02_gen.blend"), compress=False)
    gates.finish()


main()
