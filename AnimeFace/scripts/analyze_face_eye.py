import bpy

face = bpy.data.objects.get("Face")
# Faceの頂点のうち、アイラインを構成しているポリゴン/頂点を特定する
# CharacterBaseマテリアルのUV座標または頂点位置を調べる
mesh = face.data
uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None

print(f"Face vertices: {len(mesh.vertices)}, Polygons: {len(mesh.polygons)}")
vg_eye = face.vertex_groups.get("grp_eye")
eye_vert_indices = set()
if vg_eye:
    for v in mesh.vertices:
        for g in v.groups:
            if g.group == vg_eye.index and g.weight > 0.1:
                eye_vert_indices.add(v.index)

print(f"grp_eye count: {len(eye_vert_indices)}")

# 目の周りのエッジ・ポリゴンをリストアップ
upper_rim = []
for p in mesh.polygons:
    p_verts = list(p.vertices)
    if all(vi in eye_vert_indices for vi in p_verts):
        # check if it's upper rim (z > 0.01)
        cos = [mesh.vertices[vi].co for vi in p_verts]
        if any(c.z > 0.01 for c in cos):
            # check mean coordinates
            mz = sum(c.z for c in cos) / len(cos)
            mx = sum(c.x for c in cos) / len(cos)
            my = sum(c.y for c in cos) / len(cos)
            # print polygon info
            pass

# アイライン頂点群を特定するために、grp_eyeの頂点をZ座標順にダンプ
print("\n=== grp_eye vertices (sorted by X) ===")
eye_verts_sorted = sorted([(vi, mesh.vertices[vi].co) for vi in eye_vert_indices], key=lambda x: x[1].x)
for vi, co in eye_verts_sorted:
    print(f"  v[{vi:3d}]: ({co.x:8.4f}, {co.y:8.4f}, {co.z:8.4f})")
