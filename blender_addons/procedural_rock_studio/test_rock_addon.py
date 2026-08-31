import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Direct Preset Categories: PC_DESK & OFFICE_CHAIR (v7.1) ===")

# 1. Direct Category: PC_DESK
desk_direct = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="PC_DESK",
    name="Test_PC_Desk_Direct",
    table_shape="MONITOR_RISER_DESK",
    table_leg_style="STEEL_LOOP",
    size_x=1.6,
    size_y=0.75,
    size_z=0.72,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1301
)
print(f"-> 1. Direct Category PC_DESK: Verts={len(desk_direct.data.vertices)}, Polys={len(desk_direct.data.polygons)}")

# 2. Direct Category: OFFICE_CHAIR
chair_direct = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="OFFICE_CHAIR",
    name="Test_Office_Chair_Direct",
    chair_type="OFFICE_TASK_CHAIR",
    size_x=0.62,
    size_y=0.60,
    size_z=0.96,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1302
)
print(f"-> 2. Direct Category OFFICE_CHAIR: Verts={len(chair_direct.data.vertices)}, Polys={len(chair_direct.data.polygons)}")

print("=== ALL DIRECT PRESET CATEGORY TESTS PASSED! ===")
