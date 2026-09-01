# 🏛️ 家具・建築（FURNITURE & ARCHITECTURE）プロシージャル生成 完全レシピ (Furniture & Architecture Recipes)

本ドキュメントは、クラシックアンティーク家具（椅子、テーブル、チェスト、ベッド、本棚）、近代PCデスク、装飾柱、床タイル、壁ブロックの**プロシージャル幾何学、ろくろ挽き旋回、木目/ファブリックシェーダー**の完全技術仕様書です。

---

## 1. ろくろ挽き脚・装飾柱（Antique Turned Legs & Columns）幾何学

円形断面の半径を高さ方向（Z軸）の三角関数とベベル関数によって滑らかに変化させ、優美なろくろ挽き脚や装飾柱を生成：

```python
def build_antique_leg_or_column(bm, base_pos, height=0.75, radius=0.04, segments=12, rings=24, uv_layer=None):
    """ろくろ挽き（Turned Leg）アンティーク脚・装飾柱"""
    verts_rings = []
    for r in range(rings + 1):
        t = r / float(rings)
        z = base_pos.z + t * height
        # 優美なくびれとバルジ（膨らみ）の数式
        profile = (1.0
                   + math.sin(t * math.pi * 3.0) * 0.35
                   + math.sin(t * math.pi * 7.0) * 0.15)
        cur_rad = radius * max(0.4, profile)

        ring = []
        for s in range(segments):
            ang = s * (math.pi * 2.0 / segments)
            x = base_pos.x + math.cos(ang) * cur_rad
            y = base_pos.y + math.sin(ang) * cur_rad
            ring.append(bm.verts.new((x, y, z)))
        verts_rings.append(ring)

    for r in range(rings):
        for s in range(segments):
            s_next = (s + 1) % segments
            bm.faces.new((verts_rings[r][s], verts_rings[r][s_next],
                          verts_rings[r+1][s_next], verts_rings[r+1][s]))
```

---

## 2. 建築モジュール（床タイル・壁ブロック・梁アーチ）

*   **床タイル (Floor Tile)**: 正方形/長方形スラブに、ベベルエッジと有機的ひび割れ（Organic Scars/Cracks）をブーリアンで付与。
*   **壁ブロック (Wall Block)**: 石積み調ブロックの多層積み上げと目地（Mortar Grout）の自動生成。
*   **アーチ梁 (Beam Arch)**: 支柱間に渡す半円・楕円アーチの動的押し出し。

---

## 3. マテリアル ＆ サウンド連動仕様

| カテゴリ | スロット名 | Surface ID | 想定足音・接触音 |
| :--- | :--- | :--- | :--- |
| **木製家具** | `[Name]_Wood_Mat` | `SURFACE_WOOD` | 硬質木材のコンコン音、引き出しの擦れ音 |
| **布地・クッション** | `[Name]_Fabric_Mat` | `SURFACE_FABRIC_LEATHER`| 柔らかい布・革の吸音感 |
| **石畳・壁** | `[Name]_Stone_Mat` | `SURFACE_STONE_CONCRETE`| 硬質な靴音、レンガの反響 |
| **金属パーツ・取手** | `[Name]_Metal_Mat` | `SURFACE_METAL_HOLLOW` | 金属の甲高い接触音 |
