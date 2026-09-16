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

# 1. 前髪SHORT × 後ろ髪SHORT_NAPE・丸眉・丸い肩のTシャツ（左正面）
char1 = create_procedural_chibi_character(
    context=bpy.context,
    name="ShortHair_Front_Boy",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_front="SHORT",
    hair_back="SHORT_NAPE",
    eyebrow_style="DOT",
    outfit_type="T_SHIRT",
    eye_style="OVAL",
    pattern="STRIPED",
    accessory="NONE",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.32, 0.18, 0.12, 1.0), # ダークブラウン
    cloth_top_color=(0.18, 0.55, 0.85, 1.0), # 青白ボーダーTシャツ（丸い撫で肩）
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=101
)
char1.location = (-1.00, 0.05, 0.0)
char1.rotation_euler = (0, 0, 0.12)
# 目のシェイプキー（ウインク/片目まばたき）を適用
for c in char1.children:
    if "Eyes" in c.name and c.data.shape_keys:
        kb = c.data.shape_keys.key_blocks
        if "Blink" in kb:
            kb["Blink"].value = 0.85

# 2. 真横プロフィール確認用（耳のめり込み解消＆前髪・後ろ髪のレイヤー確認） (中央左)
char2 = create_procedural_chibi_character(
    context=bpy.context,
    name="Profile_Ear_Clearance_Char",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_front="SHORT_MESSY",
    hair_back="SHORT_NAPE",
    eyebrow_style="ARCH",
    outfit_type="COAT",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="NONE",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.32, 0.18, 0.12, 1.0),
    cloth_top_color=(0.75, 0.28, 0.24, 1.0), # レッドコート（丸い肩）
    shoe_color=(0.20, 0.20, 0.22, 1.0),
    seed=102
)
char2.location = (-0.32, 0.10, 0.0)
char2.rotation_euler = (0, 0, math.radians(78)) # 真横に近い角度で耳と髪の隙間をアピール

# 3. 前髪CENTER_PART × 後ろ髪TWINTAILS（お団子ツインテ）・オーバーオール・笑顔 (中央右)
char3 = create_procedural_chibi_character(
    context=bpy.context,
    name="CenterPart_Twintails_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.12,
    hair_front="CENTER_PART",
    hair_back="TWINTAILS",
    eyebrow_style="ARCH",
    outfit_type="OVERALLS",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="CHEEK_BLUSH",
    skin_color=(0.98, 0.86, 0.78, 1.0),
    hair_color=(0.88, 0.70, 0.35, 1.0), # アッシュゴールド
    cloth_top_color=(0.25, 0.65, 0.40, 1.0), # グリーンオーバーオール（丸い肩）
    shoe_color=(0.45, 0.25, 0.15, 1.0),
    seed=303
)
char3.location = (0.35, 0.0, 0.0)
char3.rotation_euler = (0, 0, -0.10)
# 笑顔シェイプキーを適用
for c in char3.children:
    if "Eyes" in c.name and c.data.shape_keys:
        kb = c.data.shape_keys.key_blocks
        if "Smile" in kb:
            kb["Smile"].value = 1.0

# 4. 前髪MUSHROOM（おかっぱ） × 後ろ髪PONYTAIL・丸メガネ・ダッフルコート (右端)
char4 = create_procedural_chibi_character(
    context=bpy.context,
    name="Mushroom_Ponytail_Char",
    gender="BOY",
    head_ratio=2.20,
    total_height=1.14,
    hair_front="MUSHROOM",
    hair_back="PONYTAIL",
    eyebrow_style="STRAIGHT",
    outfit_type="COAT",
    eye_style="ROUND",
    pattern="PLAIN",
    accessory="ROUND_GLASSES",
    skin_color=(0.92, 0.76, 0.65, 1.0), # 小麦肌
    hair_color=(0.18, 0.18, 0.22, 1.0), # ナチュラルブラック
    cloth_top_color=(0.35, 0.45, 0.60, 1.0), # ダッフルコート（丸い肩）
    shoe_color=(0.85, 0.45, 0.20, 1.0),
    seed=404
)
char4.location = (1.02, 0.10, 0.0)
char4.rotation_euler = (0, 0, -0.22)

# 3. ワールド環境光（アンビエント光）
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("ChibiWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.92, 0.94, 0.96, 1.0)
    bg_node.inputs['Strength'].default_value = 0.85

# キーライト
light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
light_data.energy = 2.5
light_data.color = (1.0, 0.98, 0.95)
light_obj = bpy.data.objects.new("KeyLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(-30))

# フィルライト
fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
fill_data.energy = 1.2
fill_data.color = (0.95, 0.98, 1.0)
fill_obj = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(140))

# 4. カメラ設定（全体が美しく収まるアングル）
cam_data = bpy.data.cameras.new("RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -3.85, 0.72)
cam_obj.rotation_euler = (math.radians(84), 0.0, 0.0)
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
