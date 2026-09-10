import bpy, sys, random, math
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)
from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

from procedural_rock_studio.generators.telescope_gen import create_procedural_telescope
from procedural_rock_studio.generators.cleanup_helper import cleanup_old_telescope

ctx = bpy.context
styles = ["MODERN_REFRACTOR","ANTIQUE_BRASS","SMART_DIGITAL","CASSEGRAIN_POP","TACTICAL_COMPACT"]
seeds_to_test = [1001, 2002, 3003]
print("=== Seed Variation Test ===")
results = {}
for style in styles:
    vcount_list = []
    for seed in seeds_to_test:
        cleanup_old_telescope(ctx, None, "TestTelescope")
        root = create_procedural_telescope(ctx, name="TestTelescope", style=style, seed=seed)
        total_verts = sum(len(o.data.vertices) for o in root.children_recursive if o.type=="MESH")
        vcount_list.append(total_verts)
        bpy.data.objects.remove(root, do_unlink=True)
    all_same = len(set(vcount_list)) == 1
    status = "FAIL (ALL SAME!)" if all_same else "PASS (varied)"
    print(f"[{style}] seeds={seeds_to_test} verts={vcount_list} -> {status}")
    results[style] = not all_same

all_pass = all(results.values())
print("=== OVERALL:", "ALL PASS" if all_pass else "FAIL - some styles identical ===")
