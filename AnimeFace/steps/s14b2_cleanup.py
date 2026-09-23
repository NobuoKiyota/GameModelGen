"""S14b2: face_s14b_human.blend の後始末（人間が作った房3つ＋主まつ毛の編集の、機械的な不具合だけを直す）。

背景（face_s14b_human.blend を検分して分かったこと）:
  - 人間は、自動生成した房（リング9の1つ）を主まつ毛（`Eyelash`）から削除し、動画の方法（Shift+D→押し出し→S→Ctrl+R→くるん→F→クリース）で、
    別オブジェクトの房を3つ作った（`Eyelash.001/.002/.003`。各12頂点、Mirror(Object=Face)+Subdivision(レベル1)）
  - 主まつ毛には、削除の後始末で、浮いた四角形1枚（頂点88-91・面のない孤立ではなく、他と繋がっていない単独の四角形）が残っていた
  - `Eyelash.002` は、先端のふた（4頂点の面）が1枚欠けていて、開いた穴になっていた
  - `Eyelash.001` は、2枚の面（中間→先端の帯）が自分自身と交差していた（ねじれた帯。頂点の位置は動かさず、ここでは直さない。見た目に気になれば、report にある頂点を動かして直す）
  - 3つとも、根元（1リング分の帯＋ふた）は、主まつ毛・顔の面と重なる（想定通り。埋め込み）。それより先（見える部分）で重なっているのは、この交差だけ

やること（頂点の位置は変えない。機械的な不具合だけ）:
  1. 主まつ毛の、浮いた四角形（頂点88-91・面1枚）を削除する
  2. `Eyelash.002` の先端に、ふた（4頂点の面）を1枚足す

入力: out/face_s14b_human.blend   出力: out/face_s14b2_gen.blend, out/s14b2_report.json
実行: blender --background --factory-startup --python steps/s14b2_cleanup.py
"""
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s14b2"
gates = C.Gates(STEP)


def rd(v):
    return tuple(round(float(c) * 1000, 1) for c in v)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s14b_human.blend"))
    for o in bpy.data.objects:
        if o.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    face = bpy.data.objects["Face"]
    eye = bpy.data.objects["Eye"]
    main_lash = bpy.data.objects["Eyelash"]
    tufts = [bpy.data.objects[n] for n in ("Eyelash.001", "Eyelash.002", "Eyelash.003")]
    gates.check("入力: Eyelash・房3つが揃っている", all(o is not None for o in [main_lash] + tufts))

    # ---- 1) 主まつ毛の浮いた四角形を削除
    me = main_lash.data
    n_v0, n_f0 = len(me.vertices), len(me.polygons)
    kept_before = {i: v.co.copy() for i, v in enumerate(me.vertices) if i < 88}
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    stray_v = [v for v in bm.verts if v.index >= 84 and all(len(f.verts) == 4 for f in v.link_faces) and len(v.link_faces) <= 1]
    stray_faces = {f for v in stray_v for f in v.link_faces}
    gates.check("主まつ毛: 浮いた四角形が1枚見つかった（頂点4・面1）", len(stray_v) == 4 and len(stray_faces) == 1, f"頂点{len(stray_v)} 面{len(stray_faces)}")
    other_users = [v for v in stray_v if any(f not in stray_faces for f in v.link_faces)]
    gates.check("その4頂点は、他の面に使われていない（安全に削除できる）", not other_users, [v.index for v in other_users])
    bmesh.ops.delete(bm, geom=list(stray_faces), context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in stray_v if v.is_valid], context="VERTS")
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.to_mesh(me)
    bm.free()
    me.update()
    gates.check("主まつ毛: 頂点92→88・面85→84（浮いた四角形を消した分だけ減った）",
                len(me.vertices) == 88 and len(me.polygons) == 84, f"V={len(me.vertices)} F={len(me.polygons)}")
    gates.check("主まつ毛: 残った頂点（0〜87）の位置は変えていない",
                all((me.vertices[i].co - kept_before[i]).length < 1e-9 for i in range(88)))

    # ---- 2) Eyelash.002 の先端のふたを足す
    t2 = bpy.data.objects["Eyelash.002"]
    m2 = t2.data
    bm2 = bmesh.new()
    bm2.from_mesh(m2)
    bm2.verts.ensure_lookup_table()
    bm2.edges.ensure_lookup_table()
    bm2.faces.ensure_lookup_table()
    be = [e for e in bm2.edges if len(e.link_faces) == 1]
    gates.check("Eyelash.002: 開いた端は1つ（4辺）", len(be) == 4, len(be))
    ring = []
    cur = be[0].verts[0]
    prev = None
    for _ in range(4):
        ring.append(cur)
        nxt = [e for e in cur.link_edges if e in be and e is not prev]
        if not nxt:
            break
        prev = nxt[0]
        cur = prev.other_vert(cur)
    gates.check("Eyelash.002: 開いた端の輪を4頂点でたどれた", len(ring) == 4, [v.index for v in ring])
    # 向き: 隣の面（bridge の最後の面）と同じ側を向くように
    ref_face = list(ring[0].link_faces)[0]
    newf = bm2.faces.new(ring)
    bm2.normal_update()
    if newf.normal.dot(ref_face.normal) < 0:
        bmesh.ops.reverse_faces(bm2, faces=[newf])
    bm2.faces.ensure_lookup_table()
    bm2.to_mesh(m2)
    bm2.free()
    m2.update()
    gates.check("Eyelash.002: 先端のふたを1枚足した（面9→10）", len(m2.polygons) == 10, len(m2.polygons))
    bm2c = bmesh.new()
    bm2c.from_mesh(m2)
    gates.check("Eyelash.002: 全ての辺が2枚の面（閉じた形になった）", all(len(e.link_faces) == 2 for e in bm2c.edges))
    bm2c.free()

    # ---- 全体の確認（頂点の位置は変えていない前提の再確認・交差の再集計）
    fverts = [tuple(v.co) for v in face.data.vertices]
    bvh_face = BVHTree.FromPolygons(fverts, [list(p.vertices) for p in face.data.polygons])
    everts = [tuple(v.co) for v in eye.data.vertices]
    bvh_eye = BVHTree.FromPolygons(everts, [list(p.vertices) for p in eye.data.polygons])
    mverts = [tuple(v.co) for v in main_lash.data.vertices]
    bvh_main = BVHTree.FromPolygons(mverts, [list(p.vertices) for p in main_lash.data.polygons])

    # 自己交差は、房（12頂点の小さい管）だけで見る（主まつ毛は84面ある曲がった管で、
    # BVHTree.overlap が離れた面どうしも「近接」で誤検出することを、s14c_gen の既知良品で確認済みなので対象外にする）
    summary = []
    for o in [main_lash] + tufts:
        md = o.data
        bmv = bmesh.new()
        bmv.from_mesh(md)
        bmv.normal_update()
        be2 = sum(1 for e in bmv.edges if len(e.link_faces) == 1)
        nm2 = sum(1 for e in bmv.edges if len(e.link_faces) > 2)
        self_hit = None
        hf = None
        if o is not main_lash:
            verts_w = [tuple(o.matrix_world @ v.co) for v in bmv.verts]
            polys = [[v.index for v in f.verts] for f in bmv.faces]
            bl = BVHTree.FromPolygons(verts_w, polys)
            self_hit = len([1 for x, y in bl.overlap(bl) if x < y and not (set(polys[x]) & set(polys[y]))])
            hf = len(bl.overlap(bvh_face))
        summary.append((o.name, len(bmv.verts), len(bmv.faces), be2, nm2, self_hit, hf))
        bmv.free()
    gates.note("最終確認（オブジェクト名, 頂点, 面, 開いた辺, 非多様体の辺, 自己交差, 顔との交差）", summary)
    gates.check("主まつ毛・房3つとも、開いた辺・非多様体がない（Eyelash.002 の先端を含め、全て閉じている）",
                all(row[3] == 0 and row[4] == 0 for row in summary), [(r[0], r[3], r[4]) for r in summary])
    remaining_self = [r for r in summary if r[5] is not None and r[5] > 0]
    gates.note("要確認: 自分自身と交差している房（頂点の位置はそのまま。気になれば手直しを）", remaining_self)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s14b2_gen.blend"), compress=False)
    gates.finish()


main()
