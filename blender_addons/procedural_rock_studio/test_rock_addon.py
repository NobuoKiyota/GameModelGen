import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Advanced Real Tree with Dual-Material Slots (v7.3) ===")

# 1. Test Oak Tree (Cross Billboard Leaves + Dual Material)
oak_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Oak_DualMat",
    tree_species="OAK",
    tree_has_leaves=True,
    tree_leaf_style="QUAD_CROSS",
    tree_leaf_count=100,
    tree_branch_levels=2,
    tree_curvature=0.7,
    size_x=3.5,
    size_y=3.5,
    size_z=4.5,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=3001
)
print(f"-> 1. Oak Tree (Cross Leaves): Verts={len(oak_tree.data.vertices)}, Polys={len(oak_tree.data.polygons)}, Mats={len(oak_tree.data.materials)}")

# 2. Test Japanese Maple (Canopy Volume)
maple_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Maple_CanopyVol",
    tree_species="JAPANESE_MAPLE",
    tree_has_leaves=True,
    tree_leaf_style="CANOPY_VOLUME",
    tree_leaf_count=80,
    tree_branch_levels=2,
    tree_curvature=0.8,
    size_x=3.0,
    size_y=3.0,
    size_z=3.8,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=3002
)
print(f"-> 2. Japanese Maple (Canopy Volume): Verts={len(maple_tree.data.vertices)}, Polys={len(maple_tree.data.polygons)}, Mats={len(maple_tree.data.materials)}")

# 3. Test Pine Tree (Conifer Tiers)
pine_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Pine_Conifer",
    tree_species="PINE",
    tree_has_leaves=True,
    tree_leaf_style="QUAD_CROSS",
    tree_leaf_count=80,
    tree_branch_levels=2,
    tree_curvature=0.4,
    size_x=2.8,
    size_y=2.8,
    size_z=5.0,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=3003
)
print(f"-> 3. Pine Tree (Conifer Tiers): Verts={len(pine_tree.data.vertices)}, Polys={len(pine_tree.data.polygons)}, Mats={len(pine_tree.data.materials)}")

# 4. Test Palm Tree (Fronds + Leaflets)
palm_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Palm_Fronds",
    tree_species="PALM",
    tree_has_leaves=True,
    tree_branch_levels=1,
    size_x=3.0,
    size_y=3.0,
    size_z=4.2,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=3004
)
print(f"-> 4. Palm Tree (Fronds & Leaflets): Verts={len(palm_tree.data.vertices)}, Polys={len(palm_tree.data.polygons)}, Mats={len(palm_tree.data.materials)}")

print("=== ALL ADVANCED REAL TREE (v7.3) TESTS PASSED! ===")
