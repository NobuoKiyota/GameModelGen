"""S09c: 頭の下側を閉じて、首の穴（12頂点の輪）だけを残す（動画 20:16〜22:08）。

字幕との対応:
  20:16〜20:39 ループ3本＋Alt+S で「丸っぽい頭」 → 側面は S09b で、測定した頭の外形へ投影済み。ここでは外形との差を数値で確認するだけ（増やさない）
  20:40〜21:19 「顎の下のラインと後ろのラインが繋げられそう」→ ループを足して Alt+S で膨らませ、つなぐ → 穴の輪（36辺）と首の輪（12頂点）の間に、
               輪をもう1本（R1）足して膨らませ、そこから首の輪へ絞る（四角形だけ）
  21:23〜21:37 「カクンと引っ込んでいるところは膨らます」→ へこみ（隣の平均が外側にある頂点）だけ、外側へ寄せる
  21:40〜22:08 側面のへこみ → 同上（側面は S09b で埋まっている）
  ※ 22:15〜 の首の円柱・結合は S10。この段階では、首の輪（12頂点）を穴として残す。

設計（先に決めたこと）:
  - 穴の輪 L（半分で 18辺・19頂点。前の正中線の頂点 133 から、後ろの正中線の頂点 265 まで）
  - 首の輪 N: 半分で 7頂点（12頂点の円周）。中心 Y=0.006、半径 0.058。前の頂点は顎の線の端（133）のすぐ内側（下絵の首の前の線 Y≈-0.06〜、後ろの線 Y≈+0.065）。高さは、前 -0.196 から後ろ -0.148 へ傾ける（下絵の首の上端）
    ※ 首の左右の幅は下絵にない（正面図に首がない）ので、前後と同じ半径（円）と仮定した → 要確認
  - 輪 R1: L の各頂点を、同じ角度の首の輪の点へ半分寄せて、外側へ 6mm 膨らませた輪（頂点は L と同数）
  - L→R1 は四角形18枚。R1→N は、L の 1辺=首の輪の1辺 ではなく、首の輪の1辺に対して R1 の辺が奇数本（1・3・5）になるように区切る（辺の数が偶数の多角形は、四角形だけに分けられる）
  - 各区切りの分け方は、全ての分け方から、内角の最小が最大になるものを選ぶ

入力: out/face_s09b3_gen.blend   出力: out/face_s09c_gen.blend, out/s09c_report.json, out/s09c_*.png
実行: blender --background --factory-startup --python steps/s09c_underside.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s09c"
gates = C.Gates(STEP)

HEAD_CENTER = Vector((0.0, 0.0, 0.086))     # 外向きの判定に使う頭の中心
NECK_YC = 0.006
NECK_R = 0.058
NECK_Z_FRONT = -0.196                        # 首の輪の前（Y=NECK_YC-NECK_R）の高さ
NECK_Z_BACK = -0.148                         # 後ろ（Y=NECK_YC+NECK_R）の高さ
R1_W = 0.5                                   # R1 は L から首の輪へ、この割合だけ寄せる
R1_BULGE = 0.006                             # 外側への膨らまし（動画の Alt+S）
CELL_A = None                                # 首の輪の各辺に対応する R1 の辺の数（角度から決める）
DENT_MM = 3.0                                # これ以上へこんでいる頂点を外側へ寄せる
DENT_MAX_MOVE = 0.008


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def neck_point(phi):
    """首の輪の点。phi は、前の正中線 0° → 横 90° → 後ろの正中線 180°（X ≤ 0 の側）。"""
    x = -NECK_R * math.sin(phi)
    y = NECK_YC - NECK_R * math.cos(phi)
    t = (y - (NECK_YC - NECK_R)) / (2 * NECK_R)
    z = NECK_Z_FRONT + (NECK_Z_BACK - NECK_Z_FRONT) * t
    if abs(phi) < 1e-9 or abs(phi - math.pi) < 1e-9:
        x = 0.0
    return Vector((x, y, z))


def angle_of(p):
    """首の輪の中心から見た角度（前 0° → 後ろ 180°）。"""
    return math.atan2(abs(p.x), -(p.y - NECK_YC))


def newell(pts):
    n = Vector((0, 0, 0))
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def interior_angles(pts):
    n = len(pts)
    out = []
    for k in range(n):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % n]
        v1, v2 = (a - b).normalized(), (c - b).normalized()
        out.append(math.degrees(math.acos(max(-1, min(1, v1.dot(v2))))))
    return out


def decompositions(n):
    """n角形（頂点番号 0..n-1 の循環）を四角形だけに分ける全ての分け方（対角線の入れ方）。"""
    memo = {}

    def rec(poly):
        key = tuple(poly)
        if key in memo:
            return memo[key]
        if len(poly) == 4:
            memo[key] = [[tuple(poly)]]
            return memo[key]
        res = []
        seen = set()
        m = len(poly)
        for i in range(m):
            for j in range(i + 2, m):
                if i == 0 and j == m - 1:
                    continue
                p1 = poly[i:j + 1]
                p2 = poly[j:] + poly[:i + 1]
                if len(p1) % 2 or len(p2) % 2 or len(p1) < 4 or len(p2) < 4:
                    continue
                for d1 in rec(p1):
                    for d2 in rec(p2):
                        cand = d1 + d2
                        sig = frozenset(frozenset(f) for f in cand)
                        if sig not in seen:
                            seen.add(sig)
                            res.append(cand)
        memo[key] = res
        return res

    return rec(list(range(n)))


def boundary_chain(bm):
    """穴の輪 L: 前の正中線の下端の頂点から、後ろの正中線の頂点まで（X=0 以外の境界辺だけをたどる）。"""
    be = [e for e in bm.edges if len(e.link_faces) == 1
          and not (abs(e.verts[0].co.x) < 1e-6 and abs(e.verts[1].co.x) < 1e-6)]
    axis_ends = [v for v in bm.verts if abs(v.co.x) < 1e-6 and any(e in be for e in v.link_edges) and v.co.z < -0.02 and v.co.y > -0.1]
    start = min(axis_ends, key=lambda v: v.co.z)
    chain = [start]
    prev = None
    cur = start
    while True:
        nxt = [e for e in cur.link_edges if e in be and e is not prev]
        if not nxt:
            break
        e = nxt[0]
        cur = e.other_vert(cur)
        chain.append(cur)
        prev = e
        if abs(cur.co.x) < 1e-6:
            break
    return chain


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09b3_gen.blend"))
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
    sizes = {}
    for f in bm.faces:
        sizes[len(f.verts)] = sizes.get(len(f.verts), 0) + 1
    gates.check("入力: 四角形357・五角形6・頂点402", sizes == {4: 357, 5: 6} and len(bm.verts) == 402, f"{sizes} V={len(bm.verts)}")
    n_v0, n_e0, n_f0 = len(bm.verts), len(bm.edges), len(bm.faces)

    # ---- 頭の表面との差（20:16〜20:39「丸っぽい頭」の確認）とへこみ（21:23〜）
    HS = M.HeadSurface()
    P = np.array([tuple(v.co) for v in bm.verts])
    g = HS.g_many(P)
    dist = np.linalg.norm(HS.project_many(P) - P, axis=1) * np.where(g > 0, 1, -1)
    sel = [i for i, v in enumerate(bm.verts) if v.co.y > 0.0125 and v.co.z > -0.03]
    dsel = dist[sel]
    gates.note("頭の側面〜後ろ（Y>0.0125, Z>-0.03）の、測定した頭の外形との差", f"{len(sel)}頂点: 平均 {dsel.mean() * 1000:.1f}mm・最大 {dsel.max() * 1000:.1f}mm・最小 {dsel.min() * 1000:.1f}mm（+は外側）")
    worst_i = np.argsort(-np.abs(dsel))[:6]
    gates.note("外形との差が大きい頂点", [(sel[k], rd(P[sel[k]]), round(dsel[k] * 1000, 1)) for k in worst_i])
    gates.note("3mm を超える頂点の数", f"{int((np.abs(dsel) > 0.003).sum())} / {len(sel)}")

    chain = boundary_chain(bm)
    n_l = len(chain) - 1
    gates.check("穴の輪 L: 18辺・両端は X=0（前 Y≈-0.0575・後ろ Y≈0.211）",
                n_l == 18 and abs(chain[0].co.x) < 1e-6 and abs(chain[-1].co.x) < 1e-6 and abs(chain[0].co.y + 0.0575) < 0.001 and abs(chain[-1].co.y - 0.2107) < 0.001,
                f"{n_l}辺 {rd(chain[0].co)} → {rd(chain[-1].co)}")
    chain_set = set(chain)

    dent_ids = []
    for _ in range(3):                                      # へこみを、外側へ少しずつ寄せる
        moves = {}
        for v in bm.verts:
            if v in chain_set or v.co.y <= 0.0125 or v.co.z <= -0.12 or len(v.link_edges) < 3 or abs(v.co.x) < 1e-6:
                continue
            nb = [e.other_vert(v).co for e in v.link_edges]
            m = sum(nb, Vector()) / len(nb)
            n = (v.co - HEAD_CENTER).normalized()
            off = (m - v.co).dot(n)
            if off > DENT_MM / 1000:
                moves[v] = n * min(off * 0.7, DENT_MAX_MOVE)
        for v, d in moves.items():
            v.co += d
            if v.index not in dent_ids:
                dent_ids.append(v.index)
        if not moves:
            break
    gates.note("へこみ（隣の平均が 3mm 以上外側）を外側へ寄せた頂点", f"{len(dent_ids)}個 {[(i, rd(bm.verts[i].co)) for i in dent_ids[:8]]}")
    moved = [(bm.verts[i].co - Vector(P[i])).length for i in dent_ids]
    gates.check("へこみを直した移動は 8mm 以下・X=0 の頂点は動かしていない", (max(moved) if moved else 0) <= 0.0081 and all(abs(v.co.x) < 1e-9 for v in bm.verts if abs(P[v.index][0]) < 1e-9))

    # ---- 首の輪 N と輪 R1（位置）
    angles = [angle_of(v.co) for v in chain]
    phis = [j * math.pi / 6 for j in range(7)]
    neck = [neck_point(p) for p in phis]
    r1_pos = []
    for i, v in enumerate(chain):
        proj = neck_point(min(max(angles[i], 0.0), math.pi))
        p = v.co + (proj - v.co) * R1_W
        p += (p - HEAD_CENTER).normalized() * R1_BULGE
        if abs(v.co.x) < 1e-6:
            p.x = 0.0
        r1_pos.append(p)

    # 区切り: R1 の頂点番号 s_0=0 < s_1 < … < s_6=18。s_j の偶奇は j と同じ（各区間が奇数本）。
    # 各区間 [s_j, s_j+1] の多角形（R1 の辺＋首の輪の1辺）を四角形に分ける全ての分け方のうち、内角の最小が最大のものを採る。
    # 区切り全体は、内角の最小が大きく、首の輪の角度（0°,30°,…）との差が小さいものを選ぶ。
    cell_memo = {}

    def cell_best(i, k, j):
        key = (i, k, j)
        if key in cell_memo:
            return cell_memo[key]
        pts = r1_pos[i:k + 1] + [neck[j + 1], neck[j]]
        ref = newell(pts)
        best = None
        for dec in decompositions(len(pts)):
            worst, ok = 180.0, True
            for f in dec:
                fp = [pts[q] for q in f]
                if newell(fp).dot(ref) <= 0:
                    ok = False
                    break
                worst = min(worst, min(interior_angles(fp)))
            if ok and (best is None or worst > best[0]):
                best = (worst, dec)
        cell_memo[key] = best
        return best

    best_plan = [None]

    def search(j, s_prev, chosen, min_w, dev):
        if j == 6:
            if s_prev == n_l:
                score = min_w - 0.3 * dev / 5
                if best_plan[0] is None or score > best_plan[0][0]:
                    best_plan[0] = (score, list(chosen), min_w, dev / 5)
            return
        for k in ((n_l,) if j == 5 else range(s_prev + 1, min(s_prev + 6, n_l))):
            if (k - s_prev) % 2 == 0 or (k - s_prev) > 5:
                continue
            if j < 5 and n_l - k < 1 * (6 - j - 1):
                continue
            res = cell_best(s_prev, k, j)
            if res is None:
                continue
            d = abs(math.degrees(angles[k]) - math.degrees(phis[j + 1])) if j < 5 else 0.0
            search(j + 1, k, chosen + [k], min(min_w, res[0]), dev + d)

    search(0, 0, [], 180.0, 0.0)
    gates.check("R1 の辺を、首の輪の6辺に、奇数本（1・3・5）ずつ割り当てられた（合計18）", best_plan[0] is not None)
    s = [0] + best_plan[0][1]
    a = [s[j + 1] - s[j] for j in range(6)]
    gates.check("各区間は奇数本・合計18", all(x % 2 == 1 for x in a) and sum(a) == 18, f"割り当て {a}、区切り {s}")
    gates.note("区切りの角度（首の輪 0°,30°,…,180° に対する L の頂点の角度）", [round(math.degrees(angles[i])) for i in s])
    gates.note("区切りの選び方", f"区間の内角の最小 {best_plan[0][2]:.0f}°、首の輪の角度とのずれの平均 {best_plan[0][3]:.0f}°")

    nv = [bm.verts.new(p) for p in neck]
    r1 = [bm.verts.new(p) for p in r1_pos]
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    # 向き: L の辺を使っている既存の面が (L_i → L_i+1) の向きなら、新しい面は逆向き
    fwd = False
    for lp in chain[0].link_loops:
        if lp.link_loop_next.vert is chain[1]:
            fwd = True
    faces_new = []

    def add_face(vs):
        vs = list(vs)
        if fwd:
            vs = vs[::-1]
        faces_new.append(bm.faces.new(vs))

    for i in range(n_l):
        add_face([chain[i], chain[i + 1], r1[i + 1], r1[i]])
    plan = []
    for j in range(6):
        outer = r1[s[j]:s[j + 1] + 1]
        poly = outer + [nv[j + 1], nv[j]]
        best = cell_best(s[j], s[j + 1], j)
        gates.check(f"区切り{j}（R1 の辺 {a[j]} 本 → 首の輪の1辺）は、折れなしで四角形に分けられる", best is not None, f"最小の内角 {best[0]:.0f}°" if best else "")
        plan.append(best)
        for f in best[1]:
            add_face([poly[k] for k in f])
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    n_new_f = len(faces_new)
    gates.check("追加: 頂点 %d（首の輪7＋R1 19）・面 %d（L→R1 18＋首の輪への区切り %d）" % (len(bm.verts) - n_v0, n_new_f, n_new_f - 18),
                len(bm.verts) - n_v0 == 26 and n_new_f == 18 + sum((x + 1) // 2 for x in a), f"V={len(bm.verts)} F={len(bm.faces)}")

    # 巻き順・非多様体
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            aa, bb = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((aa.index, bb.index)), []).append((aa.index, bb.index))
    gates.check("巻き順が一貫・3枚以上が共有する辺なし", all(len(d) <= 2 and (len(d) < 2 or d[0] == (d[1][1], d[1][0])) for d in share.values()))
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()

    gates.check("X ≤ 0 で、正中線の頂点は X=0", max(v.co.x for v in mesh.vertices) <= 1e-9)
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # ---- Mirror 後の検証
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
            aa, bb = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(tuple(sorted((aa, bb))), []).append((aa, bb))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs)) == len(pairs) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    bad_out = [p.index for p in ev.polygons if p.normal.dot(p.center - HEAD_CENTER) <= 0]
    gates.check("Mirror 後: 全面の法線が頭の外側を向いている", not bad_out, [(i, rd(ev.polygons[i].center)) for i in bad_out[:10]])
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)

    # 境界の輪: 目2（13）・口（16）・首の穴（12）だけになる
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
    gates.check("穴（境界の輪）は、目2つ（13辺）・口（16辺）・首（12辺）の4つだけ", lens == [12, 13, 13, 16], lens)
    neck_loop = [c for c in loops if len(c) == 12]
    if neck_loop:
        nvs = {v.index for e in neck_loop[0] for v in e.verts}
        pts = [bmev.verts[i].co for i in nvs]
        gates.check("首の穴は、12頂点で、中心 Y≈%.3f・半径 %.3f（前後・左右とも）" % (NECK_YC, NECK_R),
                    len(nvs) == 12 and abs(max(p.x for p in pts) - NECK_R) < 0.003 and abs(min(p.y for p in pts) - (NECK_YC - NECK_R)) < 0.003 and abs(max(p.y for p in pts) - (NECK_YC + NECK_R)) < 0.003,
                    f"X ±{max(p.x for p in pts):.3f}・Y {min(p.y for p in pts):.3f}〜{max(p.y for p in pts):.3f}・Z {min(p.z for p in pts):.3f}〜{max(p.z for p in pts):.3f}")
    bmev.free()

    # 面の内角・辺の長さ（追加した面）
    new_ids = list(range(n_f0, len(mesh.polygons)))
    ranges = []
    for i in new_ids:
        pts = [mesh.vertices[k].co for k in mesh.polygons[i].vertices]
        an = interior_angles(pts)
        ranges.append((min(an), max(an)))
    lo, hi = min(r[0] for r in ranges), max(r[1] for r in ranges)
    bad = sum(1 for r in ranges if r[0] < 25 or r[1] > 155)
    gates.note("追加した面（%d枚）の内角: 最小 %.0f°・最大 %.0f°、25°〜155° の外は %d 枚" % (len(new_ids), lo, hi, bad))
    odd = [(i, rd(mesh.polygons[i].center), round(ranges[i - n_f0][0]), round(ranges[i - n_f0][1])) for i in new_ids if ranges[i - n_f0][0] < 25 or ranges[i - n_f0][1] > 155]
    gates.note("追加した面のうち、内角が 25°〜155° の外の面（面の番号・中心・最小・最大）", odd)
    gates.check("追加した面に、折れ・退化がない（内角 5°〜179°。外向きの面・巻き順は上で確認）", lo >= 5 and hi <= 179, f"{lo:.0f}°〜{hi:.0f}°")
    el = [(mesh.vertices[e.vertices[0]].co - mesh.vertices[e.vertices[1]].co).length for e in mesh.edges[n_e0:]]
    gates.note("追加した辺の長さ", f"最小 {min(el) * 1000:.1f}mm・中央 {np.median(el) * 1000:.1f}mm・最大 {max(el) * 1000:.1f}mm")

    # L の輪をはさむ面どうしの折れ角（動画 21:23「カクンと引っ込む」がないか）
    bmc = bmesh.new()
    bmc.from_mesh(mesh)
    bmc.faces.ensure_lookup_table()
    worst = 0.0
    for e in bmc.edges:
        if len(e.link_faces) == 2:
            f0, f1 = e.link_faces
            if (f0.index >= n_f0) != (f1.index >= n_f0):
                worst = max(worst, math.degrees(f0.normal.angle(f1.normal)))
    gates.note("L の輪をはさむ、既存の面と追加した面の、折れ角の最大", f"{worst:.0f}°")
    gates.note("要確認: 壁の下端（側面と下側の角）で折れ角が大きい。動画の Alt+S の膨らましに当たる部分（人間の手直し待ち）", f"{worst:.0f}°")
    bmc.free()

    # レビュー画像
    overlay.write_wire_angle(ev, 90, C.OUT / "s09c_side_wire.png", zoom=1, crop=(112, 112, 912, 912))
    overlay.write_wire_angle(ev, 135, C.OUT / "s09c_back45_wire.png", zoom=1, crop=(112, 112, 912, 912))
    overlay.write_wire_angle(ev, 180, C.OUT / "s09c_back_wire.png", zoom=1, crop=(112, 112, 912, 912))
    write_bottom(ev, C.OUT / "s09c_bottom_wire.png")
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s09c_gen.blend"), compress=False)
    gates.finish()


def write_bottom(mesh, out_path):
    """真下から見たワイヤー（上が顔・-Y）。境界の辺は青。"""
    arr = np.ones((C.IMG_PX, C.IMG_PX, 4), dtype=np.float32)
    arr[..., :3] = 0.8
    for gx in range(0, C.IMG_PX, 64):
        arr[:, gx, :3] = 0.72
        arr[gx, :, :3] = 0.72
    pts = [(C.COL0 + v.co.x / C.K, C.COL0 + v.co.y / C.K) for v in mesh.vertices]
    cnt = {}
    for p in mesh.polygons:
        vs = list(p.vertices)
        for k in range(len(vs)):
            key = tuple(sorted((vs[k], vs[(k + 1) % len(vs)])))
            cnt[key] = cnt.get(key, 0) + 1
    for e in mesh.edges:
        key = tuple(sorted(e.vertices))
        col = (0.1, 0.1, 1.0) if cnt.get(key, 0) == 1 else (1.0, 0.1, 0.1)
        overlay._line(arr, pts[e.vertices[0]], pts[e.vertices[1]], col)
    for p in pts:
        overlay._dot(arr, p, (1.0, 1.0, 0.0), r=1)
    arr = arr[112:912, 112:912]
    img = bpy.data.images.new("bottom_tmp", 800, 800, alpha=False)
    img.pixels.foreach_set(arr[::-1].ravel())
    img.filepath_raw = str(out_path)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


main()
