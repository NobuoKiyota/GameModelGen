import bpy
import math
import sys

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

variants = [
    dict(name="Door_Roman", door_arch_style='ROMAN_ROUND', door_strap_style='CROSS_Z',
         door_stud_pattern='GRID', door_handle_style='RING_PULL', door_damage=0.35,
         door_weathering=0.60, door_moss_amount=0.25, door_has_edge_trim=True, door_edge_trim_width=0.05, x=-2.6, seed=11),
    dict(name="Door_Gothic", door_arch_style='GOTHIC_POINTED', door_strap_style='DOUBLE_DIAGONAL',
         door_stud_pattern='DIAMOND', door_handle_style='DROP_KNOCKER', door_damage=0.50,
         door_weathering=0.75, door_moss_amount=0.40, door_has_edge_trim=True, door_edge_trim_width=0.07, x=0.0, seed=22),
    dict(name="Door_Segmental", door_arch_style='SEGMENTAL', door_strap_style='HORIZONTAL_BANDS',
         door_stud_pattern='GRID', door_handle_style='RING_PULL', door_damage=0.15,
         door_weathering=0.30, door_moss_amount=0.05, door_has_edge_trim=False, door_edge_trim_width=0.05, x=2.9, seed=33),
]

created = []
for v in variants:
    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="DOOR",
        name=v["name"],
        seed=v["seed"],
        size_x=2.2, size_y=0.5, size_z=2.6,
        door_arch_style=v["door_arch_style"],
        door_pillar_shape='SQUARE_PIER',
        door_pillar_width=0.42,
        door_column_height=1.7,
        door_has_keystone=True,
        door_strap_style=v["door_strap_style"],
        door_stud_pattern=v["door_stud_pattern"],
        door_handle_style=v["door_handle_style"],
        door_has_hinges=True,
        door_wood_material='WEATHERED_OAK',
        door_iron_style='BLACK_FORGED',
        door_damage=v["door_damage"],
        door_weathering=v["door_weathering"],
        door_moss_amount=v["door_moss_amount"],
        door_has_edge_trim=v["door_has_edge_trim"],
        door_edge_trim_width=v["door_edge_trim_width"],
        door_open_angle=0.0,
        door_open_direction='OUTWARD',
        door_combine=False,
    )
    if obj is None:
        print(f"ERROR: {v['name']} returned None")
        continue
    obj.location = (v["x"], 0.0, 0.0)
    created.append(obj)
    print(f"OK: {v['name']} -> {obj.name}, children={[c.name for c in obj.children]}")

# 開閉プレビュー用にもう1体、開いた状態で生成
obj_open = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="DOOR",
    name="Door_Open_Preview",
    seed=44,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='ROMAN_ROUND',
    door_pillar_shape='ROUND_COLUMN',
    door_pillar_width=0.40,
    door_column_height=1.7,
    door_has_keystone=True,
    door_strap_style='CROSS_Z',
    door_stud_pattern='GRID',
    door_handle_style='RING_PULL',
    door_has_hinges=True,
    door_wood_material='DARK_WALNUT',
    door_iron_style='RUSTED',
    door_damage=0.40,
    door_weathering=0.65,
    door_moss_amount=0.20,
    door_open_angle=75.0,
    door_open_direction='OUTWARD',
    door_combine=False,
)
if obj_open is not None:
    obj_open.location = (5.6, 0.0, 0.0)
    created.append(obj_open)
    print(f"OK: Door_Open_Preview -> {obj_open.name}, children={[c.name for c in obj_open.children]}")
else:
    print("ERROR: Door_Open_Preview returned None")

# ワールド・ライト・床
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("DoorWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.85, 0.85, 0.85, 1.0)
    bg_node.inputs['Strength'].default_value = 0.7

key = bpy.data.lights.new(name="KeyLight", type='SUN')
key.energy = 2.2
key_obj = bpy.data.objects.new("KeyLight", key)
bpy.context.collection.objects.link(key_obj)
key_obj.rotation_euler = (math.radians(55), 0, math.radians(-35))

fill = bpy.data.lights.new(name="FillLight", type='SUN')
fill.energy = 0.6
fill_obj = bpy.data.objects.new("FillLight", fill)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(50), 0, math.radians(150))

bpy.ops.mesh.primitive_plane_add(size=14, location=(2.0, 0, 0))
floor_obj = bpy.context.active_object
mat_floor = bpy.data.materials.new("Stage_Floor")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.35, 0.33, 0.30, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
floor_obj.data.materials.append(mat_floor)

cam_data = bpy.data.cameras.new("RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (2.0, -9.5, 2.4)
cam_obj.rotation_euler = (math.radians(82), 0.0, 0.0)
cam_data.lens = 24
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1600
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.filepath = r"z:\MeshCreator\test_render_door_preset.png"

bpy.ops.render.render(write_still=True)
print("Render completed: z:\\MeshCreator\\test_render_door_preset.png")
