# 🌊 リアル水面・水域シェーダー ＆ 幾何学レシピ集 (Water & Ocean Studio)

YouTube 4大水面講座（映画「Flow」風アニメーション水面、Oceanモディファイア海洋、Chuck CG 湖・池・水たまりシェーダー）の全タイムライン・パラメータ・ノード接続を体系化した実証済みレシピ集です。

---

## 1. 物理準拠プロシージャル水面シェーダー (IOR 1.333 + Volume Absorption + 二重Bump)

```python
import bpy

def create_procedural_water_shader(mat_name, color_type='TROPICAL', wave_strength=0.12, seed=0):
    """Transmission 1.0 + IOR 1.333 + Volume Absorption (動画1 Flow) + 二重波紋Bump (動画4 Chuck CG)"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    try:
        mat.use_screen_refraction = True
    except Exception:
        pass

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # 1. Output & Principled BSDF
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.02
    node_bsdf.inputs['IOR'].default_value = 1.333 # 純水の物理屈折率
    try:
        node_bsdf.inputs['Transmission Weight'].default_value = 1.0
    except Exception:
        node_bsdf.inputs['Transmission'].default_value = 1.0

    # 4種の水質カラーパレット
    if color_type == 'DEEP_OCEAN':
        base_col = (0.015, 0.045, 0.14, 1.0)
        vol_col = (0.01, 0.08, 0.18, 1.0)
        vol_density = 1.2
    elif color_type == 'POND_GREEN':
        base_col = (0.05, 0.20, 0.12, 1.0)
        vol_col = (0.08, 0.25, 0.15, 1.0)
        vol_density = 0.85
    elif color_type == 'CRYSTAL':
        base_col = (0.85, 0.95, 1.0, 1.0)
        vol_col = (0.2, 0.6, 0.8, 1.0)
        vol_density = 0.2
    else: # TROPICAL
        base_col = (0.06, 0.62, 0.68, 1.0)
        vol_col = (0.04, 0.38, 0.45, 1.0)
        vol_density = 0.65

    node_bsdf.inputs['Base Color'].default_value = base_col
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 2. Volume Absorption (動画 1 Flow風: 水深に応じた自然な光減衰)
    node_vol = nodes.new(type='ShaderNodeVolumeAbsorption')
    node_vol.inputs['Color'].default_value = vol_col
    node_vol.inputs['Density'].default_value = vol_density
    links.new(node_vol.outputs['Volume'], node_out.inputs['Volume'])

    # 3. 二重波紋 Bump (動画 4 Chuck CG 準拠: 細波 Noise + うねり Voronoi)
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_map = nodes.new(type='ShaderNodeMapping')
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 16.0
    node_noise.inputs['Detail'].default_value = 4.0
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_vor = nodes.new(type='ShaderNodeTexVoronoi')
    node_vor.inputs['Scale'].default_value = 4.0
    links.new(node_map.outputs['Vector'], node_vor.inputs['Vector'])

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.inputs['Factor'].default_value = 0.35
    links.new(node_noise.outputs['Fac'], node_mix.inputs[2])
    links.new(node_vor.outputs['Distance'], node_mix.inputs[3])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = max(0.02, wave_strength)
    node_bump.inputs['Distance'].default_value = 0.04
    links.new(node_mix.outputs[0], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat
```

---

## 2. Ocean Modifier（海洋モディファイア ＋ 白波 Foam 属性）

```python
def setup_ocean_modifier(obj, size_x=10.0, size_y=10.0, wave_height=1.0):
    """動画 2 & 3 準拠: 大海原のリアル波浪シミュレーション"""
    ocean_mod = obj.modifiers.new(name="Ocean_Wave", type='OCEAN')
    ocean_mod.geometry_mode = 'DISPLACE'
    ocean_mod.resolution = 14
    ocean_mod.spatial_size = int(max(size_x, size_y) * 2.0)
    ocean_mod.wind_velocity = 25.0
    ocean_mod.choppiness = 1.5           # 波頭の鋭さ
    ocean_mod.wave_scale = wave_height * 0.4
    ocean_mod.use_foam = True            # 白波属性の生成
    ocean_mod.foam_coverage = 0.35
    ocean_mod.foam_layer_name = "foam"
    return ocean_mod
```

---

## 3. 5大水面形状幾何学 (LAKE, POND, SQUARE, CIRCLE, OCEAN)

| 形状プリセット | 幾何学的特徴 | ゲーム・用途 |
| :--- | :--- | :--- |
| **`LAKE` (湖・大水面)** | 多重サイン波による有機的海岸線 ＋ 緩やかな大波うねり | オープンワールド湖畔、大河 |
| **`POND` (自然池・湧水池)** | すり鉢状の泥砂利池底スラブ（Slot 1: `Water_Bed_Mat`）＋ 水面 | 庭園池、湧水、オアシス |
| **`SQUARE` (四角・プール)** | 均等細分化スクエアグリッド | 近代プール、ダンジョン水路、水槽 |
| **`CIRCLE` (円形・泉)** | 極座標リンググリッド | 街の噴水、円形水たまり、聖なる泉 |
| **`OCEAN` (大海原)** | Ocean Modifier 用フラットベースグリッド | 外海、航海シーン、海岸の波打ち際 |

---

## 4. サウンドコーディング ＆ ゲームエンジン連動 (Audio & Game Pipeline)

- **マテリアルスロット**:
  - Slot 0: `Water_Surface_Mat`（水面）
  - Slot 1: `Water_Bed_Mat`（池底スラブ）
- **サウンド判定（Wwise / FMOD / ADX2 / Unity C#）**:
  - `Water_Surface_Mat` 検知時: **水しぶき音 (Splash Sound)**、**水中泳ぎ足音 (Water Footstep)**、**水没アンビエント (Underwater Ambience)** の Surface ID に直結。
  - `Water_Bed_Mat` 検知時: **泥・湿地足音 (Mud Footstep)** に直結。

---

## 5. 湖面の微風ループアニメーション ＆ Unity/UE向けシェイプキーFBXエクスポート

映画「Flow」風（`yRXMe-1N6_Y`）に、穏やかなそよ風で湖面がゆらゆら動くアニメーションを生成し、Unity/UEでそのまま再生可能なFBXとして出力する技術仕様です。

### 5-1. さざ波モディファイア設定
- `Wave Modifier`: `height=0.035 * WindSpeed`, `width=1.2`, `narrowness=1.5`, `speed=0.22 * WindSpeed`
- 1〜60フレームの完全周期ループを形成。

### 5-2. シェイプキー自動ベイク ＆ FBX出力
1. `depsgraph.evaluated_get` により、各サンプリングフレームの頂点変位を **シェイプキー（`Wave_Frame_XXX`）** にベイク。
2. 各キーに `0.0 -> 1.0 -> 0.0` のアニメーションキーフレーム（`Action`）を生成。
3. `bpy.ops.export_scene.fbx(bake_anim=True, bake_anim_use_all_actions=True)` で出力。
4. **Unity インポート時**: `SkinnedMeshRenderer` ＋ `Animation Clip` が最初から付与され、シーンに置くだけで永久ループ再生。

---

## 6. 波頭の白波（Foam）自動合成 ＆ Nishita 物理大気スカイ（kasaharaCG様 vSgWZG2ugf0 準拠）

### 6-1. 白波（Foam）合成シェーダー
- `Ocean Modifier` の `use_foam=True`, `foam_layer_name="foam"` から波頭データを取得。
- `Attribute(foam)` → `ColorRamp` → `Mix Shader` により、波が砕ける頂点に白い泡（Base Color: 白, Roughness: 0.4）を自動合成。

### 6-2. Nishita 大気散乱スカイ ＆ Eevee 屈折・反射
- 外部HDRI画像がなくても、Blender 3.6 内蔵 `ShaderNodeTexSky(NISHITA)` を World 背景にワンクリック自動接続。
- Sun Elevation: 18°（美しい斜光・太陽反射）、Sun Rotation: 45°。
- Eevee の `use_ssr=True`, `use_ssr_refraction=True` を有効化し、水面に鮮やかな青空と太陽光が映り込むフォトリアルライティングを実現。


