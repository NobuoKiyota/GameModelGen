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

# 1. 女の子正面（2D三面図準拠：アンバー瞳 × 2重ハイライト × 白目ドーム × 目尻2本ハネ × ボタンノーズ × 丸い顎）
char1 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Front_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.12,
    hair_style="TWINTAILS",
    eyebrow_style="ARCH",
    outfit_type="ONE_PIECE",
    eye_style="OVAL",
    pattern="POLKA_DOT",
    accessory="NONE",
    skin_color=(0.96, 0.80, 0.72, 1.0), # 瑞々しいアニメピーチ肌
    hair_color=(0.92, 0.70, 0.35, 1.0), # オレンジブラウン
    cloth_top_color=(0.95, 0.42, 0.58, 1.0), # ピンクワンピース
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=101
)
char1.location = (-0.45, 0.0, 0.0)
char1.rotation_euler = (0, 0, 0.05)

# 2. 男の子側面・斜め（2D三面図準拠：鼻根の窪み〜ボタンノーズのS字プロファイル × ふっくら丸い顎 × ダークブラウン瞳）
char2 = create_procedural_chibi_character(
    context=bpy.context,
    name="Anime_Face_Profile_Boy",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT",
    eyebrow_style="STRAIGHT",
    outfit_type="T_SHIRT",
    eye_style="OVAL",
    pattern="PLAIN",
    accessory="NONE",
    skin_color=(0.95, 0.78, 0.70, 1.0), # 自然な血色感のある男の子肌
    hair_color=(0.30, 0.18, 0.12, 1.0), # ディープブラウン
    cloth_top_color=(0.20, 0.52, 0.82, 1.0), # ブルーストライプ/プレーン
    shoe_color=(0.88, 0.28, 0.22, 1.0), # 赤スニーカー
    seed=102
)
char2.location = (0.0, 0.0, 0.0)
char2.rotation_euler = (0, 0, -math.radians(38)) # 斜め〜側面寄りでS字鼻筋と丸い顎ラインを明示

# 3. 女の子笑顔表情差分（Smileシェイプキー連動：三日月まつ毛 ＆ 笑顔リップ）
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
    skin_color=(0.96, 0.80, 0.72, 1.0),
    hair_color=(0.36, 0.22, 0.16, 1.0), # ブラウンボブ
    cloth_top_color=(0.28, 0.65, 0.42, 1.0),
    shoe_color=(0.45, 0.25, 0.15, 1.0),
    seed=303
)
char3.location = (0.45, 0.0, 0.0)
char3.rotation_euler = (0, 0, -0.08)

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

# 3. ワールド環境光（アンビエント光: 明るく温かいスタジオホワイト）
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("ChibiWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.98, 0.97, 0.95, 1.0)
    bg_node.inputs['Strength'].default_value = 0.75

# キーライト（温白色）
light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
light_data.energy = 2.4
light_data.color = (1.0, 0.98, 0.96)
light_obj = bpy.data.objects.new("KeyLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(-30))

# フィルライト（影を柔らかく起こす）
fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
fill_data.energy = 1.2
fill_data.color = (0.96, 0.98, 1.0)
fill_obj = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(140))

# バウンス/フロントフィルライト（顎下やアイホールの陰影を明るく華やかに）
bounce_data = bpy.data.lights.new(name="BounceLight", type='SUN')
bounce_data.energy = 0.8
bounce_data.color = (1.0, 0.95, 0.92)
bounce_obj = bpy.data.objects.new("BounceLight", bounce_data)
bpy.context.collection.objects.link(bounce_obj)
bounce_obj.rotation_euler = (math.radians(80), 0.0, 0.0)

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
