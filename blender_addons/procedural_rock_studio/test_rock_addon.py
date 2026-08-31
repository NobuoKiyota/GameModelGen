import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Modern PC Desk & Office Chair Presets (v7.0) ===")

# 1. Test Modern PC Desk with Monitor Riser & Steel Loop Legs
desk_1 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TABLE",
    name="Test_Modern_PC_Desk_Riser",
    table_shape="MONITOR_RISER_DESK",
    table_leg_style="STEEL_LOOP",
    size_x=1.6,
    size_y=0.75,
    size_z=0.72,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1201
)
print(f"-> 1. Modern PC Desk (Monitor Riser + Steel Loop): Verts={len(desk_1.data.vertices)}, Polys={len(desk_1.data.polygons)}")

# 2. Test Modern Office Task Chair (5-Star Casters + Gas Cylinder + Ergonomic Back)
chair_office = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Modern_Office_Task_Chair",
    chair_type="OFFICE_TASK_CHAIR",
    size_x=0.62,
    size_y=0.60,
    size_z=0.96,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1202
)
print(f"-> 2. Modern Office Task Chair (5-Star Base): Verts={len(chair_office.data.vertices)}, Polys={len(chair_office.data.polygons)}")

# 3. Test Modern Eames Shell Chair
chair_shell = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Modern_Shell_Chair",
    chair_type="MODERN_SHELL_CHAIR",
    size_x=0.52,
    size_y=0.50,
    size_z=0.84,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1203
)
print(f"-> 3. Modern Shell Chair (Splayed Legs): Verts={len(chair_shell.data.vertices)}, Polys={len(chair_shell.data.polygons)}")

# 4. Test L-Shaped Studio Desk with Steel Pipe Legs
desk_L = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TABLE",
    name="Test_L_Shaped_Studio_Desk",
    table_shape="L_SHAPED_CORNER",
    table_leg_style="STEEL_PIPE",
    size_x=2.0,
    size_y=1.4,
    size_z=0.72,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=1204
)
print(f"-> 4. L-Shaped Studio Desk (Steel Pipe): Verts={len(desk_L.data.vertices)}, Polys={len(desk_L.data.polygons)}")

print("=== ALL MODERN PC DESK & OFFICE CHAIR PRESET TESTS PASSED! ===")
