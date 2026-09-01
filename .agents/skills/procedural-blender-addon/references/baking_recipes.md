# 🔥 プロシージャルPBRテクスチャ 自動ベイク ＆ Unity連携レシピ (Baking Engine)

Blender 内部のプロシージャルノード（Noise, ColorRamp, Wave木目, Bump凹凸）を画像テクスチャ（BaseColor / Normal Map）へ高速・安全にベイクし、Unity インポート時の「単色ベタ塗り（のっぺり）」を完全解消するための実践ノウハウです。

---

## 1. なぜベタ塗りになるのか？ (Root Cause)
- **FBX の制限**: FBX は 3D頂点データと画像テクスチャ参照（PNG/JPG）しか運べない。
- **数式ノードの消失**: Blender 内部の `ShaderNodeValToRGB`, `ShaderNodeTexNoise`, `ShaderNodeMix` 等の計算式は FBX に入らないため、Base Color の単一フラット値だけが Unity に渡り、のっぺりとしたベタ塗りになる。

---

## 2. 解決策：Cycles 自動ベイク ＆ マテリアル差し替え (Auto PBR Baker)

```python
import bpy, os

def bake_procedural_material_to_pbr(obj, output_dir, res=1024, bake_diffuse=True, bake_normal=True):
    """Cycles レンダラーを用いて、陰影なしの純粋なカラーと法線マップをベイク"""
    scene = bpy.context.scene
    old_engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.cycles.bake_type = 'DIFFUSE'
    scene.cycles.samples = 16 # 高速ベイク (16サンプルで十分な高画質)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    os.makedirs(output_dir, exist_ok=True)
    base_name = obj.name
    baked_textures = {}

    # 1. BaseColor (DIFFUSE pass: COLOR only, no direct/indirect lighting)
    if bake_diffuse:
        diff_img_name = f"{base_name}_BaseColor"
        diff_img = bpy.data.images.new(diff_img_name, width=res, height=res, alpha=True)
        
        bake_nodes = []
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                node.image = diff_img
                mat.node_tree.nodes.active = node
                bake_nodes.append((mat, node))
        
        try:
            # pass_filter={'COLOR'} で純粋なアルベド色のみ抽出
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=True, margin=4)
            diff_path = os.path.join(output_dir, f"{diff_img_name}.png")
            diff_img.filepath_raw = diff_path
            diff_img.file_format = 'PNG'
            diff_img.save()
            baked_textures['BaseColor'] = diff_path
        finally:
            for mat, node in bake_nodes:
                mat.node_tree.nodes.remove(node)

    # 2. Normal Map (TANGENT Space Normal)
    if bake_normal:
        norm_img_name = f"{base_name}_Normal"
        norm_img = bpy.data.images.new(norm_img_name, width=res, height=res, alpha=False)
        norm_img.colorspace_settings.name = 'Non-Color'

        bake_nodes = []
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                node.image = norm_img
                mat.node_tree.nodes.active = node
                bake_nodes.append((mat, node))

        try:
            bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', use_clear=True, margin=4)
            norm_path = os.path.join(output_dir, f"{norm_img_name}.png")
            norm_img.filepath_raw = norm_path
            norm_img.file_format = 'PNG'
            norm_img.save()
            baked_textures['Normal'] = norm_path
        finally:
            for mat, node in bake_nodes:
                mat.node_tree.nodes.remove(node)

    scene.render.engine = old_engine
    return baked_textures
```

---

## 3. ベイク済みテクスチャの自動バインド (PBR Shader Replacement)

ベイク完了後、元のプロシージャルノードを「画像テクスチャを使ったシンプルな PBR マテリアル」に差し替えることで、FBX エクスポート時に `embed_textures=True` が機能し、Unity へのドラッグ＆ドロップだけでテクスチャが自動反映されます。

```python
def apply_baked_pbr_material(obj, baked_textures):
    mat_name = f"{obj.name}_Baked_PBR_Mat"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # BaseColor
    if 'BaseColor' in baked_textures:
        img = bpy.data.images.load(baked_textures['BaseColor'], check_existing=True)
        node_col = nodes.new(type='ShaderNodeTexImage')
        node_col.image = img
        links.new(node_col.outputs['Color'], node_bsdf.inputs['Base Color'])

    # Normal Map (Non-Color)
    if 'Normal' in baked_textures:
        img = bpy.data.images.load(baked_textures['Normal'], check_existing=True)
        img.colorspace_settings.name = 'Non-Color'
        node_norm_tex = nodes.new(type='ShaderNodeTexImage')
        node_norm_tex.image = img
        node_norm_map = nodes.new(type='ShaderNodeNormalMap')
        links.new(node_norm_tex.outputs['Color'], node_norm_map.inputs['Color'])
        links.new(node_norm_map.outputs['Normal'], node_bsdf.inputs['Normal'])

    obj.data.materials.clear()
    obj.data.materials.append(mat)
```

---

## 4. Unity 側でのベストプラクティス
- **FBX インポート時**:
  - Inspector > Materials > **Location: Use External Materials (Legacy)** または **Extract Materials** を選択。
  - `*_Normal.png` は Unity の Inspector で **Texture Type: Normal map** に設定して Apply。
