import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Real Tree Presets (v7.2) ===")

# 1. Test Oak Tree (Broadleaf with Leaves)
oak_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Oak_Tree",
    tree_species="OAK",
    tree_has_leaves=True,
    tree_leaf_count=100,
    tree_branch_levels=2,
    size_x=3.5,
    size_y=3.5,
    size_z=4.5,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=2001
)
print(f"-> 1. Oak Tree (Leaves ON): Verts={len(oak_tree.data.vertices)}, Polys={len(oak_tree.data.polygons)}")

# 2. Test Pine Tree (Conifer)
pine_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Pine_Tree",
    tree_species="PINE",
    tree_has_leaves=True,
    tree_leaf_count=80,
    tree_branch_levels=2,
    size_x=2.8,
    size_y=2.8,
    size_z=5.0,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=2002
)
print(f"-> 2. Pine Tree (Conifer): Verts={len(pine_tree.data.vertices)}, Polys={len(pine_tree.data.polygons)}")

# 3. Test Palm Tree
palm_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Palm_Tree",
    tree_species="PALM",
    tree_has_leaves=False,
    tree_branch_levels=1,
    size_x=3.0,
    size_y=3.0,
    size_z=4.2,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=2003
)
print(f"-> 3. Palm Tree: Verts={len(palm_tree.data.vertices)}, Polys={len(palm_tree.data.polygons)}")

# 4. Test Willow Tree (Bare winter tree without leaves)
willow_tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Test_Willow_Bare_Tree",
    tree_species="WILLOW",
    tree_has_leaves=False,
    tree_branch_levels=2,
    size_x=3.2,
    size_y=3.2,
    size_z=4.0,
    tex_folder=r"Z:\MeshCreator\textures\Wood",
    use_folder_tex=True,
    selected_tex="",
    seed=2004
)
print(f"-> 4. Willow Tree (Bare branches): Verts={len(willow_tree.data.vertices)}, Polys={len(willow_tree.data.polygons)}")

print("=== ALL REAL TREE PRESET TESTS PASSED! ===")
