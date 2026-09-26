import bpy
from mathutils import Vector

# Let's inspect how the original skinning was created
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Check all mesh objects transforms and their armature modifier settings
print("=== INSPECTING ALL MESHES AND ARMATURE MODIFIERS ===")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        arm_mods = [m for m in obj.modifiers if m.type == 'ARMATURE']
        print(f"\n[{obj.name}]")
        print(f"  loc: {obj.location}, rot: {obj.rotation_euler}, scale: {obj.scale}")
        print(f"  parent: {obj.parent.name if obj.parent else None}")
        for m in arm_mods:
            print(f"  ArmatureMod: target={m.object.name if m.object else None}, bind_coords={getattr(m, 'use_deform_delay', None)}")
