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

# 1. 女の子正面（2D三面図準拠：縦長アンバー瞳 × 2重ハイライト × 目頭/目尻白目 × 目尻2本ハネ × ボタンノーズ × 自然なチーク）
char1 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Front_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.12,
    hair_style="SHORT",         # Option B確認用: TWINTAILSから変更
    eyebrow_style="ARCH",
    outfit_type="ONE_PIECE",
    eye_style="OVAL",
    pattern="POLKA_DOT",
    accessory="NONE",           # Option B確認用: チークなし
    skin_color=(0.96, 0.80, 0.72, 1.0),
    hair_color=(0.92, 0.70, 0.35, 1.0),
    cloth_top_color=(0.95, 0.42, 0.58, 1.0),
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=101
)
char1.location = (-0.48, 0.0, 0.0)
char1.rotation_euler = (0, 0, 0.05)

# 2. 男の子側面（目のインセット配置で横からの飛び出し根絶 × 側頭部穴あき解消 × S字鼻立ち × パーカー）
char2 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Profile_Boy",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT",
    eyebrow_style="STRAIGHT",
    outfit_type="HOODIE",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="NONE",
    skin_color=(0.95, 0.78, 0.70, 1.0), # 自然な血色感のある男の子肌
    hair_color=(0.30, 0.18, 0.12, 1.0), # ディープブラウン
    cloth_top_color=(0.20, 0.52, 0.82, 1.0), # ブルーパーカー
    shoe_color=(0.88, 0.28, 0.22, 1.0), # 赤スニーカー
    seed=102
)
char2.location = (0.0, 0.0, 0.0)
char2.rotation_euler = (0, 0, 0)  # Option B確認用: 正面向き

# 3. パーカー背面斜めアングル（新・立体袋状フードの開口部・深いくぼみ・折り返しリム × 後頭部完全カバー）
char3 = create_procedural_chibi_character(
    context=bpy.context,
    name="Hoodie_Back_Pouch_Boy",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT_MESSY",
    eyebrow_style="ARCH",
    outfit_type="HOODIE",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="NONE",
    skin_color=(0.95, 0.78, 0.70, 1.0),
    hair_color=(0.35, 0.22, 0.14, 1.0),
    cloth_top_color=(0.85, 0.55, 0.20, 1.0), # オレンジマスタードパーカー
    shoe_color=(0.25, 0.25, 0.28, 1.0),
    seed=205
)
char3.location = (0.48, 0.0, 0.0)
char3.rotation_euler = (0, 0, math.radians(20))  # Option B確認用: やや斜め前

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

# 3. ワールド環境光（アンビエント光: 白飛びを抑え、瞳の色が鮮やかに映える設定）
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("ChibiWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.95, 0.95, 0.94, 1.0)
    bg_node.inputs['Strength'].default_value = 0.65

# キーライト（温白色）
light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
light_data.energy = 1.8
light_data.color = (1.0, 0.98, 0.96)
light_obj = bpy.data.objects.new("KeyLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(-30))

# フィルライト（影を柔らかく起こす）
fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
fill_data.energy = 0.9
fill_data.color = (0.96, 0.98, 1.0)
fill_obj = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(140))

# バウンス/フロントフィルライト（適度な照度で白飛び防止）
bounce_data = bpy.data.lights.new(name="BounceLight", type='SUN')
bounce_data.energy = 0.4
bounce_data.color = (1.0, 0.96, 0.94)
bounce_obj = bpy.data.objects.new("BounceLight", bounce_data)
bpy.context.collection.objects.link(bounce_obj)
bounce_obj.rotation_euler = (math.radians(75), 0.0, 0.0)

# 4. カメラ設定（顔と表情のディテールがはっきり見える距離）
cam_data = bpy.data.cameras.new("RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -2.10, 0.70)
cam_obj.rotation_euler = (math.radians(86), 0.0, 0.0)
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
