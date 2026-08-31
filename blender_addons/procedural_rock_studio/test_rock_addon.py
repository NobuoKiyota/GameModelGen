import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Antique Furniture Suite (Chair, Chest, Bed) v6.1 ===")

# 1. Test Chair (Dining Chair, Ornamental Legs)
chair_dining = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_Dining",
    chair_type="DINING_CHAIR",
    table_leg_style="ORNAMENTAL",
    size_x=0.55,
    size_y=0.55,
    size_z=0.95,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=301
)
print(f"-> Dining Chair generated: Verts={len(chair_dining.data.vertices)}, Polys={len(chair_dining.data.polygons)}")

# 2. Test Chair (Armchair, Twisted Legs)
chair_arm = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHAIR",
    name="Test_Chair_Armchair",
    chair_type="ARMCHAIR",
    table_leg_style="TWISTED",
    size_x=0.65,
    size_y=0.60,
    size_z=0.98,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=302
)
print(f"-> Armchair (Twisted) generated: Verts={len(chair_arm.data.vertices)}, Polys={len(chair_arm.data.polygons)}")

# 3. Test Chest (3 Tiers, Ring Handle)
chest_3 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHEST",
    name="Test_Chest_3Tiers",
    chest_tiers=3,
    chest_handle_style="RING",
    size_x=1.4,
    size_y=0.6,
    size_z=1.1,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=401
)
print(f"-> 3-Tier Chest (Ring Handle) generated: Verts={len(chest_3.data.vertices)}, Polys={len(chest_3.data.polygons)}")

# 4. Test Chest (4 Tiers, Knob Handle)
chest_4 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CHEST",
    name="Test_Chest_4Tiers",
    chest_tiers=4,
    chest_handle_style="KNOB",
    size_x=1.5,
    size_y=0.6,
    size_z=1.3,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=402
)
print(f"-> 4-Tier Chest (Knob Handle) generated: Verts={len(chest_4.data.vertices)}, Polys={len(chest_4.data.polygons)}")

# 5. Test Bed (Double Size, Ornamental Posts)
bed_double = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="BED",
    name="Test_Bed_Double",
    bed_size="DOUBLE",
    column_style="ORNAMENTAL",
    size_x=1.6,
    size_y=2.1,
    size_z=1.4,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=501
)
print(f"-> Double Bed (Ornamental Posts) generated: Verts={len(bed_double.data.vertices)}, Polys={len(bed_double.data.polygons)}")

print("=== ALL CHAIR, CHEST, BED PRESET TESTS PASSED PERFECTLY! ===")
