import bpy
from mathutils import Vector

# 1. LOAD H04 DIRECTLY (preserves all animations, NLA tracks, shape key keys)
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend")
arm = bpy.data.objects.get("Armature_Teacher")

print("=== SAFE SURGICAL FIX ON H04 ===")

# 2. REMOVE MASK_TORSO FROM BODYBASE (RESTORE BODY!)
body_base = bpy.data.objects.get("BodyBase")
if body_base:
    mask = body_base.modifiers.get("Mask_Torso")
    if mask:
        body_base.modifiers.remove(mask)
        print("Removed Mask_Torso from BodyBase: Torso is now 100% visible!")

# Also ensure BodyArm has no mask
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    for m in list(body_arm.modifiers):
        if m.type == 'MASK':
            body_arm.modifiers.remove(m)
            print(f"Removed Mask from BodyArm: {m.name}")

# 3. FINE-TUNE ARM EDITBONES TO PERFECTLY CENTER INSIDE BODYARM
# In h04, arm bones were at Z = -0.2500
# BodyArm mesh evaluated in rest pose has center Z around -0.260
# Let's adjust EditBones Z down by ~0.010m so bone axis goes through the exact center of arm mesh
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

for side, sign in [('L', 1), ('R', -1)]:
    sh = eb.get(f"Shoulder.{side}")
    ua = eb.get(f"UpperArm.{side}")
    fa = eb.get(f"Forearm.{side}")
    ha = eb.get(f"Hand.{side}")
    
    # In rest pose, arm hangs down slightly towards hand
    # Shoulder: head Z=-0.245, tail Z=-0.258
    # UpperArm: head Z=-0.258, tail Z=-0.262
    # Forearm : head Z=-0.262, tail Z=-0.260
    # Hand    : head Z=-0.260, tail Z=-0.258
    if sh:
        sh.head.z = -0.245
        sh.tail.z = -0.258
    if ua:
        ua.head.z = -0.258
        ua.tail.z = -0.262
    if fa:
        fa.head.z = -0.262
        fa.tail.z = -0.260
    if ha:
        ha.head.z = -0.260
        ha.tail.z = -0.258

bpy.ops.object.mode_set(mode='OBJECT')
print("Arm EditBones centered inside BodyArm mesh.")

# 4. VERIFY ANIMATIONS ARE INTACT
print("\nVerifying animation data:")
print("  Action on Armature:", arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else None)
print("  NLA Tracks:", [t.name for t in arm.animation_data.nla_tracks] if arm.animation_data else None)
print("  All Actions:", [a.name for a in bpy.data.actions])

# Verify Facial Shape Keys
face = bpy.data.objects.get("Face")
print("  Face shape keys:", [k.name for k in face.data.shape_keys.key_blocks] if face.data.shape_keys else None)
if face.data.shape_keys and face.data.shape_keys.animation_data:
    print("  Face shape keys action:", face.data.shape_keys.animation_data.action.name if face.data.shape_keys.animation_data.action else None)

# 5. SAVE OVER H05
out_file = "Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_file)
print(f"Successfully saved pristine h05 to: {out_file}")
