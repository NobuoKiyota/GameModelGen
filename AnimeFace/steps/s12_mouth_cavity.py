"""S12: 口の中の空洞を作る（動画 33:14〜36:17）。

字幕との対応:
  33:14        「ここが少しへこんでいるので前へ」→ 好みの判断なので触らない
  33:18〜33:33 口の縁のループを選び、クリース（Shift+E）とシャープ（Ctrl+E）→ 口の縁 R0 の辺（半分で8辺）にクリース 1.0・シャープの印
  33:34〜34:17 E で押し出し、S で大きく（SZ・SX で調整）。この輪はクリース・シャープを外す。「元の口より少し大きい空洞」
               → R1: 縁の輪の上下の幅を拡大して、奥へ（クリース・シャープなし）。大きさは、皮膚・自分の面と交差せず 2.5mm 以上離れる最大のものを、6通り×2つの奥の向きから採る（最大は 上下1.6倍・奥12mm）
  34:19〜34:41 ループツールのリラックスで頂点の偏りを均す → 実装しない（R1 は縁の頂点の並びを保つので、偏りがない）
  34:41〜35:29 E Y で奥へ押し出し、奥の頂点を F で貼って埋める。ループを足して貼る。M でマージして整理
               → R2: 上下の幅を縮めて、さらに奥へ（最大は 0.7倍・奥24mm）。底は、上の唇側の頂点と下の唇側の頂点を対で結んだ四角形3枚＋コーナーの三角形1枚
                 （半分の輪は9頂点で奇数個の辺を含むため、四角形だけでは閉じられない。口の中で、ほとんど見えない）
  35:36〜36:08 透視の切り替え、顎の下を前へ・下げる → 好みの判断なので触らない

設計:
  - 奥の向きは、各頂点に接する面の法線の平均の逆（口角では頬の曲がりに沿って内側へ）。動画の E Y（世界の後ろ）は使わない。X=0 の頂点は、法線の X 成分を 0 にする
  - 上下の拡大・縮小は、上の唇の頂点と下の唇の頂点（対）の中点から。横方向（X）は拡大しない（頬の曲がりに当たるため）。口角は動かさない
  - 数値は、下絵にない（動画も「口の中はあまり見えないので、形にこだわらなくてよい」）。皮膚の内側に収まり、皮膚から離れていることだけを確かめる

入力: out/face_s11b_gen.blend   出力: out/face_s12_gen.blend, out/s12_report.json, out/s12_*.png
実行: blender --background --factory-startup --python steps/s12_mouth_cavity.py
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

STEP = "s12"
gates = C.Gates(STEP)



def rd(v):
    return tuple(round(float(c), 4) for c in v)


def mouth_chain(bm):
    """口の縁: 半分の輪（9頂点・8辺）。上の唇の正中線の頂点から、下の唇の正中線の頂点まで。"""
    cand = [e for e in bm.edges if len(e.link_faces) == 1
            and all(v.co.y < -0.19 and -0.16 < v.co.z < -0.12 and v.co.x > -0.06 for v in e.verts)
            and not all(abs(v.co.x) < 1e-6 for v in e.verts)]         # 正中線上の辺（Mirror の継ぎ目）は除く
    seam = [v for e in cand for v in e.verts if abs(v.co.x) < 1e-6]
    start = max(seam, key=lambda v: v.co.z)
    chain, prev, cur = [start], None, start
    while True:
        nxt = [e for e in cur.link_edges if e in cand and e is not prev]
        if not nxt:
            break
        prev = nxt[0]
        cur = prev.other_vert(cur)
        chain.append(cur)
        if abs(cur.co.x) < 1e-6:
            break
    return chain, cand


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s11b_gen.blend"))
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
    gates.check("入力: 頂点495・面460（四角形452・五角形7・三角形1）", n_v0 == 495 and n_f0 == 460 and sizes == {4: 452, 5: 7, 3: 1}, f"V={n_v0} {sizes}")

    P, cand = mouth_chain(bm)
    cand_edges_ordered = [next(e for e in P[i].link_edges if e.other_vert(P[i]) is P[i + 1] and e in cand) for i in range(8)]
    gates.check("口の縁: 半分の輪は9頂点・8辺、両端は X=0（上の唇・下の唇の正中線）",
                len(P) == 9 and len(cand) == 8 and abs(P[0].co.x) < 1e-6 and abs(P[-1].co.x) < 1e-6 and P[0].co.z > P[-1].co.z,
                f"{len(P)}頂点 {rd(P[0].co)} → {rd(P[-1].co)}")
    corner = min(P, key=lambda v: v.co.x)
    gates.check("口角（X が最小の頂点）は、輪の真ん中（4番目）", P.index(corner) == 4, P.index(corner))

    # 縁に接する面の法線（左右対称にするため X=0）
    nrm = Vector((0, 0, 0))
    for e in cand:
        f = e.link_faces[0]
        nrm += f.normal * f.calc_area()
    nrm.x = 0.0
    nrm.normalize()
    back = -nrm
    cen = Vector((0.0, sum(v.co.y for v in P) / 9, sum(v.co.z for v in P) / 9))
    h = Vector((1.0, 0.0, 0.0))
    vv = nrm.cross(h)                                          # 縦方向（X=0）
    gates.note("口の縁の中心・皮膚の法線（外向き）・奥の向き", f"C={rd(cen)} n={rd(nrm)} 奥={rd(back)} 縦={rd(vv)}")

    # 各頂点の奥の向き: その頂点に接する面の法線の平均の逆（口角では、頬の曲がりに沿って内側へ向く）。X=0 の頂点は X 成分を 0 に
    vn = []
    for v in P:
        nv = Vector((0, 0, 0))
        for f in v.link_faces:
            nv += f.normal * f.calc_area()
        if abs(v.co.x) < 1e-6:
            nv.x = 0.0
        vn.append(nv.normalized())

    # 上の唇の頂点 P_i と下の唇の頂点 P_(8-i) を対にして、その中点 M_i から、縦に拡大・縮小する（口角 P_4 は動かさない）。
    # 全体の中心 C からの拡大だと、口角（鋭角の楔）の先端で壁が折り返すため
    mid = [(P[i].co + P[8 - i].co) / 2 for i in range(9)]

    def ring(k, depth, mode='local'):
        out = []
        for i, (v, nv) in enumerate(zip(P, vn)):
            p = mid[i] + (v.co - mid[i]) * k - (nv if mode == 'local' else nrm) * depth
            if abs(v.co.x) < 1e-6:
                p.x = 0.0
            out.append(p)
        return out

    # 大きい順に試し、皮膚（既存の面）と交差せず 2.5mm 以上離れる最初の組み合わせを採る
    old_polys_pre = [[v.index for v in f.verts] for f in bm.faces]
    base_verts = [tuple(v.co) for v in bm.verts]
    cand_params = [(1.60, 0.012, 0.70, 0.024), (1.40, 0.012, 0.70, 0.024), (1.30, 0.010, 0.60, 0.020), (1.20, 0.010, 0.60, 0.018), (1.10, 0.008, 0.50, 0.014), (1.00, 0.008, 0.50, 0.014)]
    chosen = None
    tried = []
    fold_log = []
    skin_n = [e.link_faces[0].normal.copy() for e in cand_edges_ordered]

    def newell_n(pts):
        n = Vector((0, 0, 0))
        for k in range(len(pts)):
            a_, b_ = pts[k], pts[(k + 1) % len(pts)]
            n += Vector(((a_.y - b_.y) * (a_.z + b_.z), (a_.z - b_.z) * (a_.x + b_.x), (a_.x - b_.x) * (a_.y + b_.y)))
        return n.normalized()

    for mode in ("local", "global"):
        for prm in cand_params:
            k1, d1, k2, d2 = prm
            q1, q2 = ring(k1, d1, mode), ring(k2, d2, mode)
            allv = base_verts + [tuple(p) for p in q1 + q2]
            i1 = list(range(n_v0, n_v0 + 9))
            i2 = list(range(n_v0 + 9, n_v0 + 18))
            newp = [[P[i].index, P[i + 1].index, i1[i + 1], i1[i]] for i in range(8)] + [[i1[i], i1[i + 1], i2[i + 1], i2[i]] for i in range(8)]                 + [[i2[0], i2[1], i2[7], i2[8]], [i2[1], i2[2], i2[6], i2[7]], [i2[2], i2[3], i2[5], i2[6]], [i2[3], i2[4], i2[5]]]
            bo = BVHTree.FromPolygons(allv, old_polys_pre)
            bn = BVHTree.FromPolygons(allv, newp)
            hit = [(pn, po) for pn, po in bn.overlap(bo) if not (set(newp[pn]) & set(old_polys_pre[po]))]
            dm = min(bo.find_nearest(Vector(p))[3] for p in q1 + q2)
            # 折れ角: 新しい面どうし（共有する辺）と、縁での皮膚の面と壁の面（壁は縁→R1 の8枚）
            nn = [newell_n([Vector(allv[k]) for k in poly]) for poly in newp]
            edge_faces = {}
            for fi, poly in enumerate(newp):
                for k in range(len(poly)):
                    edge_faces.setdefault(frozenset((poly[k], poly[(k + 1) % len(poly)])), []).append(fi)
            fold = 0.0
            fold_where = None
            for key_e, fl in edge_faces.items():
                if len(fl) == 2:
                    ang_ = math.degrees(nn[fl[0]].angle(nn[fl[1]]))
                    if ang_ > fold:
                        fold, fold_where = ang_, ('新×新', fl)
            for i in range(8):
                ang_ = math.degrees(skin_n[i].angle(nn[i]))
                if ang_ > fold:
                    fold, fold_where = ang_, ('縁の皮膚×壁', i)
            fold_log.append((mode, prm[0], fold_where, round(fold)))
            selfhit = [(x, y) for x, y in bn.overlap(bn) if x < y and not (set(newp[x]) & set(newp[y]))]
            amin = 180.0
            for poly in newp:
                pts_ = [Vector(allv[k]) for k in poly]
                for k in range(len(pts_)):
                    v1, v2 = (pts_[k - 1] - pts_[k]).normalized(), (pts_[(k + 1) % len(pts_)] - pts_[k]).normalized()
                    amin = min(amin, math.degrees(math.acos(max(-1, min(1, v1.dot(v2))))))
            tried.append((mode, prm, len(hit), round(dm * 1000, 1), len(selfhit), round(amin)))
            if not hit and dm >= 0.0025 and not selfhit and amin >= 10:
                chosen = (mode,) + prm
                break
        if chosen:
            break
    gates.note("法線の角が最大の場所（口角の楔の先端は、壁どうしが鋭角なので大きい。折れではない）", fold_log[:3])
    gates.note("試した組み合わせ（奥の向き, (R1の上下の幅の倍率・奥・R2の倍率・奥), 皮膚との交差の対の数, 最小距離mm, 空洞の面どうしの交差の数, 最小の内角°）", tried)
    gates.check("皮膚と交差せず、2.5mm 以上離れ、空洞の面どうしも交差せず、内角 10° 以上の組み合わせが見つかった", chosen is not None)
    if chosen is None:
        gates.finish()
        return
    mode, k1, d1, k2, d2 = chosen
    gates.note("採用した大きさ", f"奥の向き {mode}。R1: 上下の幅を{k1}倍・奥{d1 * 1000:.0f}mm、R2: 上下の幅を{k2}倍・奥{d2 * 1000:.0f}mm")
    r1 = [bm.verts.new(p) for p in ring(k1, d1, mode)]
    r2 = [bm.verts.new(p) for p in ring(k2, d2, mode)]
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    fwd = any(lp.link_loop_next.vert is P[1] for lp in P[0].link_loops)
    new_faces = []

    def add(vs):
        vs = list(vs)
        if fwd:
            vs = vs[::-1]
        new_faces.append(bm.faces.new(vs))

    for i in range(8):
        add([P[i], P[i + 1], r1[i + 1], r1[i]])
    for i in range(8):
        add([r1[i], r1[i + 1], r2[i + 1], r2[i]])
    add([r2[0], r2[1], r2[7], r2[8]])
    add([r2[1], r2[2], r2[6], r2[7]])
    add([r2[2], r2[3], r2[5], r2[6]])
    add([r2[3], r2[4], r2[5]])
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.normal_update()
    gates.check("追加: 頂点 %d（R1 9＋R2 9）・面 %d（縁→R1 8＋R1→R2 8＋底 4）" % (len(bm.verts) - n_v0, len(new_faces)),
                len(bm.verts) - n_v0 == 18 and len(new_faces) == 20, f"V={len(bm.verts)} F={len(bm.faces)}")
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("巻き順が一貫・3枚以上が共有する辺なし", all(len(d) <= 2 and (len(d) < 2 or d[0] == (d[1][1], d[1][0])) for d in share.values()))
    # 向きと折れ: 巻き順が一貫（上で確認）していて、①底の法線が開口（皮膚の外側）へ ②四角形がねじれていない（2通りの三角形分割の法線が同じ向き）
    # ③空洞の面どうしが交差していない（折り返しがない。口角の楔の先端は鋭角なので、法線の角そのものは判断に使わない）
    bad = [idx for idx, f in enumerate(new_faces) if idx >= 16 and f.normal.dot(nrm) <= 0]
    gates.check("底の面の法線は、開口（皮膚の外側）を向く", not bad, bad[:8])
    twisted = []
    for idx, f in enumerate(new_faces):
        if len(f.verts) == 4:
            a0, a1, a2, a3 = [v.co for v in f.verts]
            n1 = (a1 - a0).cross(a2 - a0) + (a2 - a0).cross(a3 - a0)
            n2 = (a1 - a0).cross(a3 - a0) + (a2 - a1).cross(a3 - a1)
            if n1.normalized().dot(n2.normalized()) < 0.3:
                twisted.append(idx)
    gates.check("四角形がねじれていない（2通りの三角形分割の法線が近い）", not twisted, twisted)
    worst_fold = 0.0
    for e in bm.edges:
        if len(e.link_faces) == 2 and any(f in new_faces for f in e.link_faces):
            worst_fold = max(worst_fold, math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)))
    gates.note("隣り合う面の法線の角（縁を含む）の最大（口角の楔の先端は、壁どうしが鋭角なので大きい）", f"{worst_fold:.0f}°")
    bad = []
    # 皮膚との交差・距離
    old = [f for f in bm.faces if f.index < n_f0]
    verts_all = [tuple(v.co) for v in bm.verts]
    old_polys = [[v.index for v in f.verts] for f in old]
    new_polys = [[v.index for v in f.verts] for f in new_faces]
    bvh_old = BVHTree.FromPolygons(verts_all, old_polys)
    bvh_new = BVHTree.FromPolygons(verts_all, new_polys)
    real = [(pn, po) for pn, po in bvh_new.overlap(bvh_old) if not (set(new_polys[pn]) & set(old_polys[po]))]
    gates.check("空洞の面が、皮膚（既存の面）と交差していない（頂点を共有する隣り合いは除く）", not real, real[:6])
    selfhit = [(x, y) for x, y in bvh_new.overlap(bvh_new) if x < y and not (set(new_polys[x]) & set(new_polys[y]))]
    gates.check("空洞の面どうしが交差していない（折り返しがない）", not selfhit, selfhit[:6])
    dmin = [bvh_old.find_nearest(v.co)[3] for v in r1 + r2]
    gates.check("R1・R2 は、既存の面から 2mm 以上離れている", min(dmin) >= 0.002, f"最小 {min(dmin) * 1000:.1f}mm")

    # クリース・シャープ: 口の縁 R0 の8辺だけ（R1 には付けない）
    keys = {frozenset((P[i].index, P[i + 1].index)) for i in range(8)}
    face_count = len(bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    gates.check("頂点・面の数（%d→%d, %d→%d）" % (n_v0, len(mesh.vertices), n_f0, len(mesh.polygons)), len(mesh.vertices) == n_v0 + 18 and face_count == n_f0 + 20)
    cre = mesh.attributes.get("crease_edge") or mesh.attributes.new("crease_edge", "FLOAT", "EDGE")
    shp = mesh.attributes.get("sharp_edge") or mesh.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
    marked = 0
    for e in mesh.edges:
        if frozenset(e.vertices) in keys:
            cre.data[e.index].value = 1.0
            shp.data[e.index].value = True
            marked += 1
    n_cre = sum(1 for d in cre.data if d.value > 0)
    n_shp = sum(1 for d in shp.data if d.value)
    gates.check("口の縁 R0 の8辺にクリース1.0・シャープの印。眼の26辺と合わせて34辺、R1 には付けない", marked == 8 and n_cre == 34 and n_shp == 34, f"追加{marked} / クリース{n_cre} / シャープ{n_shp}")
    for p in mesh.polygons:
        p.use_smooth = True
    gates.check("X ≤ 0 で、正中線の頂点は X=0", max(v.co.x for v in mesh.vertices) <= 1e-9)
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # ---- Mirror 後の検証
    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bmev = bmesh.new()
    bmev.from_mesh(ev)
    bmev.verts.ensure_lookup_table()
    bmev.edges.ensure_lookup_table()
    bmev.faces.ensure_lookup_table()
    Vn, En, Fn = len(bmev.verts), len(bmev.edges), len(bmev.faces)
    share = {}
    for f in bmev.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                max(len(v) for v in share.values()) <= 2 and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in bmev.verts}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
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
    gates.check("穴（境界の輪）は、首の下端（12辺）だけ", lens == [12], lens)
    top = max(bmev.faces, key=lambda f: f.calc_center_median().z)
    gates.check("頭のてっぺんの面の法線が外向き（巻き順が一貫なので、全面が外向き）", top.normal.z > 0)
    comp = {0}
    stack = [bmev.faces[0]]
    while stack:
        f = stack.pop()
        for e in f.edges:
            for g in e.link_faces:
                if g.index not in comp:
                    comp.add(g.index)
                    stack.append(g)
    gates.check("面は1つの塊につながっている", len(comp) == Fn, f"{len(comp)}/{Fn}")
    bmev.free()

    def angs(pts):
        out = []
        for k in range(len(pts)):
            a, b, c2 = pts[k - 1], pts[k], pts[(k + 1) % len(pts)]
            v1, v2 = (a - b).normalized(), (c2 - b).normalized()
            out.append(math.degrees(math.acos(max(-1, min(1, v1.dot(v2))))))
        return out
    rng = [angs([mesh.vertices[k].co for k in mesh.polygons[i].vertices]) for i in range(n_f0, len(mesh.polygons))]
    lo, hi = min(min(r) for r in rng), max(max(r) for r in rng)
    gates.note("追加した面（20枚）の内角", f"最小 {lo:.0f}°・最大 {hi:.0f}°")
    gates.check("追加した面に、折れ・退化がない（内角 5°〜179°）", lo >= 5 and hi <= 179, f"{lo:.0f}°〜{hi:.0f}°")

    overlay.write_overlay(ev, 0, C.OUT / "s12_front_mouth.png", crop=(312, 560, 712, 760), zoom=2)
    overlay.write_overlay(ev, 90, C.OUT / "s12_side_mouth.png", crop=(560, 560, 760, 860), zoom=3)
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s12_gen.blend"), compress=False)
    gates.finish()


main()
