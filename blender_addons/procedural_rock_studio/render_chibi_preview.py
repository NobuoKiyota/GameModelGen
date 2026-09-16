import bpy
import math
import sys
import os

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import create_procedural_chibi_character

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

# 1. アニメフェイス正面（ショートヘア × パッチリ瞳 × 立体アイライン/ハネ × ボタンノーズ × 微笑みリップ）
char1 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Front_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.12,
    hair_style="SHORT",
    eyebrow_style="ARCH",
    outfit_type="ONE_PIECE",
    eye_style="OVAL",
    pattern="POLKA_DOT",
    accessory="NONE",
    skin_color=(0.97, 0.84, 0.76, 1.0),
    hair_color=(0.32, 0.18, 0.12, 1.0), # ダークブラウン
    cloth_top_color=(0.92, 0.78, 0.35, 1.0), # イエロー水玉ワンピース
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=101
)
char1.location = (-0.50, 0.05, 0.0)
char1.rotation_euler = (0, 0, 0.08)

# 2. アニメフェイスライン斜めアングル（頬のチークふくらみ × 顎先Vライン × 顎下引き締め × パーカー）
char2 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Angle_Boy",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT_MESSY",
    eyebrow_style="ARCH",
    outfit_type="HOODIE",
    eye_style="CAT_EYE",
    pattern="PLAIN",
    accessory="NONE",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.18, 0.18, 0.22, 1.0),
    cloth_top_color=(0.22, 0.55, 0.78, 1.0), # ブルーパーカー
    shoe_color=(0.20, 0.20, 0.22, 1.0),
    seed=102
)
char2.location = (0.0, 0.0, 0.0)
char2.rotation_euler = (0, 0, -math.radians(24)) # 斜めアングルで美しい顎Vラインと横顔の鼻立ちをアピール

# 3. 表情差分連動（ボブヘア × 笑顔シェイプキー連動: 三日月まつ毛 ＆ 笑顔リップ）
char3 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Smile_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.12,
    hair_style="BOB",
    eyebrow_style="ARCH",
    outfit_type="OVERALLS",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="ROUND_GLASSES",
    skin_color=(0.98, 0.86, 0.78, 1.0),
    hair_color=(0.88, 0.65, 0.32, 1.0), # キャラメルゴールド
    cloth_top_color=(0.75, 0.28, 0.24, 1.0),
    shoe_color=(0.45, 0.25, 0.15, 1.0),
    seed=303
)
char3.location = (0.50, 0.05, 0.0)
char3.rotation_euler = (0, 0, -0.10)

# 表情シェイプキー（Smile）を Eyes と Mouth に適用
for c in char3.children:
    if "Eyes" in c.name and c.data.shape_keys:
        kb = c.data.shape_keys.key_blocks
        if "Smile" in kb:
            kb["Smile"].value = 0.95
    if "Mouth" in c.name and c.data.shape_keys:
        kb = c.data.shape_keys.key_blocks
        if "Smile" in kb:
            kb["Smile"].value = 1.0

# 3. ワールド環境光（アンビエント光）
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("ChibiWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.92, 0.94, 0.96, 1.0)
    bg_node.inputs['Strength'].default_value = 0.55

# キーライト
light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
light_data.energy = 1.8
light_data.color = (1.0, 0.98, 0.95)
light_obj = bpy.data.objects.new("KeyLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(-30))

# フィルライト
fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
fill_data.energy = 0.7
fill_data.color = (0.95, 0.98, 1.0)
fill_obj = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(140))

# 4. カメラ設定（顔と表情のディテールがはっきり見える距離）
cam_data = bpy.data.cameras.new("RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -2.15, 0.72)
cam_obj.rotation_euler = (math.radians(85), 0.0, 0.0)
bpy.context.scene.camera = cam_obj

# 5. 床スラブ
bpy.ops.mesh.primitive_cylinder_add(radius=2.6, depth=0.08, location=(0, 0, -0.04))
floor_obj = bpy.context.active_object
mat_floor = bpy.data.materials.new("Stage_Floor")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 0.86, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
floor_obj.data.materials.append(mat_floor)

# 6. レンダリング設定
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.filepath = r"z:\MeshCreator\test_render_chibi_character.png"

bpy.ops.render.render(write_still=True)
print("Render completed: z:\\MeshCreator\\test_render_chibi_character.png")
