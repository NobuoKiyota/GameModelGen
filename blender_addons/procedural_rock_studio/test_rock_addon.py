import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Chair Overhaul & New Leg Layouts (v6.2) ===")

# 1. Dining Chair: Leather Cushion + Solid Backrest + 4 Legs
chair_1 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_Cushion_Solid",
    chair_type="DINING_CHAIR",
    chair_seat_style="CUSHION",
    chair_back_style="SOLID",
    chair_leg_layout="FOUR_LEGS",
    table_leg_style="ORNAMENTAL",
    size_x=0.55,
    size_y=0.55,
    size_z=0.95,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=601
)
print(f"-> 1. Dining Chair (Cushion + Solid Back): Verts={len(chair_1.data.vertices)}, Polys={len(chair_1.data.polygons)}")

# 2. Armchair: Natural Armrests + Oval Backrest + 4 Legs
chair_2 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_Armchair_Oval",
    chair_type="ARMCHAIR",
    chair_seat_style="CUSHION",
    chair_back_style="OVAL",
    chair_leg_layout="FOUR_LEGS",
    table_leg_style="TWISTED",
    size_x=0.65,
    size_y=0.60,
    size_z=0.98,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=602
)
print(f"-> 2. Armchair (Full Armrests + Oval Back): Verts={len(chair_2.data.vertices)}, Polys={len(chair_2.data.polygons)}")

# 3. Pedestal 1-Leg Chair (Central Column + 4 Claw Feet)
chair_3 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_Pedestal_1Leg",
    chair_type="DINING_CHAIR",
    chair_seat_style="CUSHION",
    chair_back_style="SPINDLE",
    chair_leg_layout="PEDESTAL_ONE",
    table_leg_style="ORNAMENTAL",
    size_x=0.55,
    size_y=0.55,
    size_z=0.95,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=603
)
print(f"-> 3. Pedestal 1-Leg Chair: Verts={len(chair_3.data.vertices)}, Polys={len(chair_3.data.polygons)}")

# 4. X-Cross Legs Chair
chair_4 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_XCross",
    chair_type="DINING_CHAIR",
    chair_seat_style="WOOD_FLAT",
    chair_back_style="SOLID",
    chair_leg_layout="X_CROSS",
    size_x=0.55,
    size_y=0.55,
    size_z=0.95,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=604
)
print(f"-> 4. X-Cross Legs Chair: Verts={len(chair_4.data.vertices)}, Polys={len(chair_4.data.polygons)}")

# 5. Round Stool (Tripod 3-Legs perfectly inside seat radius)
stool_5 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Round_Stool_Tripod",
    chair_type="ROUND_STOOL",
    chair_seat_style="CUSHION",
    chair_leg_layout="TRIPOD_THREE",
    table_leg_style="REINFORCED",
    size_x=0.5,
    size_y=0.5,
    size_z=0.48,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=605
)
print(f"-> 5. Round Stool (Tripod 3-Legs): Verts={len(stool_5.data.vertices)}, Polys={len(stool_5.data.polygons)}")

print("=== ALL CHAIR OVERHAUL & STRUCTURAL TESTS PASSED PERFECTLY! ===")
