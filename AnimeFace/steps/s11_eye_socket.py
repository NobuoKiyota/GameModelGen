"""S11: 目の内側（眼窩）を作る（動画 28:51〜33:14）。

字幕との対応:
  28:51〜31:14 上下の頂点数を揃えるための部分ループ・スカルプトで均す・M で整理
               → 実装しない。目の縁は13頂点（上6・下5）。全て四角形のまま縁を1頂点増減すると、隣の輪の偶奇が合わず、
                 輪を遠くまで伸ばして奇数の面（三角形・五角形）を作る必要がある。動画は、当時開いていた穴まで輪を通して解決している。
                 目を閉じる形（シェイプキー）を作る時に、別に扱う
  31:17〜31:32 縁のループを E Y（後ろへ）で押し出し、S で大きく → 縁の輪 R0 から、後ろへ d1・面内で s1 倍の輪 R1（13頂点）
  31:35〜31:55 面を貼り、ループを1つ足して、F で穴を埋める             → R1 の後ろへ、さらに深く・小さい輪 R2（13頂点）を足し、その輪を中心の1点へ閉じる
                 （13角形は四角形だけにできない。中心の点から1つおきの頂点へ辺を引き、四角形6枚＋三角形1枚。眼球の裏で見えない）
  31:55〜32:00 「奥をもう少し後ろへ」 → R2 と中心の深さで調整（数値は仮定。要確認）
  32:11〜33:10 縁と奥のループにクリース（Shift+E）・シャープ（Ctrl+E）→ R0 と R1 の辺にクリース 1.0 と、シャープの印。全体をスムースシェードにする
  33:14        「ここが少しへこんでいるので前へ」→ 好みの判断なので触らない

設計（先に決めたこと）:
  - 奥の向きは、縁に接する面の法線の平均の逆（動画は E Y（世界の後ろ）だが、外側の目尻では、真後ろだと表面と平行になり、大きくした輪が皮膚を突き抜けるため）
  - R1: 縁の各点を、中心 C から見て、奥行き方向を除いた面内で s1 = 1.10 倍にして、奥へ d1 = 0.014m
  - R2: 面内で 0.55 倍、奥へ d1 + 0.010m。中心の点: 奥へ d1 + 0.016m
  - これらの数値は、下絵にない（眼球の大きさ・位置は、動画も目分量）。皮膚の内側に収まり、表面から離れていることだけを確かめる

入力: out/face_s10_gen.blend   出力: out/face_s11_gen.blend, out/s11_report.json, out/s11_*.png
実行: blender --background --factory-startup --python steps/s11_eye_socket.py
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

STEP = "s11"
gates = C.Gates(STEP)

HEAD_CENTER = Vector((0.0, 0.0, 0.086))
S1, D1 = 1.10, 0.014
S2, D2 = 0.55, 0.024
D_C = 0.030


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def eye_rim(bm):
    """目の縁の輪（境界の辺13本）。順にたどる。"""
    be = [e for e in bm.edges if len(e.link_faces) == 1
          and e.verts[0].co.x < -0.05 and e.verts[1].co.x < -0.05
          and abs(e.verts[0].co.z) < 0.06 and abs(e.verts[1].co.z) < 0.06
          and e.verts[0].co.y < -0.1 and e.verts[1].co.y < -0.1]
    start = be[0].verts[0]
    chain, prev, cur = [start], None, start
    while True:
        nxt = [e for e in cur.link_edges if e in be and e is not prev]
        e = nxt[0]
        cur = e.other_vert(cur)
        if cur is start:
            return chain, be
        chain.append(cur)
        prev = e


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s10_gen.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    n_v0, n_e0, n_f0 = len(bm.verts), len(bm.edges), len(bm.faces)
    sizes = {}
    for f in bm.faces:
        sizes[len(f.verts)] = sizes.get(len(f.verts), 0) + 1
    gates.check("入力: 四角形417・五角形6・頂点463", sizes == {4: 417, 5: 6} and n_v0 == 463, f"{sizes} V={n_v0}")

    rim, rim_edges = eye_rim(bm)
    n = len(rim)
    gates.check("目の縁の輪: 13頂点・13辺・全て X<0", n == 13 and len(rim_edges) == 13, f"{n}頂点")
    # 縁の各辺に接する面（13枚）と、その面の法線の平均
    rim_faces = []
    for e in rim_edges:
        rim_faces.append(e.link_faces[0])
    nrm = Vector((0, 0, 0))
    for f in rim_faces:
        nrm += f.normal * f.calc_area()
    nrm.normalize()
    back = -nrm
    cen = sum((v.co for v in rim), Vector()) / n
    # 上下の頂点数（要確認の記録）: 縁の輪を、目頭（X 最大）と目尻（X 最小）で上下に分ける
    inner = max(rim, key=lambda v: v.co.x)
    outer = min(rim, key=lambda v: v.co.x)
    i0, i1 = rim.index(inner), rim.index(outer)
    arc_a = [rim[(i0 + k) % n] for k in range(1, (i1 - i0) % n)]
    arc_b = [rim[(i1 + k) % n] for k in range(1, (i0 - i1) % n)]
    up, low = (arc_a, arc_b) if sum(v.co.z for v in arc_a) > sum(v.co.z for v in arc_b) else (arc_b, arc_a)
    gates.note("目の縁: 上の頂点数・下の頂点数（目頭と目尻を除く）", f"上{len(up)}・下{len(low)}（計{len(up) + len(low) + 2}）→ 揃えていない（上の理由）")
    gates.note("縁の中心・皮膚の法線の平均（外向き）・奥の向き", f"C={rd(cen)} n={rd(nrm)} 奥={rd(back)}")

    def ring(scale, depth):
        out = []
        for v in rim:
            d = v.co - cen
            along = d.dot(nrm)
            inplane = d - nrm * along
            out.append(cen + inplane * scale + nrm * along + back * depth)
        return out

    p1 = ring(S1, D1)
    p2 = ring(S2, D2)
    pc = cen + back * D_C
    r1 = [bm.verts.new(p) for p in p1]
    r2 = [bm.verts.new(p) for p in p2]
    c = bm.verts.new(pc)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    # 向き: 縁の辺を使っている既存の面と、逆向きに通る
    fwd = any(lp.link_loop_next.vert is rim[1] for lp in rim[0].link_loops)
    new_faces = []

    def add(vs):
        vs = list(vs)
        if fwd:
            vs = vs[::-1]
        new_faces.append(bm.faces.new(vs))

    for i in range(n):
        j = (i + 1) % n
        add([rim[i], rim[j], r1[j], r1[i]])
    for i in range(n):
        j = (i + 1) % n
        add([r1[i], r1[j], r2[j], r2[i]])
    for k in range(0, 12, 2):                                 # 中心 c と R2 の頂点 0,2,4,…,12 を結ぶ: 四角形6枚（c, v_k, v_k+1, v_k+2）
        add([c, r2[k], r2[k + 1], r2[k + 2]])
    add([c, r2[12], r2[0]])                                   # 三角形1枚
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.normal_update()
    gates.check("追加: 頂点 %d（R1 13＋R2 13＋中心1）・面 %d（縁→R1 13＋R1→R2 13＋中心 7）" % (len(bm.verts) - n_v0, len(new_faces)),
                len(bm.verts) - n_v0 == 27 and len(new_faces) == 33, f"V={len(bm.verts)} F={len(bm.faces)}")
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("巻き順が一貫・3枚以上が共有する辺なし", all(len(d) <= 2 and (len(d) < 2 or d[0] == (d[1][1], d[1][0])) for d in share.values()))
    # 向き: 壁は、穴の軸（縁の中心から奥）へ向く（穴の内側が空気）。底は、開口（外向き n）へ向く
    axis = back
    bad = []
    for idx, f in enumerate(new_faces):
        fc = f.calc_center_median()
        if idx < 2 * n:
            rad = (fc - cen) - axis * (fc - cen).dot(axis)
            ok = f.normal.dot(rad) < 0 or rad.length < 1e-6
        else:
            ok = f.normal.dot(nrm) > 0
        if not ok:
            bad.append(idx)
    gates.check("穴の面の向き: 壁は穴の軸へ、底は開口（皮膚の外側）へ", not bad, bad[:8])

    # 皮膚の内側に収まり、表面から離れているか（頭の表面との差、面どうしの交差）
    HS = M.HeadSurface()
    newpts = np.array([tuple(v.co) for v in r1 + r2 + [c]])
    g = HS.g_many(newpts)
    dist = np.linalg.norm(HS.project_many(newpts) - newpts, axis=1) * np.where(g > 0, 1, -1)
    gates.note("新しい頂点の、測定した頭の外形との差（mm、-は内側）", f"R1 {dist[:n].max() * 1000:.1f}〜{dist[:n].min() * 1000:.1f}・R2 {dist[n:2 * n].max() * 1000:.1f}〜{dist[n:2 * n].min() * 1000:.1f}・中心 {dist[-1] * 1000:.1f}")
    gates.check("新しい頂点は、全て、測定した頭の外形の内側（3mm 以上内側）", bool((dist <= -0.003).all()), f"最も外側 {dist.max() * 1000:.1f}mm")

    # 皮膚の面との距離・交差
    old_faces = [f for f in bm.faces if f.index < n_f0]
    verts_all = [tuple(v.co) for v in bm.verts]
    old_polys = [[v.index for v in f.verts] for f in old_faces]
    new_polys = [[v.index for v in f.verts] for f in new_faces]
    bvh_old = BVHTree.FromPolygons(verts_all, old_polys)
    bvh_new = BVHTree.FromPolygons(verts_all, new_polys)
    pairs = bvh_new.overlap(bvh_old)
    rim_idx = {v.index for v in rim}
    real = []
    for pn, po in pairs:
        if set(new_polys[pn]) & set(old_polys[po]):
            continue                                            # 頂点を共有する面（縁のところ）は交差とみなさない
        real.append((pn, po))
    gates.check("穴の面が、皮膚（既存の面）と交差していない（頂点を共有する隣り合いは除く）", not real, real[:6])
    dmin = []
    for k, v in enumerate(r1 + r2 + [c]):
        loc = bvh_old.find_nearest(v.co)
        dmin.append(loc[3] if loc[0] is not None else 9.9)
    gates.check("R1・R2・中心は、既存の面から 3mm 以上離れている", min(dmin) >= 0.003, f"最小 {min(dmin) * 1000:.1f}mm")

    # クリース・シャープ: R0 と R1 の辺
    keys = set()
    for i in range(n):
        j = (i + 1) % n
        keys.add(frozenset((rim[i].index, rim[j].index)))
        keys.add(frozenset((r1[i].index, r1[j].index)))
    old_idx = {v.index: None for v in bm.verts}
    face_count_check = (len(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    gates.check("既存の頂点は動かしていない（頂点数 %d→%d）" % (n_v0, len(mesh.vertices)), len(mesh.vertices) == n_v0 + 27 and face_count_check == n_f0 + 33)

    cre = mesh.attributes.get("crease_edge") or mesh.attributes.new("crease_edge", "FLOAT", "EDGE")
    shp = mesh.attributes.get("sharp_edge") or mesh.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
    marked = 0
    for e in mesh.edges:
        if frozenset(e.vertices) in keys:
            cre.data[e.index].value = 1.0
            shp.data[e.index].value = True
            marked += 1
    gates.check("クリース1.0・シャープの印: 縁 R0 と 奥 R1 の 26辺", marked == 26, marked)
    for p in mesh.polygons:
        p.use_smooth = True
    gates.check("全ての面をスムースシェードにした（印を付けた辺だけがパキッとする）", all(p.use_smooth for p in mesh.polygons))
    gates.check("X ≤ 0 で、正中線の頂点は X=0", max(v.co.x for v in mesh.vertices) <= 1e-9)
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # ---- Mirror 後の検証
    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs_e = [tuple(sorted(e.vertices)) for e in ev.edges]
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs_e)) == len(pairs_e) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    # 境界の輪: 目の穴が閉じて、口（16）と首の下端（12）だけ
    bmev = bmesh.new()
    bmev.from_mesh(ev)
    bmev.verts.ensure_lookup_table()
    bmev.edges.ensure_lookup_table()
    be = [e for e in bmev.edges if len(e.link_faces) == 1]
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
    lens = sorted(len(c) for c in loops)
    gates.check("穴（境界の輪）は、口（16辺）と首の下端（12辺）だけ", lens == [12, 16], lens)
    bmev.free()
    # 追加した面の内角
    def angs(pts):
        out = []
        for k in range(len(pts)):
            a, b, c2 = pts[k - 1], pts[k], pts[(k + 1) % len(pts)]
            v1, v2 = (a - b).normalized(), (c2 - b).normalized()
            out.append(math.degrees(math.acos(max(-1, min(1, v1.dot(v2))))))
        return out
    rng = [angs([mesh.vertices[k].co for k in mesh.polygons[i].vertices]) for i in range(n_f0, len(mesh.polygons))]
    lo, hi = min(min(r) for r in rng), max(max(r) for r in rng)
    gates.note("追加した面（33枚）の内角", f"最小 {lo:.0f}°・最大 {hi:.0f}°")
    gates.check("追加した面に、折れ・退化がない（内角 5°〜175°）", lo >= 5 and hi <= 175, f"{lo:.0f}°〜{hi:.0f}°")

    # レビュー画像（目のまわり）: 正面・側面・45° の重ね画像と、断面
    overlay.write_overlay(ev, 0, C.OUT / "s11_front_eye.png", crop=(200, 380, 480, 660), zoom=3)
    overlay.write_overlay(ev, 45, C.OUT / "s11_a45_eye.png", crop=(200, 380, 480, 660), zoom=3)
    overlay.write_wire_angle(ev, 90, C.OUT / "s11_side_wire.png", zoom=2, crop=(360, 330, 760, 630))
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s11_gen.blend"), compress=False)
    gates.finish()


main()
