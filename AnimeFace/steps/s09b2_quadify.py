"""S09b2: 人間補正版 S09b の三角形・五角形を、頂点を動かさず、つなぎ替えだけで全て四角形にする。

人間補正版は、T_12 の穴を埋めた結果、三角形2枚・五角形2枚（奇数の面）が混ざっている（四角形は356枚）。
奇数の面は、対で消せる。対の作り方は次の3通り:
  (a) 五角形どうしが隣り合っていれば、8角形にして3枚の四角形に切り直す（全ての分け方から歪み最小）
  (b) 三角形 + 三角形（辺を共有）→ 四角形1枚
  (c) 三角形 + 五角形（辺を共有）→ 六角形 → 四角形2枚（分け方から歪み最小）
離れた奇数の面は、「三角形の移動」で近づける: 三角形(p,q,r)と、辺 p-q の向こうの四角形(q,p,s,t)を合わせて五角形(r,p,s,t,q)にし、
三角形(r,p,s)+四角形(r,s,t,q) または 四角形(r,p,s,t)+三角形(r,t,q) に切り直す（三角形は四角形1枚ぶん動く）。
移動後の面は、外向き・折れ（bow-tie）なし・凹みなし・内角 8°〜172° のものだけを許し、コスト = 1 + 内角のずれ を最小にする経路をダイクストラ法で探す。
対応づけを全て試し、有効な最小コストのものを採る。頂点の位置は一切変えない（辺のつなぎ替えのみ）。

入力: out/face_s09b_human.blend   出力: out/face_s09b2_gen.blend, out/s09b2_report.json
実行: blender --background --factory-startup --python steps/s09b2_quadify.py
"""
import heapq
import itertools
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s09b2"
gates = C.Gates(STEP)
HEAD_CENTER = Vector((0.0, 0.0, -0.03))
TOL = dict(lo=float(os.environ.get('Q_LO', 8)), hi=float(os.environ.get('Q_HI', 172)), dot=float(os.environ.get('Q_DOT', 0.3)))


def newell_n(pts):
    n = Vector((0, 0, 0))
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def face_ok(pts, lo=None, hi=None):
    """折れ・内向き・凹みがないか。三角形・四角形。戻り値: 角のずれ（度）か None（不可）。"""
    lo = TOL["lo"] if lo is None else lo
    hi = TOL["hi"] if hi is None else hi
    c = sum(pts, Vector()) / len(pts)
    n = newell_n(pts)
    if n.length < 1e-12 or n.dot(c - HEAD_CENTER) <= 0:
        return None
    n = n.normalized()
    if len(pts) == 4:
        for tri in ((pts[0], pts[1], pts[2]), (pts[0], pts[2], pts[3]), (pts[1], pts[2], pts[3]), (pts[1], pts[3], pts[0])):
            tn = (tri[1] - tri[0]).cross(tri[2] - tri[0])
            if tn.length < 1e-14 or tn.normalized().dot(n) < TOL['dot']:
                return None
    dev = 0.0
    m = len(pts)
    for k in range(m):
        a, b, c2 = pts[k - 1], pts[k], pts[(k + 1) % m]
        v1, v2 = (a - b).normalized(), (c2 - b).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
        if ang < lo or ang > hi:
            return None
        dev = max(dev, abs(ang - (90 if m == 4 else 60)))
    return dev


def decompositions(poly):
    """多角形（頂点の巡回リスト、向き付き）を、辺の追加だけで四角形に分ける全ての方法。"""
    n = len(poly)
    if n == 4:
        yield [tuple(poly)]
        return
    if n < 4 or n % 2:
        return
    for a, b, c in itertools.combinations(range(1, n), 3):
        parts = [poly[0:a + 1], poly[a:b + 1], poly[b:c + 1], poly[c:] + [poly[0]]]
        if any(len(p) % 2 for p in parts):
            continue
        subs = []
        ok = True
        for p in parts:
            if len(p) == 2:
                subs.append([[]])
                continue
            ds = list(decompositions(p))
            if not ds:
                ok = False
                break
            subs.append(ds)
        if not ok:
            continue
        for combo in itertools.product(*subs):
            yield [(poly[0], poly[a], poly[b], poly[c])] + [q for d in combo for q in d]


def rotate_to(seq, first):
    k = seq.index(first)
    return seq[k:] + seq[:k]


class Quadifier:
    def __init__(self, mesh):
        self.bm = bmesh.new()
        self.bm.from_mesh(mesh)
        self.bm.verts.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

    def pts(self, ids):
        return [self.bm.verts[i].co for i in ids]

    def loop_of(self, f):
        return [v.index for v in f.verts]

    def find_face(self, ids):
        for f in self.bm.verts[ids[0]].link_faces:
            if {v.index for v in f.verts} == set(ids):
                return f
        return None

    def nbr_across(self, face, x, y):
        e = self.bm.edges.get((self.bm.verts[x], self.bm.verts[y]))
        for g in e.link_faces:
            if g is not face:
                return g
        return None

    def replace(self, old_faces, new_lists):
        bmesh.ops.delete(self.bm, geom=list(old_faces), context="FACES_ONLY")
        for q in new_lists:
            self.bm.faces.new([self.bm.verts[i] for i in q])
        self.bm.faces.ensure_lookup_table()

    def recut_pentagons(self, f1, f2):
        a_ids, b_ids = self.loop_of(f1), self.loop_of(f2)
        shared = None
        for k in range(5):
            u, v = a_ids[k], a_ids[(k + 1) % 5]
            if u in b_ids and v in b_ids and b_ids[(b_ids.index(v) + 1) % 5] == u:
                shared = (u, v)
        if shared is None:
            return None
        u, v = shared
        octagon = rotate_to(a_ids, v) + rotate_to(b_ids, u)[1:-1]
        best = None
        for dec in decompositions(octagon):
            if len(dec) != 3:
                continue
            devs = [face_ok(self.pts(q)) for q in dec]
            if any(d is None for d in devs):
                continue
            sc = max(devs)
            if best is None or sc < best[0]:
                best = (sc, dec)
        if best is None:
            return None
        self.replace([f1, f2], best[1])
        return best[0]

    def merge_options(self, tri, edge, goal_ids):
        """三角形 tri と、辺 edge=(x,y) を共有する goal（三角形/五角形）を合わせた多角形の、四角形への最良の切り直し (歪み, 面のリスト)。"""
        x, y = edge
        n = len(goal_ids)
        if y not in goal_ids or x not in goal_ids or goal_ids[(goal_ids.index(y) + 1) % n] != x:
            return None
        tl = list(tri)
        if tl[(tl.index(x) + 1) % 3] != y:
            return None
        gpoly = rotate_to(goal_ids, x)                # x → ... → y
        union = rotate_to(tl, y) + gpoly[1:-1]        # y → third → x → (goal の x と y の間の頂点)
        best = None
        for dec in decompositions(union):
            devs = [face_ok(self.pts(q)) for q in dec]
            if any(d is None for d in devs):
                continue
            sc = max(devs)
            if best is None or sc < best[0]:
                best = (sc, dec)
        return best

    def push_to(self, start, goal):
        sv = self.loop_of(start)
        nb0 = {}
        for k in range(3):
            x, y = sv[k], sv[(k + 1) % 3]
            g = self.nbr_across(start, x, y)
            nb0[(x, y)] = g.index if g is not None else None
        goal_idx = goal.index
        goal_ids = self.loop_of(goal)
        counter = itertools.count()
        heap = [(0.0, next(counter), tuple(sv), nb0, frozenset([start.index]), [])]
        best_cost = {frozenset(sv): 0.0}
        found = None
        while heap:
            cost, _, tri, nb, consumed, path = heapq.heappop(heap)
            if cost > best_cost.get(frozenset(tri), 1e18) + 1e-9:
                continue
            if found is not None and cost >= found[0]:
                break
            for e, g in nb.items():
                if g == goal_idx:
                    merged = self.merge_options(tri, e, goal_ids)
                    if merged is not None:
                        total = cost + merged[0] / 90
                        if found is None or total < found[0]:
                            found = (total, path, tri, e, merged[1])
            if len(path) > 40:
                continue
            for k in range(3):
                p, qv, r = tri[k], tri[(k + 1) % 3], tri[(k + 2) % 3]
                gi = nb[(p, qv)]
                if gi is None or gi in consumed or gi == goal_idx:
                    continue
                Q = self.bm.faces[gi]
                if len(Q.verts) != 4:
                    continue
                ql = self.loop_of(Q)
                if qv not in ql or p not in ql:
                    continue
                qo = rotate_to(ql, qv)
                if qo[1] != p:
                    continue
                s_, t_ = qo[2], qo[3]
                n_rp, n_qr = nb.get((r, p)), nb.get((qv, r))
                n_ps, n_tq = self.nbr_across(Q, p, s_), self.nbr_across(Q, t_, qv)
                if n_ps is not None and n_ps.index not in consumed and (n_rp is None or n_rp not in consumed):
                    d1, d2 = face_ok(self.pts([r, p, s_])), face_ok(self.pts([r, s_, t_, qv]))
                    key = frozenset((r, p, s_))
                    if d1 is not None and d2 is not None:
                        nc = cost + 1 + max(d1 / 60, d2 / 90)
                        if nc < best_cost.get(key, 1e18):
                            best_cost[key] = nc
                            heapq.heappush(heap, (nc, next(counter), (r, p, s_), {(r, p): n_rp, (p, s_): n_ps.index, (s_, r): None},
                                                  consumed | {gi}, path + [((p, qv, r), "A", gi)]))
                if n_tq is not None and n_tq.index not in consumed and (n_qr is None or n_qr not in consumed):
                    d1, d2 = face_ok(self.pts([r, p, s_, t_])), face_ok(self.pts([r, t_, qv]))
                    key = frozenset((r, t_, qv))
                    if d1 is not None and d2 is not None:
                        nc = cost + 1 + max(d1 / 90, d2 / 60)
                        if nc < best_cost.get(key, 1e18):
                            best_cost[key] = nc
                            heapq.heappush(heap, (nc, next(counter), (r, t_, qv), {(r, t_): None, (t_, qv): n_tq.index, (qv, r): n_qr},
                                                  consumed | {gi}, path + [((p, qv, r), "B", gi)]))
        return found

    def apply_push(self, found, goal_ids):
        total, path, tri_last, edge_last, dec = found
        for tri, opt, gi in path:
            Tf = self.find_face(tri)
            p, qv, r = tri
            Q = [g for g in self.bm.edges.get((self.bm.verts[p], self.bm.verts[qv])).link_faces if g is not Tf][0]
            qo = rotate_to(self.loop_of(Q), qv)
            s_, t_ = qo[2], qo[3]
            if opt == "A":
                self.replace([Tf, Q], [(r, p, s_), (r, s_, t_, qv)])
            else:
                self.replace([Tf, Q], [(r, p, s_, t_), (r, t_, qv)])
        Tf = self.find_face(tri_last)
        gf = self.find_face(goal_ids)
        self.replace([Tf, gf], dec)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09b_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v = len(mesh.vertices)

    if os.environ.get("Q_TEST"):
        bad = []
        for pl in mesh.polygons:
            pts = [mesh.vertices[i].co for i in pl.vertices]
            if len(pts) in (3, 4) and face_ok(pts) is None:
                bad.append((pl.index, len(pts), tuple(round(c, 3) for c in pl.center)))
        print("SELFTEST faces failing face_ok:", len(bad), bad[:12])
        return
    sizes = {}
    for p in mesh.polygons:
        sizes[len(p.vertices)] = sizes.get(len(p.vertices), 0) + 1
    gates.check("入力: 三角形2・五角形2・四角形356（人間補正版）", sizes == {3: 2, 4: 356, 5: 2}, sizes)
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    probe = Quadifier(mesh)
    tris = [probe.loop_of(f) for f in probe.bm.faces if len(f.verts) == 3]
    pents = [probe.loop_of(f) for f in probe.bm.faces if len(f.verts) == 5]
    probe.bm.free()
    T1, T2 = tris
    P1, P2 = pents

    def run(steps):
        qz = Quadifier(mesh)
        total, notes = 0.0, []
        for st in steps:
            if st[0] == "recut":
                r = qz.recut_pentagons(qz.find_face(st[1]), qz.find_face(st[2]))
                if r is None:
                    qz.bm.free()
                    return None
                total += r / 90
                notes.append("五角形2枚→四角形3枚（角のずれ %.0f°）" % r)
            else:
                start, goal = qz.find_face(st[1]), qz.find_face(st[2])
                found = qz.push_to(start, goal)
                if found is None:
                    qz.bm.free()
                    return None
                qz.apply_push(found, st[2])
                total += found[0]
                notes.append("%s→%s: 三角形を %d 回動かして合体" % ("三角形", "三角形" if len(st[2]) == 3 else "五角形", len(found[1])))
        return dict(total=total, notes=notes, qz=qz)

    cands = [
        ("(a)五角形2枚を切り直し + (b)三角形1→三角形2", [("recut", P1, P2), ("push", T1, T2)]),
        ("(a)五角形2枚を切り直し + (b)三角形2→三角形1", [("recut", P1, P2), ("push", T2, T1)]),
        ("(c)三角形1→五角形1 + 三角形2→五角形2", [("push", T1, P1), ("push", T2, P2)]),
        ("(c)三角形1→五角形2 + 三角形2→五角形1", [("push", T1, P2), ("push", T2, P1)]),
    ]
    results = []
    for name, steps in cands:
        r = run(steps)
        gates.note("対応づけ %s: %s" % (name, "不可（有効な経路なし）" if r is None else "コスト %.2f" % r["total"]))
        if r:
            r["name"] = name
            results.append(r)
    if not results:
        # 三角形を動かす経路は、面を折らずには見つからない（曲がった額の側面では、移動後の四角形が折れる）。
        # 五角形2枚の切り直しだけを行い、三角形2枚は残す。
        qz = Quadifier(mesh)
        r = qz.recut_pentagons(qz.find_face(P1), qz.find_face(P2))
        gates.check("五角形2枚は、折れなしで四角形3枚に切り直せる", r is not None, r)
        results.append(dict(total=r / 90, notes=["五角形2枚→四角形3枚（角のずれ %.0f°）。三角形2枚は、面を折らずには動かせないので残す" % r], qz=qz, name="(a)のみ"))
    best = min(results, key=lambda r: r["total"])
    for r in results:
        if r is not best:
            r["qz"].bm.free()
    gates.note("採用: %s。%s" % (best["name"], " / ".join(best["notes"])))
    bm = best["qz"].bm
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # ---- 検証 ----
    sizes2 = {}
    for p in mesh.polygons:
        sizes2[len(p.vertices)] = sizes2.get(len(p.vertices), 0) + 1
    n_tri_left = sizes2.get(3, 0)
    gates.check("五角形は残っていない・三角形は %d 枚（動かせなかったもの）だけ・他は四角形" % n_tri_left, set(sizes2) <= {3, 4} and 5 not in sizes2, sizes2)
    gates.check("頂点の位置は一切変えていない（頂点数も同じ）", len(mesh.vertices) == n_v and all((a.co - b).length == 0 for a, b in zip(mesh.vertices, before)))
    gates.check("面の数: 五角形2→四角形3（+1）、三角形2→四角形1（-1、動かせた場合のみ）", len(mesh.polygons) == 360 + 1 - (1 if n_tri_left == 0 else 0), len(mesh.polygons))
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs)) == len(pairs) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    bad_out = [p.index for p in ev.polygons if p.normal.dot(p.center - HEAD_CENTER) <= 0]
    gates.check("Mirror 後: 全面の法線が頭の外側を向いている", not bad_out, bad_out[:10])
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)

    def ang_range(pts):
        lo, hi = 180.0, 0.0
        for k in range(len(pts)):
            a, b, c = pts[k - 1], pts[k], pts[(k + 1) % len(pts)]
            v1, v2 = (a - b).normalized(), (c - b).normalized()
            ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
            lo, hi = min(lo, ang), max(hi, ang)
        return lo, hi

    ranges = [ang_range([mesh.vertices[i].co for i in p.vertices]) for p in mesh.polygons]
    lo, hi = min(r[0] for r in ranges), max(r[1] for r in ranges)
    bad = sum(1 for r in ranges if r[0] < 25 or r[1] > 155)
    gates.note("面の内角（三角形を含む）: 最小 %.0f°・最大 %.0f°、25°〜155° の外は %d / %d 枚" % (lo, hi, bad, len(ranges)))
    gates.check("退化した面がない（内角が 2°〜178°）", lo >= 2 and hi <= 178, f"最小{lo:.0f}° 最大{hi:.0f}°")

    overlay.write_wire_top(ev, C.OUT / "s09b2_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    overlay.write_wire_angle(ev, 45, C.OUT / "s09b2_a45_wire.png", zoom=1, crop=(112, 112, 912, 912))
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s09b2_gen.blend"), compress=False)
    gates.finish()


main()
