"""S07b: 額の面（顔のマスクの延長。動画 14:14〜15:00）。

字幕との対応:
  14:14〜14:27「顎の方から延長させて、ちょっとずつ顔のマスクを作っていく。押し出しして」
      → 下辺の境界（鼻根の線 N0→t1→t2→17 → 目の外輪の上側 → 目尻の頂点12 → 壁の上端）を、額の上端まで4段で押し出す
  14:34〜14:41「この1頂点選択して F …ここを選んで F」 → 各段を四角面で貼る
  14:41〜15:00「1番上のおでこのラインは真上から見てなだらかなカーブに」 → 上端のラインを頭の断面の楕円に乗せる（円弧）
  ※ 15:03〜 の Subsurf 追加は S08。

上端の高さ: Z=+0.19（案B。頭の断面が球に近く、この高さで球面の傾きが約40°。17:56 の後頭部への押し出しの起点）
形: 下辺の12頂点（N0 が X=0、壁の上端が最も外側）と、同じ数の上端の頂点を、縦の列で結ぶ（11列×4段 = 四角面44枚）。
    上端の頂点は、各列の横位置の割合 f=|X|/0.194 から、断面の楕円 X=-a·sinθ, Y=-b·cosθ（θ=asin f）に置く。
    壁の上端の列だけは Y=+0.0105（耳の前縁、S07 と同じ）を保つ。
    中間の段は、下辺から楕円への補間（段ごとの重み w=0.6, 0.9, 1, 1。目の面が凹んでいる分を、眉のあたりで受ける）。
    楕円の半径 a(Z), b(Z) は、正面の輪郭の半幅と側面の前の輪郭を行ごとに測ったもの。

入力: out/face_s07_human.blend   出力: out/face_s07b_gen.blend, out/s07b_report.json, out/s07b_*_overlay.png
実行: blender --background --factory-startup --python steps/s07b_forehead.py
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

STEP = "s07b"
gates = C.Gates(STEP)

NOSE_ROOT, WALL_TOP = 40, 119                             # 鼻根 N0（X=0）、壁の上端（S07 で押し出した目尻の頂点）
Z_TOP = 0.19                                              # 額の上端の高さ（案B）
ROWS = 4
WEIGHTS = [0.6, 0.9, 1.0, 1.0]
X_WALL = 0.194                                            # 壁の X（= |X(119)|）。列の横位置の割合の基準
HEAD_CENTER = Vector((0.0, 0.0, -0.03))


def ang_range(pts):
    lo, hi = 180.0, 0.0
    for k in range(4):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % 4]
        v1, v2 = (a - b).normalized(), (c - b).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, v1.dot(v2)))))
        lo, hi = min(lo, ang), max(hi, ang)
    return lo, hi


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


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s07_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)
    gates.check("入力: 134頂点・面106・全面四角形・Mirror のみ",
                (n_v, n_f) == (134, 106) and all(len(p.vertices) == 4 for p in mesh.polygons) and [m.type for m in obj.modifiers] == ["MIRROR"], (n_v, n_f))

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # --- 下辺の境界をたどる（N0 → 上辺 → 目の外輪の上側 → 目尻の頂点12 → 壁の上端）---
    adj = {}
    for e in bm.edges:
        if len(e.link_faces) == 1:
            a, b = (v.index for v in e.verts)
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    z0 = bm.verts[NOSE_ROOT].co.z
    cur = min(adj[NOSE_ROOT], key=lambda i: abs(bm.verts[i].co.z - z0))    # 正中線を下る辺ではなく、上辺（同じ高さ）へ
    chain, seen = [NOSE_ROOT], {NOSE_ROOT}
    while True:
        chain.append(cur)
        seen.add(cur)
        if cur == WALL_TOP:
            break
        nxt = [i for i in adj[cur] if i not in seen]
        if not nxt:
            break
        cur = nxt[0]
    gates.check("下辺: 鼻根 N0 から壁の上端119まで、境界の辺で12頂点", chain[0] == NOSE_ROOT and chain[-1] == WALL_TOP and len(chain) == 12,
                (len(chain), chain))
    xs = [bm.verts[i].co.x for i in chain]
    gates.check("下辺: N0 は X=0、以降は X の絶対値が単調に増える（壁の上端が最も外側）",
                xs[0] == 0.0 and all(abs(a) < abs(b) + 1e-9 for a, b in zip(xs, xs[1:])), [round(x, 3) for x in xs])
    N = len(chain)

    # --- 頭の断面（測定）---
    table = M.head_ellipse_table()
    y_wall = bm.verts[WALL_TOP].co.y

    def ellipse_pt(theta, z):
        a, b = M.head_ellipse_at(table, z)
        return Vector((-a * math.sin(theta), -b * math.cos(theta), z)), a, b

    f = [min(abs(x) / X_WALL, 0.999) for x in xs]
    theta = [math.asin(v) for v in f]
    b_top = M.head_ellipse_at(table, Z_TOP)[1]
    theta[-1] = math.pi / 2 + math.asin(y_wall / b_top)          # 壁の上端の列は、Y=+0.0105（耳の前縁）を保つ楕円上の点

    # --- 押し出し（4段）---
    rows_pos = []                                                # rows_pos[j-1][i]
    for j in range(1, ROWS + 1):
        w = WEIGHTS[j - 1]
        row = []
        for i, vid in enumerate(chain):
            base = bm.verts[vid].co
            z = base.z + (Z_TOP - base.z) * j / ROWS
            e, a, b = ellipse_pt(theta[i], z)
            if i == N - 1:                                        # 壁の上端の列: Y を保つ
                p = Vector(((1 - w) * base.x + w * e.x, y_wall, z))
            elif i == 0:                                          # 正中線: X=0
                p = Vector((0.0, (1 - w) * base.y + w * e.y, z))
            else:
                p = Vector(((1 - w) * base.x + w * e.x, (1 - w) * base.y + w * e.y, z))
            row.append(p)
        rows_pos.append(row)
    new_v = [[bm.verts.new(p) for p in row] for row in rows_pos]
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    new_idx = [[v.index for v in row] for row in new_v]
    pos = {i: bm.verts[i].co.copy() for i in chain}
    for row in new_idx:
        for i in row:
            pos[i] = bm.verts[i].co.copy()
    levels = [chain] + new_idx
    for j in range(ROWS):
        for i in range(N - 1):
            q = outward([levels[j][i], levels[j][i + 1], levels[j + 1][i + 1], levels[j + 1][i]], pos)
            bm.faces.new([bm.verts[k] for k in q])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    n_new_v, n_new_f = len(mesh.vertices) - n_v, len(mesh.polygons) - n_f
    gates.check("既存の頂点は動いていない", all((a.co - b).length == 0 for a, b in zip(list(mesh.vertices)[:n_v], before)))
    gates.check("新しい頂点 %d（4段×12）・四角面 %d（4段×11列）" % (ROWS * N, ROWS * (N - 1)),
                n_new_v == ROWS * N and n_new_f == ROWS * (N - 1) and all(len(p.vertices) == 4 for p in mesh.polygons), (n_new_v, n_new_f))
    at0 = [i for i in range(n_v, len(mesh.vertices)) if mesh.vertices[i].co.x == 0.0]
    gates.check("X=0 の新しい頂点は各段の正中線の4つだけ", len(at0) == ROWS, at0)
    gates.check("モディファイアは Mirror のみ（Apply なし）", [m.type for m in obj.modifiers] == ["MIRROR"])

    # --- 上端のライン（おでこのライン）---
    top = [mesh.vertices[i].co for i in new_idx[-1]]
    gates.check("上端のライン: 全頂点が Z=%.2f" % Z_TOP, all(abs(p.z - Z_TOP) < 1e-6 for p in top))
    dev = []
    for k, p in enumerate(top[:-1]):
        a, b = M.head_ellipse_at(table, Z_TOP)
        dev.append(abs((p.x / a) ** 2 + (p.y / b) ** 2 - 1))
    gates.check("上端のライン: 頭の断面の楕円（測定した半幅・前後）に乗っている（|(X/a)²+(Y/b)²−1|<0.005）", max(dev) < 0.005, round(max(dev), 5))
    ys = [p.y for p in top]
    gates.check("上端のライン: 正中線が最も前で、横へ行くほど単調に後ろへ（なだらかな円弧）", all(a < b for a, b in zip(ys, ys[1:])), [round(y, 3) for y in ys])
    slopes = [(top[k + 1].y - top[k].y) / (top[k + 1].x - top[k].x) for k in range(N - 1)]
    gates.check("上端のライン: 傾きの絶対値が正中線から横へ向かって単調に増える（正中線で傾き0）",
                abs(slopes[0]) < abs(slopes[-1]) and all(abs(a) <= abs(b) + 1e-6 for a, b in zip(slopes, slopes[1:])), [round(s, 2) for s in slopes])

    # --- 下絵との一致（画像から再測定）---
    v_top = int(round(C.ROW0 - Z_TOP / C.K))
    sil = M.side_silhouette(200, 300)
    u_center = C.project(top[0], 90)[0]
    gates.check("上端の正中線: 側面の顔の前の輪郭（再測定）に ±2px", abs(u_center - sil[v_top]) <= 2, f"{u_center:.1f} vs {sil[v_top]}")
    fpx = M._px("front")
    dark = (fpx[..., 0] < 75) & (fpx[..., 1] < 75) & (fpx[..., 2] < 75)
    uu, vv = C.project(top[-1], 0)
    ok = dark[int(round(vv)) - 2:int(round(vv)) + 3, int(round(uu)) - 5:int(round(uu)) + 6].any()
    gates.check("上端の外側の頂点: 正面の頭の輪郭線（黒線）の上にある（±5px）", ok, (round(uu, 1), round(vv, 1)))

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後: 頂点346・辺648・面300", (Vn, En, Fn) == (346, 648, 300), (Vn, En, Fn))
    gates.check("Mirror 後: 辺の重複なし", len(set(pairs)) == len(pairs), f"E={En}")
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 3枚以上の面が共有する辺がない", max(len(v) for v in share.values()) <= 2, max(len(v) for v in share.values()))
    bad_wind = [e for e, d in share.items() if len(d) == 2 and d[0] != (d[1][1], d[1][0])]
    gates.check("Mirror 後: 隣り合う面の巻き順が一貫している", not bad_wind, len(bad_wind))
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
    gates.check("Mirror 後: 境界のループは4つ（目の穴2・口の穴1・外周1）", len(loops) == 4, sorted(loops))
    gates.check("Mirror 後: オイラー数 -2", Vn - En + Fn == -2, f"V={Vn} E={En} F={Fn}")

    # --- 四角形の歪み（今回貼った44枚）---
    new_pts = [[mesh.vertices[i].co for i in p.vertices] for p in list(mesh.polygons)[n_f:]]
    lo = min(ang_range(p)[0] for p in new_pts)
    hi = max(ang_range(p)[1] for p in new_pts)
    bad = [(round(sum((p[k] for k in range(4)), Vector()).x / 4, 3), round(sum((p[k] for k in range(4)), Vector()).z / 4, 3),
            round(ang_range(p)[0]), round(ang_range(p)[1])) for p in new_pts if ang_range(p)[0] < 25 or ang_range(p)[1] > 155]
    gates.check("今回貼った四角形%d枚: 内角が 25°〜155° の範囲" % len(new_pts), lo >= 25 and hi <= 155, f"最小{lo:.0f}° 最大{hi:.0f}°")
    if bad:
        gates.note("歪んだ面 (X, Z, 最小°, 最大°): %s" % bad)

    for ang, tag, crop, zoom in [(0, "front", (100, 180, 560, 600), 2), (90, "side", (600, 180, 900, 600), 2), (45, "a45", (150, 130, 850, 700), 1)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s07b_{tag}_overlay.png", crop=crop, zoom=zoom)
    overlay.write_wire_top(ev, C.OUT / "s07b_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    gates.check("レビュー画像4枚（正面・側面・45°・真上）を出力",
                all((C.OUT / f"s07b_{t}.png").exists() for t in ("front_overlay", "side_overlay", "a45_overlay", "top_wire")))

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s07b_gen.blend"), compress=False)
    gates.finish()


main()
