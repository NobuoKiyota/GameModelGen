# 🎨 PBR ＆ プロシージャルシェーダー レシピ集 (Shader Engine)

## 1. プロシージャル樹皮シェーダー（縦木目 Wave ＋ Bump）
画像テクスチャを使わず、ノイズと波形で樹皮の縦木目とバンプを完全再現。

```python
def create_procedural_bark_material(mat_name, seed=0, species="OAK"):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.88
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Mapping: Z スケールを 0.15 に引き伸ばして縦木目を表現
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.inputs['Scale'].default_value = (1.0, 1.0, 0.15)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    # Wave Texture (Bands, X方向) ＋ Noise
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'X'
    links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    # Mix Wave + Noise -> ColorRamp -> Base Color & Bump
    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    links.new(node_wave.outputs['Color'], node_mix.inputs[2])
    links.new(node_noise.outputs['Fac'], node_mix.inputs[3])

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    links.new(node_mix.outputs[0], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.55
    links.new(node_mix.outputs[0], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    return mat
```

---

## 2. リアル草ブレードシェーダー（UV.Y 縦グラデーション ＋ SSS）
Mdesign 草原動画 15:49 準拠。

```python
def create_procedural_grass_blade_shader(mat_name, seed=0):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    mat.blend_method = 'CLIP'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_trans = nodes.new(type='ShaderNodeBsdfTranslucent')
    node_trans.inputs['Color'].default_value = (0.38, 0.72, 0.12, 1.0)

    node_mix_s = nodes.new(type='ShaderNodeMixShader')
    node_mix_s.inputs['Fac'].default_value = 0.15
    links.new(node_bsdf.outputs['BSDF'], node_mix_s.inputs[1])
    links.new(node_trans.outputs['BSDF'], node_mix_s.inputs[2])
    links.new(node_mix_s.outputs['Shader'], node_out.inputs['Surface'])

    # UV Map -> Separate XYZ (Y) -> ColorRamp (根元:暗緑土色 -> 先端:ライムグリーン)
    node_uvmap = nodes.new(type='ShaderNodeUVMap')
    node_sep = nodes.new(type='ShaderNodeSeparateXYZ')
    links.new(node_uvmap.outputs['UV'], node_sep.inputs['Vector'])

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.06, 0.14, 0.03, 1.0) # 根元
    node_ramp.color_ramp.elements[1].color = (0.45, 0.72, 0.10, 1.0) # 先端
    links.new(node_sep.outputs['Y'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    return mat
```
