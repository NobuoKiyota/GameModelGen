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

# 1. 男の子キャラクター生成 (Tシャツ・袖修正確認用・左側)
boy = create_procedural_chibi_character(
    context=bpy.context,
    name="Boy_Chibi",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT",
    outfit_type="T_SHIRT",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.32, 0.20, 0.12, 1.0),
    cloth_top_color=(0.18, 0.55, 0.85, 1.0),
    shoe_color=(0.85, 0.22, 0.20, 1.0),
    seed=10
)
boy.location = (-0.68, 0.0, 0.0)
boy.rotation_euler = (0, 0, 0.30) # 袖の向きがよく見えるよう少し斜め向き

# 2. キャップ帽の島民キャラクター (中央)
cap_char = create_procedural_chibi_character(
    context=bpy.context,
    name="Cap_Chibi",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="CAP",
    outfit_type="T_SHIRT",
    skin_color=(0.98, 0.85, 0.76, 1.0),
    hair_color=(0.85, 0.28, 0.22, 1.0), # レッドキャップ
    cloth_top_color=(0.88, 0.72, 0.20, 1.0), # イエローTシャツ
    shoe_color=(0.15, 0.15, 0.18, 1.0),
    seed=33
)
cap_char.location = (0.0, 0.0, 0.0)

# 3. もこもこアフロ＆ワンピースの女の子 (右側)
afro_girl = create_procedural_chibi_character(
    context=bpy.context,
    name="Afro_Girl",
    gender="GIRL",
    head_ratio=2.1,
    total_height=1.10,
    hair_style="AFRO",
    outfit_type="ONE_PIECE",
    skin_color=(0.90, 0.74, 0.62, 1.0),
    hair_color=(0.92, 0.55, 0.30, 1.0), # キャロットアフロ
    cloth_top_color=(0.95, 0.40, 0.58, 1.0), # ピンクワンピ
    shoe_color=(0.35, 0.18, 0.12, 1.0),
    seed=55
)
afro_girl.location = (0.68, 0.0, 0.0)

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
cam_obj.location = (0.0, -3.35, 0.68)
cam_obj.rotation_euler = (math.radians(84), 0.0, 0.0)
bpy.context.scene.camera = cam_obj


# 5. 床スラブ
bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.08, location=(0, 0, -0.04))
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
