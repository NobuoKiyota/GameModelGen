# ふさこ氏 第19話『素体のリギング＆スキニング（リギング編 第1回）』詳細操作手順・スキニング仕様書

本ドキュメントは、3Dモデラー・ふさこ氏のキャラクター制作チュートリアル第19話「素体のリギング＆スキニング 〜初級から中級者向けチュートリアル〜」（34分16秒）の詳細手順書である。
本話からリギング・スキニング編が開幕する。VRM Humanoidアーマチュアのセットアップ、ボーン配置、Symmetrize（左右対称化）、既存指ボーンの統合、自動ウェイト（With Automatic Weights）の適用、剛体パーツ（頭・目・耳）の割り当て、Auto NormalizeとZero Weightsを活用したウェイトペイント、肘・膝・肩・首・手首の変形追従とボリュームロス防止トポロジー修正までを詳細に記録する。

📸 **対応スクリーンショットカタログ**:
- [docs/fusako_19_rigging_skinning_body_screenshots/README.md](../../docs/fusako_19_rigging_skinning_body_screenshots/README.md)

---

## 目次
1. [Chapter 1: 接地調整とVRM Humanoidアーマチュアの骨格セットアップ](#chapter-1-接地調整とvrm-humanoidアーマチュアの骨格セットアップ)
2. [Chapter 2: 手ボーン統合と自動ウェイト（With Automatic Weights）の適用](#chapter-2-手ボーン統合と自動ウェイトwith-automatic-weightsの適用)
3. [Chapter 3: ウェイトペイント環境設定（Auto Normalize・Zero Weights・ケージ表示）](#chapter-3-ウェイトペイント環境設定auto-normalizezero-weightsケージ表示)
4. [Chapter 4: 肩・腕・肘のウェイト調整とボリュームロス防止トポロジー修正](#chapter-4-肩腕肘のウェイト調整とボリュームロス防止トポロジー修正)
5. [Chapter 5: 手首・首の接合部ウェイト同期（数値アサイン・頂点コピー）](#chapter-5-手首首の接合部ウェイト同期数値アサイン頂点コピー)
6. [Chapter 6: 体幹（Spine/Chest）・膝・足首の調整と素体スキニング完了](#chapter-6-体幹spinechest膝足首の調整と素体スキニング完了)
7. [リギング＆スキニング Tips 総括](#リギングスキニング-tips-総括)

---

## Chapter 1: 接地調整とVRM Humanoidアーマチュアの骨格セットアップ

### Step 1-1: 全パーツ表示とワールド原点（地面）への接地調整
- アウトライナーで `Shift` キーを押しながら目のアイコンをクリックし、全オブジェクトを一括表示。
- 同様に選択不可（矢印アイコン）も一括で編集可能状態に切り替え。
- 3Dビューポートで全選択 `A` を実行し、`G Z` で靴の底面がワールド原点グリッド（$Z=0$ の地面）にピッタリ接地するようモデル全体を引き下げ。
- 不要な衣装・アクセサリーを非表示にし、素体（Body）と手（Hand）のみを表示。
[📸 参考: 01_c1_ground_alignment_shift_eye.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/01_c1_ground_alignment_shift_eye.jpg)

### Step 1-2: VRM Humanoidアーマチュアの追加と最前面・ワイヤー表示
- `Shift + A` > Armature > **VRM Humanoid** を追加（VRMアドオン機能）。
- オブジェクトデータプロパティ（緑の走る人アイコン）またはオブジェクトプロパティ > **Viewport Display**:
  - **In Front**: ON（メッシュの奥に埋まらず常に最前面に表示）。
  - **Display As: Wire**（骨をワイヤーフレーム表示にしてメッシュの透過確認を容易化）。
- 全体スケール `S` で肩や腰の高さがモデルに合うように調整。
[📸 参考: 02_c1_vrm_humanoid_add_in_front_wire.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/02_c1_vrm_humanoid_add_in_front_wire.jpg)

### Step 1-3: 編集モードでの関節位置合わせと X-Axis Mirror
- `Tab` で編集モードに入り、ヘッダー右上の **X-Axis Mirror**（X軸ミラー）をONにする。
- 正面図（テンキー `1`）および側面図（テンキー `3`）から各関節の位置をメッシュの中心軸へ移動:
  - 首（Neck）の根元、頭（Head）のピボット位置。
  - 肩（Shoulder）、上腕（UpperArm）、前腕（LowerArm）。
  - 骨盤（Hips/Spine）、太もも（UpperLeg）、膝（LowerLeg）、足首（Foot）、つま先（Toe）。
[📸 参考: 03_c1_edit_mode_joint_placement.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/03_c1_edit_mode_joint_placement.jpg)

### Step 1-4: 既存手ボーン活用のためのVRM手首先ボーン削除
- 以前の手モデリング工程（第5話・第6話）であらかじめ精密に仕込んでおいた指ボーンを活用するため、VRM Humanoidの手首から先（Handおよび全指ボーン）を選択。
- `X` キー > **Delete Bones** で削除。
[📸 参考: 04_c1_finger_bones_delete_hand_joint.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/04_c1_finger_bones_delete_hand_joint.jpg)

### Step 1-5: ボーン名のPascalCase整理と表示
- ビューポート表示設定で **Names** にチェックを入れ、画面上にボーン名を表示。
- ボーンを選択して `F2` を押し、先頭大文字（PascalCase）かつ左右対称接尾辞（`.L` / `.R`）の命名規則へ統一（例: `UpperArm.L`, `LowerArm.L`, `UpperLeg.L`）。
[📸 参考: 05_c1_bone_names_pascal_case_rename.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/05_c1_bone_names_pascal_case_rename.jpg)

### Step 1-6: 右半身削除と Symmetrize（対称化）による自動生成
- 一旦 **X-Axis Mirror** をOFFにする。
- 画面向かって左側（モデルの右半身 `.R` 側のボーン）を矩形選択して `X` で削除。
- 全ボーン選択 `A` から、アーマチュアメニュー（または右クリック）> **Symmetrize** を実行。
- 左半身（`.L`）の完全対称なボーンが `.R` 接尾辞で一発自動生成される。完了後、再度X軸ミラーをONに戻す。
[📸 参考: 06_c1_symmetrize_right_side_bones.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/06_c1_symmetrize_right_side_bones.jpg)

### Step 1-7: 手ボーンのオブジェクト統合と Keep Offset 親子付け
- オブジェクトモードで、手ボーンアーマチュアを選択後、VRM体アーマチュアを `Shift` 選択。
- `Ctrl + J` で1つのアーマチュアオブジェクトに統合。
- 編集モードで `Hand.L` ボーンを選択し、`Shift` を押しながら `LowerArm.L` を追加選択。
- `Ctrl + P` > **Keep Offset**（オフセットを保持して親子付け）を実行。
- ボーンプロパティ > **Relations > Parent** で `Hand.L` の親が `LowerArm.L`、`Hand.R` の親が `LowerArm.R` に設定されていることを確認。
[📸 参考: 07_c1_ctrl_j_join_hand_keep_offset.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/07_c1_ctrl_j_join_hand_keep_offset.jpg)

---

## Chapter 2: 手ボーン統合と自動ウェイト（With Automatic Weights）の適用

### Step 2-1: 手メッシュの一時分離（P）による既存ウェイト保全
- 手のメッシュはすでに綺麗なウェイトペイントが完了しているため、自動ウェイトによって上書き破壊されるのを防ぐ。
- 体メッシュの編集モードに入り、手首から先をリンク選択 `L`。
- `P` > **Selection** で別オブジェクトとして一時分離。
[📸 参考: 08_c2_separate_hand_p_mesh.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/08_c2_separate_hand_p_mesh.jpg)

### Step 2-2: Rootボーンの Deform（変形）チェックOFF
- アーマチュアの編集モードまたはポーズモードで、最下層の **`Root`** ボーンを選択。
- ボーンプロパティ > **Deform** のチェックボックスを外す（OFF）。
- 自動ウェイト時にモデル全体へRootボーンの影響が焼き付くのを防止。
[📸 参考: 09_c2_root_bone_deform_off.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/09_c2_root_bone_deform_off.jpg)

### Step 2-3: 体メッシュへの自動ウェイト（With Automatic Weights）適用
- 体メッシュを選択後、アーマチュアを `Shift` 選択。
- `Ctrl + P` > **With Automatic Weights**（自動ウェイトで）を実行。
- 体メッシュに **Armature モディファイア** が自動追加され、ボーン名と同名の頂点グループが生成されて自動スキニングされる。
- 一時分離しておいた手オブジェクトにも手動で **Armature モディファイア** を追加し、同一アーマチュアを指定。
[📸 参考: 10_c2_ctrl_p_automatic_weights.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/10_c2_ctrl_p_automatic_weights.jpg)

### Step 2-4: 剛体パーツ（頭・目）の直接数値アサイン
- 頭部メッシュ（Head）:
  - 編集モードで全選択 `A`。
  - オブジェクトデータプロパティで頂点グループ **`Head`** を新規作成（または選択）。
  - **Weight: 1.000** に設定し、**Assign** をクリック。Armatureモディファイアを追加。
- 目メッシュ（Eyes）:
  - 頂点グループ **`Eye.L`** に全頂点を Weight: 1.0 でアサイン。
  - ミラー反転用として空の頂点グループ **`Eye.R`** を作成（アサインは不要）。Armatureモディファイアを追加。
[📸 参考: 11_c2_head_eye_rigid_weight_assign.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/11_c2_head_eye_rigid_weight_assign.jpg)

### Step 2-5: 耳パーツの結合と Head への一括アサイン
- 耳の外側メッシュと内側の毛メッシュを選択し、`Ctrl + J` でオブジェクト結合。
- モデリング時の厚み付け用頂点グループ（SolidifyScale等）を削除。
- 全選択して頂点グループ **`Head`** に Weight: 1.0 でアサインし、Armatureモディファイアを追加。
- ポーズリセット: 全ボーン選択 `A` から `Alt + R`（回転クリア）、`Alt + G`（移動クリア）。
[📸 参考: 12_c2_ear_ctrl_j_head_weight_assign.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/12_c2_ear_ctrl_j_head_weight_assign.jpg)

---

## Chapter 3: ウェイトペイント環境設定（Auto Normalize・Zero Weights・ケージ表示）

### Step 3-1: Weight Paintモード突入と Auto Normalize の有効化
- アーマチュアを選択後、体メッシュを `Shift` 選択。
- `Ctrl + Tab` で **Weight Paint**（ウェイトペイント）モードに入る。
- `Shift + Click` でボーンを直接選択してポーズを動かせる状態にする。
- ツールプロパティ（画面右側またはNパネル）> **Options**:
  - **Auto Normalize**: **ON**（最重要：頂点に影響する全ボーンのウェイト合計を常に自動で1.0に保つ）。
[📸 参考: 13_c3_weight_paint_auto_normalize_on.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/13_c3_weight_paint_auto_normalize_on.jpg)

### Step 3-2: Zero Weights: Active による未影響頂点の完全可視化
- 3Dビューポートヘッダーの **Viewport Overlays**（重なりアイコン）を開く。
- **Zero Weights**: **Active** に設定。
- ウェイト値が `0.0` の領域が真っ黒（Black）で描画され、余計なボーンの影響が混入していないかが一目で判別可能になる。
[📸 参考: 14_c3_zero_weights_active_overlay.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/14_c3_zero_weights_active_overlay.jpg)

### Step 3-3: ケージ表示（編集モード連動）と Weights Smooth 補間
- 体メッシュの Armature モディファイアで、**「四角（ケージで頂点を調整）」と「三角（編集モードでモディファイアを表示）」** アイコンを両方ONにする。
- ポーズを曲げた状態のまま `Tab` で編集モードに入り、ガクガクに折れ曲がっている頂点を選択。
- `Ctrl + Tab` でウェイトペイントに戻り、`V` キーで **Vertex Selection Mask**（頂点マスク）をON。
- ヘッダーの **Weights > Smooth** を実行。左下のオペレーターパネルで **Factor** や **Iterations** を上げて、選択頂点のみを滑らかに補間。
[📸 参考: 15_c3_cage_display_weight_smooth.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/15_c3_cage_display_weight_smooth.jpg)

---

## Chapter 4: 肩・腕・肘のウェイト調整とボリュームロス防止トポロジー修正

### Step 4-1: 肩上げポーズ時の脇腹・胸部ウェイト消去（Subtract）
- `Shoulder.L` ボーンを選択し、`R` キーで上方向に回転させて腕を上げる。
- 自動ウェイトにより脇腹や胸部まで過剰に追従してメッシュが引き攣れているのを観察。
- ブラシの Blend を **Subtract**（引き算）に設定し、脇腹の余計なウェイトを塗り潰して消去（Auto NormalizeによりSpine/Chest側へ自動再配分される）。
- 境界の段差は **Blur** ブラシ（または Weights > Smooth）で馴染ませる。
[📸 参考: 16_c4_shoulder_subtract_brush_cleanup.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/16_c4_shoulder_subtract_brush_cleanup.jpg)

### Step 4-2: 肘曲げ状態での Subdivide 割り増しと角出し
- 前腕ボーン（`LowerArm.L`）を90度内側に曲げる。
- 割りが不足して肘の曲がりが丸く潰れるのを確認。
- ケージ編集モードに入り、肘の外側エッジを選択して右クリック > **Subdivide**（または `Ctrl + R` でループ追加）。
- 肘の突起頂点に **Add** ブラシで `UpperArm.L` のウェイトを少し足し、カチッとした関節の角を強調。
[📸 参考: 17_c4_elbow_bend_subdivide_loop.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/17_c4_elbow_bend_subdivide_loop.jpg)

### Step 4-3: 肘内側の痩せ防止（Dissolve Edges と J 繋ぎ）
- 腕を内側に深く曲げた際、関節の内側が極端にえぐれてペラペラに痩せてしまう（Candy-wrapper effect / ボリュームロス）。
- 編集モードで、内側に食い込んでいる不要な横エッジを選択し、`X` > **Dissolve Edges** で溶解。
- 対向頂点を `J` キー（Join Vertices）で斜めに繋ぎ直し、曲げ方向に対して潰れない張りのある四角面・三角面トポロジーへ再編。
[📸 参考: 18_c4_elbow_inner_dissolve_loss_prevention.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/18_c4_elbow_inner_dissolve_loss_prevention.jpg)

---

## Chapter 5: 手首・首の接合部ウェイト同期（数値アサイン・頂点コピー）

### Step 5-1: 手首接合部ループの数値入力アサイン（0.5 / 0.5）
- 手首の断面ループを選択。
- アイテムパネル（Nパネル）の **Vertex Weights**（頂点ウェイト）を確認。
- 親指などの誤混入ウェイトを `Remove` で全消去。
- `Hand.L` を **0.500**、`LowerArm.L` を **0.500** に数値入力で完全一致アサイン。
[📸 参考: 19_c5_wrist_numeric_weight_hand_lowerarm.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/19_c5_wrist_numeric_weight_hand_lowerarm.jpg)

### Step 5-2: 腕側への近接ループ追加と滑らかなグラデーション
- 手首の急激なねじれ・変形を緩和するため、腕側に `Ctrl + R` でエッジループを1本追加し、手首の境界面近くへスライド。
- 追加したループのウェイトを `Hand.L: 0.250` / `LowerArm.L: 0.750` に設定し、手首から前腕への自然なグラデーションを構築。
[📸 参考: 20_c5_wrist_loopcut_smooth_transition.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/20_c5_wrist_loopcut_smooth_transition.jpg)

### Step 5-3: 首と頭の境界ウェイト一致による裂け目防止
- 首の上端ループ（体メッシュ側）と頭部の下端ループ（頭メッシュ側）を選択。
- 首側: `Neck: 0.500`、`Head: 0.500` に設定。
- 頭側: 新規頂点グループ `Neck` を作成し、接合ループを `Neck: 0.500`、`Head: 0.500` に設定。
- 頭を上下左右に激しく回転させても、首と頭の境界線が寸分違わず同期して動き、隙間や黒ずみシェーディングが一切生じない構造を確立。
[📸 参考: 21_c5_neck_head_05_boundary_matching.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/21_c5_neck_head_05_boundary_matching.jpg)

---

## Chapter 6: 体幹（Spine/Chest）・膝・足首の調整と素体スキニング完了

### Step 6-1: 体幹（Spine/Chest）のウェイト整理と横列コピー（Copy）
- `Chest` ボーンを選択し、下腹部やお尻まで及んでいる過剰ウェイトを Subtract で消去。
- `Spine` ボーンのウェイトを段ごとに整理。
- 最も理想的なグラデーションを持つ頂点を1点選び、横列の頂点ループを選択してアイテムパネルの **Copy** ボタンを実行。全周に均一なウェイトを一括転送。
[📸 参考: 22_c6_chest_spine_row_copy_weights.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/22_c6_chest_spine_row_copy_weights.jpg)

### Step 6-2: 膝曲げ状態での Smoothness Subdivide と三角化
- 太もも・膝を曲げた状態で膝関節を点検。
- 前面の割りが不足している部分に、右クリック > **Subdivide**（オペレーターで **Smoothness** を少し上げる）を実行し、ふっくらとした膝頭を成形。
- 膝裏の潰れ方向と逆向きにエッジを `Ctrl + T` で三角化し、関節の厚みを保持。
[📸 参考: 23_c6_knee_bend_smoothness_quad_flow.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/23_c6_knee_bend_smoothness_quad_flow.jpg)

### Step 6-3: 全身ポーズ可動域チェックと素体スキニング完了
- 足首（Foot）やつま先（Toe）の後ろ側に漏れた不要ウェイトを削除。
- ポーズモードで全身のボーン（腕立て、正座、ジャンプ、首振り等）を動かし、メッシュの交差・過剰な引き攣れ・ボリュームロスがないことを全方位から確認。
- 全選択 `A` $\to$ `Alt + R`, `Alt + G` でTポーズにリセット。
- **素体のリギング＆スキニング工程がここに完全完了！**
[📸 参考: 24_c6_full_body_pose_check_complete.jpg](../../docs/fusako_19_rigging_skinning_body_screenshots/24_c6_full_body_pose_check_complete.jpg)

---

## リギング＆スキニング Tips 総括

| 項目 | テクニック / ショートカット | 効能・VRM/ゲーム開発上のメリット |
|:---|:---|:---|
| **事前接地** | 全選択 $\to$ `G Z` | モデルの原点位置を正確な床面（$Z=0$）に揃え、Unity等での足浮き・沈み込みを未然防止。 |
| **手メッシュ分離保護** | 編集モード $\to$ `P` > Selection | 体の自動ウェイト適用時に、苦労して塗った指ウェイトが破壊されるのを完全に回避。 |
| **Root Deform OFF** | `Root` ボーン $\to$ Deform: OFF | 最上位ルートボーンに頂点が追従して全体が予期せず変形するエラーを防止。 |
| **Auto Normalize** | Weight Paint Tool > Auto Normalize: ON | 頂点ウェイトの合計値を常に1.0に自動正規化。VRM出力時の破綻を撲滅。 |
| **Zero Weights 可視化** | Viewport Overlays > Zero Weights: Active | ウェイト0の領域を真っ黒表示し、微小なウェイト混入（ゴミウェイト）を一目で発見。 |
| **ポーズ追従トポロジー編集** | Armatureモディファイアの四角・三角アイコンON | ポーズを曲げた状態で編集モードに入り、関節の潰れ・痩せをリアルタイムに解消。 |
| **境界数値アサイン** | アイテムパネル > 各ボーン `0.5 / 0.5` | 首と頭、手首と前腕など、別パーツ境界のウェイトを数値で完全一致させ、裂け目を防止。 |
| **頂点ウェイトコピー** | 基準頂点を最後に選択 $\to$ `Copy` | 胴体やスカートの円筒ループ全周へ均等なウェイトを一瞬で転送。 |
