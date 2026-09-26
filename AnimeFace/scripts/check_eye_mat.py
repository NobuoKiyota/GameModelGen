import bpy

eye = bpy.data.objects.get("Eye")
print(f"Eye materials: {[m.name for m in eye.data.materials]}")
mw = eye.matrix_world
zs = [v.co.z for v in eye.data.vertices]
ys = [v.co.y for v in eye.data.vertices]
xs = [v.co.x for v in eye.data.vertices]
print(f"Eye local bounds: X=[{min(xs):.4f}, {max(xs):.4f}], Y=[{min(ys):.4f}, {max(ys):.4f}], Z=[{min(zs):.4f}, {max(zs):.4f}]")
print(f"Center: ({sum(xs)/len(xs):.4f}, {sum(ys)/len(ys):.4f}, {sum(zs)/len(zs):.4f})")
