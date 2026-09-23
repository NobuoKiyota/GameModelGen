"""S09b: 頭の側面の穴埋め（動画 19:41〜20:11）。

字幕: 「頭の側面をちょっとずつ穴埋めしていく。1頂点選んで F で面を貼って、もうちょっとこれ横に持ってきて、この4頂点を選んで F で面を貼る。
       ここの1頂点選んで F で面を貼る。これはもうちょっと横でいいか。今、頭だけ表示するとこんな感じです」
実装: 額の上端・壁の後ろの縁・弧（S09a の外側の列）・新しい下の縁で囲まれた穴を、頂点数の合った格子で埋める（F で面を貼る）。
      頂点を「もうちょっと横へ」動かす操作は、測定した頭の外形（A(Z), Bf(Z), Bb(Z)）への投影で置き換える（内部頂点は頭の表面に乗せる）。

  上辺   : 額の上端 T_2 → T_12（11頂点・10区間）
  壁     : T_12 → 耳の下 v127（16頂点・15区間。S08 のループで不揃いに増えた頂点を含む）
  弧     : 弧の外側の列（起点 T_2 → 後ろの端）。13区間なので、切り込み（Ctrl+R 相当）で2行を足して15区間に揃える
  下の縁 : 耳の下 v127 → 弧の後ろの端。新しい曲線（10区間。頭の表面に乗せる）
  格子   : 10列×15行（内部頂点 9×14=126）。4辺からのクーンズパッチ補間を、頭の表面へ投影

入力: out/face_s09a_human.blend   出力: out/face_s09b_gen.blend, out/s09b_report.json, out/s09b_*.png
実行: blender --background --factory-startup --python steps/s09b_head_side_fill.py
注意: この後、首・顎の下（20:40〜）の穴が残る。
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

STEP = "s09b"
gates = C.Gates(STEP)
HEAD_CENTER = Vector((0.0, 0.0, -0.03))
Z_TOP_ROW = 0.19
N_LOW = 10                       # 下の縁の区間数（上辺と同じ）


def newell(pts):
    n = Vector((0, 0, 0))
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def outward(ids, pos):
    pts = [pos[k] for k in ids]
    c = sum(pts, Vector()) / len(pts)
    return ids if newell(pts).dot(c - HEAD_CENTER) > 0 else ids[::-1]


def ang_range(pts):
    lo, hi = 180.0, 0.0
    for k in range(4):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % 4]
        v1, v2 = (a - b).normalized(), (c - b).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
        lo, hi = min(lo, ang), max(hi, ang)
    return lo, hi


def edge_ring(seed):
    """四角面の向かい合う辺をたどったエッジリング（S08 と同じ）。"""
    ring, seen = [seed], {seed}

    def walk(edge, face):
        while True:
            if len(face.verts) != 4:
                return
            opp = [e for e in face.edges if not (set(e.verts) & set(edge.verts))]
            if len(opp) != 1 or opp[0] in seen:
                return
            e2 = opp[0]
            ring.append(e2)
            seen.add(e2)
            others = [f for f in e2.link_faces if f is not face]
            if not others:
                return
            edge, face = e2, others[0]

    for f in seed.link_faces:
        walk(seed, f)
    return ring


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09a_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)
    gates.check("入力: 269頂点・面220・全面四角形・Mirror→Subsurf",
                (n_v, n_f) == (269, 220) and all(len(p.vertices) == 4 for p in mesh.polygons)
                and [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"], (n_v, n_f))
    hs = M.HeadSurface()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    def refresh():
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

    def boundary_adj():
        adj = {}
        for e in bm.edges:
            if len(e.link_faces) == 1:
                a, b = e.verts
                if abs(a.co.x) < 1e-9 and abs(b.co.x) < 1e-9:      # 鏡の面の辺は境界に数えない
                    continue
                adj.setdefault(a.index, []).append(b.index)
                adj.setdefault(b.index, []).append(a.index)
        return adj

    # --- 上辺: 額の上端（Z=0.19）を X の絶対値の小さい順に。最初の3つ（X=0, -0.005, -0.020）は弧の3列 ---
    top_all = sorted([v for v in bm.verts if abs(v.co.z - Z_TOP_ROW) < 1e-6 and v.co.x <= 1e-9], key=lambda v: -v.co.x)
    gates.check("額の上端の頂点が13個", len(top_all) == 13, len(top_all))
    s_top = [v.index for v in top_all[2:]]                                   # T_2 → T_12（11頂点）
    t2, t12 = s_top[0], s_top[-1]
    gates.check("上辺: T_2（X≈-0.020）から壁の上端 T_12（Y=+0.0105）まで11頂点",
                len(s_top) == 11 and abs(bm.verts[t12].co.y - 0.0105) < 1e-4, (len(s_top), round(bm.verts[t2].co.x, 4)))

    # --- 壁: T_12 から境界を下る（Y=+0.0105 の面の上）---
    adj = boundary_adj()
    s_wall, prev, cur = [t12], None, t12
    while True:
        nxt = [n for n in adj[cur] if n != prev and n not in s_top]
        if not nxt:
            break
        cand = nxt[0]
        if bm.verts[cand].co.y < 0.0105 - 1e-6:
            break
        prev, cur = cur, cand
        s_wall.append(cur)
    gates.check("壁: T_12 から耳の下まで、境界の辺で16頂点（Z=0.19 → -0.127）",
                len(s_wall) == 16 and abs(bm.verts[s_wall[-1]].co.z + 0.127) < 1e-3, (len(s_wall), round(bm.verts[s_wall[-1]].co.z, 4)))
    ear = s_wall[-1]

    # --- 弧の外側の列: T_2 から、上辺ではない方の境界をたどる ---
    def walk_ribbon():
        chain, prev, cur = [t2], None, t2
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in s_top]
            if not nxt:
                break
            cand = nxt[0]
            if prev is not None and bm.verts[cand].co.x > bm.verts[t2].co.x + 1e-4:
                break                                                          # 弧の後ろの端（次は鏡の面の方へ戻る）
            prev, cur = cur, cand
            chain.append(cur)
        return chain

    rib = walk_ribbon()
    gates.check("弧の外側の列: T_2 から後ろの端まで14頂点（13区間）", len(rib) == 14, len(rib))

    # --- 弧に行を足して 15 区間に揃える（Ctrl+R 相当）: 長い区間から2つ ---
    need = (len(s_wall) - 1) - (len(rib) - 1)
    for _ in range(need):
        lens = [(bm.verts[rib[k]].co - bm.verts[rib[k + 1]].co).length for k in range(len(rib) - 1)]
        k = int(np.argmax(lens))
        seed = bm.edges.get((bm.verts[rib[k]], bm.verts[rib[k + 1]]))
        ring = edge_ring(seed)
        gates.check("弧の行の追加: エッジリングは3辺（弧の3列を横切る）", len(ring) == 3, len(ring))
        n0 = len(bm.verts)
        bmesh.ops.subdivide_edges(bm, edges=ring, cuts=1, use_grid_fill=True)
        refresh()
        for i in range(n0, len(bm.verts)):
            p = bm.verts[i].co
            q = hs.project((p.x, p.y, p.z))
            bm.verts[i].co = Vector((0.0 if abs(p.x) < 1e-9 else q[0], q[1], q[2]))     # 頭の表面へ（正中線は X=0 のまま）
        adj = boundary_adj()
        rib = walk_ribbon()
    gates.check("弧の外側の列が壁と同じ15区間になった", len(rib) - 1 == len(s_wall) - 1 == 15, (len(rib) - 1, len(s_wall) - 1))
    r_end = rib[-1]
    n_seam_new = sum(1 for i in range(n_v, len(bm.verts)) if abs(bm.verts[i].co.x) < 1e-9)

    # --- 下の縁: 耳の下 → 弧の後ろの端（頭の表面に乗せた曲線）---
    p_ear, p_end = bm.verts[ear].co.copy(), bm.verts[r_end].co.copy()
    low_pts = []
    for s in range(1, N_LOW):
        t = s / N_LOW
        q = hs.project(tuple(p_end + (p_ear - p_end) * t))                    # r_end(t=0) → ear(t=1)
        low_pts.append(Vector(q))
    n_before_patch = len(bm.verts)
    low_new = [bm.verts.new(p) for p in low_pts]
    refresh()
    low = [r_end] + [v.index for v in low_new] + [ear]                         # i=0: 弧の端 … i=10: 耳の下

    # --- 格子: 4辺からのクーンズパッチを初期値にして、ラプラシアン緩和（隣の平均へ寄せ→頭の表面へ投影）---
    top, wall, left, lowr = s_top, s_wall, rib, low
    NI, NJ = len(top) - 1, len(left) - 1                                       # 10, 15
    posv = {i: np.array(bm.verts[i].co) for i in set(top + wall + left + lowr)}
    G = np.zeros((NI + 1, NJ + 1, 3))
    for j in range(NJ + 1):
        G[0, j], G[NI, j] = posv[left[j]], posv[wall[j]]
    for i in range(NI + 1):
        G[i, 0], G[i, NJ] = posv[top[i]], posv[lowr[i]]
    c00, c10, c01, c11 = G[0, 0], G[NI, 0], G[0, NJ], G[NI, NJ]
    for i in range(1, NI):
        for j in range(1, NJ):
            u, v = i / NI, j / NJ
            G[i, j] = ((1 - u) * G[0, j] + u * G[NI, j] + (1 - v) * G[i, 0] + v * G[i, NJ]
                       - ((1 - u) * (1 - v) * c00 + u * (1 - v) * c10 + (1 - u) * v * c01 + u * v * c11))
    inner = G[1:NI, 1:NJ].reshape(-1, 3)
    G[1:NI, 1:NJ] = hs.project_many(inner).reshape(NI - 1, NJ - 1, 3)
    RELAX_ITERS = 600
    for _ in range(RELAX_ITERS):
        avg = 0.25 * (G[:-2, 1:-1] + G[2:, 1:-1] + G[1:-1, :-2] + G[1:-1, 2:])
        avg[..., 0] = np.minimum(avg[..., 0], -0.021)                                   # 弧（X=-0.020）を越えて鏡の側へ入らない
        low_mask = avg[..., 2] < Z_TOP_ROW
        avg[..., 1] = np.where(low_mask, np.maximum(avg[..., 1], 0.0125), avg[..., 1])  # 額の上端より下では、壁（Y=0.0105）の前（既存の面）へ入らない
        G[1:NI, 1:NJ] = hs.project_many(avg.reshape(-1, 3)).reshape(NI - 1, NJ - 1, 3)
    gates.note("格子の内部頂点は、クーンズパッチの初期値から、隣の平均へ寄せて頭の表面へ投影する緩和を %d 回" % RELAX_ITERS)
    grid = {}
    for j in range(NJ + 1):
        grid[0, j], grid[NI, j] = left[j], wall[j]
    for i in range(NI + 1):
        grid[i, 0], grid[i, NJ] = top[i], lowr[i]
    interior = {}
    new_vs = []
    for i in range(1, NI):
        for j in range(1, NJ):
            nv = bm.verts.new(Vector(G[i, j]))
            new_vs.append((i, j, nv))
    refresh()
    for i, j, nv in new_vs:
        grid[i, j] = nv.index
    interior_obj = {(i, j): nv for i, j, nv in new_vs}
    pos = {k: bm.verts[k].co.copy() for k in grid.values()}
    n_e_before = len(bm.edges)
    new_faces = []
    for i in range(NI):
        for j in range(NJ):
            q = outward([grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]], pos)
            new_faces.append(bm.faces.new([bm.verts[k] for k in q]))
    new_set = set(new_faces)
    # T_12 の凹んだ角（外側270°）を4辺の格子は1枚で受けるため、折れた面（隣と巻き順が逆・法線が内向き）が出る。
    # 折れた面だけを削除し、小さな穴を残す（動画も、ここは手で F で埋めている）
    removed = []
    for _ in range(20):
        bad = set()
        bm.normal_update()
        for e in bm.edges:
            if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert:
                bad.update(f for f in e.link_faces if f in new_set)
        for f in new_set:
            if newell([v.co for v in f.verts]).dot(sum((v.co for v in f.verts), Vector()) / len(f.verts) - HEAD_CENTER) <= 0:
                bad.add(f)
        if not bad:
            break
        removed += [tuple(round(c, 3) for c in f.calc_center_median()) for f in bad]
        bmesh.ops.delete(bm, geom=list(bad), context="FACES_ONLY")
        new_set -= bad
    nv_before_del = len(bm.verts)
    loose_e = [e for e in bm.edges if not e.link_faces and e.index >= n_e_before]
    if loose_e:
        bmesh.ops.delete(bm, geom=loose_e, context="EDGES")
    loose_v = [v for v in bm.verts if not v.link_edges]
    if loose_v:
        bmesh.ops.delete(bm, geom=loose_v, context="VERTS")
    bm.verts.index_update()
    n_isolated = nv_before_del - len(bm.verts)                          # 面の削除で使われなくなった頂点（辺の削除で消えたものを含む）
    n_removed = len(removed)
    interior = {k: v.index for k, v in interior_obj.items() if v.is_valid}
    low = [r_end] + [v.index for v in low_new if v.is_valid] + [ear]
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    n_new_v, n_new_f = len(mesh.vertices) - n_v, len(mesh.polygons) - n_f
    exp_v = 3 * need + (N_LOW - 1) + (NI - 1) * (NJ - 1) - n_isolated
    exp_f = 2 * need + NI * NJ - n_removed
    moved = [i for i in range(n_v) if (mesh.vertices[i].co - before[i]).length > 1e-9]
    gates.check("既存の頂点は動いていない", not moved, moved[:10])
    gates.note("T_12 の凹んだ角のまわりで、折れた面 %d 枚を削除（小さな穴を残す）。位置(X,Y,Z): %s" % (n_removed, removed))
    gates.check("新しい頂点 %d（弧の行%d×3 + 下の縁%d + 内部%d − 使われなくなった頂点%d）・面 %d（弧の行 + 格子%d − 削除%d）" % (
        exp_v, need, N_LOW - 1, (NI - 1) * (NJ - 1), n_isolated, exp_f, NI * NJ, n_removed),
        n_new_v == exp_v and n_new_f == exp_f and all(len(p.vertices) == 4 for p in mesh.polygons), (n_new_v, n_new_f))
    gates.check("鏡の面（X=0）の新しい頂点は、弧に足した行の %d 個だけ" % need,
                sum(1 for i in range(n_v, len(mesh.vertices)) if mesh.vertices[i].co.x == 0.0) == need, n_seam_new)
    gates.check("X>0 の頂点を作っていない", all(mesh.vertices[i].co.x <= 1e-9 for i in range(n_v, len(mesh.vertices))))
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # --- 頭の表面への一致 ---
    devs = []
    for (i, j), vid in interior.items():
        p = mesh.vertices[vid].co
        devs.append(abs(hs.g((p.x, p.y, p.z))))
    gates.check("格子の内部頂点%d個が、測定した頭の外形（表面）に乗っている（|g|<0.005）" % len(devs), max(devs) < 0.005, f"最大 {max(devs):.4f}")
    low_g = [abs(hs.g(tuple(mesh.vertices[i].co))) for i in low[1:-1]]
    gates.check("下の縁の新しい頂点9個が、頭の外形に乗っている", max(low_g) < 0.005, f"最大 {max(low_g):.4f}")
    top_z = max(mesh.vertices[v].co.z for v in interior.values())
    gates.check("格子の最高点が、下絵の頭頂（Z=%.3f）を超えない" % ((C.ROW0 - 104) * C.K), top_z <= (C.ROW0 - 104) * C.K + 0.002, f"{top_z:.3f}")

    # --- Mirror 後（Subsurf 前のケージ）---
    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点・面の数が「片側×2 − 鏡の面の共有」に一致",
                (Vn, Fn) == (505 + 2 * n_new_v - n_seam_new, 440 + 2 * n_new_f), (Vn, En, Fn, n_new_v, n_new_f))
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs)) == len(pairs) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()))
    bad_out = [p.index for p in ev.polygons if p.normal.dot(p.center - HEAD_CENTER) <= 0]
    gates.check("Mirror 後: 全面の法線が頭の外側を向いている", not bad_out, bad_out[:10])
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    adj2 = {}
    for e, d in share.items():
        if len(d) == 1:
            adj2.setdefault(e[0], []).append(e[1])
            adj2.setdefault(e[1], []).append(e[0])
    seen2, loops = set(), []
    for s in adj2:
        if s in seen2:
            continue
        stack, comp = [s], 0
        while stack:
            x = stack.pop()
            if x in seen2:
                continue
            seen2.add(x)
            comp += 1
            stack += adj2[x]
        loops.append(comp)
    base_loops = sorted([13, 13, 16, 36])
    rest = list(sorted(loops))
    for l in base_loops:
        if l in rest:
            rest.remove(l)
    gates.check("Mirror 後: 境界のループは、目の穴2(13頂点)・口の穴(16)・首の穴(36) に、T_12 まわりの穴（左右対称の組）を足したもの",
                all(l in loops for l in base_loops) and len(rest) % 2 == 0 and (len(rest) == 0) == (n_removed == 0), sorted(loops))
    gates.check("Mirror 後: オイラー数 = -2 - (T_12 まわりの穴の数 %d)" % len(rest), Vn - En + Fn == -2 - len(rest), Vn - En + Fn)
    gates.note("T_12 まわりに残る穴（Mirror 後の各ループの頂点数）: %s。手で F を貼って埋める（動画 20:01 の「ここの1頂点選んで F」）" % rest)
    gates.note("残る穴（首・顎の下）の境界: %d 頂点（次の S09c で顎の下のラインと後ろのラインを繋ぐ）" % max(loops))

    # --- 四角形の歪み（格子の150枚）---
    pts_new = [[mesh.vertices[i].co for i in p.vertices] for p in list(mesh.polygons)[n_f + 2 * need:]]
    n_grid_faces = len(pts_new)
    lo = min(ang_range(p)[0] for p in pts_new)
    hi = max(ang_range(p)[1] for p in pts_new)
    bad = sum(1 for p in pts_new if ang_range(p)[0] < 25 or ang_range(p)[1] > 155)
    gates.check("格子の四角形%d枚: 退化した面なし（内角が 2°〜178° の範囲。折れた面は削除済み）" % len(pts_new), lo >= 2 and hi <= 178, f"最小{lo:.0f}° 最大{hi:.0f}°")
    gates.note("内角が 25°〜155° の範囲外の四角形: %d / %d 枚（T_12 の角と壁ぎわに集中。手直しの対象）" % (bad, len(pts_new)))

    for ang, tag, crop, zoom in [(90, "side", (60, 60, 900, 760), 1)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s09b_{tag}_overlay.png", crop=crop, zoom=zoom)
    overlay.write_wire_top(ev, C.OUT / "s09b_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    overlay.write_wire_angle(ev, 135, C.OUT / "s09b_back135_wire.png", zoom=1, crop=(112, 112, 912, 912))
    gates.check("レビュー画像3枚（側面・真上・左後ろ）を出力", all((C.OUT / f).exists() for f in ("s09b_side_overlay.png", "s09b_top_wire.png", "s09b_back135_wire.png")))
    sub.show_viewport = old_show

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s09b_gen.blend"), compress=False)
    gates.finish()


main()
