# 🌲 リアル樹木（TREE）プロシージャル生成 ＆ シェーディング完全レシピ (Tree Recipes)

本ドキュメントは、Blenderにおける**フォトリアル＆ゲーム最適化プロシージャル樹木生成（幹・枝分かれ・葉クラスタ・法線制御・PBRシェーダー）**の完全技術仕様および実証済みコード集です。

---

## 1. 幹と枝のフラクタル階層分岐アーキテクチャ (Branching Hierarchy)

リアルな樹木には、単なる2段階分岐ではなく**3〜4段階の再帰的分岐（L-System的アプローチ）**が必要です。

### 樹種別パラメータ設計表

| 樹種 (Species) | 幹の形状・うねり | 分岐階層 (Levels) | 主枝の角度 (Pitch/Angle) | 葉の配置スタイル | サウンドID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OAK (オーク)** | 太い主幹、中程度のうねり、根張り大 | 3〜4段階 | 45°〜65°（四方に力強く広がる） | ドーム状クラスタ / 密集カード | `SURFACE_WOOD` |
| **PINE (マツ・針葉樹)** | まっすぐ伸びる主幹、テーパー急 | 2〜3段階 | 70°〜85°（水平〜やや下向きの輪生枝） | 三角錐コーン状層状カード | `SURFACE_WOOD` |
| **WILLOW (シダレヤナギ)** | 上部から大きく弓なりに曲がる | 3段階 + 垂れ枝 | 30°上向き → 85°下垂 | 垂れ下がる短冊カード | `SURFACE_WOOD` |
| **PALM (ヤシの木)** | 大きく1方向にしなる幹 + フシリング | 1段階 (頂点大葉) | 頂点から放射状（30°〜60°下垂） | 羽状複葉カード | `SURFACE_WOOD` |
| **BIRCH (シラカバ)** | 細身ですらりと高く伸びる幹 | 2〜3段階 | 60°〜75°（上向きの繊細な枝） | 小ぶりで軽やかな散布カード | `SURFACE_WOOD` |
| **JAPANESE_MAPLE (モミジ)**| 低い位置で二股・三股に分かれる優美な幹 | 3〜4段階 | 35°〜55°（横に広がる繊細な枝） | 平坦層状のモミジクラスタ | `SURFACE_WOOD` |

---

## 2. 根張り（Root Flare / Buttress Roots）幾何学

地面付近（`Z = 0` 〜 `0.12 * Height`）で大地を踏ん張る太い根の張り出しを数式で生成：

```python
# 放射状の根張り数式
flare_radius = base_radius * (1.6 + 0.5 * math.cos(flare_count * angle))
```

---

## 3. 葉クラスタ ＆ 樹冠球状法線転送 (Canopy Normal Transfer)

### ① なぜ板ポリが不自然に見えるのか？
単一の平面ポリゴンは各面の法線が平坦であるため、光が当たると「四角い板が刺さっている」輪郭が露出し、CGらしさが目立ってしまいます。

### ② 解決策：樹冠球状法線（Normal Transfer）
樹木全体の中心（または枝クラスタの中心）から**外向き放射状に法線を設定**することで、無数の葉カードが集合して「1つのふんわりとしたボリューム」として光を柔らかく反射します。

```python
def apply_tree_canopy_normals(tree_obj, leaf_material_index=1):
    """葉メッシュの法線を樹冠中心からの放射状法線（球状法線）に修正してふんわり陰影を実現"""
    mesh = tree_obj.data
    # 樹冠の中心座標を算出
    leaf_verts = [v for f in mesh.polygons if f.material_index == leaf_material_index for v in f.vertices]
    if not leaf_verts:
        return
    center = mathutils.Vector((0, 0, 0))
    for vi in leaf_verts:
        center += mesh.vertices[vi].co
    center /= len(leaf_verts)

    # 頂点法線を外向きベクトルに設定（Custom Split Normals）
    mesh.use_auto_smooth = True
    mesh.normals_split_custom_set_from_vertices([
        (mesh.vertices[vi].co - center).normalized() if vi in leaf_verts else mesh.vertices[vi].normal
        for vi in range(len(mesh.vertices))
    ])
```

---

## 4. プロシージャル樹皮 ＆ 葉 PBR シェーダー

### 樹皮シェーダー（縦木目 Wave + Noise + Bump）
```python
def create_procedural_bark_material(mat_name, seed=0, species="OAK"):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.85
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Z方向に引き伸ばした Mapping (Scale X:1, Y:1, Z:0.15)
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.inputs['Scale'].default_value = (1.0, 1.0, 0.15)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'X'
    node_wave.inputs['Scale'].default_value = 8.0
    links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 12.0
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    # Mix Wave + Noise
    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    links.new(node_wave.outputs['Color'], node_mix.inputs[2])
    links.new(node_noise.outputs['Fac'], node_mix.inputs[3])

    # ColorRamp で樹種別の樹皮カラーパレットを設定
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    if species == "BIRCH":
        node_ramp.color_ramp.elements[0].color = (0.85, 0.82, 0.78, 1.0) # 白樺の白い幹
        node_ramp.color_ramp.elements[1].color = (0.12, 0.08, 0.06, 1.0) # 黒い斑点
    else:
        node_ramp.color_ramp.elements[0].color = (0.18, 0.11, 0.06, 1.0) # 深い茶色
        node_ramp.color_ramp.elements[1].color = (0.35, 0.24, 0.15, 1.0) # 明るい樹皮色

    links.new(node_mix.outputs[0], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.55
    links.new(node_mix.outputs[0], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    return mat
```

---

## 5. Unity / オーディオ連携仕様

*   **マテリアルスロット**:
    *   Slot 0: `[Name]_Bark_Mat` → Unity PhysicMaterial: `Wood` / Surface ID: `SURFACE_WOOD`
    *   Slot 1: `[Name]_Leaf_Mat` → Unity PhysicMaterial: `Foliage` / Surface ID: `SURFACE_FOLIAGE`
*   **接地点原点**: メッシュ底面頂点（`min_z`）を検出し、オブジェクト原点を厳密に `Z = 0.0` に一致させる。
