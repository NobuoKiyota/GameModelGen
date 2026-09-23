"""S10: 首の円柱を作って頭につなぐ（動画 22:15〜、28:44 の頭のガイドの削除）。

字幕との対応:
  22:15〜22:53 シリンダー追加（頂点12・キャップなし）、小さくして頭の下へ移動      → 12頂点・蓋なしの円柱（半分＝X≤0 の7頂点×輪）を作る
  22:53〜23:20 編集モードで根元のループを E+S で押し出し・拡大して、頭の穴に合わせる → 根元の輪 = S09c の首の穴の輪（12頂点）そのもの。円柱は、根元の輪から下へ伸ばす
  23:20〜23:35 オブジェクトモードでオートミラーをオン、頭と円柱を Ctrl+J で1つに      → 別メッシュを作る代わりに、同じメッシュに追加し、根元の輪の頂点を共有する（結合＋距離0でマージと同じ）
  23:35〜26:26 後頭部・顎の前を F でつなぎ、穴を埋める                                 → S09c で済み（穴の輪を首の輪へ絞った）
  26:29〜27:23 Subsurf の確認・顎のライン・全体の膨らまし                               → 面の形には手を付けない（顎の輪郭の差を数値で報告するのみ。膨らましは好みなので人間の判断）
  27:26〜28:41 透視投影・焦点距離80                                                       → メッシュには関係しない（見るときの設定）
  28:44        頭の形の参考（HeadGuide）を削除                                           → 削除する

設計:
  - 輪の高さと前後の位置は、側面の下絵の首の前後の線（行 830〜958）から測る。行 958 は首の切り口（行 ≈960）の直前。左右の幅は下絵にない（正面図に首がない）ので、円と仮定（半径 = 前後の幅の半分）
  - 輪は5本（行 830, 862, 894, 926, 958。水平）。根元の輪（傾いている）から最初の輪へ、6枚の四角形の帯（半分）
  - 下端は蓋をしない（動画のまま。体に続く）

入力: out/face_s09c_human.blend   出力: out/face_s10_gen.blend, out/s10_report.json, out/s10_*.png
実行: blender --background --factory-startup --python steps/s10_neck.py
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

STEP = "s10"
gates = C.Gates(STEP)

HEAD_CENTER = Vector((0.0, 0.0, 0.086))
RING_ROWS = [830, 862, 894, 926, 958]         # 側面下絵の行（水平の輪の高さ）
N_HALF = 7                                    # 半分の頂点（0°,30°,…,180°）


def rd(v):
    return tuple(round(float(c), 4) for c in v)


def neck_root_chain(bm):
    """根元の輪: 首の穴（半分で7頂点）。前の正中線の頂点から後ろの正中線の頂点まで。"""
    cand = [e for e in bm.edges if len(e.link_faces) == 1
            and e.verts[0].co.z < -0.14 and e.verts[1].co.z < -0.14
            and abs(e.verts[0].co.x) <= 0.07 and abs(e.verts[1].co.x) <= 0.07
            and -0.07 < e.verts[0].co.y < 0.08 and -0.07 < e.verts[1].co.y < 0.08
            and not (abs(e.verts[0].co.x) < 1e-6 and abs(e.verts[1].co.x) < 1e-6)]
    axis = [v for e in cand for v in e.verts if abs(v.co.x) < 1e-6]
    start = min(axis, key=lambda v: v.co.y)
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
    return chain, len(cand)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09c_gen.blend"))
    gen_pos = [v.co.copy() for v in bpy.data.objects["Face"].data.vertices]
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09c_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])
    same = max((a.co - b).length for a, b in zip(mesh.vertices, gen_pos)) if len(gen_pos) == len(mesh.vertices) else None
    gates.note("入力（人間版）と S09c の生成版の、頂点の位置の最大の差", "頂点数が違う" if same is None else f"{same * 1000:.4f}mm")

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    n_v0, n_e0, n_f0 = len(bm.verts), len(bm.edges), len(bm.faces)
    sizes = {}
    for f in bm.faces:
        sizes[len(f.verts)] = sizes.get(len(f.verts), 0) + 1
    gates.check("入力: 四角形387・五角形6・頂点428", sizes == {4: 387, 5: 6} and n_v0 == 428, f"{sizes} V={n_v0}")

    root, n_cand = neck_root_chain(bm)
    gates.check("根元の輪: 6辺・7頂点、両端は X=0（首の穴の半分）", len(root) == N_HALF and n_cand == 6 and abs(root[0].co.x) < 1e-6 and abs(root[-1].co.x) < 1e-6,
                f"{len(root)}頂点 {rd(root[0].co)} → {rd(root[-1].co)}")

    # ---- 首の前後の線（側面の下絵）
    edges = M.side_neck_edges(RING_ROWS)
    edges_bg = M.side_neck_edges_bg(RING_ROWS)
    gates.check("首の前後の線が全ての行で測れた", all(r in edges and r in edges_bg for r in RING_ROWS), sorted(edges))
    ring_defs = []
    for r in RING_ROWS:
        ub, uf = edges[r]
        yb, yf = -(ub - C.COL0) * C.K, -(uf - C.COL0) * C.K       # 側面: Y = -(u - 512)K（顔が -Y）
        # 側面は、u が大きいほど顔の前（-Y）: uf（前の線）→ Y が小さい
        y_front, y_back = min(yb, yf), max(yb, yf)
        ring_defs.append(dict(row=r, z=(C.ROW0 - r) * C.K, y_front=y_front, y_back=y_back,
                              yc=(y_front + y_back) / 2, rad=(y_back - y_front) / 2))
    for d in ring_defs:
        gates.note(f"輪 行{d['row']}", f"Z={d['z']:.4f} Y={d['y_front']:.4f}〜{d['y_back']:.4f}（前後の幅 {(d['y_back'] - d['y_front']) * 1000:.0f}mm・半径 {d['rad'] * 1000:.1f}mm）")
    r_root = (root[-1].co.y - root[0].co.y) / 2
    gates.note("根元の輪（S09c の首の穴）", f"前 Y={root[0].co.y:.4f}・後ろ Y={root[-1].co.y:.4f}・半径 {r_root * 1000:.1f}mm・Z {root[0].co.z:.3f}〜{root[-1].co.z:.3f}")

    # ---- 頂点
    phis = [j * math.pi / 6 for j in range(N_HALF)]
    rings = []
    for d in ring_defs:
        vs = []
        for phi in phis:
            x = 0.0 if phi in (0.0, math.pi) else -d["rad"] * math.sin(phi)
            y = d["yc"] - d["rad"] * math.cos(phi)
            vs.append(bm.verts.new((x, y, d["z"])))
        rings.append(vs)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    # ---- 面（向き: 根元の輪の辺を使っている既存の面と逆向きに通る）
    fwd = any(lp.link_loop_next.vert is root[1] for lp in root[0].link_loops)

    def quad(a, b, c, d):
        vs = [a, b, c, d]
        if fwd:
            vs = vs[::-1]
        return bm.faces.new(vs)

    new_faces = []
    layers = [root] + rings
    for k in range(len(layers) - 1):
        up, dn = layers[k], layers[k + 1]
        for j in range(N_HALF - 1):
            new_faces.append(quad(up[j], up[j + 1], dn[j + 1], dn[j]))
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    gates.check("追加: 頂点 %d（輪5×7）・面 %d（6枚×5段）" % (len(bm.verts) - n_v0, len(new_faces)),
                len(bm.verts) - n_v0 == 35 and len(new_faces) == 30, f"V={len(bm.verts)} F={len(bm.faces)}")
    over = [e for e in bm.edges if len(e.link_faces) > 2]
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("巻き順が一貫・3枚以上が共有する辺なし", not over and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()))
    # 円柱の面は、円柱の軸から見て外向き
    bm.normal_update()
    bad_axis = []
    for f in new_faces:
        c = f.calc_center_median()
        axis_pt = Vector((0.0, c.y * 0 + sum(d["yc"] for d in ring_defs) / len(ring_defs), c.z))
        if f.normal.dot(c - axis_pt) <= 0:
            bad_axis.append(f.index)
    gates.check("円柱の面は、軸から見て外向き", not bad_axis, bad_axis[:6])
    old_pos = [(v.index, v.co.copy()) for v in bm.verts if v.index < n_v0]
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    gates.check("頭側の頂点は動かしていない", all((mesh.vertices[i].co - p).length < 1e-9 for i, p in old_pos))
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
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後: 辺の重複なし・非多様体なし・巻き順が一貫",
                len(set(pairs)) == len(pairs) and max(len(v) for v in share.values()) <= 2
                and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()), f"V={Vn} E={En} F={Fn}")
    axis_y = sum(d["yc"] for d in ring_defs) / len(ring_defs)
    bad_out = []
    n_poly = len(mesh.polygons)
    gates.check("Mirror 後の面の並びは、元の面＋鏡の面（円柱の面の番号を特定できる）", Fn == 2 * n_poly, f"F={Fn} 元の面={n_poly}")
    neck_ids = set(range(n_f0, n_poly)) | set(range(n_poly + n_f0, 2 * n_poly))
    for p in ev.polygons:
        c = p.center
        if p.index in neck_ids:                                    # 円柱の面は、軸から見て外向き
            ok = p.normal.dot(c - Vector((0.0, axis_y, c.z))) > 0
        else:
            ok = p.normal.dot(c - HEAD_CENTER) > 0
        if not ok:
            bad_out.append((p.index, rd(c)))
    gates.check("Mirror 後: 全面の法線が外側を向いている（頭は頭の中心から、円柱は軸から）", not bad_out, bad_out[:8])
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)

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
    gates.check("穴（境界の輪）は、目2つ（13辺）・口（16辺）・首の下端（12辺）の4つだけ", lens == [12, 13, 13, 16], lens)
    neck_loop = [c for c in loops if len(c) == 12]
    if neck_loop:
        zs = {round(v.co.z, 5) for e in neck_loop[0] for v in e.verts}
        gates.check("首の下端の輪は、水平（同じ高さ）で、12頂点", len({v.index for e in neck_loop[0] for v in e.verts}) == 12 and len(zs) == 1, sorted(zs))
    bmev.free()

    # ---- 首の前後の線を、メッシュから測り直して、下絵（別の測り方）と比べる
    zmap = {}
    for v in ev.vertices:
        if abs(v.co.x) < 1e-9 and v.co.z <= ring_defs[0]["z"] + 1e-6:
            zmap.setdefault(round(v.co.z, 5), []).append(v.co.y)
    diffs = []
    for d in ring_defs:
        ys = zmap.get(round(d["z"], 5))
        if not ys:
            continue
        u_of = lambda y: C.COL0 - y / C.K                        # 側面: u = 512 - Y/K
        u_front, u_back = u_of(min(ys)), u_of(max(ys))            # 前（Y 小）→ u 大
        bg_b, bg_f = edges_bg[d["row"]]
        diffs.append((d["row"], round(u_back - bg_b, 1), round(u_front - bg_f, 1)))
    gates.check("メッシュの首の前後の線が、下絵（背景色との差で測り直し）と 3px 以内", all(abs(a) <= 3 and abs(b) <= 3 for _, a, b in diffs), diffs)
    front_ring_uv = [C.project(Vector((0, min(zmap[k]), k)), 90) for k in sorted(zmap)]
    gates.note("投影した輪の位置の確認（側面の重ね画像で目視）", f"{len(front_ring_uv)}輪")

    # ---- 顎の輪郭の差（動画 26:29〜: Subsurf 後の顎のライン。数値の確認のみ）
    sub.show_viewport = True
    bpy.context.view_layer.update()
    evs = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    sil = M.side_silhouette(v0=560, v1=830)
    pts2 = [C.project(v.co, 90) for v in evs.vertices]
    diffs_j = []
    for r in range(560, 830, 20):
        if r not in sil:
            continue
        us = []
        for e in evs.edges:
            (u0, v0), (u1, v1) = pts2[e.vertices[0]], pts2[e.vertices[1]]
            if (v0 - r) * (v1 - r) <= 0 and v0 != v1:
                us.append(u0 + (u1 - u0) * (r - v0) / (v1 - v0))
        if us:
            diffs_j.append((r, round(max(us) - sil[r], 1)))
    gates.note("Subsurf 後のワイヤーの側面の最前（顔の輪郭）と、側面の下絵の輪郭の差（行, px、+は輪郭より前）", diffs_j)
    sub.show_viewport = old_show

    # ---- 頭の形の参考（HeadGuide）を削除（動画 28:44）
    guide = bpy.data.objects.get("HeadGuide")
    if guide is not None:
        gm_ = guide.data
        bpy.data.objects.remove(guide, do_unlink=True)
        if gm_.users == 0:
            bpy.data.meshes.remove(gm_)
    gates.check("頭の形の参考（HeadGuide）を削除した", bpy.data.objects.get("HeadGuide") is None)

    overlay.write_overlay(ev, 90, C.OUT / "s10_side_overlay.png", crop=(262, 620, 762, 1000), zoom=2)
    overlay.write_wire_angle(ev, 90, C.OUT / "s10_side_wire.png", zoom=1, crop=(112, 112, 912, 1000))
    overlay.write_wire_angle(ev, 45, C.OUT / "s10_a45_wire.png", zoom=1, crop=(112, 112, 912, 1000))
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s10_gen.blend"), compress=False)
    gates.finish()


main()
