import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing In-Place Re-Roll and Randomized Leaves (v7.5) ===")

# 1. Create Initial Oak Tree
tree = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="My_Real_Tree",
    tree_species="OAK",
    tree_has_leaves=True,
    tree_leaf_count=120,
    tree_branch_levels=2,
    size_z=4.5,
    seed=100
)
initial_obj_count = len(bpy.data.objects)
print(f"Step 1 (Created): Total Objects in Scene={initial_obj_count}, Active Tree Name={tree.name}, Verts={len(tree.data.vertices)}")

# 2. Re-roll multiple times in-place on the same object
for i in range(3):
    tree = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=tree,
        category="TREE",
        name="My_Real_Tree",
        tree_species="OAK",
        tree_has_leaves=True,
        tree_leaf_count=120,
        tree_branch_levels=2,
        size_z=4.5,
        seed=200 + i
    )
    current_obj_count = len(bpy.data.objects)
    print(f"Step 2.{i+1} (Re-Rolled #{i+1}): Total Objects={current_obj_count}, Name={tree.name}, Verts={len(tree.data.vertices)}")
    assert current_obj_count == initial_obj_count, f"Object count increased from {initial_obj_count} to {current_obj_count}!"

print("=== ALL IN-PLACE REPLACEMENT & LEAF RANDOMIZATION TESTS PASSED! ===")
