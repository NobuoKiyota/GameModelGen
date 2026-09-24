# ふさこ氏 第19話『素体のリギング＆スキニング（リギング編 第1回）』スクリーンショットカタログ

本ドキュメントは、ふさこ氏のBlender 3Dキャラクター制作チュートリアル第19話「素体のリギング＆スキニング 〜初級から中級者向けチュートリアル〜」（34分16秒）の重要操作シーンを高解像度キャプチャした全24枚の画像カタログです。
VRM Humanoidアーマチュアの追加、ボーン配置、Symmetrize対称化、指ボーン統合、自動ウェイト（With Automatic Weights）の適用、Auto Normalize設定、肘・膝・肩・首・手首のウェイト調整とボリュームロス防止トポロジー修正までを網羅しています。

📖 **対応する詳細リギング・スキニング仕様書・操作手順書**:
- [2026-09-24_fusako_rigging_skinning_body_19_steps.md](../../.agents/handoffs/2026-09-24_fusako_rigging_skinning_body_19_steps.md)

---

## スクリーンショット一覧（全24枚）

| No | スクリーンショット（クリックで原寸表示） | タイムスタンプ | チャプター | モデリング・リギング・ウェイト操作・キー操作 |
|:---|:---|:---|:---|:---|
| 01 | [01_c1_ground_alignment_shift_eye.jpg](./01_c1_ground_alignment_shift_eye.jpg) | 00:00:35 | Ch.1 接地調整 | `Shift` ＋ 目のアイコンで全パーツを一括表示。全選択 `A` から `G Z` で靴底がワールド原点グリッド（地面）に接地するようモデル全体を引き下げ。 |
| 02 | [02_c1_vrm_humanoid_add_in_front_wire.jpg](./02_c1_vrm_humanoid_add_in_front_wire.jpg) | 00:01:55 | Ch.1 VRMアーマチュア追加 | `Shift + A` > Armature > **VRM Humanoid** を追加。オブジェクトプロパティで **In Front**（最前面表示）をON、**Display As: Wire** に設定。 |
| 03 | [03_c1_edit_mode_joint_placement.jpg](./03_c1_edit_mode_joint_placement.jpg) | 00:02:40 | Ch.1 関節位置合わせ | 編集モードで **X-Axis Mirror** をON。首、頭、肩、肘、手首、背骨、膝、足首の各関節ヘッド・テールをメッシュの中心軸へ配置。 |
| 04 | [04_c1_finger_bones_delete_hand_joint.jpg](./04_c1_finger_bones_delete_hand_joint.jpg) | 00:03:30 | Ch.1 既存指ボーン活用のための削除 | 以前作成した手・指ボーンを活かすため、VRM Humanoidの手首から先の指ボーンを選択して `X` キーで削除。 |
| 05 | [05_c1_bone_names_pascal_case_rename.jpg](./05_c1_bone_names_pascal_case_rename.jpg) | 00:05:00 | Ch.1 ボーン名の規則整理 | ビューポート表示で **Names** をON。`F2` で先頭大文字（PascalCase）かつ `.L` 接尾辞形式（例: `UpperArm.L`, `LowerArm.L`）に整理。 |
| 06 | [06_c1_symmetrize_right_side_bones.jpg](./06_c1_symmetrize_right_side_bones.jpg) | 00:05:50 | Ch.1 Symmetrizeによる対称化 | 右半身ボーンを削除後、全ボーン選択 `A` から右クリック > **Symmetrize** を実行。`.R` 側の左右対称ボーンを一発生成。 |
| 07 | [07_c1_ctrl_j_join_hand_keep_offset.jpg](./07_c1_ctrl_j_join_hand_keep_offset.jpg) | 00:06:30 | Ch.1 手ボーン統合と親子付け | 体アーマチュアと手ボーンを `Ctrl + J` で統合。`Hand.L` を選択後 `LowerArm.L` を追加選択し、`Ctrl + P` > **Keep Offset** で親子付け。 |
| 08 | [08_c2_separate_hand_p_mesh.jpg](./08_c2_separate_hand_p_mesh.jpg) | 00:07:20 | Ch.2 手メッシュの一時分離 | 自動ウェイトによる既存手ウェイトの上書き破壊を防ぐため、編集モードで手メッシュを選択して `P` > **Selection** で別オブジェクトに分離。 |
| 09 | [09_c2_root_bone_deform_off.jpg](./09_c2_root_bone_deform_off.jpg) | 00:07:35 | Ch.2 RootボーンのDeform OFF | アーマチュアの `Root` ボーンを選択し、ボーンプロパティで **Deform（変形）** のチェックをOFF（全体が不意に追従するのを防止）。 |
| 10 | [10_c2_ctrl_p_automatic_weights.jpg](./10_c2_ctrl_p_automatic_weights.jpg) | 00:07:50 | Ch.2 自動ウェイトの適用 | 体メッシュを選択後アーマチュアを `Shift` 選択し、`Ctrl + P` > **With Automatic Weights** を実行。初期スキニングを一括生成。 |
| 11 | [11_c2_head_eye_rigid_weight_assign.jpg](./11_c2_head_eye_rigid_weight_assign.jpg) | 00:09:10 | Ch.2 剛体パーツ（頭・目）の数値アサイン | 頭メッシュを全選択して頂点グループ `Head` に Weight: 1.0 で **Assign**。目メッシュも `Eye.L` に 1.0 アサインし空の `Eye.R` を作成。Armatureモディファイア追加。 |
| 12 | [12_c2_ear_ctrl_j_head_weight_assign.jpg](./12_c2_ear_ctrl_j_head_weight_assign.jpg) | 00:10:15 | Ch.2 耳パーツ結合とウェイト割り当て | 耳外側と内側毛を `Ctrl + J` で結合。不要な厚み頂点グループを削除し、全頂点を頂点グループ `Head` に Weight: 1.0 で割り当て。 |
| 13 | [13_c3_weight_paint_auto_normalize_on.jpg](./13_c3_weight_paint_auto_normalize_on.jpg) | 00:11:35 | Ch.3 Weight PaintとAuto Normalize | 体とアーマチュアを選択し `Ctrl + Tab` で Weight Paintモードへ。ツールオプションで **Auto Normalize: ON**（ウェイト合計を常に1.0維持）を設定。 |
| 14 | [14_c3_zero_weights_active_overlay.jpg](./14_c3_zero_weights_active_overlay.jpg) | 00:12:55 | Ch.3 Zero Weights表示 | ビューポートオーバーレイ > **Zero Weights: Active** をON。ウェイト値0の領域を真っ黒表示にし、影響のない頂点を明確に視覚化。 |
| 15 | [15_c3_cage_display_weight_smooth.jpg](./15_c3_cage_display_weight_smooth.jpg) | 00:13:50 | Ch.3 ケージ表示とSmooth補間 | Armatureモディファイアの四角・三角アイコンをON（ポーズ変形状態で編集・確認）。急激な折れ曲がり頂点を選択し Weights > **Smooth** で滑らか化。 |
| 16 | [16_c4_shoulder_subtract_brush_cleanup.jpg](./16_c4_shoulder_subtract_brush_cleanup.jpg) | 00:15:30 | Ch.4 肩上げポーズと脇腹消去 | 肩ボーンを上げた状態で、過剰に連動して引っ張られている脇腹・胸部メッシュを **Subtract**（引き算ブラシ）で綺麗に消去。 |
| 17 | [17_c4_elbow_bend_subdivide_loop.jpg](./17_c4_elbow_bend_subdivide_loop.jpg) | 00:17:30 | Ch.4 肘曲げとSubdivide割り増し | 肘を90度曲げた状態でトポロジーを観察。割りが不足してカクつく外側に右クリック `Subdivide` や `Ctrl + R` でループを追加し角出し。 |
| 18 | [18_c4_elbow_inner_dissolve_loss_prevention.jpg](./18_c4_elbow_inner_dissolve_loss_prevention.jpg) | 00:20:30 | Ch.4 肘内側の痩せ防止トポロジー | 内側の過度な凹み・痩せ（ボリュームロス）を防止するため、内側エッジを `Dissolve Edges` で溶解し、`J` キーで斜め対角線を繋ぎ直して形状維持。 |
| 19 | [19_c5_wrist_numeric_weight_hand_lowerarm.jpg](./19_c5_wrist_numeric_weight_hand_lowerarm.jpg) | 00:22:40 | Ch.5 手首境界の数値アサイン | 手メッシュと腕メッシュの境界ループを選択し、アイテムパネルで `Hand.L: 0.5`、`LowerArm.L: 0.5` を数値入力で完全一致アサイン。 |
| 20 | [20_c5_wrist_loopcut_smooth_transition.jpg](./20_c5_wrist_loopcut_smooth_transition.jpg) | 00:23:10 | Ch.5 手首の近接ループ追加 | 腕側に `Ctrl + R` でループを1本追加して手首へ寄せ、`Hand: 0.25` / `LowerArm: 0.75` の滑らかなグラデーションを構築。 |
| 21 | [21_c5_neck_head_05_boundary_matching.jpg](./21_c5_neck_head_05_boundary_matching.jpg) | 00:28:35 | Ch.5 首と頭の境界ウェイト一致 | 首側上端と頭部下端の接合ループを選択。双方に `Neck: 0.5`、`Head: 0.5` を数値割り当てし、頭部回転時のメッシュ裂け目を完全防止。 |
| 22 | [22_c6_chest_spine_row_copy_weights.jpg](./22_c6_chest_spine_row_copy_weights.jpg) | 00:30:45 | Ch.6 体幹ウェイト整理と横列コピー | Chestの過剰な下腹部ウェイトをSubtract消去。Spineの綺麗なウェイトを持つ頂点を選び、**Copy** ボタンで横列ループ全体へ一括転送。 |
| 23 | [23_c6_knee_bend_smoothness_quad_flow.jpg](./23_c6_knee_bend_smoothness_quad_flow.jpg) | 00:32:05 | Ch.6 膝曲げトポロジーと三角化 | 膝を曲げて正面の割りを Subdivide（Smoothness付き）で追加。膝裏の潰れを防ぐため、意図した曲がり方向へ対角エッジを三角化・反転。 |
| 24 | [24_c6_full_body_pose_check_complete.jpg](./24_c6_full_body_pose_check_complete.jpg) | 00:33:50 | Ch.6 素体スキニング完了 | 全身のボーンを回転させて可動域とメッシュ変形の破綻がないかを総合点検。素体のリギング＆スキニングがここに完全完了！ |

---

## 技術要点・スキニングの極意（第19話）

1. **Auto Normalize（自動正規化）の徹底**:
   - スキニング作業中は必ず **Auto Normalize: ON** を維持。頂点に影響する全ボーンのウェイト合計が常に1.0（100%）に保たれ、UnityやVRM出力時の正規化誤差による変形破綻・メッシュ飛びを恒久的に防ぐ。
2. **手メッシュの一時分離（P）によるウェイト保全**:
   - 体全体に `With Automatic Weights` をかける前に、あらかじめ繊細にウェイトを塗った手メッシュを `P` キーで別オブジェクトに分離。自動ウェイトによる上書き破壊を物理的に防ぐプロのワークフロー。
3. **ボーン変形状態でのトポロジー調整**:
   - Armatureモディファイアの「四角と三角」アイコン（ケージ表示）をONにすることで、ポーズをつけた変形状態のまま編集モードで頂点移動・ループカット・エッジディゾルブが可能。曲げた際の潰れ・痩せ（ボリュームロス）をリアルタイムに解消。
4. **接合境界の数値入力（0.5 / 0.5）アサイン**:
   - 首と頭、手首と腕など、別オブジェクトや境界ループで繋がる箇所は、ブラシではなくアイテムパネルの頂点ウェイトで親ボーンと子ボーンに `0.5 / 0.5` を直接数値入力。回転時の裂け目・隙間を数学的に完全ゼロ化。
5. **頂点ウェイトの横列コピー（Copy）**:
   - 胴体やスカートなど円筒トポロジーのパーツは、1頂点だけ綺麗なグラデーションを作った後、横列の頂点ループを選択して **Copy** ボタンを押すだけで、全周に均等なウェイトを一瞬で転送可能。
