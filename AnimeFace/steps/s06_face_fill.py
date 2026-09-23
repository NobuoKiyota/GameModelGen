"""S06: 頬・鼻・口の面張り（動画 11:39〜13:35）＋ 鼻・口まわりの頂点追加。

動画の操作: 顎のラインと口を Ctrl+R のループと M(At Center) でだんだんくっつける → 鼻先から線で繋ぐ → 辺を選んで F で面を貼る
            → へこみを法線方向に直して滑らかにする → 「大体正面の顔ができました」
ここでは -X 側の半分の「穴」を、頂点数の合った四角形の格子で埋める。ユーザーの指摘（鼻・口まわりの頂点が足りず、
側面の輪郭を再現できていない）を受けて、正中線に輪郭に沿った頂点を足し、行を増やした。

  ⓪ 口の輪の前後位置(Y)を、側面の輪郭（縦位置を正面に合わせた割り付け）に合わせ直す（S03 は生の輪郭を使い約12mm後ろだった）
  ① 正中線(X=0)に頂点を追加: 鼻先〜鼻下(p1) / 鼻下〜口の上(q1,q2) / 口の下〜顎先(s)。Y は側面の輪郭に沿う
  ② Ctrl+R 相当: 頬の帯の目頭側の縦の辺（17→頬の頂点51）を6分割、顎側の縦の辺（51→顎先）を2分割。目頭17→鼻根N0 の辺を3分割
  ③ 格子（3列×7行）: 上辺 17→t2→t1→N0 / 右辺 N0→N1→N2→p1→N3→q1→q2→口の上の中心 / 下辺 口の外輪の端→…→上の中心 /
     左辺 17→a1..a5→51→口の端。内部頂点12は4辺からのクーンズパッチ補間
  ④ 口の下〜顎: 8角形（口の端→口の下→s→顎先→r→頬の頂点）を、内部頂点1つの4四角形に分割（位置と繋ぎ方を全探索）
     ※ 正中線の頂点を2つ以上足すと、正中線上で3頂点が連続する四角形（内角180°）が避けられないため1つにした。
        頬の頂点と口の端がほぼ一直線のため、どの分け方でも口の端の側が楔形（最良でも内角10°〜160°）になる

入力: out/face_s05_human.blend   出力: out/face_s06_gen.blend, out/s06_report.json, out/s06_*_overlay.png
実行: blender --background --factory-startup --python steps/s06_face_fill.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import measure as M  # noqa: E402
import overlay  # noqa: E402

STEP = "s06"
gates = C.Gates(STEP)

# 頂点の役割（S02〜S05 の作成順。位置で検証する）
EYE_CORNER, NOSE = 17, [40, 41, 42, 43]                  # 目頭の頂点、鼻根→鼻筋→鼻先→鼻下
MOUTH_ALL = list(range(26, 40))                          # 口（内輪26〜32・外輪33〜39）
MOUTH_OUTER = [33, 34, 35, 36, 37, 38, 39]               # 口の外輪（上の中心→端→下の中心）
CHIN, CHEEK = 44, 51                                     # 顎先、頬の頂点（S05 の中間列の目頭側）
R0_ROW = [17, 8, 15, 14, 23, 13, 12]                     # 頬の帯の目の下の列（目頭→目尻）
R1_ROW = list(range(51, 58))                             # 頬の帯の中間の列
R2_ROW = list(range(44, 51))                             # 頬の帯の顎の列
SIL_INSET_PX, SETBACK_R = 3, 0.2                         # S03/S04 と同じ
CUTS_LEFT, CUTS_JAW = 5, 1                               # 帯の縦の辺の分割数（6分割・2分割）
FRONT_ROWS = dict(p1=617.5, q1=664.8, q2=685.2, s=782.7)   # 正中線に足す頂点の高さ（正面の行）


def ang_range(pts):
    lo, hi = 180.0, 0.0
    for k in range(4):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % 4]
        v1, v2 = (a - b).normalized(), (c - b).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
        lo, hi = min(lo, ang), max(hi, ang)
    return lo, hi


def aspect(pts):
    e = [(pts[(k + 1) % 4] - pts[k]).length for k in range(4)]
    return max((e[0] + e[2]) / (e[1] + e[3]), (e[1] + e[3]) / (e[0] + e[2]))


def on_segment(p, a, b, tol=1e-6):
    """p が線分 a-b の内側（端点を除く）にあるなら a からの割合 t。"""
    ab = b - a
    t = (p - a).dot(ab) / ab.length_squared
    if 1e-6 < t < 1 - 1e-6 and ((a + ab * t) - p).length < tol:
        return t
    return None


def newell_orient(ids, pos):
    """ニューウェル法線が -Y を向く巻き順にそろえる。"""
    pts = [pos[k] for k in ids]
    n = Vector((0, 0, 0))
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return ids if n.y < 0 else ids[::-1]


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s05_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)

    # --- 側面の輪郭（縦位置を正面に合わせる割り付け。S04 と同じ）---
    sil = M.side_silhouette()
    sub_row_s, _ = M.side_subnasale_row(sil)
    lip_row_s, chin_s, chin_f = M.side_lip_row(), M.side_chin_row(), M.front_chin_row()
    f2s = M.front_to_side_row_map([C.ROW0, sub_row_s, lip_row_s, chin_s], [C.ROW0, sub_row_s, 722.5, chin_f])

    def y_prof(v_front):
        return -(sil[int(round(f2s(v_front)))] - SIL_INSET_PX - C.COL0) * C.K

    # --- 入力の検証 ---
    co = lambda i: mesh.vertices[i].co  # noqa: E731
    gates.check("入力: 58頂点・面31・Mirror のみ", (n_v, n_f) == (58, 31) and [m.type for m in obj.modifiers] == ["MIRROR"], (n_v, n_f))
    gates.check("入力: 鼻筋・口の外輪の上下の中心・顎先が X=0",
                all(co(i).x == 0.0 for i in NOSE + [MOUTH_OUTER[0], MOUTH_OUTER[-1], CHIN]))
    gates.check("入力: 目頭の頂点は目（先頭26個）で最も鼻側、口の外輪の端は外輪の X 最小",
                EYE_CORNER == max(range(26), key=lambda i: co(i).x) and MOUTH_OUTER[3] == min(MOUTH_OUTER, key=lambda i: co(i).x))

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    def refresh():
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

    def edge_of(a, b):
        return bm.edges.get((bm.verts[a], bm.verts[b]))

    # ⓪ 口の輪の前後位置を側面の輪郭に合わせ直す（X・Z は動かさない）
    moved = []
    for i in MOUTH_ALL:
        v = bm.verts[i]
        y_new = y_prof(C.ROW0 - v.co.z / C.K) + v.co.x ** 2 / (2 * SETBACK_R)
        moved.append(y_new - v.co.y)
        v.co.y = y_new
    gates.note("口の輪(14頂点)の前後位置を側面の輪郭に合わせ直した: 移動量 平均%.1fmm 最大%.1fmm（前が正）" % (
        -sum(moved) / 14 * 1000, -min(moved) * 1000))

    # ① 正中線(X=0)に、輪郭に沿った頂点を追加
    def center_vertex(v_front):
        return bm.verts.new((0.0, y_prof(v_front), (C.ROW0 - v_front) * C.K))

    p1, q1, q2 = (center_vertex(FRONT_ROWS[k]) for k in ("p1", "q1", "q2"))
    s = center_vertex(FRONT_ROWS["s"])
    refresh()
    center_new = [p1.index, q1.index, q2.index, s.index]
    P1, Q1, Q2, S1 = center_new
    bm.edges.remove(edge_of(NOSE[2], NOSE[3]))               # 鼻先→鼻下 の辺を p1 経由に置き換える
    for a, b in ((NOSE[2], P1), (P1, NOSE[3]), (NOSE[3], Q1), (Q1, Q2), (Q2, MOUTH_OUTER[0]),
                 (MOUTH_OUTER[-1], S1), (S1, CHIN)):
        bm.edges.new((bm.verts[a], bm.verts[b]))
    refresh()

    # ② 帯の縦の辺・目頭17→鼻根 N0 の辺を分割（Ctrl+R 相当）
    rungs01 = [edge_of(a, b) for a, b in zip(R0_ROW, R1_ROW)]
    rungs12 = [edge_of(a, b) for a, b in zip(R1_ROW, R2_ROW)]
    gates.check("入力: 帯の縦の辺（目の下↔中間 7本、中間↔顎 7本）がある", all(rungs01) and all(rungs12))
    n_before_cut = len(bm.verts)
    bmesh.ops.subdivide_edges(bm, edges=rungs01, cuts=CUTS_LEFT, use_grid_fill=True)
    refresh()
    rungs12 = [edge_of(a, b) for a, b in zip(R1_ROW, R2_ROW)]
    bmesh.ops.subdivide_edges(bm, edges=rungs12, cuts=CUTS_JAW, use_grid_fill=True)
    refresh()
    bmesh.ops.subdivide_edges(bm, edges=[edge_of(EYE_CORNER, NOSE[0])], cuts=2)
    refresh()

    new_ids = list(range(n_before_cut, len(bm.verts)))
    p17, p51, p44, pN0 = (bm.verts[i].co.copy() for i in (EYE_CORNER, CHEEK, CHIN, NOSE[0]))

    def along(a, b, n):
        out = sorted(((on_segment(bm.verts[i].co, a, b), i) for i in new_ids if on_segment(bm.verts[i].co, a, b) is not None))
        ok = len(out) == n and all(abs(t - (k + 1) / (n + 1)) < 1e-4 for k, (t, _) in enumerate(out))
        return [i for _, i in out], ok

    left_new, ok1 = along(p17, p51, CUTS_LEFT)
    jaw_new, ok2 = along(p51, p44, CUTS_JAW)
    top_new, ok3 = along(p17, pN0, 2)
    gates.check("17→頬の頂点51 の縦の辺に等間隔の新しい頂点が%d個" % CUTS_LEFT, ok1, len(left_new))
    gates.check("頬の頂点51→顎先 の縦の辺に等間隔の新しい頂点が%d個" % CUTS_JAW, ok2, len(jaw_new))
    gates.check("17→鼻根 N0 の辺に等間隔の新しい頂点が2個", ok3, len(top_new))
    t2, t1 = top_new                                # 17 に近い方が t2

    # ③ 格子（3列×7行）
    m0, m1, m2, m3 = MOUTH_OUTER[:4]
    top = [EYE_CORNER, t2, t1, NOSE[0]]
    right = [NOSE[0], NOSE[1], NOSE[2], P1, NOSE[3], Q1, Q2, m0]
    bottom = [m3, m2, m1, m0]
    left = [EYE_CORNER] + left_new + [CHEEK, m3]
    ROWS = len(right) - 1
    gates.check("格子の左辺と右辺の分割数が一致（7）", len(left) - 1 == ROWS == 7, (len(left) - 1, ROWS))
    pos = {i: bm.verts[i].co.copy() for i in set(top + right + bottom + left)}
    c00, c10, c01, c11 = pos[top[0]], pos[top[3]], pos[bottom[0]], pos[bottom[3]]
    grid = {}
    for j in range(ROWS + 1):
        grid[0, j], grid[3, j] = left[j], right[j]
    for i in range(4):
        grid[i, 0], grid[i, ROWS] = top[i], bottom[i]
    for i in (1, 2):
        for j in range(1, ROWS):
            u, v = i / 3, j / ROWS
            pp = ((1 - u) * pos[left[j]] + u * pos[right[j]] + (1 - v) * pos[top[i]] + v * pos[bottom[i]]
                  - ((1 - u) * (1 - v) * c00 + u * (1 - v) * c10 + (1 - u) * v * c01 + u * v * c11))
            nv = bm.verts.new(pp)
            nv.index = len(bm.verts) - 1
            grid[i, j] = nv.index
            pos[nv.index] = pp

    refresh()

    # ④ 口の下〜顎: 8角形 [m3, m4, m5, m6, s, 顎先, r, 頬の頂点] を内部頂点1つの4四角形に分割
    m4, m5, m6 = MOUTH_OUTER[4:]
    poly_ids = [m3, m4, m5, m6, S1, CHIN] + jaw_new[::-1] + [CHEEK]      # 顎先に近い方から
    for i in poly_ids:
        pos.setdefault(i, bm.verts[i].co.copy())
    poly = [(pos[i].x, pos[i].z) for i in poly_ids]
    NP = len(poly_ids)

    def inside(pt):
        x, z = pt
        c = False
        for k in range(NP):
            (x1, z1), (x2, z2) = poly[k], poly[(k + 1) % NP]
            if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1:
                c = not c
        return c

    def quad_score(q2):
        area = sum(q2[k][0] * q2[(k + 1) % 4][1] - q2[(k + 1) % 4][0] * q2[k][1] for k in range(4)) / 2
        dev = 0.0
        for k in range(4):
            a, b, c = q2[k - 1], q2[k], q2[(k + 1) % 4]
            v1, v2 = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
            if ang < 5 or ang > 175:
                return None, area
            dev = max(dev, abs(ang - 90))
        return dev, area

    patterns = {"偶数番目": list(range(0, NP, 2)), "奇数番目": list(range(1, NP, 2))}
    best_l = None
    xs_, zs_ = [p[0] for p in poly], [p[1] for p in poly]
    x = min(xs_)
    while x <= max(xs_):
        z = min(zs_)
        while z <= max(zs_):
            if inside((x, z)):
                for name, starts in patterns.items():
                    devs, areas, ok = [], [], True
                    for s0 in starts:
                        q2 = [poly[(s0 + k) % NP] for k in range(3)] + [(x, z)]
                        d, ar_ = quad_score(q2)
                        if d is None:
                            ok = False
                            break
                        devs.append(d)
                        areas.append(ar_)
                    if ok and (all(a > 0 for a in areas) or all(a < 0 for a in areas)):
                        if best_l is None or max(devs) < best_l[0]:
                            best_l = (max(devs), name, starts, (x, z))
            z += 0.0005
        x += 0.0005
    gates.check("口の下の8角形: 内部頂点1つの4四角形分割が見つかった（内角5°〜175°・向きが一貫）", best_l is not None)
    sc_l, name_l, starts_l, (qx, qz) = best_l
    qy = sum(pos[poly_ids[(s0 + 1) % NP]].y for s0 in starts_l) / len(starts_l)
    nq = bm.verts.new((qx, qy, qz))
    nq.index = len(bm.verts) - 1
    pos[nq.index] = nq.co.copy()
    refresh()

    # --- 面を貼る ---
    grid_pts, l_pts = [], []
    for i in range(3):
        for j in range(ROWS):
            q = newell_orient([grid[i, j], grid[i, j + 1], grid[i + 1, j + 1], grid[i + 1, j]], pos)
            bm.faces.new([bm.verts[k] for k in q])
            grid_pts.append([pos[k] for k in q])
    for s0 in starts_l:
        ids = newell_orient([poly_ids[(s0 + k) % NP] for k in range(3)] + [nq.index], pos)
        bm.faces.new([bm.verts[k] for k in ids])
        l_pts.append([pos[k] for k in ids])
    gates.note("口の下の8角形: 繋ぎ方=%s・内部頂点 (X=%.3f, Z=%.3f)・最大の角のずれ %.0f°（要手直しの目安）" % (name_l, qx, qz, sc_l))

    bm.normal_update()
    bm.verts.index_update()
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    n_new_v, n_new_f = len(mesh.vertices) - n_v, len(mesh.polygons) - n_f
    exp_v = len(center_new) + 7 * CUTS_LEFT + 7 * CUTS_JAW + 2 + 2 * (ROWS - 1) + 1
    exp_f = 6 * CUTS_LEFT + 6 * CUTS_JAW + 3 * ROWS + len(starts_l)
    gates.check("既存の頂点の位置は、口の輪の前後(Y)以外動いていない",
                all((a.co - b).length == 0 or (i in MOUTH_ALL and a.co.x == b.x and a.co.z == b.z)
                    for i, (a, b) in enumerate(zip(list(mesh.vertices)[:n_v], before))))
    gates.check("追加頂点 %d = 正中線4 + 帯の分割%d + 上辺2 + 格子の内部%d + 口の下の内部1" % (exp_v, 7 * (CUTS_LEFT + CUTS_JAW), 2 * (ROWS - 1)),
                n_new_v == exp_v, n_new_v)
    gates.check("全面が四角形", all(len(p.vertices) == 4 for p in mesh.polygons), len(mesh.polygons))
    gates.check("面の追加 %d = 帯の分割 + 格子%d + 口の下%d" % (exp_f, 3 * ROWS, len(starts_l)), n_new_f == exp_f, n_new_f)
    gates.check("全面の法線が -Y（前）向き", all(p.normal.y < 0 for p in mesh.polygons), sum(1 for p in mesh.polygons if p.normal.y >= 0))
    at0 = [i for i in range(n_v, len(mesh.vertices)) if mesh.vertices[i].co.x == 0.0]
    gates.check("X=0 の新しい頂点は正中線に足した4つだけ（他はすべて X<0）", sorted(at0) == sorted(center_new), at0)
    gates.check("モディファイアは Mirror のみ（Apply なし）", [m.type for m in obj.modifiers] == ["MIRROR"])

    # --- 輪郭への一致（正中線の頂点が側面の輪郭に乗り、Z が単調に下がる）---
    chain = [NOSE[0], NOSE[1], NOSE[2], P1, NOSE[3], Q1, Q2, MOUTH_OUTER[0], MOUTH_OUTER[-1], S1, CHIN]
    zs = [mesh.vertices[i].co.z for i in chain]
    gates.check("正中線（鼻根→鼻先→鼻下→口→顎先）の Z が単調に下がる", all(a > b for a, b in zip(zs, zs[1:])), [round(z, 3) for z in zs])
    off = []
    for i in center_new + [MOUTH_OUTER[0], MOUTH_OUTER[-1]]:
        u, _ = C.project(mesh.vertices[i].co, 90)
        vf = C.ROW0 - mesh.vertices[i].co.z / C.K
        off.append(abs(u - (sil[int(round(f2s(vf)))] - SIL_INSET_PX)))
    gates.check("正中線の頂点（追加4＋口の外輪の上下の中心）が、側面の輪郭（割り付け後）に ±1px で乗っている", max(off) <= 1,
                [round(o, 1) for o in off])

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点と面の数が「片側×2 − 中心の共有」に一致",
                (Vn, Fn) == (107 + 2 * n_new_v - len(center_new), 62 + 2 * n_new_f), (Vn, En, Fn))
    gates.check("Mirror 後: 辺の重複なし", len(set(pairs)) == len(pairs), f"E={En}")
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 3枚以上の面が共有する辺がない", max(len(v) for v in share.values()) <= 2, max(len(v) for v in share.values()))
    bad_wind = [e for e, d in share.items() if len(d) == 2 and d[0] != (d[1][1], d[1][0])]
    gates.check("Mirror 後: 隣り合う面の巻き順が一貫している（共有する辺の向きが逆）", not bad_wind, len(bad_wind))
    gates.check("Mirror 後: 全面が四角形・法線 -Y 向き", all(len(p.vertices) == 4 and p.normal.y < 0 for p in ev.polygons),
                sum(1 for p in ev.polygons if p.normal.y >= 0))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    adj = {}
    for e, d in share.items():
        if len(d) == 1:
            adj.setdefault(e[0], []).append(e[1])
            adj.setdefault(e[1], []).append(e[0])
    seen, loops = set(), []
    for s in adj:
        if s in seen:
            continue
        stack, comp = [s], 0
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp += 1
            stack += adj[x]
        loops.append(comp)
    gates.check("Mirror 後: 境界のループは4つ（目の穴2・口の穴1・外周1）", len(loops) == 4, sorted(loops))
    gates.check("Mirror 後: オイラー数 -2（穴3つの円盤）", Vn - En + Fn == -2, f"V={Vn} E={En} F={Fn}")

    # --- 四角形の歪み ---
    lo = min(ang_range(p)[0] for p in grid_pts)
    hi = max(ang_range(p)[1] for p in grid_pts)
    gates.check("今回貼った格子の四角形%d枚: 内角が 25°〜155° の範囲" % len(grid_pts), lo >= 25 and hi <= 155,
                f"最小{lo:.0f}° 最大{hi:.0f}° 最大縦横比{max(aspect(p) for p in grid_pts):.1f}")
    gates.note("口の下の%d四角形の内角: 最小%.0f° 最大%.0f°（口の端が楔形になるため。要手直し）" % (
        len(l_pts), min(ang_range(p)[0] for p in l_pts), max(ang_range(p)[1] for p in l_pts)))
    bad_old = []
    for p in mesh.polygons:
        l2, h2 = ang_range([mesh.vertices[i].co for i in p.vertices])
        if (l2 < 25 or h2 > 155) and p.center.x <= 0:
            bad_old.append((round(p.center.x, 3), round(p.center.z, 3), round(l2), round(h2)))
    gates.note("歪んだ面（-X 側、内角<25°または>155°）: (X, Z, 最小°, 最大°) = %s" % bad_old)

    for ang, tag, crop, zoom in [(0, "front", (150, 440, 560, 850), 2), (45, "a45", (330, 440, 780, 850), 2),
                                 (90, "side", (640, 480, 900, 850), 3)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s06_{tag}_overlay.png", crop=crop, zoom=zoom)
    gates.check("レビュー画像3枚を出力", all((C.OUT / f"s06_{t}_overlay.png").exists() for t in ("front", "a45", "side")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s06_gen.blend"), compress=False)
    gates.finish()


main()
