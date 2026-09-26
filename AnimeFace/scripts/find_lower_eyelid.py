import bpy

face = bpy.data.objects.get("Face")
vg = face.vertex_groups.get("grp_eye")
# 目の下まぶたラインの頂点を特定する
lower_verts = []
for v in face.data.vertices:
    if any(g.group == vg.index for g in v.groups):
        if -0.06 <= v.co.z <= -0.01:
            lower_verts.append((v.index, v.co))

print(f"Lower eyelid candidates (count={len(lower_verts)}):")
for idx, co in sorted(lower_verts, key=lambda item: item[1].x):
    print(f"  v[{idx:3d}]: x={co.x:.4f}, y={co.y:.4f}, z={co.z:.4f}")
