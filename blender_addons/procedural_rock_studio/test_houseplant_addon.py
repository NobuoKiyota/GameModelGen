import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

from procedural_rock_studio.generators.core_orchestrator import generate_procedural_prop_mesh

print("=== 🌿 Testing Procedural Houseplant & Potted Foliage Engine ===")

styles = ['HANGING_MACRAME', 'PEDESTAL_URN', 'FLOOR_PALM', 'MONSTERA_DESK']
for style in styles:
    print(f"\n--- Testing Houseplant Style: {style} ---")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="HOUSEPLANT",
        name=f"Test_{style}",
        houseplant_style=style,
        houseplant_density='MEDIUM',
        houseplant_pot_material='ANTIQUE_STONE' if style == 'PEDESTAL_URN' else 'TERRACOTTA',
        houseplant_leaf_color='VIBRANT_GREEN',
        houseplant_variegated=(style == 'PEDESTAL_URN'),
        seed=42
    )

    assert obj is not None, f"Failed to generate {style}"
    assert obj.type == 'MESH', f"Generated object is not a mesh: {obj.type}"
    verts = len(obj.data.vertices)
    faces = len(obj.data.polygons)
    mats = [m.name for m in obj.data.materials if m]

    print(f"Generated {obj.name}: Verts={verts}, Faces={faces}, Mats={len(mats)} ({mats})")
    assert verts > 200, f"Mesh too simple: {verts} vertices"
    assert len(mats) >= 4, f"Materials missing: {mats}"

print("\n=== 📸 Rendering 3 User-Image Houseplants for Verification ===")

# -------------------------------------------------------------
# 1. 吊り下げマクラメ・ハンギングプランター (画像1トレース)
# -------------------------------------------------------------
print("Rendering 1: HANGING_MACRAME...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

obj_hang = generate_procedural_prop_mesh(
    context=bpy.context,
    category="HOUSEPLANT",
    name="Hanging_Macrame_Planter",
    houseplant_style='HANGING_MACRAME',
    houseplant_density='HIGH',
    houseplant_pot_material='TERRACOTTA',
    houseplant_leaf_color='VIBRANT_GREEN',
    seed=101
)

cam_data = bpy.data.cameras.new("Cam1")
cam_obj = bpy.data.objects.new("Cam1", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.7, -1.8, 0.4)
cam_obj.rotation_euler = (1.45, 0.0, 0.35)
bpy.context.scene.camera = cam_obj

world = bpy.data.worlds.new("DarkRoom1")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs['Color'].default_value = (0.02, 0.02, 0.025, 1.0)

sun = bpy.data.lights.new("Sun1", type='SUN')
sun.energy = 2.5
sun_obj = bpy.data.objects.new("Sun1", sun)
sun_obj.rotation_euler = (0.8, 0.2, 0.9)
bpy.context.collection.objects.link(sun_obj)

render = bpy.context.scene.render
render.resolution_x = 720
render.resolution_y = 960
out_hang = r"z:\MeshCreator\test_render_hanging_macrame.png"
render.filepath = out_hang
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_hang}")

# -------------------------------------------------------------
# 2. 脚付き聖杯石鉢・サンスベリア (画像2トレース)
# -------------------------------------------------------------
print("Rendering 2: PEDESTAL_URN...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

obj_urn = generate_procedural_prop_mesh(
    context=bpy.context,
    category="HOUSEPLANT",
    name="Pedestal_Urn_Sansevieria",
    houseplant_style='PEDESTAL_URN',
    houseplant_density='MEDIUM',
    houseplant_pot_material='ANTIQUE_STONE',
    houseplant_leaf_color='DEEP_FOREST',
    houseplant_variegated=True,
    seed=202
)

cam_data2 = bpy.data.cameras.new("Cam2")
cam_obj2 = bpy.data.objects.new("Cam2", cam_data2)
bpy.context.collection.objects.link(cam_obj2)
cam_obj2.location = (0.65, -1.1, 0.45)
cam_obj2.rotation_euler = (1.35, 0.0, 0.55)
bpy.context.scene.camera = cam_obj2

sun2 = bpy.data.lights.new("Sun2", type='SUN')
sun2.energy = 2.8
sun_obj2 = bpy.data.objects.new("Sun2", sun2)
sun_obj2.rotation_euler = (0.7, -0.3, 0.8)
bpy.context.collection.objects.link(sun_obj2)

render.resolution_x = 720
render.resolution_y = 960
out_urn = r"z:\MeshCreator\test_render_pedestal_urn.png"
render.filepath = out_urn
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_urn}")

# -------------------------------------------------------------
# 3. 床置き大型アレカヤシ (画像3トレース)
# -------------------------------------------------------------
print("Rendering 3: FLOOR_PALM...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

obj_palm = generate_procedural_prop_mesh(
    context=bpy.context,
    category="HOUSEPLANT",
    name="Floor_Areca_Palm",
    houseplant_style='FLOOR_PALM',
    houseplant_density='HIGH',
    houseplant_pot_material='GLAZED_CERAMIC',
    houseplant_leaf_color='VIBRANT_GREEN',
    seed=303
)

cam_data3 = bpy.data.cameras.new("Cam3")
cam_obj3 = bpy.data.objects.new("Cam3", cam_data3)
bpy.context.collection.objects.link(cam_obj3)
cam_obj3.location = (1.2, -1.8, 0.85)
cam_obj3.rotation_euler = (1.30, 0.0, 0.58)
bpy.context.scene.camera = cam_obj3

sun3 = bpy.data.lights.new("Sun3", type='SUN')
sun3.energy = 3.0
sun_obj3 = bpy.data.objects.new("Sun3", sun3)
sun_obj3.rotation_euler = (0.75, 0.25, 0.7)
bpy.context.collection.objects.link(sun_obj3)

render.resolution_x = 720
render.resolution_y = 960
out_palm = r"z:\MeshCreator\test_render_floor_palm.png"
render.filepath = out_palm
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_palm}")

print("\n=== ALL HOUSEPLANT TESTS & RENDERS PASSED 100% ===")
