# 🏔️ PBR ディスプレイスメント ＆ 3D 凹凸立体化 完全レシピ (PBR Displacement Recipes)

本ドキュメントは、Mdesign様チュートリアル『【Blender】テクスチャで凸凹を表現する』(URL: [https://www.youtube.com/watch?v=M_AoNzdC4gI](https://www.youtube.com/watch?v=M_AoNzdC4gI)) および PBR マテリアルパイプラインから習得した**Cycles Displacement と Displace Modifier による 3D 頂点立体化**の完全技術仕様書です。

---

## 1. PBR テクスチャセットの自動認識仕様

フォルダ内のテクスチャファイルを以下の命名規則で自動検知し、適切なカラースペースとノード入力に割り当てます：

| テクスチャ種別 | プレフィックス / サフィックス | カラースペース | Principled BSDF / 出力先 |
| :--- | :--- | :--- | :--- |
| **Albedo / Base Color** | `_Color`, `_BaseColor`, `_Albedo`, `_Diff` | `sRGB` | `Base Color` |
| **Normal Map (OpenGL)** | `_NormalGL`, `_Normal`, `_Nor` | `Non-Color` | `Normal Map` ノード ➔ `Normal` |
| **Roughness** | `_Roughness`, `_Rough`, `_Rogh` | `Non-Color` | `Roughness` |
| **Displacement / Height**| `_Displacement`, `_Disp`, `_Height` | `Non-Color` | `Displacement` ノード ➔ `Output.Displacement` |
| **Ambient Occlusion** | `_AmbientOcclusion`, `_AO` | `Non-Color` | `Mix Color (Multiply)` ➔ `Base Color` |

---

## 2. Cycles Displacement（非破壊レンダリング時凹凸）

レンダリング時に頂点を真の 3D 凹凸として変位させる設定：

```python
def setup_cycles_displacement(mat, disp_image, scale=0.1, midlevel=0.5):
    """Cycles レンダラーにおける Displacement 設定"""
    mat.cycles.displacement_method = 'BOTH' # Displacement と Bump の両方を有効化
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    node_out = [n for n in nodes if n.type == 'OUTPUT_MATERIAL'][0]

    node_disp = nodes.new(type='ShaderNodeDisplacement')
    node_disp.inputs['Scale'].default_value = scale
    node_disp.inputs['Midlevel'].default_value = midlevel

    node_tex_disp = nodes.new(type='ShaderNodeTexImage')
    node_tex_disp.image = disp_image
    node_tex_disp.image.colorspace_settings.name = 'Non-Color'

    links.new(node_tex_disp.outputs['Color'], node_disp.inputs['Height'])
    links.new(node_disp.outputs['Displacement'], node_out.inputs['Displacement'])
```

---

## 3. 実メッシュ頂点立体化 (Displace Modifier ＆ Unity/FBX エクスポート)

ゲームエンジン（Unity/UE）では Shader の Cycles Displacement がそのまま動かないため、**モディファイアによってメッシュ頂点そのものを 3D 立体化**します：

```python
def apply_geometry_displacement(obj, disp_image_path, strength=0.12, subdiv_levels=2):
    """Displace Modifier による実ポリゴン 3D 頂点立体化"""
    if not obj or not os.path.exists(disp_image_path):
        return

    # 1. シンプル細分化（Subdivision Surface - SIMPLE）
    mod_sub = obj.modifiers.new(name="PBR_Subdiv", type='SUBSURF')
    mod_sub.subdivision_type = 'SIMPLE'
    mod_sub.levels = subdiv_levels
    mod_sub.render_levels = subdiv_levels

    # 2. テクスチャのロードと割り当て
    tex_name = obj.name + "_DispTex"
    tex = bpy.data.textures.new(name=tex_name, type='IMAGE')
    img = bpy.data.images.load(disp_image_path, check_existing=True)
    img.colorspace_settings.name = 'Non-Color'
    tex.image = img

    # 3. ディスプレイスモディファイア
    mod_disp = obj.modifiers.new(name="PBR_Displace", type='DISPLACE')
    mod_disp.texture = tex
    mod_disp.texture_coords = 'UV'
    mod_disp.strength = strength
    mod_disp.mid_level = 0.5
```

---

## 4. Unity / サウンド連動仕様

*   **PBR アセットの Surface ID**:
    *   石畳・岩・壁: `SURFACE_STONE_CONCRETE`（硬質な接触音・足音）
    *   木製床・家具: `SURFACE_WOOD`（木材の反響音）
*   **Auto PBR Baker**: ベイク機能と連動し、Displace適用後のメッシュに対して Diffuse / Normal / Roughness を自動ベイクして Unity FBX に同封。
