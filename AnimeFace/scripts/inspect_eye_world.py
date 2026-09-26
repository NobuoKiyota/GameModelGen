import bpy
from mathutils import Vector

def inspect_obj(name):
    obj = bpy.data.objects.get(name)
    if not obj: return
    mw = obj.matrix_world
    world_coords = [mw @ v.co for v in obj.data.vertices]
    xs = [co.x for co in world_coords]
    ys = [co.y for co in world_coords]
    zs = [co.z for co in world_coords]
    print(f"\n[{name}] (World Coords)")
    print(f"  Count: {len(world_coords)}")
    print(f"  X: [{min(xs):.4f}, {max(xs):.4f}], mean={sum(xs)/len(xs):.4f}")
    print(f"  Y: [{min(ys):.4f}, {max(ys):.4f}], mean={sum(ys)/len(ys):.4f}")
    print(f"  Z: [{min(zs):.4f}, {max(zs):.4f}], mean={sum(zs)/len(zs):.4f}")

for n in ["Face", "Eye", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003", "Eyebrow"]:
    inspect_obj(n)

# Faceのgrp_eye頂点も確認
face = bpy.data.objects.get("Face")
vg_eye = face.vertex_groups.get("grp_eye")
if vg_eye:
    eye_verts = [face.matrix_world @ v.co for v in face.data.vertices if any(g.group == vg_eye.index for g in v.groups)]
    print(f"\n[Face: grp_eye] Count: {len(eye_verts)}")
    zs = [v.z for v in eye_verts]
    ys = [v.y for v in eye_verts]
    xs = [v.x for v in eye_verts]
    print(f"  X: [{min(xs):.4f}, {max(xs):.4f}]")
    print(f"  Y: [{min(ys):.4f}, {max(ys):.4f}]")
    print(f"  Z: [{min(zs):.4f}, {max(zs):.4f}]")
