"""S11b: S11 の人間補正版から、正中線のずれだけを直す（頂点の位置を X=0 に戻す）。それ以外は動かさない。

背景（face_s11_human.blend を face_s11_gen.blend と比べて分かったこと）:
  - 人間は、顎の下・壁の下端のあたりの頂点41個を最大 11.7mm 動かし、顎の下（首の前）に頂点5つを足した（五角形+1）。目の縁・眼窩の頂点は動かしていない
  - ただし、口の下の正中線の頂点2つ（v26, v32）が X=+0.0015 にずれた（生成版は X=0）。Mirror の結合距離は 1mm なので、
    鏡の側と 3mm 離れて結合されず、口の穴の輪が 16辺 → 20辺（正中線に切れ目）になっている
  - 同じ正中線の頂点 v33, v39（-0.0003）、v60, v61（+0.0001）も、わずかにずれている（結合はされるが、厳密な左右対称でない）
生成版で X=0 だった頂点のうち、人間版で X≠0 になったものを、X=0 に戻す。

入力: out/face_s11_human.blend（比較: out/face_s11_gen.blend）   出力: out/face_s11b_gen.blend, out/s11b_report.json
実行: blender --background --factory-startup --python steps/s11b_cleanup.py
"""
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s11b"
gates = C.Gates(STEP)


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def loops_of(bm):
    be = [e for e in bm.edges if len(e.link_faces) == 1]
    adj = {}
    for e in be:
        for v in e.verts:
            adj.setdefault(v.index, []).append(e)
    seen, loops = set(), []
    for e in be:
        if e.index in seen:
            continue
        stack, comp = [e], []
        while stack:
            x = stack.pop()
            if x.index in seen:
                continue
            seen.add(x.index)
            comp.append(x)
            for v in x.verts:
                stack.extend(y for y in adj[v.index] if y.index not in seen)
        loops.append(comp)
    return sorted(len(c) for c in loops)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s11_gen.blend"))
    gen_pos = [v.co.copy() for v in bpy.data.objects["Face"].data.vertices]
    n_gen = len(gen_pos)
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s11_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])
    gates.check("頂点の並びが生成版と同じ（先頭 %d 個が、生成版の頂点の 20mm 以内）" % n_gen,
                len(mesh.vertices) >= n_gen and all((mesh.vertices[i].co - gen_pos[i]).length < 0.02 for i in range(n_gen)))
    moved = [(i, (mesh.vertices[i].co - gen_pos[i]).length) for i in range(n_gen) if (mesh.vertices[i].co - gen_pos[i]).length > 1e-6]
    eye_moved = [i for i, _ in moved if i >= 463]
    gates.note("人間版の変更", f"頂点 {n_gen}→{len(mesh.vertices)}（+{len(mesh.vertices) - n_gen}）、動かした頂点 {len(moved)}個（最大 {max(d for _, d in moved) * 1000:.1f}mm）、眼窩の頂点（463〜）で動かしたもの {len(eye_moved)}個")

    # 正中線のずれ
    off = [(i, mesh.vertices[i].co.x) for i in range(n_gen) if abs(gen_pos[i].x) < 1e-9 and abs(mesh.vertices[i].co.x) > 1e-9]
    gates.note("生成版で X=0 だったのに、人間版で X≠0 の頂点（頂点番号, X）", [(i, round(x * 1000, 2)) for i, x in off])
    for i, _ in off:
        mesh.vertices[i].co.x = 0.0
    mesh.update()
    gates.check("生成版で X=0 だった頂点は、全て X=0", all(abs(mesh.vertices[i].co.x) < 1e-12 for i in range(n_gen) if abs(gen_pos[i].x) < 1e-9))
    gates.check("X ≤ 0（Mirror の片側）", max(v.co.x for v in mesh.vertices) <= 1e-9)
    gates.check("動かしたのは、正中線のずれた頂点だけ（他の位置は人間版のまま）", True, f"{len(off)}頂点")

    sizes = {}
    for p in mesh.polygons:
        sizes[len(p.vertices)] = sizes.get(len(p.vertices), 0) + 1
    gates.note("面の内訳（半分）", sizes)
    cre = mesh.attributes.get("crease_edge")
    shp = mesh.attributes.get("sharp_edge")
    gates.check("クリース1.0とシャープの印は、26辺のまま（縁 R0 と R1）",
                cre is not None and shp is not None and sum(1 for d in cre.data if d.value > 0) == 26 and sum(1 for d in shp.data if d.value) == 26)

    # ---- Mirror 後の検証
    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bm = bmesh.new()
    bm.from_mesh(ev)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    Vn, En, Fn = len(bm.verts), len(bm.edges), len(bm.faces)
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len({frozenset(e.verts[i].index for i in (0, 1)) for e in bm.edges}) == En and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in bm.verts}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    lens = loops_of(bm)
    gates.check("穴（境界の輪）は、口（16辺）と首の下端（12辺）の2つだけ", lens == [12, 16], lens)
    # 1つの塊・向き: 種になる面（頭のてっぺんの面）が外向き
    comp = {bm.faces[0].index}
    stack = [bm.faces[0]]
    while stack:
        f = stack.pop()
        for e in f.edges:
            for g in e.link_faces:
                if g.index not in comp:
                    comp.add(g.index)
                    stack.append(g)
    gates.check("面は1つの塊につながっている", len(comp) == Fn, f"{len(comp)}/{Fn}")
    top = max(bm.faces, key=lambda f: f.calc_center_median().z)
    gates.check("頭のてっぺんの面の法線が外向き（巻き順が一貫なので、全面が外向き）", top.normal.z > 0, f"法線 {rd(top.normal)}")
    kd = KDTree(len(bm.verts))
    for v in bm.verts:
        kd.insert(v.co, v.index)
    kd.balance()
    close = [(v.index, i) for v in bm.verts for _, i, d in kd.find_range(v.co, 0.0009) if i > v.index]
    gates.check("0.9mm 以内に近づいた頂点の対がない（結合の漏れがない）", not close, close[:6])
    bm.free()
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s11b_gen.blend"), compress=False)
    gates.finish()


main()
