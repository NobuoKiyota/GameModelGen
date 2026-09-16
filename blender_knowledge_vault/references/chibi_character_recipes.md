# 🐻 どうぶつの森風 デフォルメ3Dキャラクタースタジオ レシピ集 (Chibi Character Recipes)

## 概要
YouTubeチュートリアル動画『【Blender】人物の「3Dキャラクター」の作り方』（サルブレ様 / `72w5Il1HCGk`）から抽出した **「Single Vert 骨格 ＋ 3段モディファイア（Mirror + Skin + Subdiv）＋ 部位別モジュール分離モデリング」** をベースに、『どうぶつの森』特有の 2.0〜2.5頭身・コロンとした球状手足・釣鐘型胴体のプロポーションをプロシージャル化した検証済みレシピです。

---

## 1. 核心幾何学パラメータ ＆ 比率基準

| 部位 | 推奨値 / 比率 | 造形特徴 |
| :--- | :--- | :--- |
| **全高 (Total Height)** | 1.10m 〜 1.15m | デフォルメ島民標準サイズ |
| **頭身比 (Head Ratio)** | 2.1 〜 2.3 頭身 | 頭部高 約0.50m、胴体+脚 約0.63m |
| **頭部 (Head)** | X: 0.48m, Y: 0.42m, Z: 0.40m | キューブ＋Subdivision Surface (Level 2) ＋ 下膨れ頬変形 |
| **手先 (Hands)** | スキン半径 0.08m | 指を分けないミトン状・カプセル状の丸い手 |
| **胴体 (Torso)** | スキン半径 腹: 0.145m, 胸: 0.125m | 釣鐘・円錐台のコロンとしたふくらみ |
| **脚 (Legs)** | スキン半径 0.075m, 脚長 約0.24m | 短く丸い円柱脚 |
| **靴 (Shoes)** | 幅 0.10m, 長 0.15m, 高 0.085m | 接地 `Z = 0.0`、底面足音Surface ID連動 |

---

## 2. 3段モディファイアパイプライン (Blender Python)

```python
# 1. Mirror モディファイア（X軸対称）
mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
mod_mirror.use_axis[0] = True
mod_mirror.use_clip = True

# 2. Skin モディファイア（骨格ラインの肉付け）
mod_skin = obj.modifiers.new(name="Skin", type='SKIN')
skin_data = mesh.skin_vertices[0].data
# 頂点ごとの半径 (radius X, Y) を制御
skin_data[0].radius = (0.13, 0.13)   # 骨盤
skin_data[1].radius = (0.145, 0.14)  # お腹 (ふっくら)
skin_data[6].radius = (0.08, 0.08)   # 手先 (まるい手)

# 3. Subdivision Surface モディファイア（角丸め有機曲面化）
mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod_sub.levels = 2
mod_sub.render_levels = 2
```

---

## 3. ゲーム ＆ サウンド最適化マテリアルスロット

Unity / Unreal Engine などのゲームエンジン連携において、足音（Footstep）やマテリアル音（Physics Material / Surface ID）を確実に制御するため、以下の独立スロット構成を必須とします。

1. `Chibi_Skin_Mat`: やわらかな肌色（Subsurface Weight: 0.12, Roughness: 0.60）
2. `Chibi_Hair_Mat`: 髪色（Roughness: 0.45, Specular: 0.35）
3. `Chibi_ClothTop_Mat` / `Chibi_ClothBottom_Mat`: 衣服メイン・サブカラー（微細布地バンプ付き）
4. `Chibi_Footstep_Surface_Mat`: **靴底・足裏接触面（Footstep Surface ID判定専用）**
5. `Chibi_Eye_Mat` ＋ `Chibi_Eye_Highlight_Mat`: 瞳（Roughness: 0.15）および白く輝くハイライト（Emission: 0.3）

---

## 4. パーツ親子付け（Hierarchy）構造

```
[Chibi_Character_Body] (Root / Pivot Z=0.0)
  ├── Chibi_Character_Head
  │     ├── Chibi_Character_Eyes
  │     ├── Chibi_Character_Ears
  │     ├── Chibi_Character_Nose
  │     └── Chibi_Character_Hair (Short / Bob / Twintails)
  ├── Chibi_Character_Outfit (T-Shirt / One-Piece Dress)
  └── Chibi_Character_Shoes (Footstep Surface Slot included)
```
FBXエクスポート時にも構造が破綻せず、着せ替え・ボーンリグ（Armature）の適用が容易な構成です。
