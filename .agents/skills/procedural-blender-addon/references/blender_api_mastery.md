# ⚠️ Blender Python API 虎の巻 (Pitfalls & Best Practices)

## 1. 鉄則：UV 投影後は必ず `OBJECT` モードへ戻す
`bpy.ops.uv.smart_project` や `cube_project` を呼ぶために `EDIT` モードにした後は、**関数の最後で必ず `OBJECT` モードに戻す**。
これを行わないと、ユーザーがUI操作した際や自動テスト実行時に Edit Mode のまま固まる。

```python
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0)
bpy.ops.object.mode_set(mode='OBJECT') # ★必須！
```

---

## 2. ヘッドレス（`--background`）環境での `modifier_apply`
ヘッドレス実行時はアクティブオブジェクトやコンテキストが不完全な場合があるため、`temp_override` を用いる。

```python
ctx = bpy.context
ctx.view_layer.objects.active = obj
obj.select_set(True)
try:
    with ctx.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
except Exception:
    bpy.ops.object.modifier_apply(modifier=mod.name)
```

---

## 3. Sapling Tree Gen の安全な呼び出しとクリーンアップ
- `scale < 1.0` で複素数計算エラー → `base_scale = max(2.5, size_z)` を渡す。
- `leafShape` は `'hex'`, `'rect'`, `'dFace'`, `'dVert'` のみ有効（`'tri'` や `'dface'` はエラー）。
- 生成後の中間メッシュ（`treemesh`, `leavesmesh`）は事前に全削除してから生成する。
