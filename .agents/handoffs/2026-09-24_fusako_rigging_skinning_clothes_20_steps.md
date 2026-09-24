# ふさこ氏 第20話『ウェイト転送で服や揺れ物をスキニング（リギング編 第2回）』詳細操作手順・スキニング仕様書

本ドキュメントは、3Dモデラー・ふさこ氏のキャラクター制作チュートリアル第20話「ウェイト転送で服や揺れ物をスキニング 〜初級から中級者向けチュートリアル〜」（30分02秒）の詳細手順書である。
本話では、手作業でのウェイトペイントを極力排し、Blenderの **Data Transfer（データ転送モディファイア）** をフル活用した先進的スキニング手法を徹底解説する。静止バインド用ダミー素体（`WeightTransferBody`）の作成、ドロワーズ・靴・ワンピース・アウターへの一括転送、剛体髪の割り当て、小物アクセサリーの親メッシュ追従、そして「転送用プロキシ板メッシュ（Proxy Plane）」を用いた羽根・前髪・横髪・ツインテールの完全非破壊揺れ物スキニングまでを詳細に記録する。

📸 **対応スクリーンショットカタログ**:
- [docs/fusako_20_rigging_skinning_clothes_screenshots/README.md](../../docs/fusako_20_rigging_skinning_clothes_screenshots/README.md)

---

## 目次
1. [Chapter 1: 転送用ダミー素体の作成と衣服へのデータ転送スキニング](#chapter-1-転送用ダミー素体の作成と衣服へのデータ転送スキニング)
2. [Chapter 2: 剛体髪パーツの頭部（Head）ウェイト割り当て](#chapter-2-剛体髪パーツの頭部headウェイト割り当て)
3. [Chapter 3: 小物アクセサリーの親メッシュ追従データ転送](#chapter-3-小物アクセサリーの親メッシュ追従データ転送)
4. [Chapter 4: 浮遊する羽根のボーン追加とプロキシ三角板（Plane）転送](#chapter-4-浮遊する羽根のボーン追加とプロキシ三角板plane転送)
5. [Chapter 5: 前髪（センター・サイド）の揺れボーンとプロキシ板スキニング](#chapter-5-前髪センターサイドの揺れボーンとプロキシ板スキニング)
6. [Chapter 6: サイドヘア2連ボーン・ツインテールのスキニングと整理完了](#chapter-6-サイドヘア2連ボーンツインテールのスキニングと整理完了)
7. [データ転送＆プロキシ板スキニング Tips 総括](#データ転送プロキシ板スキニング-tips-総括)

---

## Chapter 1: 転送用ダミー素体の作成と衣服へのデータ転送スキニング

### Step 1-1: 転送専用ダミー素体（WeightTransferBody）の作成と分離
- ポーズモードで全ボーンを選択し、`Alt + R`、`Alt + G` でTポーズ（レスト姿勢）にリセット。
- スキニング済みの素体メッシュ（Body）を選択し、`Shift + D` で複製。
- 複製したオブジェクトを `WeightTransferBody` とリネーム。
- モディファイアプロパティで、`WeightTransferBody` の **Armature モディファイアを完全にOFF（または削除）** にする。
  - **重要理由**: ポーズを動かしたときに転送元が一緒に動いてしまうと、転送先の服が二重変形して破綻・爆発するため、常に静止したTポーズを維持する専用メッシュを用意する。
- アウトライナーで新コレクション `WeightTransfer` を作成し、そこへ移動。
[📸 参考: 01_c1_transfer_body_duplicate_armature_off.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/01_c1_transfer_body_duplicate_armature_off.jpg)

### Step 1-2: ドロワーズへの Data Transfer モディファイア設定
- ドロワーズ（インナー）を選択。
- モディファイア追加から **Data Transfer** を追加。
- 設定項目:
  - **Source**: `WeightTransferBody` を指定。
  - **Vertex Data**: チェックを入れてON。
  - **Vertex Groups**: チェックを入れてON。
  - **Mapping**: **Nearest Face Interpolated**（最も近い面の補間）を選択。
[📸 参考: 02_c1_drawers_data_transfer_nearest_face.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/02_c1_drawers_data_transfer_nearest_face.jpg)

### Step 1-3: Generate Data Layers と Armature モディファイア追加
- Data Transfer モディファイア内の **Generate Data Layers**（データレイヤーを生成）ボタンをクリック。
  - 素体が持っている全ボーンの頂点グループが一瞬でドロワーズ側に自動生成される。
- モディファイア追加から **Armature** モディファイアを追加し、VRMアーマチュアを指定。
- ボーンを動かすと、素体の下半身・お尻の滑らかなスキニングに完全同期してドロワーズが追従することを確認。
[📸 参考: 03_c1_generate_data_layers_armature_add.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/03_c1_generate_data_layers_armature_add.jpg)

### Step 1-4: Copy Attributes による靴・靴下へのモディファイア一括コピー
- 靴・靴下オブジェクトを選択後、設定済みのドロワーズを `Shift` 追加選択（ドロワーズがアクティブ）。
- `Ctrl + C` > **Copy Selected Modifiers** を実行し、Data Transfer と Armature を一括コピー。
- 靴オブジェクトを選択し、**Generate Data Layers** をクリック。靴・靴下のスキニングが一発完了。
[📸 参考: 04_c1_copy_attributes_transfer_to_shoes.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/04_c1_copy_attributes_transfer_to_shoes.jpg)

### Step 1-5: ワンピース（上半身）への転送と変形追従
- ワンピースを選択後、ドロワーズを追加選択して `Ctrl + C` でモディファイアをコピー。
- ワンピース側で **Generate Data Layers** をクリック。
- 素体の胸・背骨・腕のウェイトがワンピース上半身にそのまま高精度転送される（※スカート裾の揺れ物は後話で追加設定）。
[📸 参考: 05_c1_dress_data_transfer_body_follow.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/05_c1_dress_data_transfer_body_follow.jpg)

### Step 1-6: アウター・パーカーへの転送と袖・脇の追従点検
- パーカー・アウターにも同様に Data Transfer を適用し、Generate Data Layers を実行。
- 胴体や脇下など、素体に近い部位は素体の変形に沿って美しく追従。
- 素体から離れた袖口やフードの浮き部分は、後から微調整する前提で大枠の追従を確立。
[📸 参考: 06_c1_outer_hoodie_data_transfer_check.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/06_c1_outer_hoodie_data_transfer_check.jpg)

---

## Chapter 2: 剛体髪パーツの頭部（Head）ウェイト割り当て

### Step 2-1: 揺らさない髪（前髪・アホ毛・後頭部）のHead一括アサイン
- 物理で揺らさず頭の動きに100%固定追従させたい髪パーツを選択。
- `Tab` で編集モードに入り、全選択 `A`。
- 頂点グループ **`Head`** を選択し、**Weight: 1.000** で **Assign**（割り当て）。
- Armature モディファイアを追加（または Copy Attributes でコピー）。頭部回転時に完全に同期して動くことを確認。
[📸 参考: 07_c2_bangs_head_weight_1_assign.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/07_c2_bangs_head_weight_1_assign.jpg)

---

## Chapter 3: 小物アクセサリーの親メッシュ追従データ転送

### Step 3-1: パッチン留め（ヘアピン）の髪メッシュ追従転送
- 髪に刺さっているパッチン留め（ヘアピン）を選択。
- **Data Transfer** モディファイアを追加。
- **Source**: ボーンではなく、土台となっている横髪メッシュ（`SideHair`）を指定。
- `Vertex Data: ON`、`Vertex Groups: ON`、`Nearest Face Interpolated`、`Generate Data Layers`。
- Armature モディファイアを追加。横髪が将来物理で揺れた際、パッチン留めが髪の表面に吸着したまま完全追従する構造を確立。
[📸 参考: 08_c3_hairpin_data_transfer_from_sidehair.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/08_c3_hairpin_data_transfer_from_sidehair.jpg)

### Step 3-2: フード飾り（花・リボン）のフード追従転送
- フード側頭部に付けたお花・リボン飾りを選択。
- **Data Transfer** を追加し、**Source** に `Hood`（フードメッシュ）を指定。
- Generate Data Layers を実行後、Armature モディファイアを追加。フードの変形に飾りが完全に同期。
[📸 参考: 09_c3_hood_flower_data_transfer_from_hood.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/09_c3_hood_flower_data_transfer_from_hood.jpg)

---

## Chapter 4: 浮遊する羽根のボーン追加とプロキシ三角板（Plane）転送

### Step 4-1: 羽根用ボーン（Wing.L）の追加と Chest 親子付け
- アーマチュアの編集モードに入り、羽の根元位置に `Shift + A` でボーンを追加（`Wing.L` と命名）。
- `Wing.L` を選択後、`Chest`（胸ボーン）を追加選択し、`Ctrl + P` > **Keep Offset** で親子付け。
- 右クリック > **Symmetrize** で右側の `Wing.R` を自動生成。
[📸 参考: 10_c4_wing_bone_add_chest_parent.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/10_c4_wing_bone_add_chest_parent.jpg)

### Step 4-2: 転送用プロキシ三角板（Plane）の作成
- 羽本体のラティスモディファイアを一時OFFにする。
- `Shift + A` > Mesh > **Plane** を追加し、羽のメッシュの中心断面に重ねて配置。
- 編集モードで1頂点を削除し、羽の形状に合わせたシンプルな **「3頂点の三角板ポリゴン」** を作成。
[📸 参考: 11_c4_wing_proxy_triangle_plane.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/11_c4_wing_proxy_triangle_plane.jpg)

### Step 4-3: プロキシ板への Chest / Wing.L ウェイトアサイン
- プロキシ板に頂点グループ **`Chest`** と **`Wing.L`** を作成。
- 体（根元）側の頂点を選択し、`Chest: 1.000` をアサイン。
- 先端側の頂点を選択し、`Wing.L: 1.000` をアサイン。
- ウェイトペイントモードで確認すると、根元から先端へ完璧に均一な線形グラデーションが形成されている。
[📸 参考: 12_c4_proxy_chest_wing_vertex_weights.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/12_c4_proxy_chest_wing_vertex_weights.jpg)

### Step 4-4: 羽本体への Data Transfer 適用と非破壊ウェイト転送
- 羽メッシュを選択し、**Data Transfer** モディファイアを追加。
- **Source**: 作成したプロキシ三角板メッシュを指定。
- `Nearest Face Interpolated` で **Generate Data Layers** を実行。
- モディファイアの並び順を `Data Transfer` $\to$ `Lattice` $\to$ `Armature` に整える。
- ボーンを動かすと、立体的な羽全体が根元を固定されたまま美しくしなって動くことを確認。
[📸 参考: 13_c4_wing_data_transfer_proxy_source.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/13_c4_wing_data_transfer_proxy_source.jpg)

### Step 4-5: Mirror設定と空の Wing.R グループ作成
- プロキシ板に **Mirror** モディファイアを追加。
- プロキシ板および羽本体に空の頂点グループ **`Wing.R`** を作成。
- 羽本体側で再度 Generate Data Layers を押すことで、左右対称の羽がそれぞれのボーンで個別にしなる設定が完了。
[📸 参考: 14_c4_wing_mirror_wing_r_empty_group.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/14_c4_wing_mirror_wing_r_empty_group.jpg)

### Step 4-6: プロキシ板頂点移動による非破壊ウェイト減衰微調整
- 羽の曲がりが大きすぎる場合、羽メッシュ本体をペイントする必要は一切ない。
- プロキシ三角板の先端頂点を少し手前に縮めたり、Chestウェイトをブレンド（Normalize All）するだけで、羽全体の変形量がリアルタイムに追従・変化。
[📸 参考: 15_c4_proxy_vertex_move_tweak_falloff.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/15_c4_proxy_vertex_move_tweak_falloff.jpg)

---

## Chapter 5: 前髪（センター・サイド）の揺れボーンとプロキシ板スキニング

### Step 5-1: 前髪中央用ボーン（HairBang.C）の配置
- 前髪の中央生え際に3Dカーソルを配置（`Shift + S` > Cursor to Selected）。
- アーマチュア編集モードで `Shift + A` でボーン追加（`HairBang.C`）。
- 毛先に向かって下方向に配置し、親ボーンに `Head` を指定。
[📸 参考: 16_c5_hair_bang_c_bone_placement.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/16_c5_hair_bang_c_bone_placement.jpg)

### Step 5-2: 前髪プロキシ四角板（Plane）の作成とウェイト配分
- `Shift + A` > Mesh > **Plane** を前髪中央に配置。
- 上部2頂点を `Head: 1.000`、下部2頂点を `HairBang.C: 1.000` にアサイン。
[📸 参考: 17_c5_hair_bang_quad_proxy_plane.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/17_c5_hair_bang_quad_proxy_plane.jpg)

### Step 5-3: 前髪への Data Transfer 適用
- 前髪メッシュに Data Transfer を追加し、プロキシ四角板から転送。
- 前髪中央の毛先が滑らかに揺れるウェイトが瞬時に完成。
[📸 参考: 18_c5_hair_bang_data_transfer_follow.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/18_c5_hair_bang_data_transfer_follow.jpg)

### Step 5-4: 横前髪ボーン（HairBang.L）と三角プロキシ板
- 横前髪に `HairBang.L` ボーンを追加。
- 3頂点の三角プロキシ板を作成し、上2頂点に `Head: 1.000`、下1頂点に `HairBang.L: 1.000` を割り当て。
[📸 参考: 19_c5_hair_side_bone_triangle_proxy.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/19_c5_hair_side_bone_triangle_proxy.jpg)

### Step 5-5: Symmetrize による対称化と前髪スキニング完了
- ボーンを右クリック > **Symmetrize** で `HairBang.R` を生成。
- プロキシ板に Mirror モディファイアを追加し、空の `HairBang.R` グループを作成して転送。前髪全体の揺れ設定が完了。
[📸 参考: 20_c5_hair_side_symmetrize_transfer.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/20_c5_hair_side_symmetrize_transfer.jpg)

---

## Chapter 6: サイドヘア2連ボーン・ツインテールのスキニングと整理完了

### Step 6-1: サイドヘア2連ボーン（HairSide.001 / .002）の追加
- サイドヘアの生え際から中間、毛先にかけて `E` キーで2連ボーンを押し出し配置。
- 命名: `HairSide.001.L` $\to$ `HairSide.002.L`。
[📸 参考: 21_c6_side_hair_chain_bones_add.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/21_c6_side_hair_chain_bones_add.jpg)

### Step 6-2: 帯状プロキシ板と3段ウェイト配分による多段揺れ
- 縦長の板ポリゴン（Plane）を配置し、`Ctrl + R` でループカットを追加して3段構成にする。
- 上段: `Head: 1.000`
- 中段: `HairSide.001.L: 1.000`
- 下段: `HairSide.002.L: 1.000`
- サイドヘアへ Data Transfer で転送。2段階のしなりを持つ極めて滑らかな多関節ウェイトが完成。
[📸 参考: 22_c6_side_hair_long_strip_proxy_weights.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/22_c6_side_hair_long_strip_proxy_weights.jpg)

### Step 6-3: ツインテール用ボーンとプロキシ板転送
- ツインテール（`HairTail`）パーツに対しても同様にボーンと専用プロキシ板を作成し転送。
- 複雑にねじれたツインテール毛束も、板ポリゴン1枚からの投影により一切の歪みなくスキニング。
[📸 参考: 23_c6_twintail_bone_plane_proxy_transfer.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/23_c6_twintail_bone_plane_proxy_transfer.jpg)

### Step 6-4: プロキシコレクション整理と衣服・揺れ物スキニング完了
- 作成した転送用ダミー素体および全プロキシ板（Plane）を `WeightTransfer` コレクションへ格納し、ビューポート・レンダリングともに非表示（チェックOFF）に設定。
- 服・髪・小物アクセサリーの全スキニング工程がここに完全完了！
[📸 参考: 24_c6_proxy_collection_clean_skinning_complete.jpg](../../docs/fusako_20_rigging_skinning_clothes_screenshots/24_c6_proxy_collection_clean_skinning_complete.jpg)

---

## データ転送＆プロキシ板スキニング Tips 総括

| 手法 / テクニック | 操作内容 | 効能・ゲーム開発/VRMへのメリット |
|:---|:---|:---|
| **静止ダミー素体バインド** | 素体複製 $\to$ Armature OFF $\to$ Data Transfer | ポーズ変形による転送座標狂いを完全排除。常に安定したTポーズウェイトを衣服へ投影。 |
| **Copy Attributes 一括適用** | 複数選択 $\to$ `Ctrl + C` > Copy Selected Modifiers | ドロワーズ、靴、ワンピース、パーカーへ Data Transfer & Armature を一瞬で複製。 |
| **親子メッシュ転送** | アクセサリーの Source に親メッシュ（髪やフード）を指定 | 髪ピンやリボンが親メッシュの物理変形に100%吸着追従。めり込み・浮き上がりを防止。 |
| **転送用プロキシ板（Proxy Plane）** | 単純な板ポリゴン（3〜4頂点）にウェイト $\to$ 本番へ転送 | 複雑な毛束・羽根に手塗りする手間を全廃。頂点移動だけで全体の減衰・曲がり幅を非破壊制御。 |
| **非破壊リトポロジー耐性** | Data Transfer モディファイアを維持 | 本番モデルに後からポリゴン分割や装飾を追加しても、自動的にウェイトが再投影され手戻りゼロ。 |
