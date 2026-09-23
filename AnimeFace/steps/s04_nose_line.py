"""S04: 鼻筋のライン（動画 09:34〜10:25）。

動画の操作: 目頭の頂点を選び E X で中心(X=0)へ伸ばす → 横から見て側面の輪郭（鼻根）に合わせて移動 → そこから押し出して鼻のラインを作る。
ここでは同じ構造（目頭の頂点 → 鼻根 → 鼻筋 → 鼻先 → 鼻下 の辺の連なり。X=0 の頂点は中心に吸着、面はまだ貼らない）を bmesh で構築する。

入力: out/face_s03_gen.blend   出力: out/face_s04_gen.blend, out/s04_report.json, out/s04_*_overlay.png
実行: blender --background --factory-startup --python steps/s04_nose_line.py

座標の決め方:
  Z(高さ): 鼻根＝目頭の頂点と同じ高さ（E X は Z を変えない）。鼻先・鼻下＝側面の輪郭の鼻先(591)・鼻下(645)の行をそのまま使う。
  Y(前後): 側面の輪郭。
  ※ 正面の鼻の点(重心618)は鼻先の高さではない。鼻先(591)と鼻下(645)の中間(618)で、鼻の下半分を1つの点で描いたもの。
     最初は点を鼻先とみなして側面を縦に引き伸ばし、側面で鼻先が輪郭から外れた（レビュー画像で発見）。
     側面の縦位置の割り付けは、鼻下より下（口・顎）だけに使う（口は正面723/側面677で本当に食い違う）。
"""
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s04"
gates = C.Gates(STEP)
SIL_INSET_PX = 3  # 輪郭線の太さの半分ぶん内側を顔表面とする（S03 と同じ）


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s03_gen.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_faces, n_edges = len(mesh.polygons), len(mesh.edges)

    # --- 測定（毎回、下絵から）---
    sil = M.side_silhouette()
    tip_row_s, tip_u = M.side_nose_tip_row(sil)
    sub_row_s, sub_u = M.side_subnasale_row(sil)
    lip_row_s, chin_s = M.side_lip_row(), M.side_chin_row()
    dot_u, dot_v = M.front_nose_dot()
    chin_f = M.front_chin_row()
    mouth_f = 722.5  # S03 で測った正面の口の線の中心（S03 の入力と同じ値）
    side_rows = [C.ROW0, sub_row_s, lip_row_s, chin_s]      # 鼻下までは側面をそのまま使う（恒等）
    front_rows = [C.ROW0, sub_row_s, mouth_f, chin_f]
    f2s = M.front_to_side_row_map(side_rows, front_rows)
    s2f = M.side_to_front_row_map(side_rows, front_rows)

    def y_on_profile(v_front):
        u = sil[int(round(f2s(v_front)))] - SIL_INSET_PX
        return -(u - C.COL0) * C.K

    # 目頭の頂点 = 目の頂点（先頭26個）のうち最も鼻側（X が最大）
    eye_idx = max(range(26), key=lambda i: mesh.vertices[i].co.x)
    corner = mesh.vertices[eye_idx].co.copy()  # to_mesh 後も安全なようコピー
    v_root = C.project(corner, 0)[1]
    v_tip = s2f(tip_row_s)  # 鼻下より上は恒等なので側面の鼻先の行そのもの
    v_mid = (v_root + v_tip) / 2
    v_sub = s2f(sub_row_s)
    rows = [v_root, v_mid, v_tip, v_sub]

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    prev = bm.verts[eye_idx]  # 頂点を追加する前に取得（追加後は添字テーブルが古くなる）
    chain = [bm.verts.new((0.0, y_on_profile(v), (C.ROW0 - v) * C.K)) for v in rows]
    for nv in chain:
        bm.edges.new((prev, nv))
        prev = nv
    bm.verts.index_update()
    idx = [v.index for v in chain]
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    gates.check("既存の頂点40個は動いていない", all((a.co - b).length == 0 for a, b in zip(mesh.vertices, before)))
    gates.check("頂点4つ・辺4本を追加（面は増やさない）",
                len(mesh.vertices) == 44 and len(mesh.edges) == n_edges + 4 and len(mesh.polygons) == n_faces,
                f"V={len(mesh.vertices)} E={len(mesh.edges)} F={len(mesh.polygons)}")
    gates.check("鼻の頂点4つは X が厳密に 0（中心に吸着）", all(mesh.vertices[i].co.x == 0.0 for i in idx))
    zs = [mesh.vertices[i].co.z for i in idx]
    gates.check("鼻筋は上から下へ Z が単調減少", all(a > b for a, b in zip(zs, zs[1:])), [round(z, 4) for z in zs])
    ys = [mesh.vertices[i].co.y for i in idx]
    gates.check("鼻先が最も前（Y が最小）で、鼻根・鼻下より前", ys[2] == min(ys) and ys[2] < ys[0] and ys[2] < ys[3],
                [round(y, 4) for y in ys])
    gates.check("目頭の頂点→鼻根は同じ高さ（動画の E X は Z を変えない）",
                abs(mesh.vertices[idx[0]].co.z - mesh.vertices[eye_idx].co.z) < 1e-9,
                f"目頭の頂点#{eye_idx} Z={mesh.vertices[eye_idx].co.z:.5f} / 鼻根 Z={mesh.vertices[idx[0]].co.z:.5f}")
    gates.check("モディファイアは Mirror のみ（Apply なし）", [m.type for m in obj.modifiers] == ["MIRROR"])

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点80（+4）", len(ev.vertices) == 80, len(ev.vertices))
    gates.check("Mirror 後: 重複した辺がない", len(set(pairs)) == len(pairs), f"{len(set(pairs))} unique / {len(pairs)}")
    gates.check("Mirror 後: 面は38のまま・全面四角形・法線 -Y 向き",
                len(ev.polygons) == 38 and all(len(p.vertices) == 4 and p.normal.y < 0 for p in ev.polygons))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・中心の頂点の重複なし",
                all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == len(ev.vertices))
    deg = {}
    for a, b in pairs:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    nose_ev = [v.index for v in ev.vertices if v.co.x == 0.0 and v.co.z > (C.ROW0 - 700) * C.K and v.co.z < (C.ROW0 - 500) * C.K
               and v.co.y < -0.2]
    gates.check("Mirror 後: 鼻根には左右の目頭からの辺が2本集まる", any(deg[i] == 3 for i in nose_ev),
                sorted(deg[i] for i in nose_ev))

    # --- 下絵との一致（画像から再測定した値と比べる）---
    tip = mesh.vertices[idx[2]].co
    tu, tv = C.project(tip, 0)
    gates.check("鼻先: 高さが側面の鼻先の行（再測定）と一致 ±1px", abs(tv - tip_row_s) <= 1, f"{tv:.1f} vs {tip_row_s:.1f}")
    gates.check("鼻先: 前後位置が側面の鼻先の輪郭（再測定）と一致 ±1px", abs(C.project(tip, 90)[0] - (tip_u - SIL_INSET_PX)) <= 1,
                f"{C.project(tip, 90)[0]:.1f} vs {tip_u - SIL_INSET_PX}")
    sub = mesh.vertices[idx[3]].co
    gates.check("鼻下: 前後位置が側面の鼻下の輪郭（再測定）と一致 ±1px", abs(C.project(sub, 90)[0] - (sub_u - SIL_INSET_PX)) <= 1,
                f"{C.project(sub, 90)[0]:.1f} vs {sub_u - SIL_INSET_PX}")
    sub_v = C.project(sub, 0)[1]
    gates.check("正面の鼻の点（画像から再測定した重心）は、鼻先と鼻下の中間 ±3px", abs((tv + sub_v) / 2 - dot_v) <= 3,
                f"中間={(tv + sub_v) / 2:.1f} / 点の重心={dot_v:.1f}")
    gates.check("鼻下が口の輪の上端より上（S05 で口へ繋ぐ余地がある）",
                C.project(sub, 0)[1] < C.project(mesh.vertices[26 + 7 + 0].co, 0)[1],
                f"鼻下 v={C.project(sub, 0)[1]:.1f} / 口の外輪の上の中心 v={C.project(mesh.vertices[33].co, 0)[1]:.1f}")

    gates.note("側面の縦位置の割り付け（側面の行→正面の行）: 鼻下まで恒等 / 口 %.0f→%.1f / 顎 %.0f→%.0f（鼻先 %.0f・鼻下 %.0f）"
               % (lip_row_s, mouth_f, chin_s, chin_f, tip_row_s, sub_row_s))
    gates.note("S03 の口の前後位置 Y=%.4f は生の側面輪郭を使用。この割り付けなら口(側面の唇の行)は Y=%.4f で、約%.0fmm後ろ"
               % (mesh.vertices[26 + 3].co.y, y_on_profile(mouth_f), (mesh.vertices[26 + 3].co.y - y_on_profile(mouth_f)) * 1000))

    for ang, tag, crop in [(0, "front", (380, 470, 640, 740)), (45, "a45", (560, 470, 800, 740)),
                           (90, "side", (690, 470, 900, 740))]:
        overlay.write_overlay(ev, ang, C.OUT / f"s04_{tag}_overlay.png", crop=crop, zoom=3)
    gates.check("レビュー画像3枚を出力", all((C.OUT / f"s04_{t}_overlay.png").exists() for t in ("front", "a45", "side")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s04_gen.blend"), compress=False)
    gates.finish()


main()
