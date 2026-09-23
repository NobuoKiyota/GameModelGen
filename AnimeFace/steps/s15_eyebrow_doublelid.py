"""S15: 眉毛と二重線を作る（後編 動画 12:01〜13:50）。

字幕との対応:
  12:01〜12:11 眉毛になる辺を複製（Shift+D）                              → 別オブジェクト `Eyebrow`。形は下絵の眉（茶色の塗り）から測る
  12:11〜12:28 E で押し出し、眉尻の方へ押し出し、だいたいの位置に合わせる       → 中心線・太さを、正面の下絵から測った輪郭（上端・下端）に沿わせる
  12:28〜12:45 眉尻をもう少し奥へ。顔にふんわりかぶる程度に浮かす              → 顔の面（Face）へ光線を当てて、面から少し（OFF_OUT）浮かせた位置に置く
  12:45〜13:04 二重線も同じように、複製して作る。目からあまり離れない位置に      → 別オブジェクト `DoubleLid`。中心線を、下絵の薄い線から測る（塗りではないので、太さは一定の細さにする）
  13:04〜13:19 枠（外側）は投げておく、下から見て少しカーブがかるように         → 中心線は、下絵の実測（既に緩いカーブになっている）に従う。太さは眉より細くする
  ※ 13:31〜 は、テクスチャの試し塗り（UV展開・ペイント）で、S16 以降

設計（S14 の主まつ毛の帯と同じ、実測にもとづく方式。房で失敗した「見た目まかせの曲げ」は使わない）:
  - 眉・二重線とも、下絵の正面図から、上端・下端（眉）または中心（二重線）の行を、列ごとに測る
  - 各駅で、列の位置（px）を皮膚の表面へ光線で当て、そこから少し（OFF_OUT）浮かせる。太さ（半幅）は、眉は測った厚み、二重線は一定の細さ
  - 断面は、外側 O・前の稜 F・内側 I・後ろ K のひし形（主まつ毛と同じ）。前の稜にクリース1.0。Mirror（Object=Face）＋ Subdivision（表示1・レンダー2）
  - 駅の間は、皮膚の曲面に沿うように、線形補間で1つずつ挟んで密にする（皮膚の内側に潜らないように）

入力: out/face_s14b2_gen.blend   出力: out/face_s15_gen.blend, out/s15_report.json, out/s15_*.png
実行: blender --background --factory-startup --python steps/s15_eyebrow_doublelid.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s15"
gates = C.Gates(STEP)

OFF_OUT = 0.0007          # 皮膚の表面から、外側の点までの浮かし量
H_FRONT_BROW = 0.0012     # 眉: 前の稜（外向きの膨らみ）
H_BACK_BROW = 0.0003
H_FRONT_LID = 0.0005      # 二重線: もっと控えめ
H_BACK_LID = 0.0002
LID_HALF_MM = 1.3         # 二重線の半幅（一定）


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)


def px_to_xz(u, v):
    return (u - C.COL0) * C.K, (C.ROW0 - v) * C.K


def is_brow(px):
    r, g, b = int(px[0]), int(px[1]), int(px[2])
    return (50 < r < 180) and (20 < g < 140) and (0 < b < 120) and r > g > b and (r - b) > 25


def measure_brow():
    im = M._px("front")[..., :3]
    mask = np.zeros((im.shape[0], im.shape[1]), dtype=bool)
    for y in range(370, 430):
        for x in range(230, 430):
            if is_brow(im[y, x]):
                mask[y, x] = True
    cols = []
    for x in range(238, 427):
        col = np.where(mask[:, x])[0]
        if len(col):
            cols.append((x, int(col.min()), int(col.max())))
    # 下絵の線には画素単位のがたつきがある（上端・下端で標準偏差 1.8px、最大 7px）。
    # 移動平均で均してから使う（動画は、少ない頂点で滑らかな眉にしている。がたつきをそのまま拾わない）
    tops = smooth([c[1] for c in cols], 7)
    bots = smooth([c[2] for c in cols], 7)
    return [(cols[i][0], tops[i], bots[i]) for i in range(len(cols))]


def smooth(arr, win):
    a = np.array(arr, dtype=float)
    k = np.ones(win) / win
    pad = win // 2
    ap = np.pad(a, pad, mode="edge")
    return np.convolve(ap, k, mode="valid")[:len(a)]


def measure_doublelid():
    im = M._px("front")[..., :3]
    val = im.mean(axis=2)
    black = val < 95
    pts = []
    for x in range(276, 404):        # 404 まで（それより内側は、眉の下端と混じって誤検出する）
        col = np.where(black[420:465, x])[0] + 420   # 420 から（406 からだと、眉の下端の先端を拾ってしまう）
        if len(col) == 0:
            continue
        # 最初の連続した塊（上端に一番近いもの）だけを使う（下は睫毛の帯）
        run = [col[0]]
        for c in col[1:]:
            if c - run[-1] <= 1:
                run.append(c)
            else:
                break
        if len(run) <= 5:
            pts.append((x, float(np.mean(run))))
    xs = [p[0] for p in pts]
    ys = smooth([p[1] for p in pts], 9)
    return list(zip(xs, ys))


def build_ribbon(name, stations, half_w_fn, h_front, h_back, bvh_skin, face_obj, n_insert=1):
    """stations: [(u, v)] の並び（下絵の画素）。皮膚へ光線を当てて、ひし形の断面の管を作る。"""
    pts3 = []
    for u, v in stations:
        x, z = px_to_xz(u, v)
        hit = bvh_skin.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 2.0)
        if hit[0] is None:
            continue
        pts3.append((hit[0], hit[1], (u, v)))
    dense = [pts3[0]]
    for a, b in zip(pts3[:-1], pts3[1:]):
        for j in range(1, n_insert + 1):
            t = j / (n_insert + 1)
            u = a[2][0] * (1 - t) + b[2][0] * t
            v = a[2][1] * (1 - t) + b[2][1] * t
            x, z = px_to_xz(u, v)
            hit = bvh_skin.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 2.0)
            if hit[0] is not None:
                dense.append((hit[0], hit[1], (u, v)))
        dense.append(b)
    verts, faces, ridge = [], [], []
    tan_prev = None
    for i, (p, n, uv) in enumerate(dense):
        if i == 0:
            tan = Vector(dense[1][0]) - Vector(p)
        elif i == len(dense) - 1:
            tan = Vector(p) - Vector(dense[i - 1][0])
        else:
            tan = Vector(dense[i + 1][0]) - Vector(dense[i - 1][0])
        side = n.cross(tan)
        if side.length < 1e-8:
            side = Vector((1, 0, 0))
        side.normalize()
        hw = half_w_fn(i, len(dense), uv)
        O = p + side * hw + n * OFF_OUT
        I = p - side * hw + n * OFF_OUT
        F = p + n * (OFF_OUT + h_front)
        K = p + n * (OFF_OUT - h_back)
        base = len(verts)
        verts.extend([O, F, I, K])
        ridge.append(base + 1)
    for i in range(len(dense) - 1):
        a, b = i * 4, (i + 1) * 4
        for j in range(4):
            faces.append([a + j, a + (j + 1) % 4, b + (j + 1) % 4, b + j])
    faces.append([3, 2, 1, 0])
    last = (len(dense) - 1) * 4
    faces.append([last, last + 1, last + 2, last + 3])
    return verts, faces, ridge


def make_object(name, face_ref, verts, faces, ridge):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    # 向き: 断面の中心（帯全体の重心）から見て外向きに
    cen = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    bad = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - cen) <= 0]
    n_flip = len(bad)
    if n_flip > len(bm.faces) / 2:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
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
    obj = bpy.data.objects.new(name, me)
    (face_ref.users_collection[0] if face_ref.users_collection else bpy.context.scene.collection).objects.link(obj)
    mm = obj.modifiers.new("Mirror", "MIRROR")
    mm.use_axis[0] = True
    mm.mirror_object = face_ref
    mm.use_clip = False
    mm.use_mirror_merge = False
    sm = obj.modifiers.new("Subdivision", "SUBSURF")
    sm.levels, sm.render_levels = 1, 2
    return obj, marked


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s14b2_gen.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face = bpy.data.objects["Face"]
    gates.check("入力: Face は Mirror → Subsurf、頂点513・面480", [m.type for m in face.modifiers] == ["MIRROR", "SUBSURF"] and len(face.data.vertices) == 513 and len(face.data.polygons) == 480)
    fverts = [tuple(v.co) for v in face.data.vertices]
    fpolys = [list(p.vertices) for p in face.data.polygons]
    bvh_skin = BVHTree.FromPolygons(fverts, fpolys)

    # ---- 眉
    brow = measure_brow()
    gates.check("眉の輪郭が、189列（x238〜426）で測れた", len(brow) >= 150, len(brow))
    n_st = 13
    idxs = np.linspace(0, len(brow) - 1, n_st).astype(int)
    stations_c = [((brow[i][0]), (brow[i][1] + brow[i][2]) / 2) for i in idxs]
    thick_px = {i: max((brow[idxs[k]][2] - brow[idxs[k]][1]) / 2, 1.5) for k, i in enumerate(idxs)}
    thick_list = [thick_px[i] for i in idxs]

    N_INS_BROW = 3

    def brow_hw(i, n, uv):
        return thick_list[min(i // (N_INS_BROW + 1), len(thick_list) - 1)] * C.K

    v_b, f_b, r_b = build_ribbon("Eyebrow", stations_c, brow_hw, H_FRONT_BROW, H_BACK_BROW, bvh_skin, face, n_insert=N_INS_BROW)
    eyebrow, cre_b = make_object("Eyebrow", face, v_b, f_b, r_b)
    gates.note("眉: 駅の数・頂点・面", f"{len(stations_c)}駅 → 頂点{len(eyebrow.data.vertices)} 面{len(eyebrow.data.polygons)}")

    # ---- 二重線
    lid = measure_doublelid()
    gates.check("二重線の中心線が、%d列（x276〜418）で測れた" % len(lid), len(lid) >= 100, len(lid))
    n_st2 = 9
    idxs2 = np.linspace(0, len(lid) - 1, n_st2).astype(int)
    stations_l = [lid[i] for i in idxs2]

    def lid_hw(i, n, uv):
        return LID_HALF_MM / 1000

    v_l, f_l, r_l = build_ribbon("DoubleLid", stations_l, lid_hw, H_FRONT_LID, H_BACK_LID, bvh_skin, face, n_insert=1)
    doublelid, cre_l = make_object("DoubleLid", face, v_l, f_l, r_l)
    gates.note("二重線: 駅の数・頂点・面", f"{len(stations_l)}駅 → 頂点{len(doublelid.data.vertices)} 面{len(doublelid.data.polygons)}")

    # ---- 検証（共通）
    for obj, tag in ((eyebrow, "眉"), (doublelid, "二重線")):
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        gates.check(f"{tag}: 全ての面が四角形・全ての辺が2枚の面（閉じている）", all(len(f.verts) == 4 for f in bm.faces) and all(len(e.link_faces) == 2 for e in bm.edges))
        gates.check(f"{tag}: 価数2の頂点がない", all(len(v.link_edges) >= 3 for v in bm.verts))
        share = {}
        for f in bm.faces:
            vs = list(f.verts)
            for j in range(len(vs)):
                a, b = vs[j], vs[(j + 1) % len(vs)]
                share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
        gates.check(f"{tag}: 巻き順が一貫・3枚以上が共有する辺なし", all(len(d) <= 2 and (len(d) < 2 or d[0] == (d[1][1], d[1][0])) for d in share.values()))
        verts_w = [tuple(v.co) for v in bm.verts]
        polys = [[v.index for v in f.verts] for f in bm.faces]
        bl = BVHTree.FromPolygons(verts_w, polys)
        self_hit = len([1 for x, y in bl.overlap(bl) if x < y and not (set(polys[x]) & set(polys[y]))])
        gates.check(f"{tag}: 自分自身と交差していない", self_hit == 0, self_hit)
        gates.check(f"{tag}: X<0（左側）の側だけ", max(v.co.x for v in bm.verts) < 0)
        bm.free()

    # 顔との交差（浮かした分の隙間 OFF_OUT より、めり込みがないか）
    for obj, tag in ((eyebrow, "眉"), (doublelid, "二重線")):
        verts_w = [tuple(v.co) for v in obj.data.vertices]
        polys = [list(p.vertices) for p in obj.data.polygons]
        bl = BVHTree.FromPolygons(verts_w, polys)
        hits = len(bl.overlap(bvh_skin))
        dmin = min(bvh_skin.find_nearest(v)[3] for v in verts_w)
        gates.note(f"{tag}: 顔の面との交差・最小距離", f"交差 {hits}、最小 {dmin * 1000:.2f}mm")
        gates.check(f"{tag}: 顔の面と交差していない", hits == 0, hits)

    # 眉と二重線が、互いに交差・接触していないか（前回、内側の端で混じって接触した）
    bverts = [tuple(v.co) for v in eyebrow.data.vertices]
    bpolys = [list(p.vertices) for p in eyebrow.data.polygons]
    bvh_brow = BVHTree.FromPolygons(bverts, bpolys)
    lverts_ = [tuple(v.co) for v in doublelid.data.vertices]
    lpolys = [list(p.vertices) for p in doublelid.data.polygons]
    bvh_lid = BVHTree.FromPolygons(lverts_, lpolys)
    hits_bl = len(bvh_brow.overlap(bvh_lid))
    dmin_bl = min(bvh_brow.find_nearest(v)[3] for v in lverts_)
    gates.note("眉と二重線の交差・最小距離", f"交差 {hits_bl}、最小 {dmin_bl * 1000:.2f}mm")
    gates.check("眉と二重線が交差・接触していない（1mm 以上離れている）", hits_bl == 0 and dmin_bl >= 0.001, f"交差{hits_bl} 最小{dmin_bl * 1000:.2f}mm")

    gates.check("眉: 前の稜にクリース1.0（駅の間を3つ補ったので、辺は (駅数-1)×4 本）", cre_b == (len(stations_c) - 1) * 4, cre_b)
    gates.check("二重線: 前の稜にクリース1.0（駅の間を1つ補ったので、辺は (駅数-1)×2 本）", cre_l == (len(stations_l) - 1) * 2, cre_l)

    # ---- Mirror 後の確認・IoU（眉の正面の投影と、下絵の測った領域）
    im = M._px("front")[..., :3]
    mask_target = np.zeros((1024, 1024), dtype=bool)
    for x, t, b in brow:
        mask_target[int(round(t)):int(round(b)) + 1, x] = True

    def eval_mask(obj):
        sm = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
        old = sm.levels
        sm.levels = 2
        bpy.context.view_layer.update()
        ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        sm.levels = old
        mask = np.zeros((1024, 1024), dtype=bool)
        for p in ev.polygons:
            if max(ev.vertices[i].co.x for i in p.vertices) > 1e-6:
                continue
            uv = [C.project(ev.vertices[i].co, 0) for i in p.vertices]
            P_ = np.array(uv)
            yy0, yy1 = int(max(P_[:, 1].min(), 0)), int(min(P_[:, 1].max(), 1023))
            for a in range(1, len(uv) - 1):
                tri = [uv[0], uv[a], uv[a + 1]]
                Pt = np.array(tri)
                y0, y1 = int(max(Pt[:, 1].min(), 0)), int(min(Pt[:, 1].max(), 1023))
                for y in range(y0, y1 + 1):
                    xs = []
                    for k in range(3):
                        pa, pb = Pt[k], Pt[(k + 1) % 3]
                        yb = y + 0.5
                        if (pa[1] <= yb < pb[1]) or (pb[1] <= yb < pa[1]):
                            xs.append(pa[0] + (yb - pa[1]) * (pb[0] - pa[0]) / (pb[1] - pa[1]))
                    if len(xs) >= 2:
                        x0, x1 = sorted(xs)[:2]
                        mask[y, int(max(x0, 0)):int(min(x1, 1023)) + 1] = True
        bpy.data.meshes.remove(ev)
        return mask

    mask_brow = eval_mask(eyebrow)
    box = (230, 370, 430, 420)
    u0, v0, u1, v1 = box
    inter = (mask_brow[v0:v1, u0:u1] & mask_target[v0:v1, u0:u1]).sum()
    union = (mask_brow[v0:v1, u0:u1] | mask_target[v0:v1, u0:u1]).sum()
    iou = inter / max(union, 1)
    gates.note("眉: Subsurf 後の正面の投影と、下絵の測った領域の重なり（IoU）", round(iou, 2))
    gates.check("眉: IoU が 0.55 以上", iou >= 0.55, round(iou, 2))

    # レビュー画像
    fme = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bme = bpy.data.meshes.new_from_object(eyebrow.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    lme = bpy.data.meshes.new_from_object(doublelid.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    comb = bpy.data.meshes.new("comb15")
    verts = [tuple(v.co) for v in fme.vertices] + [tuple(v.co) for v in bme.vertices] + [tuple(v.co) for v in lme.vertices]
    o1 = len(fme.vertices)
    o2 = o1 + len(bme.vertices)
    edges = [tuple(e.vertices) for e in fme.edges] + [(e.vertices[0] + o1, e.vertices[1] + o1) for e in bme.edges] + [(e.vertices[0] + o2, e.vertices[1] + o2) for e in lme.edges]
    comb.from_pydata(verts, edges, [])
    overlay.write_overlay(comb, 0, C.OUT / "s15_front_brow.png", crop=(190, 370, 440, 470), zoom=3)
    overlay.write_overlay(comb, 90, C.OUT / "s15_side_brow.png", crop=(600, 370, 850, 470), zoom=3)
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s15_gen.blend"), compress=False)
    gates.finish()


main()
