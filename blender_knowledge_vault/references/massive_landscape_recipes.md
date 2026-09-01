# 🏞️ 広大背景・グランドキャニオン・山脈 ＆ 巨大地形 完全レシピ (Massive Landscape Recipes)

本ドキュメントは、YouTube 4大背景・地形講座（グランドキャニオン、広大背景作成、Real Environment、A.N.T. Landscape）から習得した**広大な自然背景、水平地層（Stratified Rock）、多重フラクタル地形、空気遠近法**の完全技術仕様書です。

---

## 1. グランドキャニオン・水平地層（Stratified Sandstone）シェーダー

赤色砂岩の幾重にも重なる水平な地層（Stratification）をプロシージャルに再現するシェーダー：

```python
def create_grand_canyon_stratified_material(mat_name, seed=0):
    """グランドキャニオン水平地層シェーダー (Z軸 Wave + Noise + 多段ColorRamp)"""
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.92
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 1. 座標マッピング (Z 軸を強調して水平地層を形成)
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.inputs['Scale'].default_value = (0.05, 0.05, 1.2) # Z方向に縞模様
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    # 2. 地層の縞模様 (Wave Texture - BANDS, Z方向)
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'Z'
    node_wave.inputs['Scale'].default_value = 4.5
    node_wave.inputs['Distortion'].default_value = 2.8 # 地層の自然な歪み
    node_wave.inputs['Detail'].default_value = 5.0
    links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    # 3. 砂岩の微細ノイズ
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 16.0
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

    # 4. 地層カラーパレット (赤褐色、黄土色、白層、濃赤色)
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].position = 0.0
    node_ramp.color_ramp.elements[0].color = (0.35, 0.12, 0.06, 1.0) # 深い赤褐色
    node_ramp.color_ramp.elements[1].position = 0.35
    node_ramp.color_ramp.elements[1].color = (0.62, 0.38, 0.22, 1.0) # 明るいテラコッタ砂岩
    node_ramp.color_ramp.elements.new(0.65)
    node_ramp.color_ramp.elements[2].color = (0.75, 0.68, 0.52, 1.0) # 白っぽい石灰層
    node_ramp.color_ramp.elements.new(1.0)
    node_ramp.color_ramp.elements[3].color = (0.28, 0.09, 0.04, 1.0) # 暗い褐鉄鉱層

    links.new(node_wave.outputs['Color'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    # 5. 地層とノイズの複合バンプ (Normal)
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.65
    links.new(node_wave.outputs['Color'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat
```

---

## 2. A.N.T. Landscape API による本格地形モデリング

Blender標準の `ant_landscape` アドオンをスクリプトから直接呼び出し、プロ仕様の巨大地形（山脈、峡谷、メサ台地）を高速生成：

```python
def create_ant_landscape_terrain(context, terrain_type="CANYON", size=50.0, height=12.0, subdivisions=128, seed=0):
    """A.N.T. Landscape アドオンを活用した巨大地形生成"""
    # アドオンが有効化されているか確認
    if not hasattr(bpy.ops.mesh, "landscape_add"):
        try:
            bpy.ops.preferences.addon_enable(module="ant_landscape")
        except Exception:
            pass

    if hasattr(bpy.ops.mesh, "landscape_add"):
        # A.N.T. Landscape オペレーターの呼び出し
        noise_types = {
            "CANYON": ('canyon', 1.8, 12.0),
            "MOUNTAIN": ('hetero_terrain', 2.5, 15.0),
            "MESA": ('mesa', 1.2, 8.0),
            "RIDGE": ('ridged_mfractal', 3.0, 18.0)
        }
        ntype, nscale, h_val = noise_types.get(terrain_type, ('canyon', 1.8, 12.0))
        
        bpy.ops.mesh.landscape_add(
            ant_terrain_name="Massive_Landscape",
            Subdivision_x=subdivisions,
            Subdivision_y=subdivisions,
            MeshSize_x=size,
            MeshSize_y=size,
            RandomSeed=seed,
            Noise_Type=ntype,
            Noise_Size=nscale,
            Height=height,
            Maximum=height,
            Minimum=-0.5,
            Falloff='3' # 円形・四角形フェードアウト
        )
        return context.active_object
```

---

## 3. 空気遠近法（Aerial Perspective ＆ Depth）

広大な背景において「遠くの山が青白く霞んで見える」効果（空気遠近法）を構築する技法：

*   **World Volume Scatter / Mist Pass**:
    *   `ShaderNodeVolumeScatter`（Density: `0.002〜0.005`）による大気散乱。
    *   EEVEE: `Volumetric Lighting` ＋ `Volumetric Shadows` 有効化。
*   **Camera Clipping / Focal Length**:
    *   巨大背景用カメラ: `Clip End: 5000m`、`Focal Length: 35mm〜50mm`。

---

## 4. Unity / サウンド連動仕様

*   **Surface ID**:
    *   峡谷・岩山: `SURFACE_STONE_CONCRETE`（巨大な反響・エコー）
    *   峡谷底の川・湿地: `SURFACE_WATER_SPLASH` / `SURFACE_DIRT_MUD`
*   **オーディオゾーン (Audio Reverb Zone / Wwise Spatial Audio)**:
    *   巨大峡谷内に入った際の「大空間ディレイ・リバーブ（Valley Canyon Echo）」パラメータのプリセット連携。
