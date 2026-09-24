# 【ふさこ氏 3Dキャラ制作 第22回】髪や揺れ物のスキニング・リギング総仕上げ 完全技術仕様書

本ドキュメントは、YouTubeチュートリアル動画 **『【Blender】髪や揺れ物のスキニング！【キャラクターモデル制作！#22】』**（講師: ふさこ氏、時間: 17分57秒、URL: `https://www.youtube.com/watch?v=2B7ofTckPic`）の内容を、Blender 3.6+ / 4.x および Unity/VRM/VRChat 向け出力パイプラインに対応した詳細なステップバイステップ技術仕様として完全体系化したものである。

---

## 0. 本技術仕様の全体俯瞰と核心ポイント

### 0.1 本動画で解決する課題
1. **腕下げ時の袖（Sleeve）の体幹・脇腹貫通問題**:
   - だぼっとした袖や振袖は、腕を下げた際に物理演算（VRM SpringBone / DynamicBone）の衝突判定だけでは脇や胴体への激しい貫通を完全に防ぐことができない。
   - **解決策**:
     - 肩付近のループを中心とする3Dカーソルピボットを設定し、袖全体をあらかじめ背中側へ後退回転（`R X`）させる「形状レベルの事前回避」。
     - 袖先端のプロキシメッシュ（`Proxy_Sleeve`）を作成し、`LowerArm` の子となる揺れボーン（`Sleeve.L` / `Sleeve.R`）から Data Transfer でウェイト転送。
     - **モディファイア積層順序の極意**: `Data Transfer` $\to$ `Solidify` の順に配置し、布の表裏で100%同一のウェイトを非破壊に付与。
2. **多関節しなりパーツ（尻尾・アホ毛・装飾紐）のカクつきと痩せ**:
   - `With Automatic Weights` で多関節ボーンに自動割り当てすると、各ボーンの境界で「関節ごとにカクカク折れ曲がる」不自然な変形や、内側・外側のウェイト差による「メッシュの痩せ・えぐれ（ボリュームロス）」が発生する。
   - **解決策**:
     - **Deform Pose Bones スムーズ**: ポーズを曲げたままケージ表示（四角・三角アイコン）で編集モードに入り、関節リングを選択。頂点マスク（`V`）＋ `Weights > Smooth`（Subset: `Deform Pose Bones`）で関節間を滑らかに補間。
     - **Vertex Weights Copy（円周ループ一括均一化）**: ループ内外の不揃いなウェイトを、理想的な1頂点の数値を **Vertex Weights > Copy** で全周に瞬時に転送。
3. **ゲームエンジン / VRM 必須要件（ボーン影響数4本制限）**:
   - Blender内では1頂点に5本以上のボーン影響があっても問題なく動くが、Unity / VRChat / VRM / Unreal Engine 等のゲームエンジンでは「1頂点あたり最大4ボーン（4 Influences per vertex）」というハードウェア制約がある。
   - 放置すると実機インポート時に微小ウェイトが勝手に切り捨てられ、形状崩れやエッジ割れを引き起こす。
   - **解決策**: ウェイト調整後に **Weights > Limit Total (Limit: 4)** を実行して安全にクランプする。

---

## 1. チャプター別・詳細ステップバイステップ手順

### Chapter 1: 袖（Sleeve）の貫通防止回転とプロキシスキニング (00:00〜09:15)

#### Step 1-1: 腕下げ時の体幹貫通リスクの確認
1. アーマチュアの全ボーンレイヤーを `Shift` クリックで一括表示。
2. ポーズモードで `A`（全選択）後、`Alt + R` / `Alt + G` で初期姿勢（TポーズまたはAポーズ）にリセット。
3. 腕ボーン（`UpperArm`）を下げてみて、袖の内側が脇腹や腰に深くめり込むことを確認。
   [📸 参考: 01_c1_arm_down_penetration_problem.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/01_c1_arm_down_penetration_problem.jpg)

#### Step 1-2: 肩ループを起点とした 3D Cursor ピボットの設定
1. 袖（服）オブジェクトの編集モードに入る。
2. 肩・脇の付け根に近い頂点ループを `Alt + Click` で選択。
3. `Shift + S` > **Cursor to Selected**（カーソル → 選択物）を実行し、回転中心を肩の付け根に配置。
4. トランスフォームピボットポイントを **3D Cursor** に変更。
   [📸 参考: 02_c1_shoulder_loop_cursor_pivot.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/02_c1_shoulder_loop_cursor_pivot.jpg)

#### Step 1-3: 袖メッシュの事前回転 (`R X`) による貫通回避
1. 袖の可動部分（肘から手首側）の頂点をボックス選択 (`B`)。
2. `R` > `X`（または適切なローカル軸）で、袖を背中側へ後退するようにクイッと回転。
3. **効果**: 腕を下げた際、袖が体の真横・前側ではなく「背中側の安全な空間」へ逃げるため、物理演算時の体幹貫通を劇的に軽減できる。
   [📸 参考: 03_c1_rotate_sleeve_backward_rx.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/03_c1_rotate_sleeve_backward_rx.jpg)

#### Step 1-4: 袖先端からのプロキシメッシュ複製・分離
1. 袖の先端付近の面ループを選択。
2. `Shift + D` で複製し、`Esc` で同位置に確定。
3. `P` > **Selection**（選択物）で別オブジェクトとして分離し、名前を `Proxy_Sleeve` とする。
4. プロキシオブジェクトの不要なモディファイア（Solidify, Armature, Data Transfer等）をすべて削除。
   [📸 参考: 04_c1_duplicate_sleeve_proxy_mesh.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/04_c1_duplicate_sleeve_proxy_mesh.jpg)

#### Step 1-5: 前腕からの袖揺れボーン作成 (`Sleeve.L` / `Sleeve.R`)
1. アーマチュアの編集モードに入る。
2. `LowerArm.L`（前腕ボーン）を選択し、`Shift + D` で複製。
3. 袖の垂れ下がりに合わせて少し下向きに傾け、ボーン名を `Sleeve.L` とする。
4. 反対側（`Sleeve.R`）も同様に対称化または複製して作成。
   [📸 参考: 05_c1_sleeve_bone_create_from_lowerarm.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/05_c1_sleeve_bone_create_from_lowerarm.jpg)

#### Step 1-6: 袖ボーンの前腕（LowerArm）への親子付け
1. `Sleeve.L` を選択し、最後に `LowerArm.L` を `Shift` 選択。
2. `Ctrl + P` > **Keep Offset**（オフセットを保持）を実行。
3. ポーズモードで腕を動かすと、袖ボーンが腕の動きに追従することを確認。
   [📸 参考: 06_c1_sleeve_bone_parent_lowerarm_keep_offset.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/06_c1_sleeve_bone_parent_lowerarm_keep_offset.jpg)

#### Step 1-7: プロキシメッシュへの頂点グループ割当
1. `Proxy_Sleeve` オブジェクトを選択。
2. 新規頂点グループ `Sleeve.L` を作成。
3. 編集モードで全選択 (`A`) し、Weight: `1.0` で **Assign**。
4. `M` キーで管理用の「プロキシコレクション」へ移動して非表示にしておく。
   [📸 参考: 07_c1_proxy_vertex_group_sleeve_assign.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/07_c1_proxy_vertex_group_sleeve_assign.jpg)

#### Step 1-8: 袖本体への Data Transfer モディファイア適用
1. 袖（服）オブジェクトを選択。
2. **Data Transfer** モディファイアを追加。
   - **Source**: `Proxy_Sleeve`
   - **Vertex Data**: チェックON > **Vertex Groups**
   - **Mapping**: **Nearest Face Interpolated**（面補間最近接）
3. **Generate Data Layers** を押下。
   [📸 参考: 08_c1_sleeve_data_transfer_modifier.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/08_c1_sleeve_data_transfer_modifier.jpg)

#### Step 1-9: 揺れ範囲を限定するマスク頂点グループの作成
1. このままでは袖全体が `Sleeve` ボーンに追従してしまうため、袖口の先端部分のみを編集モードで選択。
2. 新規頂点グループ `WeightTransfer_Sleeve` を作成し、Weight: `1.0` で **Assign**。
   [📸 参考: 09_c1_sleeve_mask_vertex_group_create.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/09_c1_sleeve_mask_vertex_group_create.jpg)

#### Step 1-10: Data Transfer の頂点グループ制限設定
1. Data Transfer モディファイアの **Vertex Group**（制限頂点グループ）に `WeightTransfer_Sleeve` を指定。
2. ポーズモードで `Sleeve.L` を動かし、指定した袖口のみが揺れ動くことを確認。
   [📸 参考: 10_c1_data_transfer_vertex_group_limit.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/10_c1_data_transfer_vertex_group_limit.jpg)

#### Step 1-11: ウェイトペイントによるスムーズ減衰設定
1. ウェイトペイントモードに入る。
2. 頂点グループ `WeightTransfer_Sleeve` を選択。
3. **Weights > Smooth** を実行。
   - **Subset**: **Active Group**
   - **Factor**: 0.8〜1.0
   - **Expand**: 1〜2（減衰範囲を自然に広げる）
4. これにより、袖口の揺れが肘に向かって滑らかにフェードアウトする。
   [📸 参考: 11_c1_weight_smooth_active_group_expand.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/11_c1_weight_smooth_active_group_expand.jpg)

#### Step 1-12: 脇下・親指周辺の不要ウェイト除去 (Subtract)
1. 腕を動かした際、袖の揺れで脇腹が引っ張られたり、親指が袖口を突き破ったりしないよう点検。
2. ブラシを **Subtract**（引き算）に設定し、脇下や手首寄りの不要な領域をなぞって Weight 0 に完全消去。
   [📸 参考: 12_c1_subtract_armpit_thumb_penetration_fix.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/12_c1_subtract_armpit_thumb_penetration_fix.jpg)

#### Step 1-13: 【極意】モディファイア積層順序 (Data Transfer $\to$ Solidify)
1. **重要ルール**: モディファイアスタックの順番を必ず **Data Transfer** を上に、**Solidify**（厚み付け）をその下に配置する。
2. **効果**: Data Transfer で片面（サーフェス）に転送された高精度ウェイトが、その後の Solidify 生成によって裏面頂点にも100%均等に複製されるため、布の表裏でウェイトが一切ズレなくなる。
   [📸 参考: 13_c1_modifier_order_data_transfer_solidify.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/13_c1_modifier_order_data_transfer_solidify.jpg)

#### Step 1-14: 肘曲げ時の貫通防止ループカットとねじれ修正
1. 肘を曲げたポーズで、腕の素体が袖を突き破らないか確認。
2. 必要に応じて `Ctrl + R` で肘周辺にサポートループを追加し、ねじれの強いエッジを整列させてトポロジーを最適化。
   [📸 参考: 14_c1_elbow_loopcut_and_twist_fix.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/14_c1_elbow_loopcut_and_twist_fix.jpg)

---

### Chapter 2: 尻尾（Tail）のボーン配置とウェイトスムーズ (09:15〜14:30)

#### Step 2-1: 尻尾のローカル表示と根元 3D Cursor 配置
1. 尻尾オブジェクトを選択し、テンキー `/`（スラッシュ）でローカルビュー（単体表示）に切り替え。
2. 編集モードで尻尾の根元の円周頂点ループを `Alt + Click` 選択。
3. `Shift + S` > **Cursor to Selected** で根元中心に 3D Cursor を配置。
   [📸 参考: 15_c2_tail_local_view_cursor_root.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/15_c2_tail_local_view_cursor_root.jpg)

#### Step 2-2: 単一ボーン追加と多関節押し出し (`Tail.001`〜`Tail.006`)
1. オブジェクトモードで `Shift + A` > **Armature > Single Bone** を追加。
2. 編集モードで根元ボーンの名前を `Tail.001` にリネーム（F2）。
3. `E`（押し出し）を繰り返し、尻尾のループ間隔に合わせて先端まで6節のボーンチェーン（`Tail.001`〜`Tail.006`）を作成。
   [📸 参考: 16_c2_tail_bone_chain_extrude.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/16_c2_tail_bone_chain_extrude.jpg)

#### Step 2-3: 自動ウェイト割り当てと関節カクつき確認
1. 尻尾オブジェクト $\to$ アーマチュアの順に選択し、`Ctrl + P` > **With Automatic Weights** を実行。
2. ピボットポイントを **Individual Origins**（それぞれの原点）にし、ポーズモードで全ボーンを曲げてみる。
3. **課題**: 関節の境界部分が角ばって折れ曲がり、蛇腹のような不自然なシワが生じる。
   [📸 参考: 17_c2_tail_automatic_weights_check.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/17_c2_tail_automatic_weights_check.jpg)

#### Step 2-4: ケージ表示による曲げ状態での関節頂点選択
1. ポーズを少し曲げた状態のまま保持。
2. 尻尾オブジェクトの Armature モディファイアで **Display modifier in Edit mode**（四角アイコン）および **Adjust edit cage to modified shape**（三角アイコン）を両方ONにする。
3. 編集モードに入ると、曲がった姿勢のままカクついている関節の頂点ループを選択できる。
   [📸 参考: 18_c2_cage_display_vertex_selection.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/18_c2_cage_display_vertex_selection.jpg)

#### Step 2-5: 頂点マスク＋Deform Pose Bones スムーズの適用
1. ウェイトペイントモードに移行。
2. `V` キーを押して **Vertex Selection**（頂点マスクモード）をON（先ほど編集モードで選んだ頂点だけが有効化）。
3. **Weights > Smooth** を実行。
   - **Subset**: **Deform Pose Bones**（ポーズで曲がっている全変形ボーン）
   - **Factor**: 0.7〜1.0
   - **Iterations**: 2〜4
4. カクついていた関節のウェイトが前後のボーンへ綺麗に分散され、滑らかなS字カーブを描くようになる。
   [📸 参考: 19_c2_weight_smooth_deform_pose_bones.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/19_c2_weight_smooth_deform_pose_bones.jpg)

#### Step 2-6: 【神技】Vertex Weights Copy による円周ループ一括均一化
1. **問題**: ループの内側頂点と外側頂点でウェイト配分が異なると、曲げた時に断面が歪み、チューブが潰れたり痩せたりする。
2. **解決手順**:
   - 編集モードで歪んでいる円周ループを `Alt + Click` 選択。
   - そのループの中で最も理想的な変形をしている「手本となる1頂点」を最後に `Shift + Click` してアクティブ化。
   - サイドバー（Nキー）> **Item** > **Vertex Weights** パネル内にある **Copy** ボタンを押下。
   - **結果**: 選択ループ全周の頂点ウェイトが一瞬でアクティブ頂点と100%同一化され、完全な円筒のボリュームが保たれる。
   [📸 参考: 20_c2_vertex_weights_copy_loop_unify.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/20_c2_vertex_weights_copy_loop_unify.jpg)

#### Step 2-7: 【Unity/VRM必須】Limit Total によるボーン影響数4本制限
1. ウェイトペイントモードで全選択 (`A`)。
2. **Weights > Limit Total** を実行。
   - **Subset**: **Deform pose bones**
   - **Limit**: **4**
3. **効果**: Unity/VRM規格（最大4ボーン/頂点）に準拠し、5本目以降の不要な微小ウェイトを正規化クランプ。ゲームエンジン移行時の予期せぬ形状破綻を未然に防止。
   [📸 参考: 21_c2_limit_total_4_bones_unity_vrm.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/21_c2_limit_total_4_bones_unity_vrm.jpg)

---

### Chapter 3: アーマチュア統合とボーン階層親子付け (14:30〜17:57)

#### Step 3-1: 親子関係の一時解除とアーマチュア統合 (`Ctrl + J`)
1. 尻尾オブジェクトを選択し、`Alt + P` > **Clear and Keep Transformation**（トランスフォームを維持してクリア）を実行。
2. 尻尾アーマチュア $\to$ 本体アーマチュアの順に `Shift` 選択し、`Ctrl + J` で1つのアーマチュアに統合。
3. 尻尾オブジェクトの Armature モディファイアで、統合後の本体アーマチュアを再指定。
   [📸 参考: 22_c3_clear_keep_transform_join_armature.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/22_c3_clear_keep_transform_join_armature.jpg)

#### Step 3-2: 尻尾およびスカートボーンの体幹ボーン階層への接続
1. アーマチュアの編集モードに入る。
2. `Tail.001`（尻尾根元ボーン）を選択し、最後に `Hips`（または `Spine`）を `Shift` 選択。
3. `Ctrl + P` > **Keep Offset** で親子付け。
4. 第21回で作成したスカート用ボーン群（最上段ボーン）を全選択し、最後に `Spine`（または `Hips`）を `Shift` 選択して `Ctrl + P > Keep Offset`。
   [📸 参考: 23_c3_parent_tail_and_skirt_to_hips_spine.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/23_c3_parent_tail_and_skirt_to_hips_spine.jpg)

#### Step 3-3: スカートマスク最上段ループの除外とリギング完結
1. ワンピース（服）の編集モードで、スカート最上段（ウエスト接続部）の頂点ループを選択。
2. 頂点グループ `Mask_Skirt`（第21回の転送制限マスク）から **Remove**（除外）。
3. **効果**:
   - 最上段ループは素体の体幹ウェイト（`Spine` / `Hips`）に100%吸着し、腰の動きと完全に一致。
   - 2段目以降の裾はスカートボーンに従って自然に揺れ動く。
4. 全身ポーズテスト（しゃがみ、ツイスト、ジャンプ）を行い、全身のリギング・スキニング編（全4回）が完全完了。
   [📸 参考: 24_c3_skirt_mask_top_loop_remove_complete.jpg](../../docs/fusako_22_rigging_skinning_hair_screenshots/24_c3_skirt_mask_top_loop_remove_complete.jpg)

---

## 2. 実装チェックリスト（トラブルシューティング）

| 現象 | 主な原因 | 確実な解決策 |
| :--- | :--- | :--- |
| 腕を下げると袖が体に突き刺さる | Aポーズ基準のまま袖が真横を向いている | 肩ループをピボットにして袖全体を後方（`R X`）へ事前回転させておく。 |
| 袖を揺らした時に布の裏地がめくれて表を突き破る | モディファイアの順番が逆（Solidify後にData Transfer） | `Data Transfer` を上に、`Solidify` を下に配置して表裏同一ウェイトにする。 |
| 尻尾を曲げると関節ごとにカクカク折れ曲がる | 自動ウェイトで関節ごとの減衰幅が狭すぎる | ケージ表示ON＋頂点マスク（`V`）で `Weights > Smooth`（Deform Pose Bones）をかける。 |
| 尻尾を曲げるとチューブが楕円に潰れて痩せる | ループ内外の頂点でウェイト数値が不揃い | 理想的な1頂点を選び、**Vertex Weights > Copy** で全周ループに一括転送する。 |
| UnityやVRM出力時にウェイトが勝手に崩れる | 1頂点に5本以上のボーン影響が存在している | `Weights > Limit Total (Limit: 4)` を実行して上限4本にクランプする。 |
