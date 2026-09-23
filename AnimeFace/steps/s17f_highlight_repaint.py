"""S17f: 目のハイライトを塗り直す（アルファ不具合修正を反映した上で、縁を柔らかくする）。

背景: S17bで見つけた「共有テクスチャがalpha=False（24bit）で作られており、アルファが保存後1.0に戻る」不具合は、
S17b自体をやり直した時点（S17c以降の入力）で既に修正済み（`out/face_s17e_gen.blend`は修正後の系列）。
ユーザーから改めて「アルファ不具合の修正を反映して、目のハイライトを塗り直して」と依頼されたため、
①現状の系列に不具合修正が反映済みであることを確認 ②ハイライトの丸を、輪郭が硬い円ではなく、
縁がなめらかなグラデーションになるよう塗り直す（見た目の質を上げる）。

入力: out/face_s17e_gen.blend   出力: out/face_s17e_gen.blend（上書き）, out/s17f_report.json, out/s17f_render_*.png
実行: blender --background --factory-startup --python steps/s17f_highlight_repaint.py
"""
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s17f"
gates = C.Gates(STEP)

W = H = 2048
HIGHLIGHT_COLOR = (0.99, 0.99, 1.0)


def px_of(u, v):
    return u * (W - 1), (1 - v) * (H - 1)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"))
    img = bpy.data.images["BaseColor"]
    gates.check("入力: BaseColor は32bit（アルファ有り。S16の不具合修正が反映されている）", img.depth == 32, img.depth)

    face = bpy.data.objects["Face"]
    eye = bpy.data.objects["Eye"]
    hi_faces = [p for p in eye.data.polygons if p.material_index == 1]
    gates.check("Eye: ハイライト専用面（material_index=1）が160枚見つかった", len(hi_faces) == 160, len(hi_faces))
    uv = eye.data.uv_layers.active.data
    us = [uv[li].uv.x for p in hi_faces for li in range(p.loop_start, p.loop_start + p.loop_total)]
    vs = [uv[li].uv.y for p in hi_faces for li in range(p.loop_start, p.loop_start + p.loop_total)]
    bx0, bx1, by0, by1 = min(us), max(us), min(vs), max(vs)
    gates.note("ハイライト区画のUV範囲", (round(bx0, 4), round(by0, 4), round(bx1, 4), round(by1, 4)))

    arr = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1].copy()  # top-down に変換

    hbox_x0, hbox_y1 = px_of(bx0, by0)
    hbox_x1, hbox_y0 = px_of(bx1, by1)
    x0i, x1i = int(min(hbox_x0, hbox_x1)), int(max(hbox_x0, hbox_x1))
    y0i, y1i = int(min(hbox_y0, hbox_y1)), int(max(hbox_y0, hbox_y1))
    arr[y0i:y1i + 1, x0i:x1i + 1, 3] = 0.0   # 区画全体を透明地に戻す

    def draw_soft_circle(cx_frac, cy_frac, r_frac, feather=0.35):
        cx = bx0 + (bx1 - bx0) * cx_frac
        cy = by0 + (by1 - by0) * cy_frac
        cxpx, cypx = px_of(cx, cy)
        rpx = r_frac * (x1i - x0i)
        y0 = max(int(cypx - rpx * 1.4), 0)
        y1 = min(int(cypx + rpx * 1.4), H - 1)
        x0 = max(int(cxpx - rpx * 1.4), 0)
        x1 = min(int(cxpx + rpx * 1.4), W - 1)
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        d = np.sqrt((xx - cxpx) ** 2 + (yy - cypx) ** 2) / rpx
        inner = 1.0 - feather
        a = np.clip((1.0 - d) / max(1e-6, 1.0 - inner), 0, 1) ** 1.5
        sub_a = arr[y0:y1 + 1, x0:x1 + 1, 3]
        sub_rgb = arr[y0:y1 + 1, x0:x1 + 1, :3]
        col = np.array(HIGHLIGHT_COLOR)
        new_a = np.maximum(sub_a, a)
        blend = a[..., None]
        sub_rgb[:] = sub_rgb * (1 - blend) + col[None, None, :] * blend
        sub_a[:] = new_a
        return float(a.sum())

    w1 = draw_soft_circle(0.30, 0.66, 0.065, feather=0.4)
    w2 = draw_soft_circle(0.60, 0.32, 0.032, feather=0.4)
    gates.check("ハイライトの丸2つを、縁が滑らかなグラデーションで描いた", w1 > 0 and w2 > 0, (round(w1, 1), round(w2, 1)))

    out = arr[::-1].copy()
    img.pixels.foreach_set(out.ravel())
    img.filepath_raw = str(C.OUT / "s17f_texture.png")
    img.file_format = "PNG"
    img.pack()
    img.save()

    real = np.array(img.pixels[:], dtype="float32").reshape(H, W, 4)[::-1]

    def sample(u, v):
        x, y = px_of(u, v)
        return real[int(y), int(x)]

    corner_alpha = sample(bx0 + 0.005, by0 + 0.005)[3]
    gates.check("保存後: 区画の角はアルファ0のまま", corner_alpha < 0.05, corner_alpha)
    center_alpha = sample(bx0 + (bx1 - bx0) * 0.30, by0 + (by1 - by0) * 0.66)[3]
    gates.check("保存後: 丸1の中心はアルファ1に近い", center_alpha > 0.9, center_alpha)

    # ---- レビュー用レンダリング
    for m in bpy.data.materials:
        if m.use_nodes:
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b:
                b.inputs["Roughness"].default_value = 0.9
                b.inputs["Specular IOR Level"].default_value = 0.05
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
    keep = {"Face", "Eye", "Eyebrow", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"}
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o.name not in keep

    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s17e_gen.blend"), compress=False)

    for camname, out_name in [("CAM_front", "s17f_render_front.png"), ("CAM_a45", "s17f_render_45.png")]:
        scene.camera = bpy.data.objects[camname]
        scene.render.filepath = str(C.OUT / out_name)
        bpy.ops.render.render(write_still=True)

    gates.finish()


main()
