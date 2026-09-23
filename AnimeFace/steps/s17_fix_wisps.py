"""S17 手直し2: 細いまつ毛の房（`Eyelash.001`・`Eyelash.003`）が、顔・主まつ毛と交差している問題を修正
（ユーザー指摘: 画像でオレンジ色の枠、目尻寄りに黒い塊・不自然な多角形の透けが見える）。

原因調査（BVHTreeでワールド座標の重なりを確認）:
  - `Eyelash.001`: 全10面中9面が主まつ毛(`Eyelash`)と、10面中10面が顔(`Face`)と重なっている（根元が皮膚の中に埋まっている状態）
  - `Eyelash.002`: 重なりなし（問題なし）
  - `Eyelash.003`: 全10面中11面が主まつ毛と、6面が顔と重なっている
  - `Eyelash.003` のオブジェクトスケールが 1.6778 倍になっていた（経緯不明。房を拡大したため、余計に皮膚へ食い込んでいた）
  この重なりが、埋め込まれた面どうしのZファイティング・法線の乱れとして、黒い塊や色の透けに見えていたと考えられる

修正方針:
  - 各房のオブジェクト変換（位置・回転・拡大）をメッシュへ焼き込んでから単位行列に戻す（S15cで学んだ手順。座標比較を単純にするため）
  - 房の根元付近の顔の面法線（皮膚の外向き）方向へ房全体を押し出し、必要なら中心から縮小する候補を順に試し、
    顔・主まつ毛のどちらとも重ならなくなる最小の変更（押し出しを優先、それでも足りなければ縮小も併用）を採用する
  - 見た目の位置・向きはできるだけ保たず、根元だけをずらすと不自然なので、房全体を剛体的に動かす（形は変えない）

入力: out/face_s17_gen.blend   出力: out/face_s17_gen.blend（上書き）, out/s17fix2_report.json, out/s17fix2_render_*.png
実行: blender --background --factory-startup --python steps/s17_fix_wisps.py
"""
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17fix2"
gates = C.Gates(STEP)

WISPS = ["Eyelash.001", "Eyelash.002", "Eyelash.003"]


def bvh_world(obj):
    me = obj.data
    mw = obj.matrix_world
    return BVHTree.FromPolygons([tuple(mw @ v.co) for v in me.vertices], [list(p.vertices) for p in me.polygons])


def bake_transform(obj):
    mw = obj.matrix_world.copy()
    obj.data.transform(mw)
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)


def overlap_count(bvh_a, bvh_b):
    return len(bvh_a.overlap(bvh_b))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"))
    face = bpy.data.objects["Face"]
    lash = bpy.data.objects["Eyelash"]
    wisps = {n: bpy.data.objects[n] for n in WISPS}

    bvh_face0 = bvh_world(face)
    bvh_lash0 = bvh_world(lash)
    before = {}
    for n, o in wisps.items():
        bv = bvh_world(o)
        before[n] = (overlap_count(bv, bvh_face0), overlap_count(bv, bvh_lash0))
    gates.note("修正前: 各房と顔・主まつ毛の重なり面ペア数", before)
    gates.note("修正前: Eyelash.003 のオブジェクトスケール", tuple(round(c, 4) for c in wisps["Eyelash.003"].scale))

    fixed = {}
    for n, o in wisps.items():
        n_face, n_lash = before[n]
        if n_face == 0 and n_lash == 0:
            fixed[n] = "変更なし（重なりなし）"
            continue
        bake_transform(o)
        me = o.data
        pts0 = [v.co.copy() for v in me.vertices]
        centroid = sum(pts0, Vector()) / len(pts0)
        hit = face.closest_point_on_mesh(centroid)
        push_dir = hit[2] if hit[0] else Vector((0, 0, 1))       # 近傍の顔の面法線（皮膚の外向き）
        if push_dir.length < 1e-6:
            push_dir = Vector((0, 0, 1))
        push_dir.normalize()

        chosen = None
        for scale in (1.0, 0.9, 0.8, 0.7):
            for push_mm in (0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12):
                push = push_dir * (push_mm / 1000.0)
                newpts = [centroid + (p - centroid) * scale + push for p in pts0]
                bv = BVHTree.FromPolygons([tuple(p) for p in newpts], [list(p.vertices) for p in me.polygons])
                nf = overlap_count(bv, bvh_face0)
                nl = overlap_count(bv, bvh_lash0)
                if nf == 0 and nl == 0:
                    chosen = (scale, push_mm, newpts)
                    break
            if chosen:
                break
        if chosen is None:
            fixed[n] = "候補が見つからず変更なし（要人間確認）"
            gates.note(f"{n}: 交差を解消する候補が見つからなかった", True)
            continue
        scale, push_mm, newpts = chosen
        for v, p in zip(me.vertices, newpts):
            v.co = p
        me.update()
        fixed[n] = f"倍率{scale}・皮膚の外向きへ{push_mm}mm 押し出し"

    gates.note("修正内容", fixed)

    # ---- 検証: 全ての房が、顔・主まつ毛のどちらとも重ならない
    bvh_face1 = bvh_world(face)
    bvh_lash1 = bvh_world(lash)
    after = {}
    all_clear = True
    for n, o in wisps.items():
        bv = bvh_world(o)
        nf, nl = overlap_count(bv, bvh_face1), overlap_count(bv, bvh_lash1)
        after[n] = (nf, nl)
        if nf > 0 or nl > 0:
            all_clear = False
    gates.check("修正後: 全ての房が、顔・主まつ毛のどちらとも重ならない", all_clear, after)

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"), compress=False)

    # ---- レビュー用レンダリング
    scene = bpy.context.scene
    world = bpy.data.worlds.new("ReviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1.0)
    scene.world = world
    sun = bpy.data.lights.new("ReviewSun", type='SUN')
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("ReviewSun", sun)
    sun_obj.rotation_euler = (1.0, 0.0, 0.6)
    scene.collection.objects.link(sun_obj)
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    keep = {"Face", "Eye", "Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "s17fix2_render_front.png"), ("CAM_a45", "s17fix2_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
