# 🌾 草原・草地 ＆ 地形プロシージャル生成 完全レシピ (Grass & Terrain Recipes)

本ドキュメントは、Mdesign様チュートリアル『【Blender】リアルな草原の作り方』(URL: [https://www.youtube.com/watch?v=nVjq7rn97h0](https://www.youtube.com/watch?v=nVjq7rn97h0)) および実務ゲームパイプラインから習得した**草地・テレイン・Hair Particle散布・草シェーダー**の完全技術仕様書です。

---

## 1. 自然な起伏地面（Terrain Ground）モデリング

プロポーショナル編集相当の滑らかな丘陵地形を、多重サイン波（FBM的合成）によりプロシージャル生成：

```python
def build_grass_terrain_ground(bm, size_x, size_y, seed=0, undulation=0.35, subdivisions=14):
    """自然な起伏地面（多重周波数サイン波合成）"""
    half_x = size_x * 0.5
    half_y = size_y * 0.5
    step_x = size_x / subdivisions
    step_y = size_y / subdivisions
    verts = []
    for iy in range(subdivisions + 1):
        row = []
        for ix in range(subdivisions + 1):
            x = -half_x + ix * step_x
            y = -half_y + iy * step_y
            # 低周波（大うねり）+ 中周波 + 高周波（微細凹凸）
            nx = (math.sin(x * 0.55 + seed * 0.1) * math.cos(y * 0.45 + seed * 0.07)
                + math.sin(x * 1.3 + seed * 0.3) * math.cos(y * 1.1 + seed * 0.2) * 0.35
                + math.sin(x * 2.7 + seed * 0.7) * math.cos(y * 2.3 + seed * 0.5) * 0.12)
            z = nx * undulation
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for iy in range(subdivisions):
        for ix in range(subdivisions):
            bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))
    bm.verts.ensure_lookup_table()
    return [v for row in verts for v in row]
```

---

## 2. UV縦展開（Y=0〜1）対応 5点先細り草ブレードモデリング

草シェーダーの根元〜先端グラデーションを有効にするため、**UV.Y 座標を `0.0 (根元)` から `1.0 (先端)` へ厳密にマッピング**した5頂点（2ポリゴン）メッシュを生成：

```python
def build_grass_blade_with_uv(bm, uv_layer, height=0.6, base_width=0.04, curve_x=0.0, curve_y=0.08, seed=0):
    """UV付き5点先細り草ブレード（2面構成）"""
    rng = random.Random(seed)
    h = height * rng.uniform(0.85, 1.15)
    bw = base_width * rng.uniform(0.8, 1.2)
    mid_h = h * 0.55

    v_bl  = bm.verts.new((-bw * 0.5, 0.0, 0.0))
    v_br  = bm.verts.new(( bw * 0.5, 0.0, 0.0))
    v_ml  = bm.verts.new((-bw * 0.25 + curve_x * 0.6, curve_y * 0.6, mid_h))
    v_mr  = bm.verts.new(( bw * 0.25 + curve_x * 0.6, curve_y * 0.6, mid_h))
    v_tip = bm.verts.new((curve_x, curve_y, h))

    f_bot = bm.faces.new((v_bl, v_br, v_mr, v_ml))
    f_top = bm.faces.new((v_ml, v_mr, v_tip))

    # UV マッピング: 根元(0,0)-(1,0), 中間(0,0.5)-(1,0.5), 先端(0.5,1.0)
    for loop, uv in zip(f_bot.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.5), (0.0, 0.5)]):
        loop[uv_layer].uv = uv
    for loop, uv in zip(f_top.loops, [(0.0, 0.5), (1.0, 0.5), (0.5, 1.0)]):
        loop[uv_layer].uv = uv

    return [v_bl, v_br, v_ml, v_mr, v_tip]
```

---

## 3. リアル草シェーダー（UV.Y グラデーション ＋ SSS ＋ 個体差）

*   **UV.Y による根元（暗い黄緑/茶）〜 先端（明るい若草色）の ColorRamp**
*   **Object Info (Random)** による株ごとの色相・明度のランダムな揺らぎ
*   **Translucent BSDF (半透明透過光)** による逆光時のリアルな光の透け

```python
def create_procedural_grass_blade_shader(mat_name, seed=0):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.45

    # UV 座標の Y 軸を取得
    node_uv = nodes.new(type='ShaderNodeUVMap')
    node_sep = nodes.new(type='ShaderNodeSeparateXYZ')
    links.new(node_uv.outputs['UV'], node_sep.inputs['Vector'])

    # 根元〜先端グラデーション
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].position = 0.0
    node_ramp.color_ramp.elements[0].color = (0.08, 0.16, 0.03, 1.0) # 根元の深い緑
    node_ramp.color_ramp.elements[1].position = 1.0
    node_ramp.color_ramp.elements[1].color = (0.38, 0.55, 0.12, 1.0) # 先端の明るい黄緑
    links.new(node_sep.outputs['Y'], node_ramp.inputs['Fac'])

    # 半透明 (Translucent) シェーダーの合成（逆光透過光）
    node_trans = nodes.new(type='ShaderNodeBsdfTranslucent')
    links.new(node_ramp.outputs['Color'], node_trans.inputs['Color'])

    node_mix = nodes.new(type='ShaderNodeMixShader')
    node_mix.inputs['Fac'].default_value = 0.35
    links.new(node_bsdf.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_trans.outputs['BSDF'], node_mix.inputs[2])

    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_mix.outputs['Shader'], node_out.inputs['Surface'])
    return mat
```

---

## 4. パーティクル散布 ＆ ゲーム用メッシュ実体化 (Scattering & Realization)

*   **Hair Particle 散布**: 草ブレードのコレクションをテレイン地面に散布（`render_type = 'COLLECTION'`）。
*   **密度頂点グループ（Grass_Density）**: ノイズ数式により自動ウェイトペイントを行い、起伏の窪みや自然な群生を表現。
*   **ゲーム用実メッシュ変換**: `bpy.ops.particle.disconnect_hair()` → `bpy.ops.object.modifier_convert(modifier="Grass_Scatter")` により、Unity/UE でそのまま利用可能な実ポリゴンメッシュへワンクリック変換。

---

## 5. Unity / サウンド連動仕様

| スロット名 | Surface ID | 想定足音・環境音 |
| :--- | :--- | :--- |
| `[Name]_Blade_Mat` | `SURFACE_GRASS` | 草むらのカサカサ音、草を踏みしめる音 |
| `[Name]_Ground_Mat` | `SURFACE_DIRT_MUD` | 柔らかい土、湿った泥の重い足音 |
