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

print("=== 🕯️ Testing Procedural Antique Candle Stand Engine ===")

styles = ['HANGING_CHANDELIER', 'TABLE_CANDELABRA', 'CHAMBERSTICK', 'WALL_SCONCE']
for style in styles:
    print(f"\n--- Testing Style: {style} ---")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="CANDLE_STAND",
        name=f"Test_{style}",
        candle_stand_style=style,
        candle_count=6 if style == 'HANGING_CHANDELIER' else 4,
        candle_melt_level=0.6,
        candle_has_flame=True,
        candle_add_lights=True,
        candle_holder_material='FORGED_IRON',
        candle_wax_material='IVORY_BEESWAX',
        seed=42
    )

    assert obj is not None, f"Failed to generate {style}"
    assert obj.type == 'MESH', f"Generated object is not a mesh: {obj.type}"
    verts = len(obj.data.vertices)
    faces = len(obj.data.polygons)
    mats = [m.name for m in obj.data.materials if m]
    lights = [c for c in obj.children if c.type == 'LIGHT']

    print(f"Generated {obj.name}: Verts={verts}, Faces={faces}, Mats={len(mats)}, PointLights={len(lights)}")
    assert verts > 100, f"Mesh too simple: {verts} vertices"
    assert len(mats) >= 4, f"Materials missing: {mats}"
    assert len(lights) > 0, f"Point lights missing: {len(lights)}"

print("\n--- Generating High-Quality Test Render for HANGING_CHANDELIER ---")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# シャンデリア生成
ch_obj = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CANDLE_STAND",
    name="Antique_Hanging_Chandelier",
    candle_stand_style='HANGING_CHANDELIER',
    candle_count=6,
    candle_melt_level=0.55,
    candle_has_flame=True,
    candle_add_lights=True,
    candle_holder_material='FORGED_IRON',
    candle_wax_material='IVORY_BEESWAX',
    seed=123
)

# カメラ設置
cam_data = bpy.data.cameras.new("TestCam")
cam_obj = bpy.data.objects.new("TestCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (1.5, -1.8, 0.8)
cam_obj.rotation_euler = (1.15, 0.0, 0.65)
bpy.context.scene.camera = cam_obj

# 背景暗め
world = bpy.data.worlds.new("DarkRoom")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.015, 0.015, 0.02, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5

# 補助ライト
fill_light_data = bpy.data.lights.new("FillLight", type='POINT')
fill_light_data.energy = 60.0
fill_light_data.color = (0.3, 0.4, 0.6)
fill_obj = bpy.data.objects.new("FillLight", fill_light_data)
fill_obj.location = (-1.5, 2.0, 1.5)
bpy.context.collection.objects.link(fill_obj)

# レンダリング設定 (EEVEE / Workbench)
render = bpy.context.scene.render
render.resolution_x = 960
render.resolution_y = 640
out_path = r"z:\MeshCreator\test_render_candle_chandelier.png"
render.filepath = out_path

bpy.ops.render.render(write_still=True)
print(f"Rendered test image saved to: {out_path}")

print("=== ALL ANTIQUE CANDLE STAND TESTS PASSED 100% ===")
