# 🪨 岩石・巨石・断崖（ROCK & CRAG）プロシージャル生成 完全レシピ (Rock & Crag Recipes)

本ドキュメントは、Sacoche Ito 3D 様（凸包アルゴリズム）、Chuck CG 様（多重ディスプレイス崖モデリング）等のチュートリアルから習得した**100% ソリッド岩石、多重バンプシェーダー、有機的ひび割れ**の完全技術仕様書です。

---

## 1. Sacoche Ito 式 凸包（Convex Hull）ランダム岩石モデリング

ランダムに散布した複数の球体頂点群から凸包（Convex Hull）を計算し、隙間のない 100% ソリッドな巨石を生成：

```python
def build_convex_hull_rock(bm, size_x, size_y, size_z, seed=0, points_count=24):
    """ランダム頂点群からの Convex Hull によるソリッド岩石生成"""
    rng = random.Random(seed)
    verts = []
    for _ in range(points_count):
        # 楕円体内にランダム散布
        u = rng.random()
        v = rng.random()
        theta = u * 2.0 * math.pi
        phi = math.acos(2.0 * v - 1.0)
        r = (rng.random() ** (1.0 / 3.0))
        x = r * math.sin(phi) * math.cos(theta) * size_x * 0.5
        y = r * math.sin(phi) * math.sin(theta) * size_y * 0.5
        z = r * math.cos(phi) * size_z * 0.5
        verts.append(bm.verts.new((x, y, z)))
    bm.verts.ensure_lookup_table()

    # Convex Hull 実行
    res = bmesh.ops.convex_hull(bm, input=verts)
    # 不要な内部頂点・ジオメトリをパージ
    bmesh.ops.delete(bm, geom=res['geom_interior'], context='VERTS')
    bm.verts.ensure_lookup_table()
    return bm.verts[:]
```

---

## 2. Chuck CG 式 スカルプト不要の多重ディスプレイス崖モデリング

モディファイアの多重積層により、スカルプトを行わずに切り立った崖肌を構築：

```python
def apply_procedural_cliff_modifiers(obj, scale_large=0.4, strength_large=0.25, scale_small=0.08, strength_small=0.06):
    """Subdivision + Displace(大) + Displace(小) のスタック"""
    # 1. 細分化
    subdiv = obj.modifiers.new(name="Cliff_Subdiv", type='SUBSURF')
    subdiv.subdivision_type = 'SIMPLE'
    subdiv.levels = 3

    # 2. ディスプレイス (大うねり Clouds テクスチャ)
    tex_large = bpy.data.textures.new(name=obj.name + "_DispLarge", type='CLOUDS')
    tex_large.noise_scale = scale_large
    disp_large = obj.modifiers.new(name="Disp_Large", type='DISPLACE')
    disp_large.texture = tex_large
    disp_large.strength = strength_large

    # 3. ディスプレイス (エッジ微細凹凸)
    tex_small = bpy.data.textures.new(name=obj.name + "_DispSmall", type='CLOUDS')
    tex_small.noise_scale = scale_small
    disp_small = obj.modifiers.new(name="Disp_Small", type='DISPLACE')
    disp_small.texture = tex_small
    disp_small.strength = strength_small
```

---

## 3. プロシージャル岩石シェーダー（多重バンプ直列リンク ＆ エッジ風化）

*   **多重バンプリンク**: 大うねり用バンプと砂利・風化用ノイズバンプを**直列（Normal ➔ Normal）**に接続。
*   **ColorRamp エッジ風化**: 凸部（削れた明るい岩肌）と凹部（暗い土や苔）の階調表現。

```python
def build_procedural_rock_material(mat_name, seed=0, palette="GRANITE"):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.82
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')

    # 1. 大うねりノイズ
    node_noise_lg = nodes.new(type='ShaderNodeTexNoise')
    node_noise_lg.inputs['Scale'].default_value = 2.5
    links.new(node_coord.outputs['Object'], node_noise_lg.inputs['Vector'])

    # 2. 微細砂利ノイズ
    node_noise_sm = nodes.new(type='ShaderNodeTexNoise')
    node_noise_sm.inputs['Scale'].default_value = 18.0
    links.new(node_coord.outputs['Object'], node_noise_sm.inputs['Vector'])

    # 3. 直列バンプ接続
    bump_lg = nodes.new(type='ShaderNodeBump')
    bump_lg.inputs['Strength'].default_value = 0.4
    links.new(node_noise_lg.outputs['Fac'], bump_lg.inputs['Height'])

    bump_sm = nodes.new(type='ShaderNodeBump')
    bump_sm.inputs['Strength'].default_value = 0.25
    links.new(node_noise_sm.outputs['Fac'], bump_sm.inputs['Height'])
    links.new(bump_lg.outputs['Normal'], bump_sm.inputs['Normal']) # 直列接続！
    links.new(bump_sm.outputs['Normal'], node_bsdf.inputs['Normal'])

    # 4. ColorRamp パレット
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.15, 0.15, 0.16, 1.0) # 凹部
    node_ramp.color_ramp.elements[1].color = (0.55, 0.52, 0.48, 1.0) # 凸部
    links.new(node_noise_lg.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    return mat
```

---

## 4. Unity / サウンド連動仕様

*   **Surface ID**: `SURFACE_STONE_CONCRETE`（硬質岩石・巨石の足音・落下音・衝突音）
*   **コライダー自動生成**: `UCX_` プレフィックスの凸包コライダーを Unity/UE 向けに自動バンドル。
