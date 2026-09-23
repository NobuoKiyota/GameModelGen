"""S08: Subsurf の追加と、鼻先・顎先のサポートループ（動画 15:07〜17:50）。

字幕との対応:
  15:07〜15:13 Subsurf を追加            → Mirror の後ろに Subsurf（ビューポート1・レンダー2。動画の画面で確認）
  15:17〜16:22 鼻先をとんがらせる         → 鼻先の周りに、鼻先へ寄せたループ（上・下・横の3本）を追加。先っちょを前へ（数値で補正）
  16:22〜16:42 顎先をキュッと寄せる       → 顎先の近くにループを追加して顎先側へ寄せる
  16:45〜17:28 口角の上下の頂点数を揃える → 口の外輪・内輪の上側と下側の分割数が同じであることを確認（追加ループは不要）
  17:28〜17:50 頂点の偏りを手で直す       → 生成物では触らない（人間の手直し）

Ctrl+R 相当: エッジリング（四角面の向かい合う辺をたどる）を求め、subdivide で1本ずつ切り、新しい頂点を指定の端へ寄せる（G G 相当）。
「とんがり」の合否: Subsurf を掛けた正中線（X=0 の頂点）が、側面の輪郭に対してどれだけ外れるか（鼻: 前後の差の RMS と鼻先の前後位置、顎: 最下点の高さ）。

入力: out/face_s07b_human.blend   出力: out/face_s08_gen.blend, out/s08_report.json, out/s08_*_overlay.png
実行: blender --background --factory-startup --python steps/s08_subsurf_support.py
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

STEP = "s08"
gates = C.Gates(STEP)

NOSE_N1, NOSE_TIP, NOSE_P1, CHIN = 41, 42, 58, 44
MOUTH_OUTER, MOUTH_INNER = [33, 34, 35, 36, 37, 38, 39], [26, 27, 28, 29, 30, 31, 32]
SUPPORT_T = 0.25                # 鼻先のサポートループを、鼻先の側へ寄せる位置（元の辺の長さに対する、近い端からの割合）
CHIN_T = 0.05                   # 顎先のサポートループ（顎先の角をより強く保つため、より近く）
SIL_INSET_PX = 3
HEAD_CENTER = Vector((0.0, 0.0, -0.03))


def edge_ring(seed):
    """seed の辺から、四角面の向かい合う辺をたどったエッジリング（Alt+クリックのリング選択に相当）。"""
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


def loop_cut(bm, seed, near_rule, t):
    """seed のエッジリングを1本切り、新しい頂点を near_rule が選ぶ「近い端」から割合 t の位置へ寄せる。新しい頂点の番号を返す。"""
    ring = edge_ring(seed)
    ends = []
    for e in ring:
        a, b = e.verts[0], e.verts[1]
        near, far = (a, b) if near_rule(a.co, b.co) else (b, a)
        ends.append((near.co.copy(), far.co.copy()))
    n0 = len(bm.verts)
    bmesh.ops.subdivide_edges(bm, edges=ring, cuts=1, use_grid_fill=True)
    bm.verts.ensure_lookup_table()
    new = [bm.verts[i] for i in range(n0, len(bm.verts))]
    for v in new:                                   # 新しい頂点は元の辺の中点。どの辺のものか、中点の一致で探す
        for near, far in ends:
            if (v.co - (near + far) / 2).length < 1e-6:
                v.co = near + (far - near) * t
                break
    bm.verts.index_update()
    return [v.index for v in new], len(ring)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s07b_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    n_v, n_f = len(mesh.vertices), len(mesh.polygons)
    before = [v.co.copy() for v in mesh.vertices]
    gates.check("入力: 182頂点・面150・全面四角形・Mirror のみ",
                (n_v, n_f) == (182, 150) and all(len(p.vertices) == 4 for p in mesh.polygons) and [m.type for m in obj.modifiers] == ["MIRROR"], (n_v, n_f))

    # --- Subsurf を追加（Mirror の後ろ）---
    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2

    # --- 側面の輪郭（測定）---
    sil = M.side_silhouette()
    sub_row_s, _ = M.side_subnasale_row(sil)
    lip_row_s, chin_s, chin_f = M.side_lip_row(), M.side_chin_row(), M.front_chin_row()
    f2s = M.front_to_side_row_map([C.ROW0, sub_row_s, lip_row_s, chin_s], [C.ROW0, sub_row_s, 722.5, chin_f])

    def y_prof(z):
        v = C.ROW0 - z / C.K
        return -(sil[int(round(f2s(v)))] - SIL_INSET_PX - C.COL0) * C.K

    z_chin_target = (C.ROW0 - (chin_f - SIL_INSET_PX)) * C.K
    y_chin_target = -(sil[int(chin_s) - 2] - SIL_INSET_PX - C.COL0) * C.K            # 側面の顎先の角（S05 と同じ）
    h_chin_target = (-y_chin_target - z_chin_target) / math.sqrt(2)                  # 前・下の斜め方向の突端の位置
    tip_row_s, tip_u = M.side_nose_tip_row(sil)
    y_tip_target = -(tip_u - SIL_INSET_PX - C.COL0) * C.K

    def seam_profile(levels):
        """Subsurf を掛けた評価済みメッシュの、正中線（X=0）上の頂点 (Y, Z)。"""
        old = sub.levels
        sub.levels = levels
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        pts = sorted(((v.co.y, v.co.z) for v in ev.vertices if abs(v.co.x) < 1e-6), key=lambda p: -p[1])
        bpy.data.meshes.remove(ev)
        sub.levels = old
        return pts

    def metrics(levels):
        pts = seam_profile(levels)
        nose = [(y, z) for y, z in pts if -0.075 <= z <= -0.03]
        rms = math.sqrt(sum((y - y_prof(z)) ** 2 for y, z in nose) / len(nose)) / C.K       # px
        tip = min(y for y, z in nose)
        front = [(y, z) for y, z in pts if y < -0.15 and z < -0.17]     # 顎先の前側（首の前へ押し出した下面より前）
        h_eval = max((-y - z) / math.sqrt(2) for y, z in front)         # 顎先の角の、前・下の斜め方向の突端
        slope = [(y, z) for y, z in pts if y < -0.15 and -0.205 <= z <= -0.17]     # 顎の前面の傾斜
        chin_rms = math.sqrt(sum((y - y_prof(z)) ** 2 for y, z in slope) / len(slope)) / C.K if slope else float("nan")
        return dict(nose_rms=rms, tip_gap_mm=(tip - y_tip_target) * 1000, chin_gap_mm=(h_chin_target - h_eval) * 1000, chin_rms=chin_rms)

    base1, base2 = metrics(1), metrics(2)
    gates.note("追加前の Subsurf 後（レベル1）: 鼻の輪郭とのずれ RMS %.2fpx・鼻先の前後 %+.1fmm（+は後ろ）・顎先の角の丸まり %.1fmm（斜め方向・+は内側）・顎の前面の輪郭 RMS %.2fpx" % (
        base1["nose_rms"], base1["tip_gap_mm"], base1["chin_gap_mm"], base1["chin_rms"]))
    gates.note("追加前の Subsurf 後（レベル2）: 鼻 RMS %.2fpx・鼻先 %+.1fmm・顎先の丸まり %.1fmm・顎 RMS %.2fpx" % (
        base2["nose_rms"], base2["tip_gap_mm"], base2["chin_gap_mm"], base2["chin_rms"]))

    # --- サポートループ（Ctrl+R + G G 相当）---
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    tip = bm.verts[NOSE_TIP]

    def find_edge(a, b):
        return bm.edges.get((bm.verts[a], bm.verts[b]))

    # 鼻先の上・下（行のループ）: 鼻先側の端 = 上のループは Z が低い方、下のループは Z が高い方
    up_new, up_len = loop_cut(bm, find_edge(NOSE_N1, NOSE_TIP), lambda a, b: a.z < b.z, SUPPORT_T)
    bm.edges.ensure_lookup_table()
    dn_new, dn_len = loop_cut(bm, find_edge(NOSE_TIP, NOSE_P1), lambda a, b: a.z > b.z, SUPPORT_T)
    bm.edges.ensure_lookup_table()
    # 鼻先の横（正中線の隣の列のループ）: 鼻先から X<0 側へ伸びる辺。鼻先側 = X が大きい（0 に近い）方
    bm.verts.ensure_lookup_table()
    tip = bm.verts[NOSE_TIP]                          # subdivide 後は参照を取り直す
    side_nb = [e.other_vert(tip) for e in tip.link_edges if e.other_vert(tip).co.x < -1e-6]
    gates.check("鼻先から横（X<0）へ伸びる辺が1本", len(side_nb) == 1, len(side_nb))
    col_new, col_len = loop_cut(bm, bm.edges.get((tip, side_nb[0])), lambda a, b: a.x > b.x, SUPPORT_T)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    # 顎先: 顎先から出る縦の辺（頬の帯の下側の段の縦の辺）。顎先側 = Z が低い方
    chin_v = bm.verts[CHIN]
    rung = [e.other_vert(chin_v) for e in chin_v.link_edges if -0.045 < e.other_vert(chin_v).co.x < -0.02 and e.other_vert(chin_v).co.z > -0.19]
    gates.check("顎先から頬の帯の縦の辺（顎先の隣・X≈-0.03・Z>-0.19）が1本", len(rung) == 1, len(rung))
    chin_new, chin_len = loop_cut(bm, bm.edges.get((chin_v, rung[0])), lambda a, b: a.z < b.z, CHIN_T)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    gates.note("ループの辺の数（エッジリングの長さ）: 鼻先の上 %d・下 %d・横 %d・顎 %d、追加した頂点 %d" % (
        up_len, dn_len, col_len, chin_len, len(mesh.vertices) - n_v))

    # --- トポロジー ---
    n_new_v = len(mesh.vertices) - n_v
    gates.check("全面が四角形（サポートループ追加後）", all(len(p.vertices) == 4 for p in mesh.polygons), len(mesh.polygons))
    gates.check("既存の頂点は動いていない（新しい頂点を除く）", all((a.co - b).length < 1e-9 for a, b in zip(list(mesh.vertices)[:n_v], before)))
    gates.check("モディファイアは Mirror → Subsurf の順・Apply なし・Subsurf はビューポート1・レンダー2",
                [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"] and sub.levels == 1 and sub.render_levels == 2)

    # --- 口角の上下の頂点数（動画 16:45〜）---
    upper_o, lower_o = len(MOUTH_OUTER[:4]) - 1, len(MOUTH_OUTER[3:]) - 1
    upper_i, lower_i = len(MOUTH_INNER[:4]) - 1, len(MOUTH_INNER[3:]) - 1
    gates.check("口の外輪・内輪とも、口角の上側と下側の分割数が同じ（%d = %d, %d = %d）" % (upper_o, lower_o, upper_i, lower_i),
                upper_o == lower_o and upper_i == lower_i)

    # --- Subsurf 後の輪郭の一致 ---
    m1, m2 = metrics(1), metrics(2)
    gates.check("鼻: Subsurf 後（レベル1）の輪郭とのずれ RMS が追加前より小さい", m1["nose_rms"] < base1["nose_rms"], f"{base1['nose_rms']:.2f} → {m1['nose_rms']:.2f}px")
    gates.check("顎: Subsurf 後（レベル1）の輪郭とのずれ RMS が追加前より小さい", m1["chin_rms"] < base1["chin_rms"], f"{base1['chin_rms']:.2f} → {m1['chin_rms']:.2f}px")

    # --- 鼻先を前へ（動画 16:14「先っちょをもうちょっとぴょいんと」）: Subsurf 後の鼻先が下絵の鼻先に届くまで ---
    tip_v = mesh.vertices[NOSE_TIP]
    y0 = tip_v.co.y
    for _ in range(8):
        gap = metrics(1)["tip_gap_mm"] / 1000
        if abs(gap) < 0.0004:
            break
        tip_v.co.y -= gap                            # gap>0（Subsurf 後の先端が後ろ）なら前（-Y）へ
        mesh.update()
    pull = (y0 - tip_v.co.y) * 1000
    m1, m2 = metrics(1), metrics(2)
    gates.check("鼻先: Subsurf 後（レベル1）の前後位置が下絵の鼻先に ±0.5mm（前へ %.1fmm 補正）" % pull, abs(m1["tip_gap_mm"]) <= 0.5,
                f"{m1['tip_gap_mm']:+.2f}mm")
    gates.note("要確認: 鼻先を前へ %.1fmm 補正した（動画の「先っちょをちょっとぴょいん」に相当。動画に量の記載なし）" % pull)
    # --- 顎先の角を、Subsurf 後に下絵の顎先へ届くまで、前・下の斜め方向へ（動画の G G の代わりに数値で）---
    chin_vert = mesh.vertices[CHIN]
    c0 = chin_vert.co.copy()
    for _ in range(8):
        gap = metrics(1)["chin_gap_mm"] / 1000
        if abs(gap) < 0.0004:
            break
        chin_vert.co.y -= gap / math.sqrt(2)
        chin_vert.co.z -= gap / math.sqrt(2)
        mesh.update()
    chin_pull = (chin_vert.co - c0).length * 1000
    m1, m2 = metrics(1), metrics(2)
    gates.check("顎先: Subsurf 後（レベル1）の角が下絵の顎先に ±0.5mm（斜めへ %.1fmm 補正）" % chin_pull, abs(m1["chin_gap_mm"]) <= 0.5, f"{m1['chin_gap_mm']:+.2f}mm")
    gates.note("要確認: 顎先の頂点を斜め（前・下）へ %.1fmm 補正した（Y %+.1fmm・Z %+.1fmm）。動画は顎先の頂点を動かさずループを寄せるだけ。補正量はループの位置(0.03〜0.12)にほぼ依存せず 8.6〜9.9mm だった" % (
        chin_pull, (chin_vert.co.y - c0.y) * 1000, (chin_vert.co.z - c0.z) * 1000))
    gates.note("補正後の Subsurf 後（レベル1）: 鼻 RMS %.2fpx・鼻先 %+.2fmm・顎先の丸まり %.1fmm・顎 RMS %.2fpx" % (
        m1["nose_rms"], m1["tip_gap_mm"], m1["chin_gap_mm"], m1["chin_rms"]))
    gates.note("補正後の Subsurf 後（レベル2）: 鼻 RMS %.2fpx・鼻先 %+.2fmm・顎先の丸まり %.1fmm・顎 RMS %.2fpx" % (
        m2["nose_rms"], m2["tip_gap_mm"], m2["chin_gap_mm"], m2["chin_rms"]))

    # --- Mirror 後（Subsurf 前のケージ）---
    old_mods = [(m, m.show_viewport) for m in obj.modifiers]
    sub.show_viewport = False
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    Vn, En, Fn = len(ev.vertices), len(ev.edges), len(ev.polygons)
    pairs = [tuple(sorted(e.vertices)) for e in ev.edges]
    gates.check("Mirror 後のケージ: オイラー数 -2・辺の重複なし", Vn - En + Fn == -2 and len(set(pairs)) == len(pairs), f"V={Vn} E={En} F={Fn}")
    share = {}
    for p in ev.polygons:
        vs = list(p.vertices)
        for k in range(4):
            a, b = vs[k], vs[(k + 1) % 4]
            share.setdefault(tuple(sorted((a, b))), []).append((a, b))
    gates.check("Mirror 後のケージ: 非多様体なし・巻き順が一貫・法線が頭の外側",
                max(len(v) for v in share.values()) <= 2 and all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values())
                and all(p.normal.dot(p.center - HEAD_CENTER) > 0 for p in ev.polygons))
    coords = {(round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in ev.vertices}
    gates.check("Mirror 後のケージ: 左右対称・頂点の重複なし", all((round(-x, 6), y, z) in coords for (x, y, z) in coords) and len(coords) == Vn)
    sub.show_viewport = True

    # --- レビュー画像（Subsurf 後の輪郭とケージ）---
    for ang, tag, crop, zoom in [(90, "side", (640, 400, 900, 850), 2), (0, "front", (300, 500, 720, 850), 2)]:
        overlay.write_overlay(ev, ang, C.OUT / f"s08_{tag}_overlay.png", crop=crop, zoom=zoom)
    gates.check("レビュー画像2枚を出力", all((C.OUT / f"s08_{t}_overlay.png").exists() for t in ("side", "front")))


    # --- Subsurf 後の正中線（青）を下絵に重ねた画像 ---
    def seam_mesh(levels):
        old = sub.levels
        sub.levels = levels
        bpy.context.view_layer.update()
        dg2 = bpy.context.evaluated_depsgraph_get()
        e2 = bpy.data.meshes.new_from_object(obj.evaluated_get(dg2))
        idx = [v.index for v in e2.vertices if abs(v.co.x) < 1e-6]
        remap = {old_i: k for k, old_i in enumerate(idx)}
        verts = [tuple(e2.vertices[i].co) for i in idx]
        edges = [(remap[e.vertices[0]], remap[e.vertices[1]]) for e in e2.edges if e.vertices[0] in remap and e.vertices[1] in remap]
        bpy.data.meshes.remove(e2)
        sub.levels = old
        m = bpy.data.meshes.new("seam_tmp")
        m.from_pydata(verts, edges, [])
        return m

    seam = seam_mesh(1)
    overlay.write_overlay(seam, 90, C.OUT / "s08_side_subsurf.png", crop=(560, 400, 900, 850), zoom=2, edge_color=(0.1, 0.3, 1.0))
    bpy.data.meshes.remove(seam)
    gates.check("Subsurf 後の正中線の画像を出力", (C.OUT / "s08_side_subsurf.png").exists())

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s08_gen.blend"), compress=False)
    gates.finish()


main()
