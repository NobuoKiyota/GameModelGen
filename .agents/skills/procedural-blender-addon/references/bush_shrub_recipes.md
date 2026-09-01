# 🌿 低木・茂み・シダ植物（BUSH & SHRUB）プロシージャル生成 完全レシピ (Bush & Shrub Recipes)

本ドキュメントは、Blenderにおける**低木・茂み・シダ植物・生垣（Round Bush, Wild Shrub, Fern Clump, Hedge Row）**のプロシージャル幾何学、樹冠球状法線転送（Spherical Normal Transfer）、およびPBRマテリアル設計の完全技術仕様書です。

---

## 1. 低木・茂みの 4 大アーキテクチャ (Bush Types)

| タイプ (Type) | 構造と形状 | 構成要素 | 主な用途 | サウンド ID |
| :--- | :--- | :--- | :--- | :--- |
| **`ROUND_BUSH` (丸型低木)** | 半球ドーム状に丸く広がるふんわり茂み | 多層放射状葉クラスタカード | 庭園、公園、森林の低木 | `SURFACE_FOLIAGE` |
| **`WILD_SHRUB` (野生の藪)** | 根元から四方に細枝が伸びる自然な雑木 | 複数細枝チューブ ＋ 枝先の葉カード | 荒野、深い森、道端の藪 | `SURFACE_BUSH_RUSTLE` |
| **`FERN_CLUMP` (シダの株)** | 放射状にアーチを描いて広がる羽状複葉 | 8〜24本のアーチ葉（Fronds） | 湿地、森林の足元、日陰 | `SURFACE_FOLIAGE` |
| **`HEDGE_ROW` (生垣ブロック)** | 長さ・幅・高さを指定できる生垣 | 3次元グリッド状の葉カード散布 | 敷地境界、迷路、街並み | `SURFACE_FOLIAGE` |

---

## 2. 樹冠球状法線転送（Spherical Normal Transfer）による板ポリ感解消

### なぜ低木の板ポリゴンが不自然に見えるのか？
個々の葉カードが平面法線のままだと、光が当たった時に「平らな板が刺さっている」輪郭が露出してしまいます。

### 解決策：球状法線転送
茂みの中心座標（`Z = Height * 0.45`）から**外向き放射状ベクトルを計算し、各頂点法線（Custom Split Normals）に設定**します。これにより、無数の板ポリゴンが1つの滑らかな球体ボリュームとして光を均一に反射し、ふんわりとした高品質な茂みになります。

```python
def apply_bush_spherical_normals(obj, leaf_mat_idx=0):
    """茂みの中心から放射状に外向き法線を設定（球状法線転送）"""
    mesh = obj.data
    mesh.calc_normals()
    center = mathutils.Vector((0, 0, obj.dimensions.z * 0.45))

    custom_normals = []
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            vert_idx = mesh.loops[loop_idx].vertex_index
            v_co = mesh.vertices[vert_idx].co
            if poly.material_index == leaf_mat_idx:
                dir_vec = (v_co - center).normalized()
                custom_normals.append(dir_vec)
            else:
                custom_normals.append(mesh.vertices[vert_idx].normal)

    mesh.use_auto_smooth = True
    mesh.normals_split_custom_set(custom_normals)
```

---

## 3. マテリアル ＆ サウンド連動仕様

*   **マテリアルスロット**:
    *   Slot 0: `[Name]_Leaf_Mat` → 半透明透過光（Translucent BSDF）付き葉シェーダー
    *   Slot 1: `[Name]_Stem_Mat` → 木目 PBR 細枝シェーダー
*   **Surface ID (Unity / UE / Wwise)**:
    *   `SURFACE_BUSH_RUSTLE`（プレイヤーが通り抜けたときの「ガサガサッ」という擦れ音）
    *   `SURFACE_FOLIAGE`（草葉のタッチ音）
*   **接地点原点**: メッシュ最底面頂点（`Z = 0.0`）に原点を厳密固定。
