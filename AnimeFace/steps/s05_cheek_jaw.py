"""S05: 頬から顎先へのフェイスライン（動画 10:32〜11:36）。

動画の操作: 目の下のラインを選択 → E で押し出し → R で回転 → もう一度 E → 真ん中(顎先)まで持ってくる
            → 横から見て顎のラインに合わせ、正面から見て顔の横のラインになるようにざっくり配置。
ここでは同じ構造（目の下の7頂点の列 → 中間の列 → 顎の列、四角面2段×6枚）を bmesh で構築する。

入力: out/face_s04_gen.blend   出力: out/face_s05_gen.blend, out/s05_report.json, out/s05_*_overlay.png
実行: blender --background --factory-startup --python steps/s05_cheek_jaw.py

座標の決め方:
  顎の列(7頂点): 顎先(X=0)→耳の下。正面の顔の輪郭から (X, Z)、側面の顎のライン（耳の下→顎先の斜めの影の線）から Y。
                 2本の曲線を、顎先→耳の下の弧長の割合 t で対応づける（正面と側面の縦のズレの影響を受けない）
  中間の列: 目の下の列と顎の列の中点（動画も「ざっくり」。顔の表面には乗っていない仮置き）
"""
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s05"
gates = C.Gates(STEP)
N = 7                  # 目の下の列の頂点数（外輪の下側: 目頭の頂点 → 目尻の頂点）
SIL_INSET_PX = 3


def outer_lower_chain(mesh):
    """目（先頭26頂点）の外輪の境界ループから、目頭(Xが最大)→目尻(Xが最小)の下側の経路を返す。"""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    adj = {}
    for e in bm.edges:
        if len(e.link_faces) == 1 and all(v.index < 26 for v in e.verts):
            a, b = (v.index for v in e.verts)
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    bm.free()
    seen, loops = set(), []
    for s in adj:
        if s in seen:
            continue
        loop, prev, cur = [s], None, s
        seen.add(s)
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            loop.append(cur)
            seen.add(cur)
        loops.append(loop)
    xs = lambda L: max(mesh.vertices[i].co.x for i in L) - min(mesh.vertices[i].co.x for i in L)  # noqa: E731
    outer = max(loops, key=xs)
    i_in = max(outer, key=lambda i: mesh.vertices[i].co.x)
    i_out = min(outer, key=lambda i: mesh.vertices[i].co.x)
    a, b = outer.index(i_in), outer.index(i_out)
    n = len(outer)
    path1 = [outer[(a + k) % n] for k in range((b - a) % n + 1)]
    path2 = [outer[(a - k) % n] for k in range((a - b) % n + 1)]
    z = lambda P: sum(mesh.vertices[i].co.z for i in P) / len(P)  # noqa: E731
    return path1 if z(path1) < z(path2) else path2


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s04_gen.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_e, n_f = len(mesh.vertices), len(mesh.edges), len(mesh.polygons)

    r0 = outer_lower_chain(mesh)
    gates.check(f"目の下の列は{N}頂点（目頭→目尻）", len(r0) == N, r0)

    sil = M.side_silhouette()
    pf = M.front_jaw_contour(N)          # 顎先(t=0)→耳の下(t=1)
    ps = M.side_jaw_line(N, sil)
    jaw = []
    for (uf, vf), (us, _) in zip(pf, ps):
        X = (uf - C.COL0) * C.K
        jaw.append((0.0 if abs(uf - C.COL0) < 1e-9 else X, -(us - C.COL0) * C.K, (C.ROW0 - vf) * C.K))

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    row0 = [bm.verts[i] for i in r0]
    # 顎の列は顎先(t=0)→耳の下(t=1) の順。目の下の列（目頭→目尻）と向きが揃い、目頭↔顎先・目尻↔耳の下 で対応する
    row2 = [bm.verts.new(p) for p in jaw]
    row1 = []
    for a, b in zip(row0, row2):
        row1.append(bm.verts.new((a.co + b.co) / 2))
    for rows in ((row0, row1), (row1, row2)):
        top, bot = rows
        for i in range(N - 1):
            bm.faces.new((top[i], top[i + 1], bot[i + 1], bot[i]))           # 法線 -Y 向きの巻き順
    bm.verts.index_update()
    i1, i2 = [v.index for v in row1], [v.index for v in row2]
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    gates.check("既存の頂点44個は動いていない", all((a.co - b).length == 0 for a, b in zip(mesh.vertices, before)))
    gates.check("頂点14個（中間7＋顎7）・四角面12枚を追加",
                len(mesh.vertices) == n_v + 14 and len(mesh.polygons) == n_f + 12 and
                all(len(p.vertices) == 4 for p in mesh.polygons), f"V={len(mesh.vertices)} F={len(mesh.polygons)}")
    gates.check("辺は26本追加（列の辺12＋段の辺14）", len(mesh.edges) == n_e + 26, len(mesh.edges) - n_e)
    at0 = [i for i in i2 if mesh.vertices[i].co.x == 0.0]
    gates.check("顎先の頂点だけが X=0（厳密）", len(at0) == 1 and at0[0] == i2[0], at0)
    gates.check("他の追加頂点はすべて X<0（-X 側）", all(mesh.vertices[i].co.x < 0 for i in i1 + i2[1:]))
    gates.check("顎の列は顎先から耳の下へ X が単調に外へ・Z が単調に上へ",
                all(mesh.vertices[a].co.x > mesh.vertices[b].co.x and mesh.vertices[a].co.z < mesh.vertices[b].co.z
                    for a, b in zip(i2, i2[1:])),
                [(round(mesh.vertices[i].co.x, 3), round(mesh.vertices[i].co.z, 3)) for i in i2])
    gates.check("モディファイアは Mirror のみ（Apply なし）", [m.type for m in obj.modifiers] == ["MIRROR"])

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点107（顎先は左右で共有）", len(ev.vertices) == 80 + 14 * 2 - 1, len(ev.vertices))
    gates.check("Mirror 後: 面62・辺171・辺の重複なし",
                len(ev.polygons) == 62 and len(ev.edges) == 171 and len(set(pairs)) == len(pairs),
                f"F={len(ev.polygons)} E={len(ev.edges)} unique={len(set(pairs))}")
    gates.check("Mirror 後: 全面が四角形・法線が -Y 向き", all(len(p.vertices) == 4 and p.normal.y < 0 for p in ev.polygons),
                sum(1 for p in ev.polygons if p.normal.y >= 0))
    share = {}
    for p in ev.polygons:
        for k in range(4):
            e = tuple(sorted((p.vertices[k], p.vertices[(k + 1) % 4])))
            share[e] = share.get(e, 0) + 1
    gates.check("Mirror 後: 3枚以上の面が共有する辺がない（非多様体なし）", max(share.values()) <= 2, max(share.values()))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし",
                all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == len(ev.vertices))

    # --- 下絵との一致（画像から再測定）---
    front_px = M._px("front")
    dark = (front_px[..., 0] < 75) & (front_px[..., 1] < 75) & (front_px[..., 2] < 75)
    off = []
    for i in i2:
        u, v = C.project(mesh.vertices[i].co, 0)
        ui, vi = int(round(u)), int(round(v))
        off.append(not dark[vi - 3:vi + 4, ui - 3:ui + 4].any())
    gates.check("顎の列の7頂点が、正面の輪郭線（黒線）の上にある（±3px）", not any(off), [i for i, o in zip(i2, off) if o])
    chin_v = C.project(mesh.vertices[i2[0]].co, 0)[1]
    gates.check("顎先の高さが正面の顎の最下部（再測定 %.0f）の内側 3px ±1.5px" % M.front_chin_row(),
                abs(chin_v - (M.front_chin_row() - 3)) <= 1.5, f"{chin_v:.1f}")
    chin_u_side = C.project(mesh.vertices[i2[0]].co, 90)[0]
    gates.check("顎先の前後位置が側面の顎先の輪郭（再測定）の内側 3px ±1.5px",
                abs(chin_u_side - (sil[int(M.side_chin_row()) - 2] - SIL_INSET_PX)) <= 1.5, f"{chin_u_side:.1f}")
    su = [C.project(mesh.vertices[i].co, 90)[0] for i in i2]
    gates.check("顎の列の前後位置は顎先から耳の下へ単調に後ろへ（側面の斜めの線に沿う）",
                all(a > b for a, b in zip(su, su[1:])), [round(u) for u in su])

    dv = [C.project(mesh.vertices[i].co, 90)[1] for i in i2]
    gates.note("側面の顎の線との縦のズレ: 顎先 側面の行 %.0f / 正面基準の行 %.0f（差 %.0fpx）。耳の下は側面 %.0f / 正面 %.0f"
               % (ps[0][1], dv[0], dv[0] - ps[0][1], ps[-1][1], dv[-1]))
    gates.note("中間の列は仮置き（線形補間）。中心付近で顔の表面より約40mm奥に沈む。S06 の面張りで手を入れる前提")

    for ang, tag, crop, zoom in [(0, "front", (150, 470, 560, 850), 2), (45, "a45", (330, 470, 760, 850), 2),
                                 (90, "side", (440, 620, 800, 850), 3)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s05_{tag}_overlay.png", crop=crop, zoom=zoom)
    gates.check("レビュー画像3枚を出力", all((C.OUT / f"s05_{t}_overlay.png").exists() for t in ("front", "a45", "side")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s05_gen.blend"), compress=False)
    gates.finish()


main()
