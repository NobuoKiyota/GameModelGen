# ふさこ氏 第20話『ウェイト転送で服や揺れ物をスキニング（リギング編 第2回）』スクリーンショットカタログ

本ドキュメントは、ふさこ氏のBlender 3Dキャラクター制作チュートリアル第20話「ウェイト転送で服や揺れ物をスキニング 〜初級から中級者向けチュートリアル〜」（30分02秒）の重要操作シーンを高解像度キャプチャした全24枚の画像カタログです。
素体から衣服への Data Transfer（データ転送モディファイア）による一括スキニング、Copy Attributes Menu による設定複製、剛体髪の割り当て、小物アクセサリーの追従、そして「転送用プロキシ板メッシュ（Plane）」を用いた羽根・前髪・横髪・ツインテールの超高精度かつ非破壊な揺れ物スキニング技法を網羅しています。

📖 **対応する詳細リギング・スキニング仕様書・操作手順書**:
- [2026-09-24_fusako_rigging_skinning_clothes_20_steps.md](../../.agents/handoffs/2026-09-24_fusako_rigging_skinning_clothes_20_steps.md)

---

## スクリーンショット一覧（全24枚）

| No | スクリーンショット（クリックで原寸表示） | タイムスタンプ | チャプター | モデリング・リギング・ウェイト操作・キー操作 |
|:---|:---|:---|:---|:---|
| 01 | [01_c1_transfer_body_duplicate_armature_off.jpg](./01_c1_transfer_body_duplicate_armature_off.jpg) | 00:00:35 | Ch.1 転送用ダミー素体の作成 | スキニング済み素体を `Shift + D` で複製し `WeightTransferBody` と命名。ArmatureモディファイアをOFFにし、ポーズ変形の影響を受けない静止基準メッシュを別コレクションへ分離。 |
| 02 | [02_c1_drawers_data_transfer_nearest_face.jpg](./02_c1_drawers_data_transfer_nearest_face.jpg) | 00:01:45 | Ch.1 ドロワーズへのデータ転送設定 | ドロワーズに **Data Transfer** モディファイアを追加。Source: `WeightTransferBody`、**Vertex Data: ON**、**Vertex Groups: ON**、**Mapping: Nearest Face Interpolated** に設定。 |
| 03 | [03_c1_generate_data_layers_armature_add.jpg](./03_c1_generate_data_layers_armature_add.jpg) | 00:02:05 | Ch.1 データレイヤー生成とArmature追加 | **Generate Data Layers** をクリックして素体の全頂点グループを一括自動生成。Armatureモディファイアを追加してボーン追従を開始。 |
| 04 | [04_c1_copy_attributes_transfer_to_shoes.jpg](./04_c1_copy_attributes_transfer_to_shoes.jpg) | 00:03:15 | Ch.1 Copy Attributesによるモディファイア一括複製 | 靴・靴下を選択後ドロワーズを `Shift` 選択し、`Ctrl + C` > **Copy Selected Modifiers**（Data Transfer & Armature）を実行。靴側で Generate Data Layers を押して一発追従。 |
| 05 | [05_c1_dress_data_transfer_body_follow.jpg](./05_c1_dress_data_transfer_body_follow.jpg) | 00:04:25 | Ch.1 ワンピースへの転送と変形追従 | ワンピースにも同様にモディファイアをコピーし Generate Data Layers。素体の滑らかなグラデーションウェイトがそのままワンピース上半身へ正確に転送。 |
| 06 | [06_c1_outer_hoodie_data_transfer_check.jpg](./06_c1_outer_hoodie_data_transfer_check.jpg) | 00:05:30 | Ch.1 アウター・パーカーの転送と腕・脇点検 | パーカー・アウターへのデータ転送。素体に近い脇・胴体は美しく追従。素体から離れている袖先などは後から微調整する方針で一括適用。 |
| 07 | [07_c2_bangs_head_weight_1_assign.jpg](./07_c2_bangs_head_weight_1_assign.jpg) | 00:06:50 | Ch.2 剛体髪のHeadウェイト割り当て | 前髪・頭部髪パーツを編集モードで全選択 `A`。頂点グループ `Head` に Weight: 1.0 で **Assign**。Armatureモディファイアを追加して頭部に完全同期。 |
| 08 | [08_c3_hairpin_data_transfer_from_sidehair.jpg](./08_c3_hairpin_data_transfer_from_sidehair.jpg) | 00:08:35 | Ch.3 パッチン留め（ヘアピン）の転送追従 | パッチン留めに Data Transfer を追加し、Sourceに土台となる横髪（`SideHair`）を指定。将来横髪が物理で揺れた際にもクリップが完全に同期追従する構造を構築。 |
| 09 | [09_c3_hood_flower_data_transfer_from_hood.jpg](./09_c3_hood_flower_data_transfer_from_hood.jpg) | 00:09:30 | Ch.3 フード飾り（花・リボン）の転送追従 | フード横のお花・リボン飾りに Data Transfer を追加し、Sourceに `Hood`（フード）を指定。フードの曲面変形に小物が寸分違わず同期。 |
| 10 | [10_c4_wing_bone_add_chest_parent.jpg](./10_c4_wing_bone_add_chest_parent.jpg) | 00:11:00 | Ch.4 羽根ボーンの追加とChest親子付け | 羽の根元に `Shift + A` でボーン追加（`Wing.L`）。親ボーンに `Chest`（胸）を指定し `Ctrl + P > Keep Offset`。右クリック `Symmetrize` で `Wing.R` を自動生成。 |
| 11 | [11_c4_wing_proxy_triangle_plane.jpg](./11_c4_wing_proxy_triangle_plane.jpg) | 00:12:10 | Ch.4 転送用プロキシ三角板（Plane）作成 | 【神Tips】羽の立体メッシュ内部に `Shift + A` > Plane を配置。1頂点を削除して3頂点の極小「三角板ポリゴン」を作成。 |
| 12 | [12_c4_proxy_chest_wing_vertex_weights.jpg](./12_c4_proxy_chest_wing_vertex_weights.jpg) | 00:12:40 | Ch.4 プロキシ板のウェイト割り当て | 三角板の根元頂点に `Chest: 1.0`、先端頂点に `Wing.L: 1.0` をアサイン（Normalize Allで合計1.0化）。完璧な線形グラデーション板を構築。 |
| 13 | [13_c4_wing_data_transfer_proxy_source.jpg](./13_c4_wing_data_transfer_proxy_source.jpg) | 00:13:15 | Ch.4 羽本体へのプロキシ板転送適用 | 羽本体に Data Transfer を追加し、Sourceに三角プロキシ板を指定。Nearest Face Interpolated で転送し、羽の立体形状全体へ破綻のない滑らかウェイトを一発転送。 |
| 14 | [14_c4_wing_mirror_wing_r_empty_group.jpg](./14_c4_wing_mirror_wing_r_empty_group.jpg) | 00:14:05 | Ch.4 Mirror対応と空のWing.Rグループ | プロキシ板に Mirror モディファイアを追加し、羽本体に空の頂点グループ `Wing.R` を作成。左右の羽が独立して個別にボーン揺れ追従する構成を確立。 |
| 15 | [15_c4_proxy_vertex_move_tweak_falloff.jpg](./15_c4_proxy_vertex_move_tweak_falloff.jpg) | 00:14:35 | Ch.4 プロキシ板頂点移動による減衰微調整 | 羽根がボーンに対して動きすぎないよう、プロキシ板の先端頂点を少し手前に縮めたり、Chestウェイトをブレンド。わずか数頂点の移動だけで羽全体の曲がり度合いを自在に制御。 |
| 16 | [16_c5_hair_bang_c_bone_placement.jpg](./16_c5_hair_bang_c_bone_placement.jpg) | 00:16:20 | Ch.5 前髪センター用ボーンの配置 | 前髪中央に `HairBang.C` ボーンを追加。親ボーンを `Head` に設定。 |
| 17 | [17_c5_hair_bang_quad_proxy_plane.jpg](./17_c5_hair_bang_quad_proxy_plane.jpg) | 00:17:00 | Ch.5 前髪プロキシ四角板の作成 | 4頂点のシンプルな Plane を前髪に重ねて配置。上部2頂点を `Head: 1.0`、下部2頂点を `HairBang.C: 1.0` にアサイン。 |
| 18 | [18_c5_hair_bang_data_transfer_follow.jpg](./18_c5_hair_bang_data_transfer_follow.jpg) | 00:17:55 | Ch.5 前髪へのData Transfer転送 | 前髪メッシュへ Data Transfer を追加しプロキシ四角板から転送。手塗りでは不可能な完全均一の縦グラデーションウェイトが前髪全体に適用。 |
| 19 | [19_c5_hair_side_bone_triangle_proxy.jpg](./19_c5_hair_side_bone_triangle_proxy.jpg) | 00:19:40 | Ch.5 横前髪ボーンと三角プロキシ板 | 横前髪に `HairBang.L` ボーンを追加。三角プロキシ板を配置し、上2頂点に `Head: 1.0`、下1頂点に `HairBang.L: 1.0` を割り当て。 |
| 20 | [20_c5_hair_side_symmetrize_transfer.jpg](./20_c5_hair_side_symmetrize_transfer.jpg) | 00:21:25 | Ch.5 Symmetrizeと前髪転送完了 | ボーンを Symmetrize して `HairBang.R` を生成。プロキシ板に Mirror を追加し、左右対称の前髪揺れスキニングが完了。 |
| 21 | [21_c6_side_hair_chain_bones_add.jpg](./21_c6_side_hair_chain_bones_add.jpg) | 00:23:15 | Ch.6 サイドヘア2連ボーンの追加 | サイドヘアの根元から毛先にかけて2連ボーン（`HairSide.001` $\to$ `HairSide.002`）を `E` キーで押し出し追加。 |
| 22 | [22_c6_side_hair_long_strip_proxy_weights.jpg](./22_c6_side_hair_long_strip_proxy_weights.jpg) | 00:24:35 | Ch.6 帯状プロキシ板と3段ウェイト配分 | 縦長の長方形板ポリゴンを作成しループカットで3段に分割。上段 `Head: 1.0`、中段 `HairSide.001: 1.0`、下段 `HairSide.002: 1.0` をアサインしてサイドヘアへ転送。 |
| 23 | [23_c6_twintail_bone_plane_proxy_transfer.jpg](./23_c6_twintail_bone_plane_proxy_transfer.jpg) | 00:28:00 | Ch.6 ツインテール用ボーンとプロキシ転送 | ツインテール（`HairTail`）にボーンを追加し、専用の板プロキシを作成してウェイト転送。複雑な束感を持つ髪型も瞬時に破綻なくスキニング。 |
| 24 | [24_c6_proxy_collection_clean_skinning_complete.jpg](./24_c6_proxy_collection_clean_skinning_complete.jpg) | 00:29:30 | Ch.6 プロキシコレクション整理とスキニング完了 | 作成した全プロキシ板（Plane）を `WeightTransfer` コレクションへ集約・非表示化。服・髪・揺れ物アクセサリーの全スキニングが完全完了！ |

---

## 技術要点・スキニングの極意（第20話）

1. **静止ダミー素体（`WeightTransferBody`）による安全転送**:
   - スキニング済み素体から服へウェイト転送する際、素体がボーンポーズで動いてしまうと転送元の座標が狂い、服が爆発・破綻する。
   - 素体を複製して Armature モディファイアを完全にOFFにした「純粋なTポーズ静止体」を転送専用ソースとすることで、ポーズ状態に関係なく常に安定した転送を保証。
2. **転送用プロキシ板メッシュ（Proxy Plane）の革新性**:
   - ハイポリや複雑な3次元曲面（羽、束状の髪、ツインテール等）に対し、直接ブラシで手塗りすると、毛束の内外や裏表でウェイトムラ・凹みが発生しやすい。
   - **わずか3〜4頂点の単純な板ポリゴン（Plane）を内部に仕込み、板にボーンウェイトを割り当てて Data Transfer（Nearest Face Interpolated）で本番メッシュへ投影**。
   - 頂点スライド（`G G`）やスケールで板の形を変えるだけで、全体のしなり具合や減衰グラデーションを非破壊かつリアルタイムに微調整可能。
3. **トポロジー変更への完全な耐性**:
   - 手動ペイントしたメッシュは、後から頂点や分割ループを追加するとウェイトが崩れて塗り直しになる。
   - プロキシ板からの Data Transfer をモディファイアとして保持しておけば、本番メッシュのポリゴン数を増やしたりリダクションしても、自動的に最新トポロジーへウェイトが再投影されるため、手戻りコストがゼロ化。
4. **階層追従の連鎖（Hair $\to$ Hairpin、Hood $\to$ Ribbon）**:
   - パッチン留めやリボンなどの装飾品は、ボーンから直接転送するのではなく、**「土台となる髪メッシュやフードメッシュ」から Data Transfer でウェイトを転送**。
   - これにより、土台の髪が物理ボーンで揺れた際、ピン留めされたアクセサリーが寸分の狂いもなく完全に貼り付いて追従する。
