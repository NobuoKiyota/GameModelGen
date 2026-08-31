# 🎮 Unity / Unreal Engine ゲームパイプライン ＆ オーディオ連動

## 1. FBX エクスポート標準仕様
- **座標軸**: `axis_forward='-Z'`, `axis_up='Y'`
- **スケール**: `apply_scale_options='FBX_SCALE_ALL'`, `global_scale=1.0`
- **テクスチャ同封**: `path_mode='COPY'`, `embed_textures=True`

```python
def export_unity_fbx(obj, fbx_path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
        bake_space_transform=True
    )
```

---

## 2. マテリアル分離による足音（Footstep / Surface Switch）連動
アセットごとに明確なマテリアルスロットを付与することで、Unity側での Raycast / Physic Material 判定が容易になる。

| マテリアル名 | Unity Surface ID | 想定足音・接触音 (Wwise / FMOD / ADX2) |
| :--- | :--- | :--- |
| `*_Blade_Mat` | `SURFACE_GRASS` | 草むらのカサカサ音、葉の擦れ音 |
| `*_Ground_Mat` | `SURFACE_DIRT_MUD` | 柔らかい土、湿った泥の重い足音 |
| `*_Bark_Mat` | `SURFACE_WOOD` | 木幹、硬い木材のコンコン音 |
| `*_PBR_Mat` (Rock/Wall) | `SURFACE_STONE_CONCRETE` | 石畳、レンガ、硬質岩石の甲高い衝撃音 |
