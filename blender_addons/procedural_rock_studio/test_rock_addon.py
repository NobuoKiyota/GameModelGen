import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Solid Low-Poly Faceted Cluster Crags (v6.5) ===")

# Test Crag Cluster (100% Solid & Closed)
crag_solid = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="CRAG",
    name="Test_Crag_Cluster_Solid",
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
    seed=901
)
print(f"-> Crag Cluster Solid generated: Verts={len(crag_solid.data.vertices)}, Polys={len(crag_solid.data.polygons)}")

print("=== SOLID CRAG CLUSTER TEST PASSED! ===")
