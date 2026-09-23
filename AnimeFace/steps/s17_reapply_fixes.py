"""S17 手直しの再適用: S16のUV島分割修正（眼窩内側・口の中を別島に）に伴い、S17をS16からやり直した（=一度やり直すと、
その上に重ねていた手直しが失われるため）。すでにユーザーに確認・承認された3つの手直しを、新しいS17の上に再度適用する。

1. 眉のY方向オフセット -26.8mm（ユーザーが `face_s17_human.blend` で手直し、「埋没」解消）
2. 眼窩内側（白目）の目頭寄りの面を、白から柔らかい暖色へブレンド（「白目が目頭まで浸食している」指摘への対応）
3. 細いまつ毛の房（Eyelash.001/.003）を、顔・主まつ毛と重ならない位置まで押し出す（黒い塊・多角形の透けの解消）

入力: out/face_s17_gen.blend（S16やり直し後に作り直したS17）   出力: out/face_s17_gen.blend（上書き）
実行: blender --background --factory-startup --python steps/s17_reapply_fixes.py
"""
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17reapply"
gates = C.Gates(STEP)

W = H = 2048
EYE_WHITE = (0.96, 0.96, 0.97)
INNER_TONE = (0.92, 0.74, 0.70)
EYEBROW_Y_OFFSET = -0.026804964989423752
WISPS = ["Eyelash.001", "Eyelash.002", "Eyelash.003"]


def px_of(u, v):
    return u * (W - 1), (1 - v) * (H - 1)


def poly_px(obj, p):
    uv = obj.data.uv_layers.active.data
    return [px_of(*uv[li].uv) for li in range(p.loop_start, p.loop_start + p.loop_total)]


def fill_poly_mask(mask, pts):
    P = np.array(pts, dtype=float)
    y0 = int(max(P[:, 1].min(), 0))
    y1 = int(min(P[:, 1].max(), H - 1))
    for y in range(y0, y1 + 1):
        xs = []
        for k in range(len(P)):
            a, b = P[k], P[(k + 1) % len(P)]
            if (a[1] <= y + 0.5 < b[1]) or (b[1] <= y + 0.5 < a[1]):
                xs.append(a[0] + (y + 0.5 - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            x0i, x1i = int(max(xs[j], 0)), int(min(xs[j + 1], W - 1))
            mask[y, x0i:x1i + 1] = True


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


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"))
    face = bpy.data.objects["Face"]
    me = face.data
    eyebrow = bpy.data.objects["Eyebrow"]
    lash = bpy.data.objects["Eyelash"]
    wisps = {n: bpy.data.objects[n] for n in WISPS}

    # ---- 1) 眉のオフセット
    eyebrow.location.y += EYEBROW_Y_OFFSET
    gates.check("眉にY方向オフセットを適用した", abs(eyebrow.location.y - EYEBROW_Y_OFFSET) < 1e-6, tuple(eyebrow.location))

    # ---- 2) 白目の目頭側グラデーション（眼窩内側は今回S16で別島になったので、島の中で同じロジックを適用）
    socket_faces = [p for p in me.polygons if p.index < 460 and all(vi >= 463 for vi in p.vertices)]
    gates.check("Face: 眼窩内側（白目）の面が20枚見つかった", len(socket_faces) == 20, len(socket_faces))
    xs_all = [p.center.x for p in socket_faces]
    xmin, xmax = min(xs_all), max(xs_all)

    img = bpy.data.images["BaseColor"]
    arr = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1, :, :3].copy()
    col = np.array(INNER_TONE)
    n_touched = 0
    for p in socket_faces:
        t = (p.center.x - xmin) / max(xmax - xmin, 1e-6)
        a = float(np.clip((t - 0.55) / 0.45, 0, 1)) * 0.8
        if a <= 0.001:
            continue
        mask = np.zeros((H, W), dtype=bool)
        fill_poly_mask(mask, poly_px(face, p))
        ys, xs_ = np.where(mask)
        arr[ys, xs_] = arr[ys, xs_] * (1 - a) + col[None, :] * a
        n_touched += 1
    gates.check("目頭寄りの面のうち、色を寄せた面がある", n_touched > 0, n_touched)

    out = np.ones((H, W, 4), dtype="float32")
    out[:, :, :3] = arr
    img.pixels.foreach_set(out[::-1].ravel())
    img.pack()

    # ---- 3) 房の押し出し
    bvh_face0 = bvh_world(face)
    bvh_lash0 = bvh_world(lash)
    fixed = {}
    for n, o in wisps.items():
        bv = bvh_world(o)
        nf0, nl0 = len(bv.overlap(bvh_face0)), len(bv.overlap(bvh_lash0))
        if nf0 == 0 and nl0 == 0:
            fixed[n] = "変更なし（重なりなし）"
            continue
        bake_transform(o)
        me_w = o.data
        pts0 = [v.co.copy() for v in me_w.vertices]
        centroid = sum(pts0, Vector()) / len(pts0)
        hit = face.closest_point_on_mesh(centroid)
        push_dir = hit[2] if hit[0] else Vector((0, 0, 1))
        if push_dir.length < 1e-6:
            push_dir = Vector((0, 0, 1))
        push_dir.normalize()
        chosen = None
        for scale in (1.0, 0.9, 0.8, 0.7):
            for push_mm in (0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15):
                push = push_dir * (push_mm / 1000.0)
                newpts = [centroid + (p - centroid) * scale + push for p in pts0]
                bv2 = BVHTree.FromPolygons([tuple(p) for p in newpts], [list(p.vertices) for p in me_w.polygons])
                if len(bv2.overlap(bvh_face0)) == 0 and len(bv2.overlap(bvh_lash0)) == 0:
                    chosen = (scale, push_mm, newpts)
                    break
            if chosen:
                break
        if chosen is None:
            fixed[n] = "候補が見つからず変更なし（要確認）"
            continue
        scale, push_mm, newpts = chosen
        for v, p in zip(me_w.vertices, newpts):
            v.co = p
        me_w.update()
        fixed[n] = f"倍率{scale}・皮膚の外向きへ{push_mm}mm 押し出し"
    gates.note("房の修正内容", fixed)

    bvh_face1 = bvh_world(face)
    bvh_lash1 = bvh_world(lash)
    all_clear = True
    after = {}
    for n, o in wisps.items():
        bv = bvh_world(o)
        nf, nl = len(bv.overlap(bvh_face1)), len(bv.overlap(bvh_lash1))
        after[n] = (nf, nl)
        if nf > 0 or nl > 0:
            all_clear = False
    gates.check("修正後: 全ての房が、顔・主まつ毛のどちらとも重ならない", all_clear, after)

    img.filepath_raw = str(C.OUT / "s17_texture.png")
    img.file_format = "PNG"
    img.save()
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
    for camname, out_name in [("CAM_front", "s17reapply_render_front.png"), ("CAM_a45", "s17reapply_render_45.png"), ("CAM_side", "s17reapply_render_side.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
