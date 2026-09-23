"""S09b3: S09b2 の人間補正版から、ごみ（誤って残った面・孤立した頂点）だけを取り除く。頂点の位置は動かさない。

背景（face_s09b2_human.blend を face_s09b2_gen.blend と比べて分かったこと）:
  - 人間版は、三角形2枚を五角形6枚（＋壁ぎわに三角形1枚）にした（額の上端に頂点6・壁ぎわに頂点1を追加、頂点3つを移動）。
  - ただし壁ぎわの三角形 (145,383,144) は、両側の辺がすでに四角形2枚ずつで閉じているので、余分な面（法線は内向き）。
    この面のせいで、辺2本が3枚の面を共有している（非多様体）。
  - 同じ位置の頂点が2つ（398=144, 399=383）、面のない孤立した頂点＋辺として残っている。
この面・辺・頂点だけを消す（面を消すと、三角形の3辺目だけが残るので、それも消す）。

入力: out/face_s09b2_human.blend   出力: out/face_s09b3_gen.blend, out/s09b3_report.json, out/s09b3_*.png
実行: blender --background --factory-startup --python steps/s09b3_cleanup.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402
import overlay  # noqa: E402

STEP = "s09b3"
gates = C.Gates(STEP)
HEAD_CENTER = Vector((0.0, 0.0, -0.03))


def rd(v):
    return tuple(round(c, 4) for c in v)


def health(bm):
    """辺の面の数・巻き順・孤立を数える。"""
    over = [e for e in bm.edges if len(e.link_faces) > 2]
    wire = [e for e in bm.edges if len(e.link_faces) == 0]
    loose = [v for v in bm.verts if not v.link_edges]
    off_axis_boundary = [e for e in bm.edges if len(e.link_faces) == 1 and not (abs(e.verts[0].co.x) < 1e-6 and abs(e.verts[1].co.x) < 1e-6)]
    inward = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - HEAD_CENTER) <= 0]
    return over, wire, loose, off_axis_boundary, inward


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s09b2_human.blend"))
    obj = bpy.data.objects["Face"]
    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    mesh = obj.data
    gates.check("入力: モディファイアは Mirror → Subsurf", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])
    before = [v.co.copy() for v in mesh.vertices]
    n_v0, n_e0, n_f0 = len(mesh.vertices), len(mesh.edges), len(mesh.polygons)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    over, wire, loose, _, inward = health(bm)
    gates.note("入力の状態", f"V={n_v0} E={n_e0} F={n_f0} / 3枚以上が共有する辺 {len(over)} / 面のない辺 {len(wire)} / 孤立頂点 {len(loose)} / 内向きの面 {len(inward)}")

    # 消す面: 「3枚以上が共有する辺を持つ」かつ「法線が内向き」の三角形だけ（それ以外は触らない）
    stray = [f for f in bm.faces if len(f.verts) == 3 and f.normal.dot(f.calc_center_median() - HEAD_CENTER) <= 0
             and any(len(e.link_faces) > 2 for e in f.edges)]
    gates.check("消す面は三角形1枚（内向き・辺が3枚以上の面に共有されている）", len(stray) == 1, [(f.index, rd(f.calc_center_median())) for f in stray])
    stray_centers = [rd(f.calc_center_median()) for f in stray]
    bmesh.ops.delete(bm, geom=stray, context="FACES_ONLY")
    bm.edges.ensure_lookup_table()
    wires = [e for e in bm.edges if len(e.link_faces) == 0]
    gates.note("面を消した後に残った、面のない辺", [(e.verts[0].index, e.verts[1].index, rd(e.verts[0].co), rd(e.verts[1].co)) for e in wires])
    bmesh.ops.delete(bm, geom=wires, context="EDGES")     # 孤立した頂点も一緒に消える（398・399 も、この辺でつながっていた）
    bm.verts.ensure_lookup_table()
    left_loose = [v for v in bm.verts if not v.link_edges]
    if left_loose:
        bmesh.ops.delete(bm, geom=left_loose, context="VERTS")
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    over2, wire2, loose2, off_axis2, inward2 = health(bm)
    gates.check("消した後: 3枚以上が共有する辺・面のない辺・孤立頂点・内向きの面がない",
                not over2 and not wire2 and not loose2 and not inward2, f"{len(over2)} / {len(wire2)} / {len(loose2)} / {len(inward2)}")
    sizes = {}
    for f in bm.faces:
        sizes[len(f.verts)] = sizes.get(len(f.verts), 0) + 1
    gates.check("面の内訳: 三角形0・五角形6・四角形357（ほかの面は触っていない）", sizes == {4: 357, 5: 6}, sizes)
    gates.check("頂点2・辺2・面1だけ減った（404→402、767→765、364→363）",
                (len(bm.verts), len(bm.edges), len(bm.faces)) == (402, 765, 363), f"V={len(bm.verts)} E={len(bm.edges)} F={len(bm.faces)}")
    # 巻き順
    share = {}
    for f in bm.faces:
        vs = list(f.verts)
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            share.setdefault(frozenset((a.index, b.index)), []).append((a.index, b.index))
    gates.check("巻き順が一貫している", all(len(d) < 2 or d[0] == (d[1][1], d[1][0]) for d in share.values()))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # 位置は動かしていない（残った頂点は、元の頂点のどれかと同じ位置）
    kept = {tuple(round(c, 6) for c in p) for p in before}
    gates.check("頂点の位置は変えていない（残った頂点は、すべて元の頂点と同じ位置）", all(tuple(round(c, 6) for c in v.co) in kept for v in mesh.vertices))
    gates.check("X ≤ 0（Mirror の片側）で、正中線の頂点は X=0", max(v.co.x for v in mesh.vertices) <= 1e-9)
    gates.check("モディファイアは Mirror → Subsurf のまま", [m.type for m in obj.modifiers] == ["MIRROR", "SUBSURF"])

    # Mirror 後の検証
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
    gates.note("Mirror 後の面の内訳", f"V={Vn} E={En} F={Fn}（人間版は 773/1501/728、s09b2_gen は 757/1483/722）")

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
    gates.note("面の内角: 最小 %.0f°・最大 %.0f°、25°〜155° の外は %d / %d 枚（五角形は 180° の頂点を含むため、そのぶん外に数える）" % (lo, hi, bad, len(ranges)))
    gates.check("退化した面がない（内角が 2°〜178°。五角形の直線上の頂点 180° は除く）",
                all(r[0] >= 2 for r in ranges), f"最小{lo:.0f}°")

    # レビュー画像: 消した面のまわり（側面 90°）と、額の上端の五角形（真上と側面）
    overlay.write_wire_angle(ev, 90, C.OUT / "s09b3_side_wire.png", zoom=1, crop=(112, 112, 912, 912))
    overlay.write_wire_angle(ev, 90, C.OUT / "s09b3_side_wall_zoom.png", zoom=4, crop=(400, 340, 600, 540))
    overlay.write_wire_angle(ev, 90, C.OUT / "s09b3_side_forehead_zoom.png", zoom=4, crop=(560, 130, 760, 330))
    overlay.write_wire_top(ev, C.OUT / "s09b3_top_wire.png", zoom=1, crop=(112, 112, 912, 912))
    gates.note("消した面の位置", stray_centers)
    sub.show_viewport = old_show
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s09b3_gen.blend"), compress=False)
    gates.finish()


main()
