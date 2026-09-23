"""S09a: 頭のガイドと、頭の上から後ろへの弧（動画 17:56〜19:36）。

字幕との対応:
  18:01〜18:41 ガイドを置く（キューブ＋Subsurf2 を小さくして上へ。「ちょうどいい位置」）
      → 頭の断面（下絵から測った半幅・前後）に当てはめた楕円体のガイド。動画の丸いキューブの代わりに、下絵に合わせた形にした（表示用の目安。弧は測定した輪郭に沿わせる）
  18:43〜19:06 表示をワイヤーにする（Optimal Display を外す）                → ガイドの表示をワイヤーに、Subsurf の Optimal Display を外す
  19:08〜19:36「一番前の3頂点を選択して E で押し出し、R で回して、E … この辺までで」
      → 額の上端の一番前の3頂点を、ガイドの断面（X 一定の面と楕円体の交線）に沿って、頭の上から後ろへ押し出す（帯状の弧）
  ※ 19:41〜 の側面の穴埋め・膨らまし・顎の下との接続は S09b/S09c。

入力: out/face_s08_human.blend   出力: out/face_s09a_gen.blend, out/s09a_report.json, out/s09a_*_overlay.png
実行: blender --background --factory-startup --python steps/s09a_head_arc.py
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

STEP = "s09a"
gates = C.Gates(STEP)

Z_TOP_ROW = 0.19          # 額の上端（S07b）
Z_END = -0.03             # 弧の後ろの端（後頭部の下寄り。動画は「この辺まで」）
STEP_M = 0.055            # 弧の分割の長さ（目安）
N_COLS = 3                # 一番前の3頂点（動画 19:13）
HEAD_CENTER = Vector((0.0, 0.0, -0.03))


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


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s08_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    before = [v.co.copy() for v in mesh.vertices]
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)
    gates.check("入力: 230頂点・面194・全面四角形・Mirror→Subsurf",
                (n_v, n_f) == (230, 194) and all(len(p.vertices) == 4 for p in mesh.polygons)
                and [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"], (n_v, n_f))

    # --- ガイド: 頭の断面の測定から楕円体を当てはめる ---
    table = M.head_ellipse_table(v0=120, v1=470)
    a0, zc, c_ax = M.head_ellipsoid_fit(table)
    z_probe = [0.06 + 0.02 * k for k in range(0, 12)]
    resid = []
    for z in z_probe:
        a_m, b_m = M.head_ellipse_at(table, z)
        rho = a0 * math.sqrt(max(0.0, 1 - ((z - zc) / c_ax) ** 2))
        resid.append(max(abs(rho - a_m), abs(rho - b_m)))
    gates.check("ガイドの楕円体（a0=b0=%.3f, 中心 Z=%.3f, 縦の半径 %.3f）が、測定した頭の断面に ±4mm（Z=0.06〜0.28）" % (a0, zc, c_ax),
                max(resid) <= 0.004, f"最大 {max(resid) * 1000:.1f}mm")
    top_z = zc + c_ax
    tip_probe = -(M.side_silhouette(104, 110).get(106, 0) - C.COL0) * C.K
    gates.check("ガイドの頂点の高さが、下絵の頭頂（v=104 → Z=%.3f）に ±5mm" % ((C.ROW0 - 104) * C.K), abs(top_z - (C.ROW0 - 104) * C.K) <= 0.005, f"{top_z:.3f}")

    gm = bpy.data.meshes.new("HeadGuide")
    gb = bmesh.new()
    bmesh.ops.create_uvsphere(gb, u_segments=32, v_segments=16, radius=1.0)
    for v in gb.verts:
        v.co = Vector((v.co.x * a0, v.co.y * a0, v.co.z * c_ax + zc))
    gb.to_mesh(gm)
    gb.free()
    guide = bpy.data.objects.new("HeadGuide", gm)
    coll = bpy.data.collections.new("GUIDE")
    bpy.context.scene.collection.children.link(coll)
    coll.objects.link(guide)
    guide.display_type = "WIRE"                       # 動画 19:02「ワイヤーにしておきます」
    guide.hide_render = True
    guide.hide_select = True
    sub = [m for m in obj.modifiers if m.type == "SUBSURF"][0]
    sub.show_only_control_edges = False               # 動画 18:53「オプティマルディスプレイのチェックを外す」
    gates.check("ガイド: ワイヤー表示・レンダーに出さない・Optimal Display を外した",
                guide.display_type == "WIRE" and guide.hide_render and not sub.show_only_control_edges)

    # --- 額の上端の一番前の3頂点 ---
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    top = sorted([v for v in bm.verts if abs(v.co.z - Z_TOP_ROW) < 1e-6 and v.co.x <= 1e-9], key=lambda v: -v.co.x)
    gates.check("額の上端（Z=%.2f）の頂点が13個（S08 の縦のループで1つ増えた）" % Z_TOP_ROW, len(top) == 13, len(top))
    cols = top[:N_COLS]
    xs = [v.co.x for v in cols]
    gates.check("一番前の3頂点: 先頭が X=0（正中線）で、X の絶対値が増える順", xs[0] == 0.0 and abs(xs[1]) < abs(xs[2]),
                [round(x, 4) for x in xs])
    col_ids = [v.index for v in cols]

    # --- 弧: X 一定の面と頭の外形の交線に沿って、頭の上から後ろへ ---
    # 外形は測定した輪郭そのもの: 前側 Y=-Bf(Z)·√(1-(X/A(Z))²)、後ろ側 Y=+Bb(Z)·√(1-(X/A(Z))²)。
    # 断面の頂点は √ が0になる Z（A(Z)=|X|）で前と後ろが繋がる。ガイドの楕円体は近似（最大3mmのずれ・後頭部の下は外れる）なので使わない。
    outl = M.head_outlines()
    rows_o = sorted(outl)

    def OA(z):
        v = C.ROW0 - z / C.K
        return float(np.interp(v, rows_o, [outl[r][0] for r in rows_o]))

    def OBf(z):
        v = C.ROW0 - z / C.K
        return float(np.interp(v, rows_o, [outl[r][1] for r in rows_o]))

    def OBb(z):
        v = C.ROW0 - z / C.K
        return float(np.interp(v, rows_o, [outl[r][2] for r in rows_o]))

    def slice_path(x, z_start, z_end, n=1500):
        """X=x の面での交線 (Y,Z) の折れ線: z_start(前側) → 頂点 → z_end(後ろ側)。"""
        zs_top = [z for z in np.linspace(z_start, (C.ROW0 - 106) * C.K, n) if OA(z) >= abs(x)]
        z_apex = zs_top[-1]
        path = []
        for z in np.linspace(z_start, z_apex, n // 2):
            path.append((-OBf(z) * math.sqrt(max(0.0, 1 - (x / OA(z)) ** 2)), float(z)))
        for z in np.linspace(z_apex, z_end, n // 2):
            path.append((OBb(z) * math.sqrt(max(0.0, 1 - (x / max(OA(z), abs(x) + 1e-9)) ** 2)), float(z)))
        return np.array(path)

    def at_fraction(path, f):
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        cum = np.concatenate([[0], np.cumsum(seg)])
        t = cum[-1] * f
        return Vector((0, float(np.interp(t, cum, path[:, 0])), float(np.interp(t, cum, path[:, 1])))), float(cum[-1])

    paths = [slice_path(xs[i], cols[i].co.z, Z_END) for i in range(N_COLS)]
    L0 = at_fraction(paths[0], 1.0)[1]
    K = max(4, int(round(L0 / STEP_M)))
    gates.note("弧の長さ（正中線）%.3fm を %d 分割（1段 約%.0fmm）" % (L0, K, L0 / K * 1000))
    # 最初の段（実際の頂点）と輪郭の差を、後ろへ向かって3段で消す（頂点の飛びを避ける）
    p_first = [at_fraction(paths[i], 0.0)[0] for i in range(N_COLS)]
    off_y = [cols[i].co.y - p_first[i].y for i in range(N_COLS)]
    new_pos = []
    for k in range(1, K + 1):
        row = []
        for i in range(N_COLS):
            q, _ = at_fraction(paths[i], k / K)
            w = max(0.0, 1 - k / 3.0)
            row.append(Vector((0.0 if i == 0 else xs[i], q.y + off_y[i] * w, q.z)))
        new_pos.append(row)
    new_v = [[bm.verts.new(p) for p in row] for row in new_pos]
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    new_idx = [[v.index for v in row] for row in new_v]
    pos = {i: bm.verts[i].co.copy() for i in col_ids}
    for row in new_idx:
        for i in row:
            pos[i] = bm.verts[i].co.copy()
    levels = [col_ids] + new_idx
    for k in range(K):
        for i in range(N_COLS - 1):
            q = outward([levels[k][i], levels[k][i + 1], levels[k + 1][i + 1], levels[k + 1][i]], pos)
            bm.faces.new([bm.verts[j] for j in q])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    # --- ソースのトポロジー ---
    n_new_v, n_new_f = len(mesh.vertices) - n_v, len(mesh.polygons) - n_f
    gates.check("既存の頂点は動いていない", all((a.co - b).length == 0 for a, b in zip(list(mesh.vertices)[:n_v], before)))
    gates.check("新しい頂点 %d（%d段×3列）・四角面 %d（%d段×2列）" % (K * N_COLS, K, K * 2, K),
                n_new_v == K * N_COLS and n_new_f == K * 2 and all(len(p.vertices) == 4 for p in mesh.polygons), (n_new_v, n_new_f))
    at0 = [i for i in range(n_v, len(mesh.vertices)) if mesh.vertices[i].co.x == 0.0]
    gates.check("X=0 の新しい頂点は、各段の正中線の %d 個だけ" % K, len(at0) == K, len(at0))
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # --- 弧がガイド・下絵に乗っているか ---
    devs = []
    for row in new_idx:
        for vid in row:
            p = mesh.vertices[vid].co
            e = (p.x / a0) ** 2 + (p.y / a0) ** 2 + ((p.z - zc) / c_ax) ** 2
            devs.append(abs(math.sqrt(e) - 1) * a0)
    gates.note("弧の頂点とガイド（楕円体・近似）の距離: 平均 %.1fmm・最大 %.1fmm（前後の輪郭に沿わせたため、後頭部の下ほど離れる）" % (
        sum(devs) / len(devs) * 1000, max(devs) * 1000))
    center = [mesh.vertices[row[0]].co for row in new_idx]
    sp = M._px("side")
    dark_s = (sp[..., 0] < 75) & (sp[..., 1] < 75) & (sp[..., 2] < 75)

    def dist_to_outline(p, r=12):
        """側面の下絵で、点 p（側面の画素 (u,v)）から最も近い黒画素（頭の輪郭）までの距離 [px]。頭頂付近の輪郭がほぼ水平でも安定。"""
        u, v = C.project(p, 90)
        u0, v0 = int(round(u)), int(round(v))
        win = dark_s[v0 - r:v0 + r + 1, u0 - r:u0 + r + 1]
        vv, uu = np.where(win)
        if not len(vv):
            return float("inf")
        return float(np.min(np.hypot(uu - r + (u0 - u), vv - r + (v0 - v))))

    dists = [dist_to_outline(p) for p in center]
    gates.check("弧の正中線の全頂点が、側面の頭の輪郭（黒線）の上にある（最短距離 ≤ 1.5px）", max(dists) <= 1.5, [round(d, 1) for d in dists])
    zs = [p.z for p in center]
    zmax_i = zs.index(max(zs))
    gates.check("弧の正中線は、頭頂（最高点）を越えて後ろへ下がる（Z が増えてから減る）", 0 < zmax_i < len(zs) - 1 and zs[-1] < zs[zmax_i] - 0.1,
                f"最高点 Z={max(zs):.3f}（{zmax_i + 1}段目）、端 Z={zs[-1]:.3f}")
    widths = [(mesh.vertices[row[2]].co - mesh.vertices[row[0]].co).length for row in new_idx]
    gates.note("弧の帯の幅（1列目〜3列目の距離）: 最小 %.0fmm・最大 %.0fmm（頭頂に向かって細くなる分を含む）" % (min(widths) * 1000, max(widths) * 1000))

    # --- Mirror 後 ---
    dg = bpy.context.evaluated_depsgraph_get()
    old_show = sub.show_viewport
    sub.show_viewport = False
    bpy.context.view_layer.update()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後のケージ: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs)) == len(pairs) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    gates.check("Mirror 後のケージ: 全面の法線が頭の外側を向いている", all(p.normal.dot(p.center - HEAD_CENTER) > 0 for p in ev.polygons))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後のケージ: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    gates.check("Mirror 後のケージ: オイラー数（弧の追加で変化しない）= 元の -2", Vn - En + Fn == -2, f"{Vn - En + Fn}")
    new_pts = [[mesh.vertices[i].co for i in p.vertices] for p in list(mesh.polygons)[n_f:]]
    lo = min(ang_range(p)[0] for p in new_pts)
    hi = max(ang_range(p)[1] for p in new_pts)
    gates.check("今回貼った四角形%d枚: 内角が 25°〜155° の範囲" % len(new_pts), lo >= 25 and hi <= 155, f"最小{lo:.0f}° 最大{hi:.0f}°")

    for ang, tag, crop, zoom in [(90, "side", (100, 60, 900, 760), 1), (45, "a45", (100, 60, 900, 760), 1)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s09a_{tag}_overlay.png", crop=crop, zoom=zoom)
    overlay.write_wire_top(ev, C.OUT / "s09a_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    gates.check("レビュー画像3枚（側面・45°・真上）を出力", all((C.OUT / f).exists() for f in ("s09a_side_overlay.png", "s09a_a45_overlay.png", "s09a_top_wire.png")))
    sub.show_viewport = old_show

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s09a_gen.blend"), compress=False)
    gates.finish()


main()
