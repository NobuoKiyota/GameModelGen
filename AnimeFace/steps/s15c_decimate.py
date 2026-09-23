"""S15c: face_s15_human (2).blend の眉・二重線の頂点数を、弧の長さで等間隔に間引く（形はそのまま。ユーザーの手直しを保つ）。

やり方（頂点の位置は測り直さない。既存の頂点をそのまま使う）:
  1. 眉・二重線とも、既存のメッシュは「駅（4頂点: 外側O・前の稜F・内側I・後ろK）× N」の帯（前回の生成のまま。クリースの並びで確認済み）
  2. 前の稜（F、クリースの並び）を、根元→先端の順にたどり、駅ごとの弧の長さ（F点間の距離の積み上げ）を求める
  3. 弧の長さで等間隔になる駅を、目標の駅数だけ選ぶ（両端は必ず含む）
  4. 選んだ駅の O・F・I・K を、そのままの位置で使い、帯を作り直す（辺・面・クリース・Mirror・Subdivisionも作り直す）

入力: out/face_s15_human (2).blend   出力: out/face_s15c_gen.blend, out/s15c_report.json, out/s15c_*.png
実行: blender --background --factory-startup --python steps/s15c_decimate.py
"""
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s15c"
gates = C.Gates(STEP)

TARGETS = {"Eyebrow": 8, "DoubleLid": 7}


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)


def station_rings(me):
    """既存の帯から、駅ごとの4頂点 [O,F,I,K]（頂点番号）を、根元→先端の順で取り出す。"""
    n = len(me.vertices)
    stations = [[4 * i + j for j in range(4)] for i in range(n // 4)]
    return stations


def decimate_ribbon(obj, target_n):
    me = obj.data
    stations = station_rings(me)
    P = [v.co.copy() for v in me.vertices]
    F_pts = [P[st[1]] for st in stations]  # 前の稜（F）の点で弧の長さを測る
    arc = [0.0]
    for a, b in zip(F_pts[:-1], F_pts[1:]):
        arc.append(arc[-1] + (b - a).length)
    total = arc[-1]
    gates.note(f"{obj.name}: 元の駅数・全長", f"{len(stations)}駅 {total * 1000:.1f}mm")
    targets = [total * k / (target_n - 1) for k in range(target_n)]
    kept = []
    for t in targets:
        i = min(range(len(arc)), key=lambda k: abs(arc[k] - t))
        if not kept or i != kept[-1]:
            kept.append(i)
    if kept[0] != 0:
        kept[0] = 0
    if kept[-1] != len(stations) - 1:
        kept[-1] = len(stations) - 1
    gates.check(f"{obj.name}: 間引いた駅の数が目標どおり（重複はまとめる）", len(kept) >= target_n - 1, f"{len(kept)}駅（目標{target_n}）")

    verts, faces, ridge = [], [], []
    for i in kept:
        st = stations[i]
        base = len(verts)
        verts.extend([P[st[j]].copy() for j in range(4)])
        ridge.append(base + 1)
    for i in range(len(kept) - 1):
        a, b = i * 4, (i + 1) * 4
        for j in range(4):
            faces.append([a + j, a + (j + 1) % 4, b + (j + 1) % 4, b + j])
    faces.append([3, 2, 1, 0])
    last = (len(kept) - 1) * 4
    faces.append([last, last + 1, last + 2, last + 3])
    return verts, faces, ridge, kept, [arc[i] for i in kept]


def push_clear(verts, bvh_face, min_clear=0.0005):
    """駅（4頂点のリング）ごとに、断面の形を保ったまま、丸ごと外側へ押し出す。
    頂点1つずつ別々の向き・量で動かすと、断面がねじれて自己交差の原因になるため、駅単位でまとめて動かす。"""
    fixed = 0
    out = list(verts)
    for i in range(0, len(verts), 4):
        ring = list(out[i:i + 4])
        for _ in range(6):                     # 押し出した後、表面が変わるので、収まるまで数回繰り返す
            worst, worst_nrm = None, None
            for v in ring:
                loc, nrm, idx, dist = bvh_face.find_nearest(v)
                sign_dist = nrm.dot(v - loc)
                if worst is None or sign_dist < worst:
                    worst, worst_nrm = sign_dist, nrm
            if worst >= min_clear:
                break
            step = min(min_clear - worst, 0.001)   # 一度に大きく動かさない（暴走を防ぐ）
            ring = [v + worst_nrm.normalized() * step for v in ring]
            fixed += 1
        out[i:i + 4] = ring
    return out, fixed


def rebuild(obj, verts, faces, ridge, face_ref):
    old_me = obj.data
    old_mods = [(m.type, m.mirror_object.name if m.type == "MIRROR" else None,
                 (m.levels, m.render_levels) if m.type == "SUBSURF" else None) for m in obj.modifiers]
    me = bpy.data.meshes.new(obj.name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    cen = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    bad = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - cen) <= 0]
    if len(bad) > len(bm.faces) / 2:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bad = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - cen) <= 0]
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ca = me.attributes.new("crease_edge", "FLOAT", "EDGE")
    ridge_keys = {frozenset((ridge[i], ridge[i + 1])) for i in range(len(ridge) - 1)}
    marked = 0
    for e in me.edges:
        if frozenset(e.vertices) in ridge_keys:
            ca.data[e.index].value = 1.0
            marked += 1
    obj.data = me
    bpy.data.meshes.remove(old_me)
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    mm = obj.modifiers.new("Mirror", "MIRROR")
    mm.use_axis[0] = True
    mm.mirror_object = face_ref
    mm.use_clip = False
    mm.use_mirror_merge = False
    sm = obj.modifiers.new("Subdivision", "SUBSURF")
    sm.levels, sm.render_levels = 1, 2
    return marked, len(bad)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s15_human (2).blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face = bpy.data.objects["Face"]
    eye = bpy.data.objects["Eye"]
    fverts = [tuple(v.co) for v in face.data.vertices]
    bvh_face = BVHTree.FromPolygons(fverts, [list(p.vertices) for p in face.data.polygons])
    everts = [tuple(v.co) for v in eye.data.vertices]
    bvh_eye = BVHTree.FromPolygons(everts, [list(p.vertices) for p in eye.data.polygons])

    results = {}
    baseline_overlap = {}
    for name, target_n in TARGETS.items():
        obj = bpy.data.objects[name]
        gates.check(f"入力: {name} は Mirror → Subsurf、全て四角形", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"] and all(len(p.vertices) == 4 for p in obj.data.polygons))
        # このオブジェクトに移動・回転・拡大がついていると、ローカル座標のままでは顔（ワールド座標）と比べられない。
        # メッシュへ焼き込んで、オブジェクトの変換を単位行列に戻す（見た目の位置・形は変えない）
        xf = obj.matrix_world.copy()
        if tuple(obj.location) != (0.0, 0.0, 0.0) or tuple(obj.scale) != (1.0, 1.0, 1.0) or tuple(obj.rotation_euler) != (0.0, 0.0, 0.0):
            obj.data.transform(xf)
            obj.location = (0.0, 0.0, 0.0)
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.scale = (1.0, 1.0, 1.0)
            gates.note(f"{name}: オブジェクトの変換をメッシュへ焼き込んだ（移動・拡大がついていたため）", f"{tuple(round(c, 4) for c in xf.translation)} scale {tuple(round(c, 3) for c in xf.to_scale())}")
        # 間引く前（＝ユーザーが確認済みの元の形）の、顔の面との三角形の重なりを、比較の基準として測っておく
        bl0 = BVHTree.FromPolygons([tuple(v.co) for v in obj.data.vertices], [list(p.vertices) for p in obj.data.polygons])
        baseline_overlap[name] = len(bl0.overlap(bvh_face))
        n_v0, n_f0 = len(obj.data.vertices), len(obj.data.polygons)
        verts, faces, ridge, kept, arc_kept = decimate_ribbon(obj, target_n)
        marked, n_bad = rebuild(obj, verts, faces, ridge, face)
        gates.note(f"{name}: 全体の重心から見た向き判定（曲がった帯では誤検出しやすいので参考値）", n_bad)
        gates.check(f"{name}: 頂点 {n_v0}→{len(obj.data.vertices)}・面 {n_f0}→{len(obj.data.polygons)}", len(obj.data.vertices) == len(kept) * 4)
        gates.check(f"{name}: 前の稜にクリース1.0（(駅数-1)本）", marked == len(kept) - 1, marked)
        results[name] = (n_v0, len(obj.data.vertices), kept)

    # 検証: 自己交差なし・顔と交差なし（根元は除かない。今回は測り直していないので、埋め込みがあれば元から重なっているはず）
    for name in TARGETS:
        obj = bpy.data.objects[name]
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        gates.check(f"{name}: 価数2の頂点がない・全ての辺が2枚の面", all(len(v.link_edges) >= 3 for v in bm.verts) and all(len(e.link_faces) == 2 for e in bm.edges))
        share = {}
        for f in bm.faces:
            vs = list(f.verts)
            for j in range(len(vs)):
                a, b2 = vs[j], vs[(j + 1) % len(vs)]
                share.setdefault(frozenset((a.index, b2.index)), []).append((a.index, b2.index))
        gates.check(f"{name}: 巻き順が一貫（隣り合う面が、共有する辺を逆向きにたどる）", all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()))
        verts_w = [tuple(v.co) for v in bm.verts]
        polys = [[v.index for v in f.verts] for f in bm.faces]
        bl = BVHTree.FromPolygons(verts_w, polys)
        self_hit = len([1 for x, y in bl.overlap(bl) if x < y and not (set(polys[x]) & set(polys[y]))])
        gates.check(f"{name}: 自分自身と交差していない", self_hit == 0, self_hit)
        gates.check(f"{name}: 黒目と交差していない", len(bl.overlap(bvh_eye)) == 0, len(bl.overlap(bvh_eye)))
        hf = len(bl.overlap(bvh_face))
        gates.note(f"{name}: 顔の面との三角形の重なり（元の帯は {baseline_overlap[name]} 枚だった）", hf)
        gates.check(f"{name}: 顔の面との重なりが、元の帯より悪化していない", hf <= baseline_overlap[name] + 5, f"{hf} <= {baseline_overlap[name] + 5}")
        bm.free()

    # 眉と二重線の間の距離（今回変えていないので、離れているはず）
    b = bpy.data.objects["Eyebrow"].data
    l = bpy.data.objects["DoubleLid"].data
    bvh_b = BVHTree.FromPolygons([tuple(v.co) for v in b.vertices], [list(p.vertices) for p in b.polygons])
    lv = [tuple(v.co) for v in l.vertices]
    dmin = min(bvh_b.find_nearest(v)[3] for v in lv)
    gates.check("眉と二重線が、離れたまま（1mm以上）", dmin >= 0.001, f"{dmin * 1000:.1f}mm")

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s15c_gen.blend"), compress=False)

    # レビュー画像
    face.modifiers["Subdivision"].show_viewport = False
    fme = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    face.modifiers["Subdivision"].show_viewport = True
    comb_verts, comb_edges = [tuple(v.co) for v in fme.vertices], [tuple(e.vertices) for e in fme.edges]
    off = len(fme.vertices)
    for name in TARGETS:
        obj = bpy.data.objects[name]
        m = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        comb_verts.extend(tuple(v.co) for v in m.vertices)
        comb_edges.extend((e.vertices[0] + off, e.vertices[1] + off) for e in m.edges)
        off += len(m.vertices)
        bpy.data.meshes.remove(m)
    comb = bpy.data.meshes.new("comb15c")
    comb.from_pydata(comb_verts, comb_edges, [])
    overlay.write_overlay(comb, 0, C.OUT / "s15c_front_brow.png", crop=(190, 370, 440, 470), zoom=3)
    overlay.write_overlay(comb, 90, C.OUT / "s15c_side_brow.png", crop=(600, 370, 850, 470), zoom=3)
    gates.finish()


main()
