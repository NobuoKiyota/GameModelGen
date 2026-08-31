import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Coexistence of Round Rock & Jagged Crag (v6.4) ===")

# 1. Test Traditional Round Boulder (ROCK)
rock_round = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="ROCK",
    name="Test_Round_Boulder",
    style="BOULDER",
    size_x=2.2,
    size_y=2.0,
    size_z=1.6,
    roughness=0.7,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=801
)
print(f"-> 1. Traditional Round Boulder (ROCK): Verts={len(rock_round.data.vertices)}, Polys={len(rock_round.data.polygons)}")

# 2. Test Ultra-Rugged Jagged Crag (CRAG)
crag_jagged = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CRAG",
    name="Test_Jagged_Crag",
    style="JAGGED_CRAG",
    size_x=2.4,
    size_y=2.2,
    size_z=1.8,
    roughness=0.85,
    chisel_strength=0.9,
    big_chunk_cuts=3,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=802
)
print(f"-> 2. Ultra-Rugged Jagged Crag (CRAG): Verts={len(crag_jagged.data.vertices)}, Polys={len(crag_jagged.data.polygons)}")

print("=== ALL ROUND ROCK & JAGGED CRAG PRESET TESTS PASSED! ===")
