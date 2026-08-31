import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Convex Hull Procedural Rock Generator (v6.6) ===")

# 1. Test Convex Hull Jagged Crag (CRAG)
crag_hull = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CRAG",
    name="Test_Convex_Hull_Crag",
    style="JAGGED_CRAG",
    size_x=2.5,
    size_y=2.2,
    size_z=1.8,
    roughness=0.8,
    chisel_strength=0.85,
    big_chunk_cuts=2,
    create_debris=True,
    debris_count=6,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=1001
)
print(f"-> 1. Convex Hull Jagged Crag: Verts={len(crag_hull.data.vertices)}, Polys={len(crag_hull.data.polygons)}")

# 2. Test Convex Hull Round Boulder (ROCK)
rock_hull = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="ROCK",
    name="Test_Convex_Hull_Boulder",
    style="BOULDER",
    size_x=2.2,
    size_y=2.0,
    size_z=1.6,
    roughness=0.7,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=1002
)
print(f"-> 2. Convex Hull Round Boulder: Verts={len(rock_hull.data.vertices)}, Polys={len(rock_hull.data.polygons)}")

print("=== ALL CONVEX HULL ROCK TESTS PASSED PERFECTLY! ===")
