import bpy

face = bpy.data.objects.get("Face")
vg = face.vertex_groups.get("grp_eye")
upper_verts = []
for v in face.data.vertices:
    if any(g.group == vg.index for g in v.groups):
        if 0.02 <= v.co.z <= 0.06:
            upper_verts.append((v.index, v.co))

print(f"Upper eyelid candidates (count={len(upper_verts)}):")
for idx, co in sorted(upper_verts, key=lambda item: item[1].x):
    print(f"  v[{idx:3d}]: x={co.x:.4f}, y={co.y:.4f}, z={co.z:.4f}")
