import bpy
import math
import sys

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh
from procedural_rock_studio.generators.door_destruction_gen import generate_door_destruction

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

door_frame = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="DOOR",
    name="TestDoor",
    seed=11,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='ROMAN_ROUND',
    door_pillar_shape='SQUARE_PIER',
    door_pillar_width=0.42,
    door_column_height=1.7,
    door_has_keystone=True,
    door_strap_style='CROSS_Z',
    door_stud_pattern='GRID',
    door_handle_style='RING_PULL',
    door_has_hinges=True,
    door_has_edge_trim=True,
    door_edge_trim_width=0.05,
    door_wood_material='WEATHERED_OAK',
    door_iron_style='BLACK_FORGED',
    door_damage=0.35,
    door_weathering=0.55,
    door_moss_amount=0.20,
    door_open_angle=0.0,
    door_open_direction='OUTWARD',
    door_combine=False,
)
print("Door frame created:", door_frame.name, "children:", [c.name for c in door_frame.children])

leaf_l, leaf_r = None, None
for child in door_frame.children:
    if child.name.endswith("_Leaf_L"):
        leaf_l = child
    elif child.name.endswith("_Leaf_R"):
        leaf_r = child
print("Leaves found:", leaf_l, leaf_r)

combined_obj, action = generate_door_destruction(
    context=bpy.context,
    leaf_obj_l=leaf_l,
    leaf_obj_r=leaf_r,
    frame_obj=door_frame,
    shard_count=8,
    frame_count=30,
    sample_step=3,
    impact_strength=1.2,
    impact_frames=4,
    subdivide_cuts=1,
    seed=42,
    name="TestDoor_Destruction",
)
print("Destruction bake complete:", combined_obj.name)
# --- shape key の生値を直接検査 ---
bpy.context.scene.frame_set(20)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
eval_obj = combined_obj.evaluated_get(dg)
eval_mesh = eval_obj.to_mesh()
print("frame=20 eval vertex[0].co =", eval_mesh.vertices[0].co)
print("frame=20 raw (unevaluated) mesh.vertices[0].co =", combined_obj.data.vertices[0].co)
print("basis (shape_keys.key_blocks[0]) vert0 co =", combined_obj.data.shape_keys.key_blocks[0].data[0].co)
for kb in combined_obj.data.shape_keys.key_blocks[1:4]:
    print(f"  shapekey {kb.name} value={kb.value} vert0.co={kb.data[0].co}")
eval_obj.to_mesh_clear()
bpy.context.scene.frame_set(1)
print("--- ALL SCENE OBJECTS ---")
for o in bpy.data.objects:
    print(f"  {o.name}  (type={o.type}, users={o.users if hasattr(o,'users') else '?'})")
print("-------------------------")
print("Vertex count:", len(combined_obj.data.vertices))
print("Shape keys:", len(combined_obj.data.shape_keys.key_blocks) if combined_obj.data.shape_keys else 0)
print("Action fcurves:", len(action.fcurves))
print("Scene frame range:", bpy.context.scene.frame_start, bpy.context.scene.frame_end)

# --- レンダリング設定 ---
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("DestructionWorld")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.6, 0.6, 0.6, 1.0)
    bg_node.inputs['Strength'].default_value = 0.9

key = bpy.data.lights.new(name="KeyLight", type='SUN')
key.energy = 2.5
key_obj = bpy.data.objects.new("KeyLight", key)
bpy.context.collection.objects.link(key_obj)
key_obj.rotation_euler = (math.radians(55), 0, math.radians(-35))

bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
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
cam_obj.location = (3.2, -6.5, 2.2)
cam_obj.rotation_euler = (math.radians(80), 0.0, math.radians(25))
cam_data.lens = 30
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100

for f in (1, 8, 16, 30):
    scene.frame_set(f)
    scene.render.filepath = rf"z:\MeshCreator\test_render_destruction_f{f:03d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered frame {f}")

print("ALL DONE")
