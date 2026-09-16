# 🐻 どうぶつの森風 デフォルメ3Dキャラクタースタジオ レシピ集 (Chibi Character Recipes)

## 概要
YouTubeチュートリアル動画『【Blender】人物の「3Dキャラクター」の作り方』（サルブレ様 / `72w5Il1HCGk`）から抽出した **「Single Vert 骨格 ＋ 3段モディファイア（Mirror + Skin + Subdiv）＋ 部位別モジュール分離モデリング」** をベースに、『どうぶつの森』特有の 2.0〜2.5頭身・コロンとした球状手足・釣鐘型胴体のプロポーションをプロシージャル化した検証済みレシピです。

---

## 1. 核心幾何学パラメータ ＆ 比率基準

| 部位 | 推奨値 / 比率 | 造形特徴 ＆ 最適化ポリゴン配分 |
| :--- | :--- | :--- |
| **全高 (Total Height)** | 1.10m 〜 1.15m | デフォルメ島民標準サイズ |
| **頭身比 (Head Ratio)** | 2.1 〜 2.3 頭身 | 頭部高 約0.50m、胴体+脚 約0.63m |
| **顔正面・頭部 (Head)** | 16x12 UV球 ＋ Subdiv 1 | 後頭部は髪で隠れるため適正間引き（約730頂点）。顔正面の愛らしい下膨れ頬をキープ |
| **前髪・髪型 (Hair)** | 20x12 UV球 ＋ Subdiv 1 | 滑らかなM字アーチの生え際 ＋ 前髪房（約960頂点）。後頭部の過密を排除 |
| **衣装 (Outfit)** | 20 segments ＋ 袖 (12 segments) | 袖で腕の貫通を完全ガードしつつ適正分割（約700頂点） |
| **手先・胴体 (Body)** | スキン半径 腹:0.145m, 手:0.08m | Subdiv Level 2（約1,080頂点）。ミトン状丸い手を低負荷で滑らかに |
| **耳 (Ears)** | 12x8 UV球 (Subdivなし) | 丸耳をスムーズシェードのみで美しく表現（約170頂点、94%間引き） |
| **表情・目 (Eyes/Nose)** | 瞳 20 seg, 鼻 12 seg | **顔全高の約19%** の黄金比（rx:0.026m, rz:0.040m）。どうぶつの森特有のつぶらで愛らしい表情（`chibi_eye_scale` スライダー完備、約200頂点） |
| **靴 (Shoes)** | 幅 0.10m, 長 0.15m, 高 0.085m | 接地 `Z = 0.0`、底面足音Surface ID連動（約196頂点） |
| **総ポリゴン密度** | **評価頂点数 約4,000 verts** | **40,000頂点から約90%の軽量化を達成**したリアルタイム実用最適バランス |



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
  │     ├── Chibi_Character_Eyes (Shape Keys: Basis, Blink, Smile, Wide, Squint)
  │     ├── Chibi_Character_Eyebrows (Arch / Dot / Straight)
  │     ├── Chibi_Character_Ears
  │     ├── Chibi_Character_Nose
  │     └── Chibi_Character_Hair (Pure Hairstyles x12)
  ├── Chibi_Character_Outfit (Top Cloth + Small Buttons Slot: Overalls/Coat/T-Shirt)
  └── Chibi_Character_Shoes (Footstep Surface Slot included)
```
FBXエクスポート時にも構造が破綻せず、着せ替え・ボーンリグ（Armature）の適用、Unity/UEでのBlendShape表情アニメーションや足音判定が容易な構成です。

---

## 5. どうぶつの森風「つぶらな表情」黄金比率 ＆ シェイプキー（表情差分）

アニメ・少女漫画調のキャラクターと『どうぶつの森』キャラクターの決定的な違いは **「目の比率と配置」** にあります。

- **目と頭部の黄金比**:
  - 頭部全高（約0.42m）に対して瞳の縦幅は **約0.080m（約19%）** が最も「どうぶつの森らしい」素朴なつぶらさを演出します。30%を超えるとアニメ・少女漫画風になり世界観が崩れるため注意。
- **重心と目鼻の三角形**:
  - 瞳の中心Z座標を頭部中心よりわずかに低め（`head_center_z - 0.040m`）に配置し、鼻をその直下（`head_center_z - 0.054m`）に置くことで、幼児的で愛らしいコンパクトな顔面三角形を形成。
- **シェイプキー（Blend Shapes）による表情アニメーション**:
  - 目のメッシュには生成時に以下のシェイプキーが自動装備されます：
    - `Basis`: デフォルトの目（開眼）
    - `Blink`: 自然なまばたき・目閉じ
    - `Smile`: にっこり三日月笑顔
    - `Wide`: 見開き・驚き
    - `Squint`: じと目・照れ
  - Unity / Unreal Engine のアニメーションやスクリプトから `SetBlendShapeWeight` で瞬時に表情を切り替え可能。

---

## 6. 純粋ヘアスタイル（12種）とハイポリ有機造形

帽子・被り物は頭部へのめり込みリスクがあるため全撤廃し、純粋なヘアスタイル12種に特化。高密度UV球（44×28分割）と数学的境界スナップにより、カクつきのない滑らかな毛束フリンジ、もみあげ、首筋に沿うV/W字襟足カーブを実現しています。

| スタイルID | スタイル名 | 造形特徴 |
| :--- | :--- | :--- |
| `SHORT` | ✂️ ショートヘア | 眉上に沿う斜め毛束フリンジ ＆ 耳前もみあげ ＆ 首筋V字襟足 |
| `SHORT_MESSY`| 🌪️ 無造作ショート | アシンメトリーな毛束フリンジと立体ハネ感 |
| `CENTER_PART`| 🪞 センター分け | おでこを覗かせ左右に流れるナチュラルヘア |
| `BOB` | 💇‍♀️ ふんわりボブ | フェイスラインを包む丸い内巻きボブ |
| `MUSHROOM` | 🍄 キノコマッシュ | 丸いボウル形状とおかっぱ前髪 |
| `TWINTAILS` | 🎀 ツインテール | 両サイドのポンポンお団子ヘア |
| `BRAIDS` | 👧 おさげ・三つ編み | 左右に垂れる球体ステップ編み込み |
| `PONYTAIL` | 🐴 ポニーテール | 結び目リング ＋ 後方に流れるポニーテール房 |
| `TOPKNOT` | 🍙 ちょんまげ/お団子 | 頭頂部の一結びお団子ノット |
| `SPIKY` | ⚡ ツンツンヘア | 頭頂部〜後頭部の元気なハネスパイク |
| `WAVY_LONG` | 🌊 ウェーブロング | 肩口まで届く長髪ウェーブ |
| `AFRO` | 🐑 もこもこアフロ | 頭部をふんわり包むボリュームヘア（顔面くり抜き） |

- **境界頂点スナップアルゴリズム**:
  UV球のステップ削除後に境界頂点（`is_boundary`）を連続曲線関数 `calc_hair_cutoff(norm_x, norm_y)` のZ値へ投影。離散グリッドによる階段状ギザギザを解消し、BlenderのSubsurfと相まって極めて滑らかな有機的シルエットを生成。

---

## 7. 眉毛パーツ（4種）と衣装の立体装飾ボタン

- **眉毛パーツ**:
  - `ARCH`: なだらかなアーチ眉
  - `DOT`: ちょこんとした丸眉（麻呂眉）
  - `STRAIGHT`: キリッとしたまっすぐ眉
  - `NONE`: 眉毛なし
  - 顔の楕円曲面に自動フィットし、Mirrorモディファイアで左右対称配置。
- **衣装の装飾丸ボタン**:
  - `OVERALLS`: 左右の肩紐留め具に小さな丸ボタン（2個）
  - `COAT`: 前立てに小さな丸ボタン（縦2個）
  - `T_SHIRT`: 首元ヘンリーネックのワンポイントボタン（1個）
  - ボタン専用のマテリアルスロット（`BUTTON`）を付与し、金具・光沢の個別調整が可能。


