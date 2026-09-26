import bpy

face = bpy.data.objects['Face']
# Let's inspect polygons forming the lips
mouth_verts = [26, 203, 27, 30, 32, 218, 31, 33, 204, 34, 474, 475, 476, 481, 482]
print("Mouth lip polygons:")
for p in face.data.polygons:
    if any(vi in mouth_verts for vi in p.vertices):
        coords = [face.data.vertices[vi].co for vi in p.vertices]
        print(f"poly {p.index}: verts={list(p.vertices)}")

print("\nLip vertices coordinates:")
for vi in mouth_verts:
    co = face.data.vertices[vi].co
    print(f"  v[{vi:3d}]: ({co.x:+.4f}, {co.y:+.4f}, {co.z:+.4f})")
