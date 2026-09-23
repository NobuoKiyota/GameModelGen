"""S17 手直し: 白目が目頭側に大きく浸食して見える点を修正（ユーザー指摘、画像添付）。

背景: `face_s17_human.blend` は、S17生成物に対する人間の手直し（Eyebrowをオブジェクト単位でY方向へ26.8mm移動。
「埋没」＝皮膚面に埋まって見えていたのを手前に出した）。この手直しは保持したまま、白目の色を塗った範囲だけを直す。

原因: 眼窩内側の面（socket面、20枚）を、位置に関わらず全て同じ EYE_WHITE で塗っていた。実際は、目頭側
（X が 0 に近い側）の面まで真っ白になり、白目が目頭まで大きく浸食しているように見えた。

修正: 目頭側（X が 0 に近い、内眼角寄り）の面ほど、白から目頭の柔らかい色（涙丘に近いトーン）へ寄せるグラデーションを、
既存の白塗り部分の上から重ねる。境界がはっきり分かれないよう、しきい値からなだらかに立ち上げる。

入力: out/face_s17_human.blend   出力: out/face_s17_gen.blend（上書き）, out/s17fix_report.json, out/s17fix_render_*.png
実行: blender --background --factory-startup --python steps/s17_fix_sclera.py
"""
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17fix"
gates = C.Gates(STEP)

W = H = 2048
EYE_WHITE = (0.96, 0.96, 0.97)
INNER_TONE = (0.92, 0.74, 0.70)      # 目頭寄り（涙丘に近い、肌に近い柔らかいトーン）


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


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17_human.blend"))
    face = bpy.data.objects["Face"]
    me = face.data
    eyebrow = bpy.data.objects["Eyebrow"]
    gates.check("入力: Eyebrow の手直し（Y方向オフセット）が保持されている", abs(eyebrow.location.y) > 0.02, tuple(eyebrow.location))

    socket_faces = [p for p in me.polygons if p.index < 460 and all(vi >= 463 for vi in p.vertices)]
    gates.check("Face: 眼窩内側（白目）の面が20枚見つかった", len(socket_faces) == 20, len(socket_faces))
    xs_all = [p.center.x for p in socket_faces]
    xmin, xmax = min(xs_all), max(xs_all)
    gates.note("眼窩内側の面のX範囲（外側→目頭側）", (round(xmin, 4), round(xmax, 4)))

    img = bpy.data.images["BaseColor"]
    arr = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1, :, :3].copy()

    col = np.array(INNER_TONE)
    n_touched = 0
    for p in socket_faces:
        t = (p.center.x - xmin) / max(xmax - xmin, 1e-6)     # 0=外側, 1=目頭側
        a = float(np.clip((t - 0.55) / 0.45, 0, 1)) * 0.8
        if a <= 0.001:
            continue
        mask = np.zeros((H, W), dtype=bool)
        fill_poly_mask(mask, poly_px(face, p))
        ys, xs_ = np.where(mask)
        arr[ys, xs_] = arr[ys, xs_] * (1 - a) + col[None, :] * a
        n_touched += 1
    gates.check("目頭寄りの面のうち、色を寄せた面がある（浸食部分を直した）", n_touched > 0, n_touched)

    # ---- 検証: 一番目頭側の面は元の白より暗く/暖色寄りに、一番外側の面は白のまま
    def sample(p):
        pts = poly_px(face, p)
        cx = sum(pt[0] for pt in pts) / len(pts)
        cy = sum(pt[1] for pt in pts) / len(pts)
        return arr[int(cy), int(cx)]

    inner_face = max(socket_faces, key=lambda p: p.center.x)
    outer_face = min(socket_faces, key=lambda p: p.center.x)
    c_inner = sample(inner_face)
    c_outer = sample(outer_face)
    gates.check("最も目頭側の面は白より暖色・やや暗くなった", c_inner[0] > c_inner[2] and c_inner[2] < EYE_WHITE[2] - 0.05, [round(float(c), 3) for c in c_inner])
    gates.check("最も外側の面は白のまま", all(abs(float(a) - b) < 0.02 for a, b in zip(c_outer, EYE_WHITE)), [round(float(c), 3) for c in c_outer])

    out = np.ones((H, W, 4), dtype="float32")
    out[:, :, :3] = arr
    img.pixels.foreach_set(out[::-1].ravel())
    img.filepath_raw = str(C.OUT / "s17_texture.png")
    img.file_format = "PNG"
    img.pack()
    img.save()

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17_gen.blend"), compress=False)

    # ---- レビュー用レンダリング（一時ライト、.blendには保存しない）
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
    scene.render.resolution_x = 800
    scene.render.resolution_y = 800
    keep = {"Face", "Eye", "Eyelash", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep
    for camname, out_name in [("CAM_front", "s17fix_render_front.png"), ("CAM_a45", "s17fix_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
