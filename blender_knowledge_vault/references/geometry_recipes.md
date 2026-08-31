# 📐 幾何モデリング レシピ集 (Geometry Recipes)

## 1. 凸包（Convex Hull）による完全ソリッド岩石（Sacoche Ito 3D 技法）
内部が完全に詰まった 100% ソリッドな多面体岩石・巨石を生成する技法。

```python
import bpy, bmesh, random, math

def build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=18, is_crag=True, seed=0):
    random.seed(seed)
    points = []
    rx, ry, rz = size_x * 0.5, size_y * 0.5, size_z * 0.5
    for _ in range(point_count):
        u = random.random()
        theta = random.uniform(0, math.pi * 2)
        phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
        rad_scale = (u ** 0.5) if is_crag else (u ** 0.8)
        px = math.cos(phi) * math.cos(theta) * rx * rad_scale
        py = math.cos(phi) * math.sin(theta) * ry * rad_scale
        pz = math.sin(phi) * rz * rad_scale
        points.append((px, py, pz))

    created_verts = [bm.verts.new(p) for p in points]
    bm.verts.ensure_lookup_table()
    res_hull = bmesh.ops.convex_hull(bm, input=created_verts, use_existing_faces=False)
    internal_verts = [v for v in created_verts if v not in res_hull['geom']]
    bmesh.ops.delete(bm, geom=internal_verts, context='VERTS')
    return bm.verts[:]
```

---

## 2. 多重サイン波プロポーショナル起伏地面（Mdesign 草原技法 01:13 & 03:37）
プロポーショナル編集（Proportional Falloff）に相当する自然な丘陵起伏を生成。

```python
def build_grass_terrain_ground(bm, size_x, size_y, seed=0, undulation=0.35, subdivisions=16):
    random.seed(seed)
    half_x, half_y = size_x * 0.5, size_y * 0.5
    step_x, step_y = size_x / subdivisions, size_y / subdivisions
    verts = []
    for iy in range(subdivisions + 1):
        row = []
        for ix in range(subdivisions + 1):
            x = -half_x + ix * step_x
            y = -half_y + iy * step_y
            nx = (math.sin(x * 0.55 + seed * 0.1) * math.cos(y * 0.45 + seed * 0.07)
                + math.sin(x * 1.3 + seed * 0.3) * math.cos(y * 1.1 + seed * 0.2) * 0.35
                + math.sin(x * 2.7 + seed * 0.7) * math.cos(y * 2.3 + seed * 0.5) * 0.12)
            z = nx * undulation
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for iy in range(subdivisions):
        for ix in range(subdivisions):
            bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))
    return [v for row in verts for v in row]
```

---

## 3. UV縦展開（Y=0〜1）対応 5点先細り草ブレード（Mdesign 草原技法 05:30）
グラデーションシェーダーと完全連動する、ローポリ先細り草ブレード。

```python
def build_grass_blade_with_uv(bm, uv_layer, height=0.6, base_width=0.04, curve_x=0.0, curve_y=0.08, seed=0):
    rng = random.Random(seed)
    h = height * rng.uniform(0.82, 1.18)
    bw = base_width * rng.uniform(0.8, 1.2)
    mid_h = h * 0.55
    v_bl  = bm.verts.new((-bw * 0.5, 0.0, 0.0))
    v_br  = bm.verts.new(( bw * 0.5, 0.0, 0.0))
    v_ml  = bm.verts.new((-bw * 0.25 + curve_x, curve_y, mid_h))
    v_mr  = bm.verts.new(( bw * 0.25 + curve_x, curve_y, mid_h))
    v_tip = bm.verts.new((curve_x * 1.2, curve_y * 1.2, h))

    f_bot = bm.faces.new((v_bl, v_br, v_mr, v_ml))
    f_top = bm.faces.new((v_ml, v_mr, v_tip))
    # UV: Y=0 (根元) ~ Y=1 (先端)
    for face, uvs in [(f_bot, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.5), (0.0, 0.5)]),
                      (f_top, [(0.0, 0.5), (1.0, 0.5), (0.5, 1.0)])]:
        for loop, uv in zip(face.loops, uvs):
            loop[uv_layer].uv = uv
    return [v_bl, v_br, v_ml, v_mr, v_tip]
```
