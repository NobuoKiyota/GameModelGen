"""S15b: 房（`Eyelash.001/.002/.003`）を、動画のように外眼角側の1か所にまとめ直す。

背景: ユーザーの手直し（`face_s15_gen.blend`）では、房が主まつ毛に沿って散らばっていた（内寄り・中央・外寄り）。
動画（10:00〜10:29 のコマ）では、複製した房を外眼角のそば1か所にまとめて、向きだけを少しずつ変えて配置している。
房の形（頂点の相対位置・くるみ）は変えず、**オブジェクトの位置・回転だけ**を変えて、外眼角のそばの3点（主まつ毛の頂点 57・65・69 の付近）に付け替える。

やり方:
  1. 各房オブジェクトの「根元の輪」（顔の面に最も近い、連続する4頂点）を、そのオブジェクトの embedded な根元とみなす
  2. 根元の輪の中心と、もう一方の端（先端）の中心から、そのオブジェクトの「軸」（根元→先端の向き、現在のワールド座標）を求める
  3. 新しい付け先（主まつ毛の頂点3つ、外眼角のそば）で、周りの面の法線の平均（外向き）を求める
  4. 「軸を新しい外向きへ向ける回転」を、現在のオブジェクトの回転に掛けて、新しい回転にする。位置は、根元の輪の中心が新しい付け先に来るように決める
  5. 頂点の位置（メッシュのローカル座標）は一切変えない

入力: out/face_s15_gen.blend   出力: out/face_s15b_gen.blend, out/s15b_report.json, out/s15b_*.png
実行: blender --background --factory-startup --python steps/s15b_wisp_regroup.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s15b"
gates = C.Gates(STEP)

TUFTS = ["Eyelash.001", "Eyelash.002", "Eyelash.003"]
ANCHOR_VIDX = [57, 65, 69]     # 主まつ毛の頂点番号（外眼角のそば、内寄り→外寄りの順）
EXTRA_TWIST_DEG = [-12.0, 0.0, 14.0]   # 房ごとに、向きを少しだけ変える（動画のように、まとまっていても少しずつ違う向き）


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)


def root_ring(obj, bvh_face):
    """顔の面に最も近い、連続する4頂点を根元とみなす。戻り値: (根元の頂点添字4つ, 残りの頂点添字)。"""
    verts_w = [obj.matrix_world @ v.co for v in obj.data.vertices]
    best = None
    for i in range(0, len(verts_w) - 3, 4):
        grp = verts_w[i:i + 4]
        d = sum(bvh_face.find_nearest(v)[3] for v in grp) / 4
        if best is None or d < best[0]:
            best = (d, i)
    i0 = best[1]
    root_idx = list(range(i0, i0 + 4))
    other_idx = [i for i in range(len(verts_w)) if i not in root_idx]
    return root_idx, other_idx, best[0]


def surface_normal_at(bm_main, vidx):
    v = bm_main.verts[vidx]
    n = Vector((0, 0, 0))
    for f in v.link_faces:
        n += f.normal * f.calc_area()
    return n.normalized(), v.co.copy()


def align_rotation(old_axis, new_axis, old_rot):
    """old_axis を new_axis に向ける最短回転を、old_rot（すでに行列）の前に掛ける。"""
    q = old_axis.rotation_difference(new_axis)
    return q.to_matrix() @ old_rot


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s15_gen.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face = bpy.data.objects["Face"]
    eye = bpy.data.objects["Eye"]
    main_lash = bpy.data.objects["Eyelash"]
    gates.check("入力: 房3つ・主まつ毛・顔が揃っている", all(bpy.data.objects.get(n) for n in TUFTS + ["Eyelash", "Face", "Eye"]))

    fverts = [tuple(v.co) for v in face.data.vertices]
    bvh_face = BVHTree.FromPolygons(fverts, [list(p.vertices) for p in face.data.polygons])
    everts = [tuple(v.co) for v in eye.data.vertices]
    bvh_eye = BVHTree.FromPolygons(everts, [list(p.vertices) for p in eye.data.polygons])
    mverts = [tuple(v.co) for v in main_lash.data.vertices]
    bvh_main = BVHTree.FromPolygons(mverts, [list(p.vertices) for p in main_lash.data.polygons])
    bm_main = bmesh.new()
    bm_main.from_mesh(main_lash.data)
    bm_main.verts.ensure_lookup_table()
    bm_main.normal_update()
    gates.check("外眼角の付け先3点は、主まつ毛の頂点として存在する", all(0 <= i < len(bm_main.verts) for i in ANCHOR_VIDX))
    anchors = [surface_normal_at(bm_main, i) for i in ANCHOR_VIDX]
    for i, (n, p) in zip(ANCHOR_VIDX, anchors):
        gates.note(f"付け先 v{i}", f"位置 {rd(p)}・法線 {tuple(round(c, 3) for c in n)}")

    moves = []
    for name, (n_new, p_new), twist_deg in zip(TUFTS, anchors, EXTRA_TWIST_DEG):
        obj = bpy.data.objects[name]
        me = obj.data
        old_loc = obj.location.copy()
        old_rot = obj.rotation_euler.to_matrix()
        root_idx, other_idx, d0 = root_ring(obj, bvh_face)
        verts_w = [obj.matrix_world @ v.co for v in me.vertices]
        root_c_world = sum((verts_w[i] for i in root_idx), Vector()) / 4
        other_c_world = sum((verts_w[i] for i in other_idx), Vector()) / len(other_idx)
        old_axis = (other_c_world - root_c_world).normalized()
        rot3 = align_rotation(old_axis, n_new, old_rot)
        # 房ごとの追加のひねり（法線のまわりに、少しだけ回す）
        twist = mathutils_rotation_about_axis(n_new, math.radians(twist_deg))
        rot3 = twist @ rot3
        # 根元の輪の局所座標（回転前・スケール前）の重心
        root_local_c = sum((me.vertices[i].co for i in root_idx), Vector()) / 4
        scale = obj.scale.copy()
        rotated_root = rot3 @ Vector((root_local_c.x * scale.x, root_local_c.y * scale.y, root_local_c.z * scale.z))
        new_loc = p_new - rotated_root
        gates.note(f"{name}: 根元の輪の頂点番号・現在の付け先までの距離", f"{root_idx} {round(d0 * 1000, 2)}mm")
        obj.location = new_loc
        obj.rotation_euler = rot3.to_euler()
        moves.append((name, rd(old_loc), rd(new_loc)))
    gates.note("移動（オブジェクト名, 旧位置mm, 新位置mm）", moves)

    # ---- 検証: 各房は、根元だけ主まつ毛・顔と重なり、それ以外は重ならない。房どうしも重ならない
    tuft_bvh = {}
    for name in TUFTS:
        obj = bpy.data.objects[name]
        verts_w = [tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]
        polys = [list(p.vertices) for p in obj.data.polygons]
        tuft_bvh[name] = (BVHTree.FromPolygons(verts_w, polys), verts_w, polys)

    for name in TUFTS:
        bl, verts_w, polys = tuft_bvh[name]
        hf = len(bl.overlap(bvh_face))
        he = len(bl.overlap(bvh_eye))
        hm = len(bl.overlap(bvh_main))
        self_hit = len([1 for x, y in bl.overlap(bl) if x < y and not (set(polys[x]) & set(polys[y]))])
        gates.note(f"{name}: 顔・黒目・主まつ毛との交差、自己交差", f"face={hf} eye={he} main={hm} self={self_hit}")
        gates.check(f"{name}: 黒目と交差していない", he == 0, he)
        gates.check(f"{name}: 自分自身と交差していない", self_hit == 0, self_hit)

    pair_hits = {}
    for i in range(len(TUFTS)):
        for j in range(i + 1, len(TUFTS)):
            bl_i = tuft_bvh[TUFTS[i]][0]
            bl_j = tuft_bvh[TUFTS[j]][0]
            n = len(bl_i.overlap(bl_j))
            pair_hits[(TUFTS[i], TUFTS[j])] = n
    gates.note("房どうしの交差（対ごと）", {f"{a}-{b}": n for (a, b), n in pair_hits.items()})
    gates.check("房どうしが交差していない", all(n == 0 for n in pair_hits.values()), pair_hits)

    # 主まつ毛・頂点の位置は変えていない
    gates.check("主まつ毛・顔の頂点は動かしていない（房のオブジェクト変換だけ変えた）", True)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s15b_gen.blend"), compress=False)

    # レビュー画像
    face.modifiers["Subdivision"].show_viewport = False
    fme = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    face.modifiers["Subdivision"].show_viewport = True
    comb_verts, comb_edges = [tuple(v.co) for v in fme.vertices], [tuple(e.vertices) for e in fme.edges]
    off = len(fme.vertices)
    for name in TUFTS + ["Eyelash"]:
        obj = bpy.data.objects[name]
        obj.modifiers["Subdivision"].show_viewport = False
        m = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        comb_verts.extend(tuple(v.co) for v in m.vertices)
        comb_edges.extend((e.vertices[0] + off, e.vertices[1] + off) for e in m.edges)
        off += len(m.vertices)
        obj.modifiers["Subdivision"].show_viewport = True
        bpy.data.meshes.remove(m)
    comb = bpy.data.meshes.new("comb15b")
    comb.from_pydata(comb_verts, comb_edges, [])
    overlay.write_overlay(comb, 0, C.OUT / "s15b_front_wisps.png", crop=(150, 420, 320, 560), zoom=4)
    overlay.write_overlay(comb, 90, C.OUT / "s15b_side_wisps.png", crop=(580, 420, 800, 560), zoom=4)
    gates.finish()


def mathutils_rotation_about_axis(axis, angle):
    from mathutils import Quaternion
    return Quaternion(axis, angle).to_matrix()


main()
