"""S01: 空シーンに3枚の下絵(画像エンプティ)とオルソカメラを配置し、配置の正しさを数値検証する。

実行: blender --background --factory-startup --python steps/s01_setup_blueprints.py
出力: out/face_s01.blend, out/s01_report.json, out/verify/*.png
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import common as C  # noqa: E402

STEP = "s01"
gates = C.Gates(STEP)


def load_pixels(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px


def make_reference(coll, key, spec):
    a = math.radians(spec["angle_deg"])
    img = bpy.data.images.load(str(C.BP_DIR / spec["file"]))
    e = bpy.data.objects.new(f"REF_{key}", None)
    e.empty_display_type = "IMAGE"
    e.data = img
    e.empty_display_size = C.IMG_M
    e.empty_image_offset = (-0.5, -0.5)
    e.location = (C.REF_DIST * math.sin(a), C.REF_DIST * math.cos(a), (C.ROW0 - 512.0) * C.K)
    e.rotation_euler = (math.radians(90), 0, -a)
    e.use_empty_image_alpha = True
    e.color[3] = 0.6
    e.show_empty_image_only_axis_aligned = True
    e.hide_select = True
    coll.objects.link(e)
    return e


def make_camera(coll, key, spec):
    a = math.radians(spec["angle_deg"])
    cd = bpy.data.cameras.new(f"CAM_{key}")
    cd.type = "ORTHO"
    cd.ortho_scale = C.IMG_M
    cd.clip_start = 0.01
    cd.clip_end = 10.0
    co = bpy.data.objects.new(f"CAM_{key}", cd)
    co.location = (-C.CAM_DIST * math.sin(a), -C.CAM_DIST * math.cos(a), (C.ROW0 - 512.0) * C.K)
    co.rotation_euler = (math.radians(90), 0, -a)
    coll.objects.link(co)
    return co


def make_probe_plane(ref, img_path):
    """検証用: 下絵エンプティと同じ matrix_world に置く実メッシュ平面（エンプティは描画されないため）。"""
    h = C.IMG_M / 2
    mesh = bpy.data.meshes.new("probe")
    mesh.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UV")
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    obj = bpy.data.objects.new("probe", mesh)
    obj.matrix_world = ref.matrix_world.copy()
    mat = bpy.data.materials.new("probe_mat")
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path), check_existing=False)
    tex.interpolation = "Closest"
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mesh.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    coll = bpy.data.collections.new("REF")
    scene.collection.children.link(coll)
    refs = {k: make_reference(coll, k, s) for k, s in C.BLUEPRINTS.items()}
    cams = {k: make_camera(coll, k, s) for k, s in C.BLUEPRINTS.items()}

    # --- ゲート1: 素材の寸法 ---
    for k, e in refs.items():
        w, h = e.data.size
        gates.check(f"下絵 {k} は 1024x1024", (w, h) == (C.IMG_PX, C.IMG_PX), f"{w}x{h}")

    # --- ゲート2: 下絵を実メッシュに貼ってカメラで撮り、元画像とピクセル一致するか ---
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = C.IMG_PX
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "TEXTURE"
    scene.display.render_aa = "OFF"

    verify_dir = C.OUT / "verify"
    verify_dir.mkdir(parents=True, exist_ok=True)

    def render_probe(k):
        spec = C.BLUEPRINTS[k]
        probe = make_probe_plane(refs[k], C.BP_DIR / spec["file"])
        scene.camera = cams[k]
        out_png = verify_dir / f"probe_{k}.png"
        scene.render.filepath = str(out_png)
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(probe)
        return out_png

    # Workbench はセッション最初のテクスチャ付き描画が白紙になるため、捨て描画を1回行う
    render_probe("front")

    for k, spec in C.BLUEPRINTS.items():
        src = C.BP_DIR / spec["file"]
        out_png = render_probe(k)

        a = load_pixels(src)[..., :3]
        b = load_pixels(out_png)[..., :3]
        d0 = float(np.abs(a - b).mean())
        shifts = {}
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dy, dx) == (0, 0):
                    continue
                shifts[(dy, dx)] = float(np.abs(a - np.roll(b, (dy, dx), axis=(0, 1))).mean())
        flipped = float(np.abs(a - b[:, ::-1]).mean())
        best_shift = min(shifts, key=shifts.get)
        gates.check(f"配置 {k}: 元画像との平均差 < 0.01", d0 < 0.01, f"diff={d0:.5f}")
        gates.check(f"配置 {k}: 位置ズレ0px（±1pxずらすより一致）", d0 < shifts[best_shift],
                    f"diff0={d0:.5f} best_shift={best_shift}:{shifts[best_shift]:.5f}")
        # 正面はほぼ左右対称なので、この検査が有効なのは 45°/側面のみ
        gates.check(f"配置 {k}: 左右反転していない", d0 * 5 < flipped, f"diff={d0:.5f} flipped={flipped:.5f}")

    # 検証用の残骸を除去
    for m in [m for m in bpy.data.materials if m.name.startswith("probe")]:
        bpy.data.materials.remove(m)
    for me in [me for me in bpy.data.meshes if me.name.startswith("probe")]:
        bpy.data.meshes.remove(me)
    gates.check("メッシュオブジェクトが残っていない", not [o for o in bpy.data.objects if o.type == "MESH"])

    scene.camera = cams["front"]
    bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT / "face_s01.blend"), compress=False)
    gates.finish()


main()
