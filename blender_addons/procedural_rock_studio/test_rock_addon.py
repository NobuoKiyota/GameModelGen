import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Ultra-Rugged Jagged Craggy Rock Generator (v6.3) ===")

# 1. Test Jagged Crag (Default Rugged)
rock_jagged = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="ROCK",
    name="Test_Rock_Jagged_Crag",
    style="JAGGED_CRAG",
    size_x=2.4,
    size_y=2.2,
    size_z=1.8,
    roughness=0.85,
    chisel_strength=0.9,
    crack_depth=0.6,
    big_chunk_cuts=3,
    create_debris=True,
    debris_count=6,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=701
)
print(f"-> 1. Jagged Crag generated: Verts={len(rock_jagged.data.vertices)}, Polys={len(rock_jagged.data.polygons)}")

# 2. Test Columnar Cliff
rock_cliff = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="ROCK",
    name="Test_Rock_Columnar_Cliff",
    style="COLUMNAR_CLIFF",
    size_x=3.0,
    size_y=1.5,
    size_z=2.5,
    roughness=0.8,
    chisel_strength=0.95,
    big_chunk_cuts=4,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=702
)
print(f"-> 2. Columnar Cliff generated: Verts={len(rock_cliff.data.vertices)}, Polys={len(rock_cliff.data.polygons)}")

# 3. Test Volcanic Spike
rock_spike = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="ROCK",
    name="Test_Rock_Volcanic_Spike",
    style="VOLCANIC_SPIKE",
    size_x=1.6,
    size_y=1.6,
    size_z=3.2,
    roughness=0.9,
    chisel_strength=0.9,
    big_chunk_cuts=3,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=703
)
print(f"-> 3. Volcanic Spike generated: Verts={len(rock_spike.data.vertices)}, Polys={len(rock_spike.data.polygons)}")

print("=== ALL RUGGED CRAGGY ROCK TESTS PASSED PERFECTLY! ===")
