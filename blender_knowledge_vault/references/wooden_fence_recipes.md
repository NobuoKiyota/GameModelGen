# 🪵 木製の柵・フェンス・砦（WOODEN FENCE & PALISADE）プロシージャル生成 完全レシピ (Wooden Fence Recipes)

本ドキュメントは、YouTube 木製柵チュートリアル（ローポリフェンス、杭型柵、牧場風クロス柵、丸太砦）から習得した**木製の柵・フェンス・バリケードのプロシージャル幾何学、リピート配置、木目シェーダー**の完全技術仕様書です。

---

## 1. 木製柵の 4 大アーキテクチャ (Fence Types)

| タイプ (Type) | 構造の特徴 | 支柱の形状 | 横木・板の構成 | 主な用途 | サウンド ID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **POST_AND_RAIL (牧場柵)** | シンプルな2〜3段横木 | 丸太 or 角柱 | 水平な長尺丸太/角材 | 牧場、農場、道沿い境界 | `SURFACE_WOOD` |
| **PICKET_FENCE (ピケット柵)**| 先端が尖った縦板が等間隔に並ぶ | 角柱 | 2段横木 + 先端山型縦板 | 住宅、庭園、村の境界 | `SURFACE_WOOD` |
| **CROSS_BRACE (X筋交い柵)**| X字の斜め筋交いで補強された頑丈な柵 | 太い角柱 | 水平上下木 + 中央Xクロス | 牧場、砦、防護柵 | `SURFACE_WOOD` |
| **LOG_PALISADE (丸太砦/防壁)**| 先端を槍状に尖らせた太い丸太が密着連なる | 尖り丸太（Spike） | 背面補強梁 + 結束ロープ | 城壁、キャンプ、砦 | `SURFACE_WOOD` |

---

## 2. 幾何学ビルダー Python コード仕様

### ① 支柱（Post）と先端尖り（Picket / Spike）
```python
def build_fence_post(bm, pos, width=0.1, height=1.2, spike_type="PYRAMID", seed=0):
    """先端尖り付きフェンス支柱（角柱 / ピラミッド型先端）"""
    rng = random.Random(seed)
    # 経年劣化の微細な傾き（Jitter）
    rot_jitter_x = rng.uniform(-0.03, 0.03)
    rot_jitter_y = rng.uniform(-0.03, 0.03)

    half_w = width * 0.5
    body_h = height * 0.85 if spike_type != "FLAT" else height
    
    # 柱胴体
    v_b1 = bm.verts.new((pos.x - half_w, pos.y - half_w, pos.z))
    v_b2 = bm.verts.new((pos.x + half_w, pos.y - half_w, pos.z))
    v_b3 = bm.verts.new((pos.x + half_w, pos.y + half_w, pos.z))
    v_b4 = bm.verts.new((pos.x - half_w, pos.y + half_w, pos.z))

    v_t1 = bm.verts.new((pos.x - half_w, pos.y - half_w, pos.z + body_h))
    v_t2 = bm.verts.new((pos.x + half_w, pos.y - half_w, pos.z + body_h))
    v_t3 = bm.verts.new((pos.x + half_w, pos.y + half_w, pos.z + body_h))
    v_t4 = bm.verts.new((pos.x - half_w, pos.y + half_w, pos.z + body_h))

    # 4側面
    bm.faces.new((v_b1, v_b2, v_t2, v_t1))
    bm.faces.new((v_b2, v_b3, v_t3, v_t2))
    bm.faces.new((v_b3, v_b4, v_t4, v_t3))
    bm.faces.new((v_b4, v_b1, v_t1, v_t4))

    if spike_type == "PYRAMID":
        # ピラミッド型尖り先端
        v_tip = bm.verts.new((pos.x, pos.y, pos.z + height))
        bm.faces.new((v_t1, v_t2, v_tip))
        bm.faces.new((v_t2, v_t3, v_tip))
        bm.faces.new((v_t3, v_t4, v_tip))
        bm.faces.new((v_t4, v_t1, v_t_{}))
    else:
        bm.faces.new((v_t4, v_t3, v_t2, v_t1))
```

### ② 連続フェンスユニット生成（横木・筋交い・ピケット）
```python
def build_procedural_fence_segment(bm, start_pt, end_pt, fence_type="POST_AND_RAIL", height=1.1, post_width=0.1, rails_count=2, seed=0):
    """2点間を結ぶフェンスセグメント（支柱 + 横木 / X筋交い / ピケット）"""
    rng = random.Random(seed)
    dir_vec = (end_pt - start_pt)
    seg_len = dir_vec.length
    if seg_len < 0.01:
        return
    dir_norm = dir_vec.normalized()
    side_norm = mathutils.Vector((-dir_norm.y, dir_norm.x, 0.0))

    # 1. 始点と終点の支柱
    build_fence_post(bm, start_pt, width=post_width, height=height, seed=seed)
    build_fence_post(bm, end_pt, width=post_width, height=height, seed=seed + 1)

    # 2. 横木（Rails）
    rail_thick = post_width * 0.6
    for ri in range(rails_count):
        t_z = height * (0.3 + 0.45 * (ri / max(1, rails_count - 1)))
        # 水平梁の押し出し
        r_start = start_pt + mathutils.Vector((0, 0, t_z))
        r_end = end_pt + mathutils.Vector((0, 0, t_z))
        # ボックス生成（横木）
        # ...
```

---

## 3. マテリアル ＆ サウンド連動仕様

*   **マテリアルスロット**:
    *   Slot 0: `[Name]_Wood_Mat` → 木材の縦木目 PBR シェーダー（Wave + Noise）
    *   Slot 1: `[Name]_Rope_Mat` → 丸太結束ロープ / 鉄釘（Iron Nail）
*   **Surface ID (Unity / UE / Wwise)**:
    *   `SURFACE_WOOD`（フェンスに接触した時・飛び越えた時の「コトッ」「コンッ」という乾いた木材音）
    *   `SURFACE_WOOD_FENCE_CREAK`（寄りかかった時のキシミ音）
