import bpy
import os
import sys

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio.generators.core_orchestrator import generate_procedural_prop_mesh
from procedural_rock_studio.utils.baker import bake_procedural_material_to_pbr

bpy.ops.wm.read_factory_settings(use_empty=True)

obj = generate_procedural_prop_mesh(
    context=bpy.context,
    category="WATER",
    name="Test_Lake_Bake",
    water_shape="LAKE",
    water_color_type="TROPICAL",
    size_x=4.0, size_y=4.0, size_z=0.5,
    seed=10
)

out_dir = r"z:\MeshCreator\exports\test_water_bake"
res = bake_procedural_material_to_pbr(obj, out_dir, res=512)
print("Bake result:", res)
for k, v in res.items():
    if os.path.exists(v):
        print(f"  {k}: {v} (size={os.path.getsize(v)} bytes)")
