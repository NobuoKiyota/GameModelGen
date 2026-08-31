import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Clean Single Rock (Debris Disabled) (v6.7) ===")

# Test Single Clean Crag (No Debris)
crag_clean = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CRAG",
    name="Test_Clean_Crag",
    style="JAGGED_CRAG",
    size_x=2.5,
    size_y=2.2,
    size_z=1.8,
    roughness=0.8,
    chisel_strength=0.85,
    big_chunk_cuts=2,
    create_debris=False,
    debris_count=0,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    seed=1101
)
print(f"-> Single Clean Crag generated: Verts={len(crag_clean.data.vertices)}, Polys={len(crag_clean.data.polygons)}")

print("=== CLEAN SINGLE ROCK TEST PASSED! ===")
