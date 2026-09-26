import bpy

face = bpy.data.objects['Face']
guide_m = bpy.data.objects.get('GUIDE_mouth_center')
guide_e = bpy.data.objects.get('GUIDE_eye_center')

print("Face modifiers:", [f"{m.name}({m.type})" for m in face.modifiers])

# Find all vertices around mouth
near_mouth = []
for i, v in enumerate(face.data.vertices):
    dist = (v.co - guide_m.location).length
    if dist < 0.06:
        near_mouth.append((i, dist, v.co))

print(f"\nMouth vertices within 6cm of GUIDE_mouth_center ({len(near_mouth)}):")
for idx, d, co in sorted(near_mouth, key=lambda x: (x[2].z, x[2].x)):
    print(f"  v[{idx:3d}]: co=({co.x:+.4f}, {co.y:+.4f}, {co.z:+.4f}), dist={d:.4f}")

# Check eye components: Eye, Eyelash.001, Eyelash.002, Eyelash.003, DoubleLid, Eyebrow
eye_objs = ['Eye', 'Eyelash.001', 'Eyelash.002', 'Eyelash.003', 'DoubleLid', 'Eyebrow']
for name in eye_objs:
    o = bpy.data.objects.get(name)
    if o:
        zs = [v.co.z for v in o.data.vertices]
        ys = [v.co.y for v in o.data.vertices]
        xs = [v.co.x for v in o.data.vertices]
        print(f"\n{name} ({len(o.data.vertices)} verts):")
        print(f"  X: [{min(xs):.4f}, {max(xs):.4f}], Y: [{min(ys):.4f}, {max(ys):.4f}], Z: [{min(zs):.4f}, {max(zs):.4f}]")
        print(f"  Modifiers: {[f'{m.name}({m.type})' for m in o.modifiers]}")
