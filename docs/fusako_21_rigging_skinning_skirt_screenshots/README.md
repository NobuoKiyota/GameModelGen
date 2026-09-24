# ふさこ氏 第21話『スカートなどのスキニング・ウェイト転送（リギング編 第3回）』スクリーンショットカタログ

本ドキュメントは、ふさこ氏のBlender 3Dキャラクター制作チュートリアル第21話「スカートなどのスキニング・ウェイト転送 〜初級から中級者向けチュートリアル〜」（27分06秒）の重要操作シーンを高解像度キャプチャした全24枚の画像カタログです。
円筒プロキシメッシュを用いた後ろ髪のボーン配置とウェイト転送、プロキシの押し出し厚み付けによる内側ウェイト改善、スカート裾のプロキシメッシュ作成、3Dカーソル中心のボーンロール再計算（放射状Z軸整列）、With Empty Groups による1頂点1ボーン手動アサイン、空の頂点グループ（Spine/Chest: 0）による素体ウェイト完全置換、および制限頂点グループによる上半身・下半身の部位マスク制御までを網羅しています。

📖 **対応する詳細リギング・スキニング仕様書・操作手順書**:
- [2026-09-24_fusako_rigging_skinning_skirt_21_steps.md](../../.agents/handoffs/2026-09-24_fusako_rigging_skinning_skirt_21_steps.md)

---

## スクリーンショット一覧（全24枚）

| No | スクリーンショット（クリックで原寸表示） | タイムスタンプ | チャプター | モデリング・リギング・ウェイト操作・キー操作 |
|:---|:---|:---|:---|:---|
| 01 | [01_c1_cylinder_8verts_hair_proxy.jpg](./01_c1_cylinder_8verts_hair_proxy.jpg) | 00:00:30 | Ch.1 後ろ髪プロキシ作成 | `Shift + A` > Mesh > Cylinder（頂点数8、Cap: Nothing）を追加。`S` と `G Z` で後ろ髪全体をふんわり覆う円筒プロキシメッシュを作成。 |
| 02 | [02_c1_snap_bone_chain_to_cylinder.jpg](./02_c1_snap_bone_chain_to_cylinder.jpg) | 00:01:45 | Ch.1 頂点スナップによる髪ボーン配置 | Single Boneを追加し、頂点スナップでシリンダー面に沿ってボーン列を配置（`HairBack.A.001`, `B.001`, `C.001`）。Subdivideで2段化。 |
| 03 | [03_c1_autoname_symmetrize_hair_bones.jpg](./03_c1_autoname_symmetrize_hair_bones.jpg) | 00:02:35 | Ch.1 自動命名と左右対称化 | `Names > AutoName Left/Right` で `.L` 接尾辞を自動付与。右クリック `Symmetrize` で右側の `.R` ボーンを一発生成。 |
| 04 | [04_c1_cylinder_automatic_weights.jpg](./04_c1_cylinder_automatic_weights.jpg) | 00:03:25 | Ch.1 シリンダーへの自動ウェイト適用 | シリンダーメッシュと髪アーマチュアを選択し、`Ctrl + P` > **With Automatic Weights**。シリンダーの各段が対応ボーンに綺麗に連動。 |
| 05 | [05_c1_cylinder_top_vertices_head_assign.jpg](./05_c1_cylinder_top_vertices_head_assign.jpg) | 00:05:00 | Ch.1 シリンダー上端のHeadウェイト固定 | シリンダー上端ループの髪ボーンウェイトを消去し、頂点グループ `Head` に Weight: 1.0 でアサイン。頭部回転時の固定根元を確立。 |
| 06 | [06_c1_hair_data_transfer_from_cylinder.jpg](./06_c1_hair_data_transfer_from_cylinder.jpg) | 00:05:45 | Ch.1 後ろ髪へのData Transfer転送 | 後ろ髪メッシュに Data Transfer を追加し、Sourceにシリンダーを指定。Nearest Face Interpolated で転送し、複雑な後ろ髪全体がボーンに連動。 |
| 07 | [07_c1_hair_mask_vertex_group_remove.jpg](./07_c1_hair_mask_vertex_group_remove.jpg) | 00:08:10 | Ch.1 転送制限頂点グループによるマスク | 後ろ髪に制限用頂点グループ `WeightTransfer` を作成。動かしたくない生え際・内側頂点を除外し、Data Transfer のマスクに指定。 |
| 08 | [08_c1_extrude_cylinder_thickness_inner_fix.jpg](./08_c1_extrude_cylinder_thickness_inner_fix.jpg) | 00:09:40 | Ch.1 プロキシ押し出し厚み付け（内側改善） | 【神Tips】髪内側のウェイト乱れを解消するため、シリンダーを `E` $\to$ `Alt + S` で内側へ押し出し立体化。内側まで完全なウェイトを補間。 |
| 09 | [09_c1_display_as_wire_inner_skinning_check.jpg](./09_c1_display_as_wire_inner_skinning_check.jpg) | 00:10:15 | Ch.1 ワイヤー表示と髪内側の変形点検 | プロキシを Display As: Wire に設定。髪の内側メッシュが破綻なく滑らかにしなって追従していることを確認。 |
| 10 | [10_c1_hair_bones_parent_head_keep_offset.jpg](./10_c1_hair_bones_parent_head_keep_offset.jpg) | 00:11:30 | Ch.1 髪ボーンのHead親子付け | 髪ボーンの最上段を選択後、`Head` ボーンを追加選択し、`Ctrl + P` > **Keep Offset**。頭を振ると髪全体が完全追従。 |
| 11 | [11_c1_bone_layer_move_hide.jpg](./11_c1_bone_layer_move_hide.jpg) | 00:12:15 | Ch.1 Mキーによるボーンレイヤー整理 | 増えすぎた髪ボーンを選択し、`M` キーで第2レイヤーへ移動。体ボーンの作業領域をスッキリと視覚整理。 |
| 12 | [12_c2_duplicate_dress_hem_skirt_proxy.jpg](./12_c2_duplicate_dress_hem_skirt_proxy.jpg) | 00:13:15 | Ch.2 ワンピース裾の複製とスカートプロキシ | ワンピース裾のポリゴンを `Shift + D` で複製し `P` > Selection で分離。中心を `G X` で結合し、単純な円筒スカートプロキシを作成。 |
| 13 | [13_c2_skirt_bone_chain_snap_placement.jpg](./13_c2_skirt_bone_chain_snap_placement.jpg) | 00:14:45 | Ch.2 スカートボーンの頂点スナップ配置 | 裾プロキシの各頂点にボーン基点をスナップ配置。横列をA〜E、縦列を001〜002とする規則的な2段ボーン列を敷設。 |
| 14 | [14_c2_skirt_bones_symmetrize.jpg](./14_c2_skirt_bones_symmetrize.jpg) | 00:15:50 | Ch.2 Symmetrizeによるスカートボーン全周化 | 片半身のボーンに `AutoName Left/Right` で `.L` を付与し、右クリック `Symmetrize` で左右対称な全周スカートボーンを完成。 |
| 15 | [15_c2_bone_axes_display_local_z.jpg](./15_c2_bone_axes_display_local_z.jpg) | 00:16:35 | Ch.2 ボーンローカル軸（Axes）の表示確認 | Viewport Display で **Axes** をON。各ボーンのローカルZ軸がバラバラな方向を向いており、スカートの均等な広がり操作が困難な状態を視認。 |
| 16 | [16_c2_recalculate_roll_cursor_center.jpg](./16_c2_recalculate_roll_cursor_center.jpg) | 00:17:20 | Ch.2 3Dカーソル中心のボーンロール再計算 | 【重要技】3Dカーソルを腰の中心に置き、全ボーン選択 `A` から `Armature > Bone Roll > Recalculate Roll > Cursor` を実行。全Z軸を中心向きに一括整列。 |
| 17 | [17_c2_individual_origins_rxx_flare_test.jpg](./17_c2_individual_origins_rxx_flare_test.jpg) | 00:17:40 | Ch.2 Individual Origins RXX広がりテスト | ピボットを `Individual Origins` にし、`R X X` を実行。全ボーンが一斉に外側へ均等に開き、スカートが綺麗にフワッと広がる挙動を確認。 |
| 18 | [18_c3_skirt_proxy_with_empty_groups.jpg](./18_c3_skirt_proxy_with_empty_groups.jpg) | 00:19:15 | Ch.3 With Empty Groups による空グループ生成 | スカートプロキシとアーマチュアで `Ctrl + P` > **With Empty Groups**。自動計算によるウェイト混入を排し、空の頂点グループを用意。 |
| 19 | [19_c3_cage_display_1to1_vertex_assign.jpg](./19_c3_cage_display_1to1_vertex_assign.jpg) | 00:19:50 | Ch.3 ケージ表示ONでの1対1厳密数値アサイン | Armatureモディファイアのケージ（四角・三角）をON。各頂点に対応するボーンの頂点グループへ Weight: 1.0 をアサインし即時変形を確認。 |
| 20 | [20_c3_skirt_proxy_individual_rotation_check.jpg](./20_c3_skirt_proxy_individual_rotation_check.jpg) | 00:20:15 | Ch.3 スカートプロキシのねじれ・広がり点検 | 1頂点1ボーンの割り当てが完了。各ボーンの `R X X`（広がり）や `R Z Z`（ねじれ）にプロキシメッシュが完全同期して変形。 |
| 21 | [21_c4_skirt_data_transfer_body_armature_join.jpg](./21_c4_skirt_data_transfer_body_armature_join.jpg) | 00:21:40 | Ch.4 体アーマチュアへの統合とData Transfer | スカートボーンを別レイヤーへ移動後、体アーマチュアと `Ctrl + J` で統合。ワンピース裾へプロキシから Data Transfer を設定。 |
| 22 | [22_c4_empty_groups_spine_override_trick.jpg](./22_c4_empty_groups_spine_override_trick.jpg) | 00:23:15 | Ch.4 空頂点グループによる素体ウェイト置換 | 【超重要テク】転送用プロキシに `Spine/Chest: 0` の空頂点グループを持たせることで、素体の体幹ウェイトを上書き置換し、裾ボーン100%追従を実現。 |
| 23 | [23_c4_dress_mask_group_upper_lower_split.jpg](./23_c4_dress_mask_group_upper_lower_split.jpg) | 00:24:40 | Ch.4 制限頂点グループによる部位分離 | ワンピースに `WeightTransfer` 頂点グループを作成し裾のみに割り当て。Data Transfer のマスクに指定し、上半身（素体追従）と裾（スカートボーン）を完全分離。 |
| 24 | [24_c4_skirt_sway_and_body_motion_complete.jpg](./24_c4_skirt_sway_and_body_motion_complete.jpg) | 00:26:30 | Ch.4 スカート揺れと体幹ポーズの完全調和 | 体を前屈・回転させても胸元は素体に沿い、裾はスカートボーンで美しく広がる完全なスキニングが完成！ |

---

## 技術要点・スキニングの極意（第21話）

1. **ボーンロールの3Dカーソル中心再計算（Recalculate Roll > Cursor）**:
   - スカートやマントなど放射状に並ぶボーンは、通常それぞれバラバラのローカル軸を持ち、一括で広げることができない。
   - 腰の中心に3Dカーソルを配置し、`Recalculate Roll > Cursor` を実行することで、**全ボーンのローカルZ軸が中心（または外側）へ一括整列**。
   - `Individual Origins`（個々の原点）＋ `R X X` だけで、全周のスカートが一斉にフワッと広がる直感的な操作性を実現。
2. **厚みプロキシによる立体メッシュの内側ウェイト破綻防止**:
   - 厚みや裏表のあるメッシュ（後ろ髪や多層スカート）に対し、1枚の板ポリゴンから転送すると、内側の頂点が離れすぎてウェイトがグチャグチャに乱れる。
   - プロキシメッシュ自体を `E`（押し出し）＋ `Alt + S` で内側へ膨らませて**「立体的な筒状プロキシ」**にすることで、押し出し元からウェイトが均等コピーされ、内側頂点まで完璧に安定したウェイトが転送される。
3. **空頂点グループ（Weight: 0）による素体ウェイトの上書き置換（Override）**:
   - Data Transfer は通常、転送元に存在する頂点グループのみを上書きするため、素体から転送済みの `Spine` や `Hips` のウェイトが裾に残り、スカートボーンの動きが半減してしまう。
   - 転送用プロキシにあらかじめ体アーマチュアを `With Empty Groups` でペアレントし、`Spine` や `Hips` の**「ウェイト値ゼロの空グループ」**を持たせておくことで、素体の体幹ウェイトを完全に消去・置換し、スカートボーン100%の追従を確立。
4. **制限頂点グループ（Vertex Group Mask）による部位分離**:
   - 1つのメッシュ（ワンピースなど）の中で、「上半身は素体に追従させ、下半身はスカートボーンに追従させたい」場合、Data Transfer モディファイアの **Vertex Group（制限グループ）** を使用。
   - 裾部分だけにウェイト1を塗ったマスクグループを指定することで、モディファイアの影響範囲をピンポイントに限定し、上半身の胸部・背中ウェイトを一切破壊せずに裾だけを揺らすことができる。
