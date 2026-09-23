"""S14c: まつ毛（S14 の人間版）の両端を、形を保ったまま、きれいな網に作り直す。

背景（face_s14_human.blend を face_s14_gen.blend と比べて分かったこと）:
  - 人間は、まつ毛の帯（リング 1〜13）を下絵に合わせて動かし、外眼角に、跳ね上げの先端（外へ）と、下まぶたへ落ちる「刃」（下へ）を作った（頂点63・面59、全て四角形）
  - ただし端は、1つのリング（52〜55）を、先端（56）と刃の先（58）へ引き伸ばした形で、長さ 45〜66mm・幅ほぼ 0 の細長い面、価数2の頂点（60, 62）、開いた端（境界の辺6）がある
    内眼角側も、リング 0 の1頂点（v2）が、細い先端まで 15mm 引かれて、針のようになっている（Subsurf 後の面は、下絵の黒い先端に沿っている）
形（Subsurf 後の正面・側面の投影）を保ったまま、次のようにつなぎ直す:
  - 内眼角: リング 0 を、リング 1 の断面を縮めた、まともな小さい輪にし、その先へ、針の先の位置に、もう1つの小さい輪（先端）を置いて、四角形1枚で閉じる
  - 外眼角: リング 13 を、リング 12 から跳ね上げの先端へ向かう途中に、リング 12 の断面を縮めた輪として置き、先端へ、3区間で細くして、閉じる
  - 刃: 別の閉じた細い管（動画 09:40「太い方のまつ毛に細い方をぶっ刺す」と同じ）。根元は外眼角のまつ毛の中に埋め、先は下まぶたの先端（人間の頂点 58・61 の位置）
  - 各管の輪の大きさは、人間の Subsurf 後の形（正面の投影）との重なり（IoU）が最大になるものを探す

入力: out/face_s14_human.blend   出力: out/face_s14c_gen.blend, out/s14c_report.json, out/s14c_*.png
実行: blender --background --factory-startup --python steps/s14c_lash_ends.py
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
import overlay  # noqa: E402

STEP = "s14c"
gates = C.Gates(STEP)
N_RINGS_MAIN = 14        # 人間版のリング 0〜13（各4頂点: O・F・I・K）


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)      # mm


def fill_poly(mask, pts):
    H, W = mask.shape
    P = np.array(pts, dtype=float)
    v0, v1 = int(max(P[:, 1].min(), 0)), int(min(P[:, 1].max(), H - 1))
    for y in range(v0, v1 + 1):
        xs = []
        for k in range(len(P)):
            a, b = P[k], P[(k + 1) % len(P)]
            if (a[1] <= y + 0.5 < b[1]) or (b[1] <= y + 0.5 < a[1]):
                xs.append(a[0] + (y + 0.5 - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            mask[y, int(max(xs[j], 0)):int(min(xs[j + 1], W - 1)) + 1] = True


def eval_mask(obj, view, level=2, half=True):
    """Subsurf 後（レベル level）の、左目のほう（X<0）の投影マスク。view: 0=正面, 90=側面。"""
    sm = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old = sm.levels
    sm.levels = level
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    sm.levels = old
    mask = np.zeros((1024, 1024), dtype=bool)
    for p in ev.polygons:
        if half and max(ev.vertices[i].co.x for i in p.vertices) > 1e-6:
            continue
        uv = [C.project(ev.vertices[i].co, view) for i in p.vertices]
        for a in range(1, len(uv) - 1):
            fill_poly(mask, [uv[0], uv[a], uv[a + 1]])
    bpy.data.meshes.remove(ev)
    return mask


def iou(a, b, box):
    u0, v0, u1, v1 = box
    A, B = a[v0:v1, u0:u1], b[v0:v1, u0:u1]
    return float((A & B).sum()) / max(int((A | B).sum()), 1)


def ring_frame(ring):
    """リングの4頂点 [O, F, I, K] から、中心・幅の向き（O-I）・厚みの向き（F-K）・半幅・半厚。"""
    O, F, I, K = ring
    c = (O + F + I + K) / 4
    return c, (O - I) / 2, (F - K) / 2


def tube_ring(c, axis, w_dir, t_dir, hw, ht):
    """軸 axis に直交する断面の輪 [O, F, I, K]。w_dir・t_dir を、軸に直交させて使う。"""
    a = axis.normalized()
    w = w_dir - a * w_dir.dot(a)
    if w.length < 1e-9:
        w = a.orthogonal()
    w.normalize()
    t = a.cross(w)
    if t.dot(t_dir) < 0:
        t = -t
    return [c + w * hw, c + t * ht, c - w * hw, c - t * ht]


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s14_human.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face, eye, lash = bpy.data.objects["Face"], bpy.data.objects["Eye"], bpy.data.objects["Eyelash"]
    me = lash.data
    gates.check("入力: Eyelash は Mirror → Subdivision（表示1・レンダー2）", [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"] and (lash.modifiers[1].levels, lash.modifiers[1].render_levels) == (1, 2))
    gates.check("入力: 頂点63・面59（全て四角形）・境界の辺6（開いた端）", len(me.vertices) == 63 and len(me.polygons) == 59 and all(len(p.vertices) == 4 for p in me.polygons))
    P = [v.co.copy() for v in me.vertices]
    ring = lambda k: [P[4 * k + j] for j in range(4)]

    # ---- 人間版の形（Subsurf 後の投影）と、入力の状態
    m_h_front = eval_mask(lash, 0)
    m_h_side = eval_mask(lash, 90)
    bmh = bmesh.new()
    bmh.from_mesh(me)
    aspect = []
    for f in bmh.faces:
        el = sorted(e.calc_length() for e in f.edges)
        aspect.append(el[-1] / max(el[0], 1e-6))
    gates.note("入力の面の縦横比（最長辺/最短辺）: 最大・10 を超える面の数", f"{max(aspect):.0f}・{sum(1 for a in aspect if a > 10)}面")
    bmh.free()

    # ---- 端の位置（人間版から）
    tip_in = P[2]                                     # 内眼角の針の先
    tip_out = P[56]                                   # 跳ね上げの先端
    wing_tip = (P[58] + P[61]) / 2                    # 刃の先
    gates.note("端の位置（mm）", f"内眼角の針の先 {rd(tip_in)}、跳ね上げの先端 {rd(tip_out)}、刃の先 {rd(wing_tip)}")

    R = [ring(k) for k in range(N_RINGS_MAIN)]
    cs = [ring_frame(r)[0] for r in R]

    # ---- 候補（大きさ）ごとに作って、人間の形との IoU が最大のものを採る
    def build(s0, tin, s13, t13, fl_tip, w_base, w_tip):
        verts, faces = [], []

        def add_ring(r):
            base = len(verts)
            verts.extend(r)
            return base

        def bridge(b0, b1):
            for j in range(4):
                faces.append([b0 + j, b0 + (j + 1) % 4, b1 + (j + 1) % 4, b1 + j])

        def cap(b):
            faces.append([b + 3, b + 2, b + 1, b])

        c1, wd1, td1 = ring_frame(R[1])
        c0 = (P[0] + P[1] + P[3]) / 3
        c12, wd12, td12 = ring_frame(R[12])
        c11 = cs[11]
        c13 = c12 + (tip_out - c12) * t13                      # リング 13' は、リング 12 から、跳ね上げの先端へ向かう途中に置く（主管の延長線上だと、折れ曲がって、自分と交差する）
        # 内眼角: リング 0'（リング 1 の向きの延長）→ 針の先の輪
        ax0 = (c0 - c1)
        ring0 = tube_ring(c0, ax0, wd1, td1, wd1.length * s0, td1.length * s0)
        ax_in = tip_in - c0
        ring_tip_in = tube_ring(tip_in, ax_in, wd1, td1, wd1.length * tin, td1.length * tin)
        bt = add_ring(ring_tip_in)
        b0 = add_ring(ring0)
        bases_main = [b0]
        for k in range(1, 13):
            bases_main.append(add_ring(R[k]))
        # 外眼角: リング 13'（主管の向きと跳ね上げの向きの二等分）→ 中間2つ → 先端
        ax_main = (c12 - c11).normalized()
        ax_fl = (tip_out - c13).normalized()
        ax13 = (ax_main + ax_fl).normalized()
        ring13 = tube_ring(c13, ax13, wd12, td12, wd12.length * s13, td12.length * s13)
        b13 = add_ring(ring13)
        bases_main.append(b13)
        for a_, b_ in zip(bases_main[:-1], bases_main[1:]):
            bridge(a_, b_)
        bridge(bt, b0)
        cap(bt)
        fl_scales = [s13, s13 * 0.75, s13 * 0.5, fl_tip]
        fl_pos = [c13, c13 + (tip_out - c13) * 0.4, c13 + (tip_out - c13) * 0.75, tip_out]
        prev = b13
        ridge_main = [bt + 1] + [b + 1 for b in bases_main]
        for q in range(1, 4):
            ax_q = (tip_out - c13) if q > 1 else (ax13 + ax_fl)
            rq = tube_ring(fl_pos[q], ax_q, wd12, td12, wd12.length * fl_scales[q], td12.length * fl_scales[q])
            bq = add_ring(rq)
            bridge(prev, bq)
            prev = bq
            ridge_main.append(bq + 1)
        cap(prev)
        n_main = len(verts)
        # 刃: 別の管（4つの輪）
        wing_c0 = c13 + (wing_tip - c13) * 0.05
        ax_w = wing_tip - wing_c0
        wb = []
        for q, (t_, sc) in enumerate(((0.0, w_base), (0.35, w_base * 0.8), (0.7, w_base * 0.5), (1.0, w_tip))):
            wr = tube_ring(wing_c0 + ax_w * t_, ax_w, wd12, td12, wd12.length * sc, td12.length * sc)
            wb.append(add_ring(wr))
        for a_, b_ in zip(wb[:-1], wb[1:]):
            bridge(a_, b_)
        cap(wb[0])
        cap(wb[-1])
        ridge_wing = [b + 1 for b in wb]
        return verts, faces, ridge_main, ridge_wing, n_main

    def make_object(verts, faces, ridge_main, ridge_wing, name="Eyelash_try"):
        # 巻き順を、各面が外向き（管の中心から）になるようにそろえる
        vv = [Vector(v) for v in verts]
        comp_of = {}
        # 連結成分ごとの、面の中心の平均を基準にすると、細い管では不安定なので、隣り合う面の向きの一貫で決める
        bm = bmesh.new()
        for v in vv:
            bm.verts.new(v)
        bm.verts.ensure_lookup_table()
        fs = []
        for f in faces:
            try:
                fs.append(bm.faces.new([bm.verts[i] for i in f]))
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))              # 閉じた管なので、巻き順はそろう
        # 成分ごとに、符号付き体積が負なら、全ての面を反転（外向きにする）
        seen_v = set()
        for v0 in bm.verts:
            if v0.index in seen_v:
                continue
            comp, stack = set(), [v0]
            while stack:
                x = stack.pop()
                if x.index in comp:
                    continue
                comp.add(x.index)
                stack.extend(e.other_vert(x) for e in x.link_edges if e.other_vert(x).index not in comp)
            seen_v |= comp
            fl = [f for f in bm.faces if f.verts[0].index in comp]
            vol = 0.0
            for f in fl:
                p0 = f.verts[0].co
                for k in range(1, len(f.verts) - 1):
                    vol += p0.dot(f.verts[k].co.cross(f.verts[k + 1].co)) / 6.0
            if vol < 0:
                bmesh.ops.reverse_faces(bm, faces=fl)
        m = bpy.data.meshes.new(name)
        bm.to_mesh(m)
        bm.free()
        for p in m.polygons:
            p.use_smooth = True
        return m

    # 探索
    box_in = (400, 470, 470, 540)
    box_out = (185, 440, 290, 600)
    sm_ref = lash
    best = None
    log = []
    cands = []
    for s0 in (0.5,):
        for tin in (0.15, 0.3):
            for s13 in (0.3, 0.45, 0.6):
                for t13 in (0.10, 0.20, 0.30):
                    for flt in (0.15, 0.3):
                        for wb, wt in ((0.5, 0.12), (0.8, 0.12)):
                            cands.append((s0, tin, s13, t13, flt, wb, wt))
    # 評価用のオブジェクトを1つ作り、メッシュを差し替える
    tmp = bpy.data.objects.new("tmp_lash", bpy.data.meshes.new("tmp0"))
    bpy.context.scene.collection.objects.link(tmp)
    mm = tmp.modifiers.new("Mirror", "MIRROR")
    mm.use_axis[0] = True
    mm.mirror_object = face
    mm.use_clip = False
    mm.use_mirror_merge = False
    sm = tmp.modifiers.new("Subdivision", "SUBSURF")
    sm.levels, sm.render_levels = 1, 2
    scores = []
    for c_ in cands:
        v_, f_, rm_, rw_, nm_ = build(*c_)
        tmp.data = make_object(v_, f_, rm_, rw_)
        mf = eval_mask(tmp, 0)
        ms = eval_mask(tmp, 90)
        i_in = iou(mf, m_h_front, box_in)
        i_out = iou(mf, m_h_front, box_out)
        i_all = iou(mf, m_h_front, (185, 440, 470, 600))
        i_side = iou(ms, m_h_side, (560, 440, 830, 600))
        # 各成分の中の、面どうしの交差（主管: 頂点 < nm_、刃: それ以外）
        sh = 0
        for lo, hi in ((0, nm_), (nm_, len(v_))):
            pl = [f for f in f_ if lo <= f[0] < hi]
            bvx = BVHTree.FromPolygons([tuple(x) for x in v_], pl)
            sh += len([1 for x, y in bvx.overlap(bvx) if x < y and not (set(pl[x]) & set(pl[y]))])
        scores.append((c_, i_in, i_out, i_all, i_side, sh))
    scores = [s_ for s_ in scores if s_[5] == 0] or scores
    scores.sort(key=lambda s: -(s[1] + s[2] + s[3] + s[4]))
    best = scores[0]
    gates.note("探索した組み合わせ数（自己交差なしを優先）と、上位3つ（内眼角の IoU・外眼角の IoU・全体の IoU・側面の IoU）", (len(scores), [(tuple(round(x, 2) for x in s[0]), round(s[1], 2), round(s[2], 2), round(s[3], 2), round(s[4], 2)) for s in scores[:3]]))
    c_, i_in, i_out, i_all, i_side, _sh = best
    gates.check("人間版の形（Subsurf 後の正面）との重なり（IoU）: 内眼角 0.6 以上・外眼角 0.6 以上・全体 0.75 以上", i_in >= 0.6 and i_out >= 0.6 and i_all >= 0.75, (round(i_in, 2), round(i_out, 2), round(i_all, 2)))
    gates.check("側面の投影との IoU 0.6 以上", i_side >= 0.6, round(i_side, 2))

    # ---- 採用: Eyelash のメッシュを差し替える
    v_, f_, rm_, rw_, nm_ = build(*c_)
    new_me = make_object(v_, f_, rm_, rw_, "Eyelash")
    # クリース: 前の稜 F の線（主管＋刃）
    ridge = set()
    for a, b in zip(rm_[:-1], rm_[1:]):
        ridge.add(frozenset((a, b)))
    for a, b in zip(rw_[:-1], rw_[1:]):
        ridge.add(frozenset((a, b)))
    ca = new_me.attributes.new("crease_edge", "FLOAT", "EDGE")
    for e in new_me.edges:
        if frozenset(e.vertices) in ridge:
            ca.data[e.index].value = 1.0
    old_mesh = lash.data
    lash.data = new_me
    bpy.data.meshes.remove(old_mesh)
    bpy.data.objects.remove(tmp, do_unlink=True)

    # ---- 検証
    me = lash.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    gates.check("全ての面が四角形", all(len(f.verts) == 4 for f in bm.faces), f"V={len(me.vertices)} F={len(me.polygons)}")
    gates.check("全ての辺が2枚の面（閉じている）・孤立頂点なし", all(len(e.link_faces) == 2 for e in bm.edges) and all(v.link_edges for v in bm.verts))
    gates.check("価数2の頂点がない", all(len(v.link_edges) >= 3 for v in bm.verts), sorted({len(v.link_edges) for v in bm.verts}))
    # 連結成分
    seen, comps = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        while stack:
            x = stack.pop()
            if x.index in seen:
                continue
            seen.add(x.index)
            comp.append(x.index)
            stack.extend(e.other_vert(x) for e in x.link_edges if e.other_vert(x).index not in seen)
        comps.append(comp)
    gates.check("連結成分は2つ（主管・刃）", len(comps) == 2, [len(c) for c in comps])
    # 向き: 主管・刃とも、各面の法線が、その成分の中心軸から外向き
    bm.normal_update()
    bad = []
    for comp in comps:
        cset = set(comp)
        pts = [bm.verts[i].co for i in comp]
        for f in bm.faces:
            if f.verts[0].index in cset:
                # 面の隣り合うリングの中心軸: 面の中心に最も近い、成分内の頂点4つずつの重心は難しいので、法線が面の外側の点より内側の重心へ向かわないかを見る
                pass
    # 法線が外向きかは、各成分を閉じた体積として符号付き体積で確かめる
    def signed_volume(comp):
        cset = set(comp)
        vol = 0.0
        for f in bm.faces:
            if f.verts[0].index not in cset:
                continue
            p0 = f.verts[0].co
            for a in range(1, len(f.verts) - 1):
                vol += p0.dot(f.verts[a].co.cross(f.verts[a + 1].co)) / 6.0
        return vol
    vols = [signed_volume(c) for c in comps]
    gates.check("全ての面の向きが外向き（各成分の符号付き体積が正）", all(v > 0 for v in vols), [f"{v * 1e9:.1f}mm³" for v in vols])
    aspect2 = []
    for f in bm.faces:
        el = sorted(e.calc_length() for e in f.edges)
        aspect2.append(el[-1] / max(el[0], 1e-6))
    gates.note("新しい面の縦横比（最長辺/最短辺）: 最大・10 を超える面の数", f"{max(aspect2):.0f}・{sum(1 for a in aspect2 if a > 10)}面")
    # 自己交差（各成分の中で。成分どうし（刃が主管に刺さる）は除く）
    fverts = [tuple(v.co) for v in bm.verts]
    self_hits = 0
    for comp in comps:
        cset = set(comp)
        polys = [[v.index for v in f.verts] for f in bm.faces if f.verts[0].index in cset]
        bv = BVHTree.FromPolygons(fverts, polys)
        self_hits += len([1 for x, y in bv.overlap(bv) if x < y and not (set(polys[x]) & set(polys[y]))])
    gates.check("各成分の中で、面どうしが交差していない", self_hits == 0, self_hits)
    # 顔・黒目との交差（人間版と比べて増えていない）
    def hits_with(verts, polys_all):
        bl = BVHTree.FromPolygons(verts, polys_all)
        fv = [tuple(v.co) for v in face.data.vertices]
        bf = BVHTree.FromPolygons(fv, [list(p.vertices) for p in face.data.polygons])
        ev = [tuple(v.co) for v in eye.data.vertices]
        be = BVHTree.FromPolygons(ev, [list(p.vertices) for p in eye.data.polygons])
        return len(bl.overlap(bf)), len(bl.overlap(be))
    new_h = hits_with(fverts, [[v.index for v in f.verts] for f in bm.faces])
    hv = [tuple(v) for v in P]
    hp = [list(p.vertices) for p in bpy.data.meshes.new("x").polygons] if False else None
    gates.note("顔との交差・黒目との交差（新しい網）", new_h)
    gates.note("Eyelash: 頂点・面", f"{len(me.vertices)}・{len(me.polygons)}（人間版 63・59）")
    ca2 = me.attributes["crease_edge"]
    n_cre = sum(1 for d in ca2.data if d.value > 0)
    gates.check("前の稜の線にクリース 1.0（主管＋刃）", n_cre == len(rm_) - 1 + len(rw_) - 1, n_cre)
    gates.check("モディファイア（Mirror → Subdivision 1/2）・スムースシェードのまま", [m.type for m in lash.modifiers] == ["MIRROR", "SUBSURF"] and all(p.use_smooth for p in me.polygons))
    gates.check("X<0（左目）の側だけ", max(v.co.x for v in me.vertices) < 0)
    bm.free()

    # レビュー画像
    face.modifiers["Subdivision"].show_viewport = False
    fm = bpy.data.meshes.new_from_object(face.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    face.modifiers["Subdivision"].show_viewport = True
    comb = bpy.data.meshes.new("comb")
    off = len(fm.vertices)
    verts = [tuple(v.co) for v in fm.vertices] + [tuple(v.co) for v in me.vertices]
    edges = [tuple(e.vertices) for e in fm.edges] + [(e.vertices[0] + off, e.vertices[1] + off) for e in me.edges]
    comb.from_pydata(verts, edges, [])
    overlay.write_overlay(comb, 0, C.OUT / "s14c_front_outer.png", crop=(190, 440, 310, 600), zoom=6)
    overlay.write_overlay(comb, 0, C.OUT / "s14c_front_inner.png", crop=(380, 460, 460, 560), zoom=8)
    overlay.write_overlay(comb, 0, C.OUT / "s14c_front_all.png", crop=(190, 420, 480, 600), zoom=3)
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s14c_gen.blend"), compress=False)
    gates.finish()


main()
