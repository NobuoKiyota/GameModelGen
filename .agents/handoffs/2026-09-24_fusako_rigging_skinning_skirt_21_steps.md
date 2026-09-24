# 【ふさこ氏 3Dキャラ制作 第21回】スカートなどのスキニング・ウェイト転送 完全技術仕様書

本ドキュメントは、YouTubeチュートリアル動画 **『【Blender】スカートなどのスキニング・ウェイト転送！【キャラクターモデル制作！#21】』**（講師: ふさこ氏、時間: 27分06秒、URL: `https://www.youtube.com/watch?v=et1L4Bsa8Rg`）の内容を、Blender 3.6+ / 4.x に対応した詳細なステップバイステップ技術仕様として完全体系化したものである。

---

## 0. 本技術仕様の全体俯瞰と核心ポイント

### 0.1 本動画で解決する課題
1. **多重房・カール構造の後ろ髪スキニング**:
   - 複雑な立体感を持つ後ろ髪をそのままボーンにペアレント（自動ウェイト）すると、房の内側や重なり部分でウェイトが破綻し、ギザギザに変形する。
   - **解決策**: 8角形のシンプルな「円柱プロキシメッシュ（筒）」を配置し、筒の内側に厚みをつけた上でウェイトを転送する。
2. **スカート・ワンピース裾のスキニング**:
   - 円周上に広がるプリーツスカートや裾は、単純な親子付けや素体からの転送だけでは足の貫通やねじれ、不自然な潰れが生じる。
   - **解決策**:
     - **ボーンロールの3Dカーソル中心再計算 (`Recalculate Roll > Cursor`)**: 全スカートボーンのローカルZ軸を腰の中心（3Dカーソル）へ放射状に向けることで、`Individual Origins`（それぞれの原点）＋ `R X X` で全周が一斉にふわりと広がり、`R Z Z` で綺麗にねじれる操作性を確立。
     - **空のグループ (`With Empty Groups`) による体幹ウェイト上書き消去**: スカートプロキシにウェイトを自動割り当てする際、不要な `Spine` や `Chest` などを Weight 0 で保持させて転送し、素体から転送された上半身のウェイトを完全置換・除外する。
     - **制限頂点グループによる部位分離**: ワンピースの「裾（スカート部）」だけにアサインしたマスク頂点グループを用意し、Data Transfer でそのグループのみを対象とすることで、上半身（素体追従）と裾（スカートボーン追従）を完全分離。

---

## 1. チャプター別・詳細ステップバイステップ手順

### Chapter 1: 後ろ髪のプロキシスキニング（厚み付き円柱転送法） (00:00〜12:30)

#### Step 1-1: ガイド用 8角形円柱プロキシの配置
1. `Shift + A` > **Mesh > Cylinder** を追加。
   - 頂点数 (`Vertices`): **8**
   - 半径・高さを後ろ髪全体のボリュームを包み込むサイズに調整。
2. 編集モードで後ろ髪の房の流れ（上から下へ少し広がる形）に合わせてループカット (`Ctrl + R`) を3〜4本入れ、頂点を配置。
   [📸 参考: 01_c1_cylinder_8verts_hair_proxy.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/01_c1_cylinder_8verts_hair_proxy.jpg)

#### Step 1-2: 髪用ボーンチェーンの作成とスナップ配置
1. アーマチュアを選択し、編集モードで `Shift + A` で単一ボーンを追加。
2. `E` で下向きに押し出し、3〜4節のボーンチェーンを作成。
3. `Snap`（頂点スナップ）を有効化し、円柱プロキシの中心軸または表面頂点に合わせてボーンの各ジョイントを吸着配置。
   [📸 参考: 02_c1_snap_bone_chain_to_cylinder.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/02_c1_snap_bone_chain_to_cylinder.jpg)

#### Step 1-3: ボーンの自動左右命名と対称化
1. 左右対称の髪房（ツインテールやサイドバック）の場合、ボーン名末尾に `.L` を付加（例: `Hair_Back.L.001`）。
2. **Armature > Names > AutoName Left/Right** で確認後、**Armature > Symmetrize** を実行して `.R` 側のボーンを一括自動生成。
   [📸 参考: 03_c1_autoname_symmetrize_hair_bones.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/03_c1_autoname_symmetrize_hair_bones.jpg)

#### Step 1-4: 円柱プロキシへの自動ウェイト割り当て
1. オブジェクトモードで円柱プロキシを選択し、次にアーマチュアを `Shift` 選択。
2. `Ctrl + P` > **With Automatic Weights** を実行。
3. ポーズモードでボーンを回転させ、円柱プロキシが滑らかに追従することを確認。
   [📸 参考: 04_c1_cylinder_automatic_weights.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/04_c1_cylinder_automatic_weights.jpg)

#### Step 1-5: 根元頂点の頭部ボーン（Head）固定
1. 円柱プロキシの編集モードに入る。
2. 最上段の円周頂点を選択し、頂点グループ `Head` を選択。
3. Weight: `1.0` で **Assign** を押下。これにより頭部との接続部が絶対に千切れたり離れたりしなくなる。
   [📸 参考: 05_c1_cylinder_top_vertices_head_assign.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/05_c1_cylinder_top_vertices_head_assign.jpg)

#### Step 1-6: 後ろ髪メッシュへの Data Transfer モディファイア適用
1. 後ろ髪オブジェクトを選択し、**Data Transfer** モディファイアを追加。
   - **Source**: 円柱プロキシメッシュ
   - **Vertex Data**: チェックON > **Vertex Groups** を選択
   - **Mapping**: **Nearest Face Interpolated**（面補間最近接）または **Nearest Vertex**
2. モディファイアの **Generate Data Layers** を押下。
3. 後ろ髪オブジェクトに **Armature** モディファイアを追加し、アーマチュアを指定。
   [📸 参考: 06_c1_hair_data_transfer_from_cylinder.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/06_c1_hair_data_transfer_from_cylinder.jpg)

#### Step 1-7: 頭皮接続部以外の不要ウェイト整理
1. 房の先端や内部で意図しない素体ボーン（`Spine` や `Neck` 等）のウェイトが混入していないか確認。
2. 必要に応じてマスク用の頂点グループを作成し、転送範囲を制限。
   [📸 参考: 07_c1_hair_mask_vertex_group_remove.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/07_c1_hair_mask_vertex_group_remove.jpg)

#### Step 1-8: 【極意】円柱の内側押し出し（厚みプロキシ化）による内側ウェイト破綻防止
1. **重要課題**: 単純な1枚板の円柱から転送すると、後ろ髪の「内側（裏側）」の頂点が円柱の外側ウェイトと近接判定で混線し、反転や潰れが発生する。
2. **解決手順**:
   - 円柱プロキシの編集モードで全選択 (`A`)。
   - `E`（押し出し）直後に `Enter`。
   - `Alt + S`（法線沿いに縮小/収縮）で内側へ押し込んで厚みを持たせる。
   - これにより、円柱の内壁と外壁の間に後ろ髪のメッシュがすっぽり挟まれ、内側頂点まで完璧なウェイトが補間される。
   [📸 参考: 08_c1_extrude_cylinder_thickness_inner_fix.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/08_c1_extrude_cylinder_thickness_inner_fix.jpg)

#### Step 1-9: ワイヤーフレーム表示による内部スキニング追従検証
1. オブジェクトプロパティ > **Viewport Display** > **Display As: Wire** に変更。
2. ポーズモードで髪ボーンを動かし、内側の髪房まで綺麗に連動して曲がることを確認。
   [📸 参考: 09_c1_display_as_wire_inner_skinning_check.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/09_c1_display_as_wire_inner_skinning_check.jpg)

#### Step 1-10: 髪ボーンの頭部ボーン（Head）への親子付け
1. アーマチュアの編集モードに入る。
2. 髪ボーンの根元（`Hair_Root.L`, `Hair_Root.R` など）を選択し、最後に `Head` ボーンを `Shift` 選択。
3. `Ctrl + P` > **Keep Offset** を実行。
   [📸 参考: 10_c1_hair_bones_parent_head_keep_offset.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/10_c1_hair_bones_parent_head_keep_offset.jpg)

#### Step 1-11: ボーンレイヤーの整理と非表示
1. 設定が完了した髪ボーンを選択し、`M` キーを押してサブのボーンレイヤー（またはボーンコレクション）へ移動し、作業ビューをすっきりさせる。
   [📸 参考: 11_c1_bone_layer_move_hide.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/11_c1_bone_layer_move_hide.jpg)

---

### Chapter 2: スカートボーンの配置とロール最適化 (12:30〜18:00)

#### Step 2-1: ワンピース裾からのスカートプロキシ複製
1. ワンピース（またはスカート）の編集モードに入る。
2. 裾から腰回りにかけての主要なメッシュ面を選択し、`Shift + D` で複製。
3. `P` > **Selection** で別オブジェクトとして分離し、名称を `Proxy_Skirt` とする。
   [📸 参考: 12_c2_duplicate_dress_hem_skirt_proxy.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/12_c2_duplicate_dress_hem_skirt_proxy.jpg)

#### Step 2-2: スカート用ボーンチェーンの作成とスナップ配置
1. アーマチュアの編集モードで、腰の高さ（Hips付近）に新規ボーンを作成。
2. 裾に向かって2〜3節で押し出し (`E`)。
3. プロキシメッシュの円周（前・斜め前・横・斜め後ろ・後ろ）に沿って配置。
   [📸 参考: 13_c2_skirt_bone_chain_snap_placement.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/13_c2_skirt_bone_chain_snap_placement.jpg)

#### Step 2-3: スカートボーンの左右対称化 (Symmetrize)
1. 片側（左側 `.L`）のボーンチェーン群（前左、横左、後左など）を命名。
2. **Armature > Symmetrize** で右側（`.R`）へ正確に対称化。
   [📸 参考: 14_c2_skirt_bones_symmetrize.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/14_c2_skirt_bones_symmetrize.jpg)

#### Step 2-4: ボーンローカル軸（Local Axes）の表示確認
1. アーマチュアプロパティ > **Viewport Display** > **Axes** にチェックを入れ、各ボーンのローカル座標軸（X, Y, Z）を表示。
2. この時点では、各ボーンのロール（傾き）が不揃いで、ローカル軸の向きがバラバラであることを確認。
   [📸 参考: 15_c2_bone_axes_display_local_z.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/15_c2_bone_axes_display_local_z.jpg)

#### Step 2-5: 【核心技術】3Dカーソル中心のボーンロール再計算 (Recalculate Roll > Cursor)
1. 3Dカーソルを腰の中心（`Hips` ボーンのヘッド位置など）に配置（`Shift + S` > **Cursor to Selected**）。
2. スカート用ボーンを全選択。
3. **Armature > Bone Roll > Recalculate Roll > Cursor** を実行。
4. **効果**: 全スカートボーンのローカルZ軸（またはX軸）が一斉に「3Dカーソル（腰中心）」へ向かって放射状に整列する。
   [📸 参考: 16_c2_recalculate_roll_cursor_center.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/16_c2_recalculate_roll_cursor_center.jpg)

#### Step 2-6: それぞれの原点＋ローカル回転によるスカート広がりテスト
1. トランスフォームピボットポイントを **Individual Origins**（それぞれの原点）に設定。
2. ポーズモードでスカートボーンを全選択し、`R` > `X` > `X`（ローカルX軸回転）を実行。
3. **結果**: 全周のスカートが一斉にフワッと外側に均等に広がる。
4. `R` > `Z` > `Z`（ローカルZ軸回転）で全周が綺麗に同方向へねじれる。この極めて自然な挙動がボーンロール整列の最大の利点である。
   [📸 参考: 17_c2_individual_origins_rxx_flare_test.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/17_c2_individual_origins_rxx_flare_test.jpg)

---

### Chapter 3: スカートプロキシのウェイト付けとケージ調整 (18:00〜21:00)

#### Step 3-1: スカートプロキシへの親子付け（With Empty Groups）
1. `Proxy_Skirt` を選択し、アーマチュアを `Shift` 選択。
2. `Ctrl + P` > **With Empty Groups**（空のグループで）を実行。
   [📸 参考: 18_c3_skirt_proxy_with_empty_groups.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/18_c3_skirt_proxy_with_empty_groups.jpg)

#### Step 3-2: 編集モードでの頂点1:1割り当て（ケージ割り当て）
1. プロキシメッシュの編集モードに入る。
2. 各ボーンに対応する円周の頂点ループを選択。
3. 対応する頂点グループ（例: `Skirt_Front_01.L` など）を選択し、Weight: `1.0` で **Assign**。
4. 関節の境界部分はグラデーションになるよう、上段と下段で適切にウェイト配分（または **Smooth Vertex Weights**）。
   [📸 参考: 19_c3_cage_display_1to1_vertex_assign.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/19_c3_cage_display_1to1_vertex_assign.jpg)

#### Step 3-3: 個別ボーン回転によるプロキシ変形確認
1. ポーズモードで各スカートボーンを個別に曲げ、プロキシがギザギザにならず美しい筒状を保ちながら追従することを確認。
   [📸 参考: 20_c3_skirt_proxy_individual_rotation_check.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/20_c3_skirt_proxy_individual_rotation_check.jpg)

---

### Chapter 4: 本番メッシュへのウェイト転送と結合 (21:00〜27:06)

#### Step 4-1: スカートプロキシからワンピース裾への Data Transfer
1. ワンピースオブジェクトを選択。
2. **Data Transfer** モディファイアを追加。
   - **Source**: `Proxy_Skirt`
   - **Vertex Data**: チェックON > **Vertex Groups**
   - **Mapping**: **Nearest Face Interpolated**（面補間最近接）
3. **Generate Data Layers** を押下。
   [📸 参考: 21_c4_skirt_data_transfer_body_armature_join.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/21_c4_skirt_data_transfer_body_armature_join.jpg)

#### Step 4-2: 【重要テクニック】空グループ（Weight 0）による素体ウェイト上書き置換
1. **問題の発生**:
   - ワンピースは第20回で「素体（Body）」からウェイト転送しているため、裾部分に `Spine`（背骨）や `Pelvis`（骨盤）、`Thigh`（太もも）の強いウェイトが既に入っている。
   - そのままスカートボーンのウェイトを転送すると、ウェイトが加算・合算され、腰ボーンを動かした時に裾が引っ張られて伸びてしまう。
2. **解決策**:
   - `Proxy_Skirt` 側に、あらかじめ `Spine` や `Pelvis` という名前の空の頂点グループ（Weight: 0.0）を作成しておく。
   - Data Transfer の転送設定で **Replace**（置換）を行うことで、裾部分の素体ウェイトが Weight 0 で上書き消去され、スカートボーンのウェイトが100%綺麗に適用される。
   [📸 参考: 22_c4_empty_groups_spine_override_trick.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/22_c4_empty_groups_spine_override_trick.jpg)

#### Step 4-3: ワンピース裾マスク頂点グループによる上下分離
1. ワンピースの編集モードで、「スカートとして揺らしたい下半身部分」のみを選択。
2. 新規頂点グループ `Mask_Skirt` を作成し、Weight: `1.0` で **Assign**。
3. Data Transfer モディファイアの **Vertex Group**（制限頂点グループ）に `Mask_Skirt` を指定。
4. **効果**:
   - 上半身（胸、背中、袖など）は第20回の素体ウェイト転送が100%維持される。
   - 下半身（裾）だけが `Proxy_Skirt` のスカートボーンウェイトに100%置き換わる。
   [📸 参考: 23_c4_dress_mask_group_upper_lower_split.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/23_c4_dress_mask_group_upper_lower_split.jpg)

#### Step 4-4: 揺れと体幹連動モーションの総合動作テスト
1. ポーズモードで体を前屈、しゃがみ、左右ステップさせ、足がスカートを突き破らないか確認。
2. スカートボーンを回転させて裾をなびかせ、しわや潰れのない美しい変形が得られることを確認して完成。
   [📸 参考: 24_c4_skirt_sway_and_body_motion_complete.jpg](../../docs/fusako_21_rigging_skinning_skirt_screenshots/24_c4_skirt_sway_and_body_motion_complete.jpg)

---

## 2. 実装チェックリスト（トラブルシューティング）

| 現象 | 主な原因 | 確実な解決策 |
| :--- | :--- | :--- |
| スカートが横に広がらず斜めにつぶれる | ボーンロール（Local Z軸）がバラバラ | 3Dカーソルを腰中心に置き、`Recalculate Roll > Cursor` を実行する。 |
| 体を動かした時にスカートの裾が引き伸ばされる | 素体の `Spine` や `Thigh` ウェイトが裾に残っている | プロキシ側に Weight 0 の空グループを作って置換転送するか、頂点ウェイトパネルで不要グループを削除する。 |
| 上半身の服までスカートボーンで崩れる | Data Transfer の転送範囲が全体にかかっている | 裾だけの頂点グループ `Mask_Skirt` を作り、モディファイアの制限グループに指定する。 |
| 後ろ髪の内側の毛先がギザギザに破綻する | プロキシ円柱が薄い板状で内側をカバーできていない | 円柱を `E` ＋ `Alt + S` で内側に押し出して厚みを持たせる。 |
