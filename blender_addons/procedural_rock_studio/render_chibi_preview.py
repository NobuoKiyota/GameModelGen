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

# 1. キノコマッシュ・水玉ワンピ・丸メガネの女の子 (左端)
char1 = create_procedural_chibi_character(
    context=bpy.context,
    name="Mushroom_Girl",
    gender="GIRL",
    head_ratio=2.15,
    total_height=1.10,
    hair_style="MUSHROOM",
    outfit_type="ONE_PIECE",
    eye_style="DROOPY",
    pattern="POLKA_DOT",
    accessory="ROUND_GLASSES",
    skin_color=(0.98, 0.86, 0.78, 1.0),
    hair_color=(0.28, 0.16, 0.12, 1.0),
    cloth_top_color=(0.88, 0.28, 0.35, 1.0), # 赤白水玉
    shoe_color=(0.22, 0.22, 0.25, 1.0),
    seed=101
)
char1.location = (-1.05, 0.15, 0.0)
char1.rotation_euler = (0, 0, 0.20)

# 2. ツンツン髪・ボーダーパーカーの男の子 (中央左)
char2 = create_procedural_chibi_character(
    context=bpy.context,
    name="Spiky_Hoodie_Boy",
    gender="BOY",
    head_ratio=2.25,
    total_height=1.16,
    hair_style="SPIKY",
    outfit_type="HOODIE",
    eye_style="CAT_EYE",
    pattern="STRIPED",
    accessory="NONE",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.88, 0.68, 0.25, 1.0), # 金髪
    cloth_top_color=(0.18, 0.55, 0.85, 1.0), # 青白ボーダーパーカー
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=202
)
char2.location = (-0.35, 0.0, 0.0)
char2.rotation_euler = (0, 0, 0.08)

# 3. みつあみ・オーバーオール・葉っぱマーク・笑顔チークの女の子 (中央右)
char3 = create_procedural_chibi_character(
    context=bpy.context,
    name="Braids_Overalls_Girl",
    gender="GIRL",
    head_ratio=2.10,
    total_height=1.12,
    hair_style="BRAIDS",
    outfit_type="OVERALLS",
    eye_style="SMILING",
    pattern="ISLAND_LEAF",
    accessory="CHEEK_BLUSH",
    skin_color=(0.90, 0.74, 0.62, 1.0), # 健康的な小麦肌
    hair_color=(0.85, 0.42, 0.25, 1.0), # オレンジブラウンおさげ
    cloth_top_color=(0.25, 0.65, 0.38, 1.0), # グリーン葉っぱオーバーオール
    shoe_color=(0.45, 0.25, 0.15, 1.0),
    seed=303
)
char3.location = (0.35, 0.0, 0.0)
char3.rotation_euler = (0, 0, -0.08)

# 4. 魔女帽子・和装ゆかたのファンタジー島民 (右端)
char4 = create_procedural_chibi_character(
    context=bpy.context,
    name="Witch_Kimono_Char",
    gender="GIRL",
    head_ratio=2.20,
    total_height=1.14,
    hair_style="WITCH_HAT",
    outfit_type="KIMONO",
    eye_style="ROUND",
    pattern="PLAIN",
    accessory="CHEEK_BLUSH",
    skin_color=(0.98, 0.88, 0.82, 1.0),
    hair_color=(0.55, 0.32, 0.68, 1.0), # パープル魔女帽子
    cloth_top_color=(0.52, 0.35, 0.68, 1.0), # 紫着物
    shoe_color=(0.85, 0.22, 0.25, 1.0),
    seed=404
)
char4.location = (1.05, 0.15, 0.0)
char4.rotation_euler = (0, 0, -0.20)

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
