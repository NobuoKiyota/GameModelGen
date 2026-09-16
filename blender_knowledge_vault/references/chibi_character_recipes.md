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
  │     ├── Chibi_Character_Eyes
  │     ├── Chibi_Character_Ears
  │     ├── Chibi_Character_Nose
  │     └── Chibi_Character_Hair (Short / Bob / Twintails)
  ├── Chibi_Character_Outfit (T-Shirt / One-Piece Dress)
  └── Chibi_Character_Shoes (Footstep Surface Slot included)
```
FBXエクスポート時にも構造が破綻せず、着せ替え・ボーンリグ（Armature）の適用が容易な構成です。

---

## 5. どうぶつの森風「つぶらな表情」黄金比率

アニメ・少女漫画調のキャラクターと『どうぶつの森』キャラクターの決定的な違いは **「目の比率と配置」** にあります。

- **目と頭部の黄金比**:
  - 頭部全高（約0.42m）に対して瞳の縦幅は **約0.080m（約19%）** が最も「どうぶつの森らしい」素朴なつぶらさを演出します。30%を超えるとアニメ・少女漫画風になり世界観が崩れるため注意。
- **重心と目鼻の三角形**:
  - 瞳の中心Z座標を頭部中心よりわずかに低め（`head_center_z - 0.040m`）に配置し、鼻をその直下（`head_center_z - 0.054m`）に置くことで、幼児的で愛らしいコンパクトな顔面三角形を形成。
- **UI調整スライダー**:
  - `chibi_eye_scale`（0.5〜1.6、デフォルト 1.0）により、キャラクターごとの個性（くりくりした目〜極小のつぶらな点目）をノンコーディングで微調整可能。

---

---

## 6. バリエーション拡張（髪型14種・衣装6種・目5種・柄4種・アクセ3種）

キャラクターメイキングの自由度を劇的に高めるため、どうぶつの森ライクな多様なモジュールを完備しています。

### 髪型 (Hair Styles - 14種)
| スタイルID | スタイル名 | 造形特徴 |
| :--- | :--- | :--- |
| `SHORT` | ✂️ ショートヘア | 前髪の自然なウェーブ束感（男の子定番） |
| `BOB` | 💇‍♀️ ふんわりボブ | フェイスラインを包む丸い内巻きボブ |
| `TWINTAILS`| 🎀 ツインテール/お団子 | 両サイドのポンポンお団子ヘア |
| `SPIKY` | ⚡ ツンツンヘア | 元気な男の子風のハネスパイク（6房） |
| `PONYTAIL` | 🐴 ポニーテール | 後頭部の結び目リング ＋ 後方に流れるポニーテール房 |
| `AFRO` | 🐑 もこもこアフロ | 頭部をふんわり包むボリュームヘア（顔面くり抜き） |
| `CAP` | 🧢 つば付きキャップ | 前方に突き出すバイザー（つば）＋頭頂部の天ボタン |
| `MUSHROOM` | 🍄 マッシュルーム | まるいキノコ型マッシュボウルカット・どう森大定番 |
| `BRAIDS` | 👩‍🌾 みつあみ・おさげ | 両サイドに垂れる素朴で愛らしい三連コブのおさげ |
| `TOPKNOT` | 🍙 ちょんまげ/お団子 | 頭頂部にちょこんと乗った結び玉・和風＆侍スタイル |
| `WAVY_LONG` | 💁‍♀️ ウェーブロング | 肩まで届くゆるふわウェーブ長髪 |
| `CAT_HOOD` | 🐱 ネコ耳フード | どうぶつの森らしいネコ耳着ぐるみフード |
| `KNIT_CAP` | 🧶 ポンポンニット帽 | 冬の島民スタイル・折り返しカフとポンポン付き |
| `WITCH_HAT` | 🧙‍♀️ 魔女のとんがり帽子 | 大つばと後方に少し曲がるとんがりコーン |

### 衣装 (Outfits - 6種)
| 衣装ID | 衣装名 | 造形特徴 |
| :--- | :--- | :--- |
| `T_SHIRT` | 👕 Tシャツ＆短パン | 半袖＋胴体（袖による腕の貫通完全ガード） |
| `ONE_PIECE`| 👗 釣鐘型ワンピース | 裾がふわりと広がる愛らしいワンピースドレス |
| `HOODIE` | 🧥 フード付きパーカー | ゆったり胴体＋長袖＋背中のふっくらフード袋 |
| `OVERALLS` | 👖 オーバーオール | むらびとの大定番サロペット作業着＋肩紐サスペンダー |
| `KIMONO` | 👘 着物・ゆかた | 足首までストレートに伸びる裾＋角型振袖＋帯 |
| `COAT` | 🧥 ダッフルコート | 厚手の長袖＋折り返し襟＋腰下まで覆う冬コート |

### 目の形状 (Eye Styles - 5種)
- `OVAL`: 縦長の愛らしいアニメ調のつぶらな瞳
- `ROUND`: クリっとした真ん丸ドット瞳
- `DROOPY`: おっとり癒やし系の素朴なたれ目
- `CAT_EYE`: クールで勝ち気なネコ目・つり目
- `SMILING`: にっこり三日月笑顔（細い円弧アーチ目）

### 服の柄 (Patterns - 4種)
- `PLAIN`: 単色無地カラー
- `STRIPED`: プロシージャル横シマボーダー柄
- `POLKA_DOT`: ポップな水玉ドット柄
- `ISLAND_LEAF`: どうぶつの森の象徴・胸の葉っぱワンポイント

### アクセサリー (Accessories - 3種)
- `NONE`: 装飾なし
- `ROUND_GLASSES`: 知的な丸型フレームメガネ（レンズ枠＋ブリッジ＋ツル）
- `CHEEK_BLUSH`: 両頬のふんわりピンクチーク

---

## 7. リアルタイム即時反映（Live Morphing）仕様

UIのスライダーやドロップダウン（髪型、衣装、柄、アクセサリー、目の形、目のサイズ、各種カラー）を変更すると、
Blenderのプロパティコールバック `update=update_chibi_character_live` が発動し、
「🔄 更新」ボタンを押さずとも、選択中のChibiキャラクターがビューポート上でリアルタイムに即座に変形・反映されます。
さらに「🎲 ガチャ抽選 (Re-Roll)」を押すことで、全パーツ・全カラーがランダムに組み合わさった個性豊かな島民が瞬時に誕生します。


