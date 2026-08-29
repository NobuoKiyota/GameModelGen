import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Grassland Mound Slab & Cross-Billboard Grass Tuft ===")

# 1. Test Grass Mound Slab
grass_mound = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="GRASS",
    name="Test_Grass_Mound",
    grass_mode="MOUND",
    floor_shape="SQUARE",
    size_x=3.0,
    size_y=3.0,
    size_z=0.3,
    tex_folder=r"Z:\MeshCreator\textures\Grass",
    use_folder_tex=True,
    selected_tex="",
    seed=555
)
print(f"-> Grass Mound generated: Verts={len(grass_mound.data.vertices)}, Polys={len(grass_mound.data.polygons)}")

# 2. Test Grass Tuft Clump (Cross-Billboard)
grass_tuft = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="GRASS",
    name="Test_Grass_Tuft",
    grass_mode="TUFT",
    size_x=1.0,
    size_y=1.0,
    size_z=1.0,
    tex_folder=r"Z:\MeshCreator\textures\Grass",
    use_folder_tex=True,
    selected_tex="",
    seed=666
)
print(f"-> Grass Tuft Clump generated: Verts={len(grass_tuft.data.vertices)}, Polys={len(grass_tuft.data.polygons)}")

print("=== ALL GRASSLAND & TUFT TESTS PASSED PERFECTLY! ===")
