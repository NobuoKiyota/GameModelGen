# ふさこ氏『手のモデリング/リギング/スキニング（後編）』操作手順・トポロジー仕様書（第6回）

## 1. 動画メタデータ（公式事実）
- **正式タイトル**: 『Blenderでキャラクターモデル制作！06 | 手のモデリング/リギング/スキニング（後編）〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=kbQzguK_p18
- **動画長**: 36分43秒（2203秒）
- **チャンネル**: ふさこ / 3D工房
- **アップロード日**: 2023年5月24日
- **字幕データ**:
  - VTT生データ: `z:\MeshCreator\.agents\handoffs\fusako_06_subtitles_raw.ja.vtt`
  - タイムスタンプ付きテキスト: `z:\MeshCreator\.agents\handoffs\fusako_06_subtitles_timestamped.txt`
- **重要シーン・スクリーンショット集**:
  - 保存フォルダ: [`z:\MeshCreator\docs\fusako_06_hand_screenshots/`](file:///z:/MeshCreator/docs/fusako_06_hand_screenshots/)
  - 画像カタログ: [`z:\MeshCreator\docs\fusako_06_hand_screenshots/README.md`](file:///z:/MeshCreator/docs/fusako_06_hand_screenshots/README.md)

---

## 2. チャプター構成一覧

| # | タイムスタンプ | チャプター名 | 主な対象 | 概要 |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | 00:00 - 05:00 | 掌（手のひら）のベースモデリング | 手のひらメッシュ | Cube上下面削除の4面筒 $\to$ 指の根元ラインに合わせたループカット $\to$ 小指球・母指球のAlt+S膨らみ |
| **C2** | 05:00 - 10:00 | 親指の独立化と手のひらへの接続 | 親指・付け根メッシュ | 親指のリンク解除（Make Single User） $\to$ 付け根面削除＋Alt+S $\to$ 頂点スナップ＆面張り（F）で母指球と接続 |
| **C3** | 10:00 - 15:00 | リンク解除・ボーンリネーム・統合 | 5本指・全ボーン | Make Single User（Object & Data） $\to$ ボーンリネーム（頂点グループ自動連動） $\to$ Ctrl+Aトランスフォーム適用 $\to$ Ctrl+J統合 |
| **C4** | 15:00 - 24:00 | 指と手のひらの接合と手首の形成 | 接合・手首シリンダー | シアー傾斜アーチ $\to$ ナイフツール割追加 $\to$ 頂点スナップ＋オートマージ $\to$ 手首E押し出し＋S Z 0整流 |
| **C5** | 24:00 - 36:43 | 手のひら・前腕ボーン追加とスキニング | Hand/LowerArmウェイト | Hand/LowerArmボーン追加・親子付け $\to$ 0.5按分ウェイト $\to$ Weights > Smooth & ブラー $\to$ Auto Normalize $\to$ 完成 |

---

## 3. モデリング方針とトポロジー黄金律

### 核心方針: 「リンク解除の一括化、ボーンリネーム自動連動、そして手首への整流」
1. **ボーンリネームと頂点グループの「自動連動」**:
   - `With Empty Groups` で親子付けされたメッシュは、**アーマチュア編集モードでボーン名を変更（F2）すると、メッシュ側の対応する頂点グループ名も自動的に一括変更される**。
   - 手動で頂点グループを1つずつ打ち直す必要がなく、ヒューマノイド規格への移行が極めて安全かつ迅速に行える。
2. **Make Single User（リンク解除）の確実な実行**:
   - 前編で `Alt + D` によりリンクされていた指メッシュとボーンは、各指の微調整・統合の直前に **Object > Relations > Make Single User > Object & Data** で独立化させる。
   - 緑の下三角アイコンの横に「共有ユーザー数」の数字が出ていないことを必ず確認する。
3. **ボーン統合前の「全トランスフォーム適用（Ctrl + A）」**:
   - 個別に回転・配置したアーマチュア同士を `Ctrl + J` で結合する前に、**必ず `Ctrl + A` $\to$ 「全トランスフォーム（All Transforms）」を適用** する（回転・スケールの歪みによる接合後のアニメーション破綻を完全防止）。
4. **手のひら・水かきの曲げ破綻防止（0.5按分とSmooth）**:
   - 指の付け根（MP関節・水かき部）には、指ボーン（`Proximal`）と手のひらボーン（`Hand`）のウェイトを **0.5 : 0.5** でブレンド。
   - 急激なウェイト境界には **`Weights > Smooth`（反復回数調整）** または **ブラーブラシ** をかけ、なだらかな球状変形を実現する。
5. **Auto Normalize（自動正規化）の厳守**:
   - ウェイトペイント時はオプションの **「自動正規化（Auto Normalize）」を常にON** にし、1つの頂点に影響する全ボーンのウェイト合計が常に `1.0` を超えないよう保つ。

---

## 4. パーツ別詳細手順

### Part 1: 手のひら（掌）のベースモデリング (00:00〜05:00)
> [📸 参考: 01_c1_palm_cube_open_tube.jpg](../../docs/fusako_06_hand_screenshots/01_c1_palm_cube_open_tube.jpg) / [02_c1_palm_little_finger_loop.jpg](../../docs/fusako_06_hand_screenshots/02_c1_palm_little_finger_loop.jpg) / [03_c1_palm_index_finger_loop.jpg](../../docs/fusako_06_hand_screenshots/03_c1_palm_index_finger_loop.jpg) / [04_c1_palm_middle_ring_loops.jpg](../../docs/fusako_06_hand_screenshots/04_c1_palm_middle_ring_loops.jpg) / [05_c1_hypothenar_alts_fatten.jpg](../../docs/fusako_06_hand_screenshots/05_c1_hypothenar_alts_fatten.jpg) / [06_c1_thenar_alts_fatten.jpg](../../docs/fusako_06_hand_screenshots/06_c1_thenar_alts_fatten.jpg)
1. `Shift + S` $\to$ **「カーソル $\to$ ワールド原点」** で3Dカーソルを中心に戻す。
2. `Shift + A` $\to$ **メッシュ > 立方体（Cube）** を追加。
3. 編集モードで **一番上と一番下の面を選択して `X` $\to$ 面を削除**（4面筒）。
4. `S` で全体スケールを下絵の手のひら（掌）に合わせる。
5. **指のラインに沿った縦ループの追加**:
   - `Ctrl + R` で縦ループを順次追加し、人差し指、中指、薬指、小指のセンターラインおよび側面に繋がる位置へ `G G`（スライド）で配分。
   - 各ループを選択し、`Alt + S` で前後にふっくらと膨らませる。
6. **母指球・小指球の肉厚形成**:
   - 横から見た際、小指側の付け根（小指球）および親指側の付け根（母指球）がふっくらと盛り上がるよう、横方向のループカットを追加し、`Alt + S` で膨らませる。

---

### Part 2: 親指の独立化と手のひらへの接続 (05:00〜10:00)
> [📸 参考: 07_c2_thumb_make_single_user.jpg](../../docs/fusako_06_hand_screenshots/07_c2_thumb_make_single_user.jpg) / [08_c2_thumb_base_delete_fatten.jpg](../../docs/fusako_06_hand_screenshots/08_c2_thumb_base_delete_fatten.jpg) / [09_c2_thumb_vertex_snap_approach.jpg](../../docs/fusako_06_hand_screenshots/09_c2_thumb_vertex_snap_approach.jpg) / [10_c2_thumb_face_fill_f.jpg](../../docs/fusako_06_hand_screenshots/10_c2_thumb_face_fill_f.jpg) / [11_c2_thumb_webbing_topology.jpg](../../docs/fusako_06_hand_screenshots/11_c2_thumb_webbing_topology.jpg)
1. **親指のリンク解除**:
   - 親指は他の4指と大幅に角度・肉付きが異なるため、プロパティのメッシュタブ（緑の三角）にあるユーザー数「5」をクリックして **シングルユーザー化**（リンク解除）。
2. **親指付け根の開口と肉厚調整**:
   - 親指の一番下の面・エッジループを削除。
   - 腹側を `Alt + S` で大きく膨らませ、手のひら（母指球）の断面へ近づける。
3. **頂点スナップによる歩み寄り**:
   - `Shift + Tab` でスナップをON（スナップ先: 頂点）。
   - 手のひら側の対応する面を削除し、親指の付け根と手のひらの頂点を互いにスナップ吸着させて位置を合わせる。
   - 面が抜けている隙間は 4頂点を選んで `F`（面張り）で塞ぐ。

---

### Part 3: リンク解除・ボーンリネーム・オブジェクト統合 (10:00〜15:00)
> [📸 参考: 12_c3_make_single_user_obj_data.jpg](../../docs/fusako_06_hand_screenshots/12_c3_make_single_user_obj_data.jpg) / [13_c3_armature_single_user.jpg](../../docs/fusako_06_hand_screenshots/13_c3_armature_single_user.jpg) / [14_c3_bone_rename_index_proximal.jpg](../../docs/fusako_06_hand_screenshots/14_c3_bone_rename_index_proximal.jpg) / [15_c3_vgroup_auto_sync_check.jpg](../../docs/fusako_06_hand_screenshots/15_c3_vgroup_auto_sync_check.jpg) / [16_c3_armatures_apply_all_transforms.jpg](../../docs/fusako_06_hand_screenshots/16_c3_armatures_apply_all_transforms.jpg) / [17_c3_armatures_join_ctrl_j.jpg](../../docs/fusako_06_hand_screenshots/17_c3_armatures_join_ctrl_j.jpg)
1. **全指・全ボーンのシングルユーザー化**:
   - オブジェクトモードで人差し指〜小指を選択。
   - ヘッダーの **オブジェクト > 関係 > シングルユーザー化 > オブジェクトとデータ（Object > Relations > Make Single User > Object & Data）** を実行。
   - ボーンも同様にすべてシングルユーザー化。
2. **Unity規格へのボーンリネーム（自動連動）**:
   - 各指のボーンを選択し、編集モードで `F2` によりリネーム:
     - 人差し指: `Index_Proximal`, `Index_Intermediate`, `Index_Distal`
     - 中指: `Middle_Proximal`, `Middle_Intermediate`, `Middle_Distal`
     - 薬指: `Ring_Proximal`, `Ring_Intermediate`, `Ring_Distal`
     - 小指: `Little_Proximal`, `Little_Intermediate`, `Little_Distal`
     - 親指: `Thumb_Proximal`, `Thumb_Intermediate`, `Thumb_Distal`
   - **確認**: メッシュ側の頂点グループ一覧を開くと、ボーンと同名に自動更新されていることを確認。
3. **アーマチュアのトランスフォーム適用と統合**:
   - 全指のボーンを選択し、**`Ctrl + A` $\to$ 「全トランスフォーム（All Transforms）」** を実行。
   - その後、**`Ctrl + J` で1つのアーマチュアに統合**。
4. **指メッシュと手のひらメッシュの統合**:
   - 全指メッシュと手のひらメッシュを選択し、**`Ctrl + J` で1つのオブジェクトに統合**。

---

### Part 4: 指と手のひらの接合・手首の形成 (15:00〜24:00)
> [📸 参考: 18_c4_finger_base_shear_arch.jpg](../../docs/fusako_06_hand_screenshots/18_c4_finger_base_shear_arch.jpg) / [19_c4_snap_automerge_fingers_to_palm.jpg](../../docs/fusako_06_hand_screenshots/19_c4_snap_automerge_fingers_to_palm.jpg) / [20_c4_merge_by_distance.jpg](../../docs/fusako_06_hand_screenshots/20_c4_merge_by_distance.jpg) / [21_c4_knife_cuts_on_palm.jpg](../../docs/fusako_06_hand_screenshots/21_c4_knife_cuts_on_palm.jpg) / [22_c4_fill_webbing_faces.jpg](../../docs/fusako_06_hand_screenshots/22_c4_fill_webbing_faces.jpg) / [23_c4_wrist_extrude_sz0_level.jpg](../../docs/fusako_06_hand_screenshots/23_c4_wrist_extrude_sz0_level.jpg) / [24_c4_wrist_cross_section_oval.jpg](../../docs/fusako_06_hand_screenshots/24_c4_wrist_cross_section_oval.jpg)
1. **付け根のシアー傾斜調整**:
   - 人差し指・薬指・小指の付け根ループを選択し、**シアー（`Shift + Ctrl + Alt + S`）** で中指を頂点とする緩やかな山なりアーチに角度を整流。
2. **ナイフツールによるトポロジー整流**:
   - 手のひら・手の甲に `K`（ナイフツール）でエッジを切り込み、指の8頂点ループと綺麗に接続できるよう分割を足す。
3. **頂点マージによる接合**:
   - 頂点スナップ＋Auto MergeをONにし、手のひら側の頂点を指の付け根頂点にスナップ結合。
   - 全選択 `A` $\to$ **`M` $\to$ 「距離でマージ（By Distance）」** で二重頂点を完全溶接。
4. **手首シリンダーの押し出し**:
   - 手のひら下端の開口部エッジループを `Alt + 左クリック` で選択。
   - **`E`（押し出し） $\to$ `S Z 0`** で水平に揃え、手首断面のシリンダーを腕側へ伸ばす。
   - 歪んだ断面を `Alt + S` や `S X`, `S Y` で綺麗な楕円形に整流。

---

### Part 5: 手のひら・前腕ボーン追加とスキニング (24:00〜36:43)
> [📸 参考: 25_c5_add_hand_lowerarm_bones.jpg](../../docs/fusako_06_hand_screenshots/25_c5_add_hand_lowerarm_bones.jpg) / [26_c5_bone_parenting_keep_offset.jpg](../../docs/fusako_06_hand_screenshots/26_c5_bone_parenting_keep_offset.jpg) / [27_c5_create_vgroups_hand_lowerarm.jpg](../../docs/fusako_06_hand_screenshots/27_c5_create_vgroups_hand_lowerarm.jpg) / [28_c5_assign_hand_half_weight.jpg](../../docs/fusako_06_hand_screenshots/28_c5_assign_hand_half_weight.jpg) / [29_c5_pose_mode_finger_curl_test.jpg](../../docs/fusako_06_hand_screenshots/29_c5_pose_mode_finger_curl_test.jpg) / [30_c5_vertex_mask_blur_brush.jpg](../../docs/fusako_06_hand_screenshots/30_c5_vertex_mask_blur_brush.jpg) / [31_c5_weights_smooth_filter.jpg](../../docs/fusako_06_hand_screenshots/31_c5_weights_smooth_filter.jpg) / [32_c5_auto_normalize_checkbox.jpg](../../docs/fusako_06_hand_screenshots/32_c5_auto_normalize_checkbox.jpg) / [33_c5_lowerarm_wrist_weight.jpg](../../docs/fusako_06_hand_screenshots/33_c5_lowerarm_wrist_weight.jpg) / [34_c5_webbing_tri_quad_retarget.jpg](../../docs/fusako_06_hand_screenshots/34_c5_webbing_tri_quad_retarget.jpg) / [35_c5_hand_complete_pose_persp.jpg](../../docs/fusako_06_hand_screenshots/35_c5_hand_complete_pose_persp.jpg)
1. **Hand & LowerArm ボーンの追加**:
   - アーマチュアの編集モードで `Shift + A` $\to$ 手首の位置に新規ボーンを追加。
   - 手首〜手のひら中央へ伸ばし、名前を **`Hand`** に設定。
   - 手首から前腕側へ逆方向に押し出し、名前を **`LowerArm`** に設定。
2. **ボーンの親子関係（Parenting）の構築**:
   - 各指の付け根ボーン（`*_Proximal`）を選択 $\to$ `Hand` を最後に追加選択 $\to$ **`Ctrl + P` $\to$ 「オフセットを保持（Keep Offset）」**。
   - `Hand` を選択 $\to$ `LowerArm` を追加選択 $\to$ **`Ctrl + P` $\to$ 「オフセットを保持（Keep Offset）」**。
3. **頂点グループの作成と初期割り当て**:
   - メッシュに新規頂点グループ **`Hand`** と **`LowerArm`** を追加。
   - 手のひら本体の頂点を選択し、`Hand: 1.0` を割り当て。
   - 指の付け根（水かき部）ループを選択し、`Hand: 0.5` / 各指の `Proximal: 0.5` を半々で割り当て。
   - 手首上端ループには `Hand: 0.5` / `LowerArm: 0.5` を割り当て、手首下端には `LowerArm: 1.0` を割り当て。
4. **ウェイトの平滑化（Smooth & Blur）**:
   - `Ctrl + Tab` でウェイトペイントモードに入る。
   - ツールオプションで **「自動正規化（Auto Normalize）」をON**。
   - `V` キーで頂点選択モードにし、関節の境界ループを選択。
   - ヘッダーの **ウェイト > スムーズ（Weights > Smooth）** を実行（サブセット: 変形ポーズボーン、反復回数を調整して滑らかなグラデーションを生成）。
   - 必要に応じて `Shift + Space` $\to$ **ブラーブラシ（Blur）** で手動でなじませる。
5. **ポーズモードでの最終曲げテスト**:
   - ポーズモードで指を握り拳（グー）に曲げ、水かきが不自然にめり込まないか、手の甲が綺麗にアーチを描くか検証。
   - 不自然なシワ・歪みがある箇所は、編集モードで `J`（頂点連結）や `X` $\to$ 「辺を溶解」で三角面/四角面の流れを手動整流。

---

## 5. 必須テクニック＆ショートカット早見表

| ショートカット / 機能 | 操作名称 | 本チュートリアルでの用途 |
| :--- | :--- | :--- |
| `Make Single User` | シングルユーザー化 | リンク複製された指やボーンを独立した実体データに変換する |
| `F2` (ボーン編集) | ボーンリネーム | ボーン名を変更すると、紐づくメッシュの頂点グループ名も完全自動同期する |
| `Ctrl + A` $\to$ All Transforms | 全トランスフォーム適用 | ボーン統合前に回転・位置・スケールを初期化し、リグ変形の破綻を防ぐ |
| `S Z 0` | 座標ゼロ化 | 手首の押し出し断面の高さを完全な水平（同一Z平面）に揃える |
| `Ctrl + P` $\to$ Keep Offset | オフセット保持親子付け | 指ボーンと手のひらボーンを物理的な位置関係を保ったまま階層リンクする |
| `Weights > Smooth` | ウェイトスムーズ | 関節・水かき部の急激なウェイト変化を数学的になだらかなグラデーションにする |
| オートノーマライズ (Auto Normalize) | 自動正規化 | ウェイトペイント時に全ボーンの影響度合計を常に1.0に自動調整する |
| `V` (ウェイトペイント中) | 頂点選択マスク | 選択した頂点だけにブラシやスムーズの影響を限定し、他の指への誤塗りを完全防止する |

---

## 6. 本プロジェクト（AnimeFace / 素体パイプライン）との連動・実装指針

1. **第4回（腕部シリンダー）との接合規格**:
   - 第4回仕様書（Part 3）で作成した腕メッシュの手首開口部（8頂点）と、本仕様書の手首シリンダーは、同一の頂点数で設計されています。
   - `LoopTools > Bridge` または頂点スナップにより、腕と手を1対1の四角面で完全に一体化可能です。
2. **ゲームエンジン（Unity/UE）へのエクスポート互換性**:
   - 指（15ボーン）＋手掌（`Hand`）＋前腕（`LowerArm`）の構造は、Unityのヒューマノイドアバターリグ構成と完全一致しており、FBXエクスポート時に一切の追加設定なしで標準アニメーション（グー・チョキ・パー等）が再生可能です。
