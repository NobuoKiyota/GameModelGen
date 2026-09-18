import bpy
import sys

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
from procedural_rock_studio.generators import generate_procedural_prop_mesh

bpy.ops.wm.read_factory_settings(use_empty=True)
rock_studio_addon.register()

door_frame = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="DOOR",
    name="OpDoor",
    seed=7,
    size_x=2.2, size_y=0.5, size_z=2.6,
    door_arch_style='GOTHIC_POINTED',
    door_pillar_shape='OCTAGONAL',
    door_pillar_width=0.42,
    door_column_height=1.7,
    door_has_keystone=True,
    door_strap_style='DOUBLE_DIAGONAL',
    door_stud_pattern='DIAMOND',
    door_handle_style='DROP_KNOCKER',
    door_has_hinges=True,
    door_has_edge_trim=True,
    door_edge_trim_width=0.06,
    door_wood_material='DARK_WALNUT',
    door_iron_style='RUSTED',
    door_damage=0.40,
    door_weathering=0.60,
    door_moss_amount=0.15,
    door_open_angle=0.0,
    door_open_direction='OUTWARD',
    door_combine=False,
)

props = bpy.context.scene.prop_studio_props
props.export_folder = r"Z:\MeshCreator\exports"
props.asset_name = "OpDoor"
props.door_destruction_shard_count = 10
props.door_destruction_frame_count = 40

bpy.context.view_layer.objects.active = door_frame
door_frame.select_set(True)

result = bpy.ops.mesh.generate_door_destruction()
print("Operator result:", result)

for o in bpy.data.objects:
    print("  obj:", o.name, o.type)

import glob
fbx_files = glob.glob(r"Z:\MeshCreator\exports\OpDoor*.fbx")
print("FBX files:", fbx_files)
for f in fbx_files:
    import os
    print(f"  {f} size={os.path.getsize(f)} bytes")

print("OPERATOR TEST DONE")
