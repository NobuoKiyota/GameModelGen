# ふさこ氏『Blenderでキャラクターモデル制作！』第37話 スクリーンショットカタログ
## 03 | 喜怒哀楽などの表情シェイプキー

本カタログは、YouTubeチュートリアル動画 **ふさこ氏『03 | 喜怒哀楽などの表情シェイプキー』**（動画ID: `ZbrGz3ma19I`）から抽出した高解像度スクリーンショット（全24枚）のインデックスです。

詳細な操作手順、ショートカットキー、設定パラメータ、理論的背景については、以下の仕様書を参照してください：
- **詳細技術仕様書**: [`.agents/handoffs/2026-09-25_fusako_emotions_shapekey_37_steps.md`](../../.agents/handoffs/2026-09-25_fusako_emotions_shapekey_37_steps.md)

---

### スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル名（クリックで表示） | 場面・工程タイトル | 主な解説・技術ポイント |
|:---:|:---:|:---|:---|:---|
| 01 | 00:15 | [fusako37_01_blender_mouth_smile_active_element_planning.jpg](./fusako37_01_blender_mouth_smile_active_element_planning.jpg) | 笑顔口（mth_smile）の計画とActive Element | 口角を上げて笑い口を作るため、口角の端点を選択しピボットをActive Elementに設定 |
| 02 | 00:35 | [fusako37_02_blender_mouth_smile_topology_crease_note.jpg](./fusako37_02_blender_mouth_smile_topology_crease_note.jpg) | 口角引き上げによる歪みと修正方針 | ローポリ状態で面が歪んで不要な線・影が出る現象。Subdivision適用後に直す方針を確認 |
| 03 | 01:05 | [fusako37_03_blender_mouth_angry_pull_down_edges.jpg](./fusako37_03_blender_mouth_angry_pull_down_edges.jpg) | への字口（mth_angry）の作成 | 怒り・不満のへの字口を作成。口角を選択しSキーまたはGZで下方へ引き下げ |
| 04 | 01:30 | [fusako37_04_blender_mouth_angry_shape_verification.jpg](./fusako37_04_blender_mouth_angry_shape_verification.jpg) | への字口の形状確認と命名 | 下げすぎず不機嫌さが伝わる絶妙なラインで確定し、キー名を `mth_angry` に設定 |
| 05 | 01:55 | [fusako37_05_blender_combine_brow_eye_mouth_for_joy.jpg](./fusako37_05_blender_combine_brow_eye_mouth_for_joy.jpg) | 喜怒哀楽コンビネーション（喜び顔）の合成 | `brow_fun` (1.0), `eye_smile` (1.0), `mth_smile` (1.0) をスライダーで同時適用 |
| 06 | 02:15 | [fusako37_06_blender_new_shape_from_mix_all_joy.jpg](./fusako37_06_blender_new_shape_from_mix_all_joy.jpg) | New Shape from Mixによるall_joy抽出 | 合成した表情から一括で新規キー `all_joy` を作成。個別スライダーをリセットして確認 |
| 07 | 05:15 | [fusako37_07_blender_teeth_mouth_cavity_all_joy_sync.jpg](./fusako37_07_blender_teeth_mouth_cavity_all_joy_sync.jpg) | 口内・歯オブジェクトへのall_joy同期 | 歯オブジェクトにも同名キー `all_joy` を作成し、Mio3 Shapekeyによる完全自動連動を確立 |
| 08 | 06:10 | [fusako37_08_blender_highlight_all_joy_motion_sync.jpg](./fusako37_08_blender_highlight_all_joy_motion_sync.jpg) | 瞳ハイライトのall_joy連動 | 笑顔目でハイライトが隠れないよう、ハイライトにも同名キーを設定して位置を連動 |
| 09 | 06:40 | [fusako37_09_blender_modifier_cannot_apply_shapekey_error.jpg](./fusako37_09_blender_modifier_cannot_apply_shapekey_error.jpg) | 【Blender標準制限】モディファイア適用エラー | シェイプキーがあるメッシュにモディファイアを直接適用しようとすると発生する警告エラー |
| 10 | 07:00 | [fusako37_10_blender_apply_modifier_keep_shapekeys_addon.jpg](./fusako37_10_blender_apply_modifier_keep_shapekeys_addon.jpg) | 神アドオン Apply Modifier Keep Shapekeys | シェイプキーを破壊せずにモディファイアを強制適用できる必須アドオンのメニュー |
| 11 | 07:20 | [fusako37_11_blender_mirror_apply_collection_fix.jpg](./fusako37_11_blender_mirror_apply_collection_fix.jpg) | ミラー適用とコレクション・参照復元 | ミラーモディファイアを適用後、移動したコレクションの復元と瞳のミラー参照を顔に再指定 |
| 12 | 08:15 | [fusako37_12_blender_asymmetric_wink_planning.jpg](./fusako37_12_blender_asymmetric_wink_planning.jpg) | 左右非対称ウインク（_L / _R）の作成計画 | ミラー適用が完了したため、左右対称キーから片側だけのウインクを作成する計画 |
| 13 | 08:35 | [fusako37_13_blender_select_side_of_active_half_mesh.jpg](./fusako37_13_blender_select_side_of_active_half_mesh.jpg) | 【標準技】Select Side of Activeによる半身選択 | 中心頂点を選択後、`Select > Side of Active` (Axis: Negative) で片側頂点を一括選択 |
| 14 | 09:00 | [fusako37_14_blender_blend_from_shape_basis_wink_make.jpg](./fusako37_14_blender_blend_from_shape_basis_wink_make.jpg) | 【標準技】Vertex Blend From Shapeで片目Basis復元 | 選択頂点のみにBasis（初期開眼）をブレンドして片目を開け、片側ウインク `eye_blink_L` を完成 |
| 15 | 10:15 | [fusako37_15_blender_shape_keys_util_booth_addon.jpg](./fusako37_15_blender_shape_keys_util_booth_addon.jpg) | 【神アドオン】Shape Keys Util（BOOTH無料） | 4ステップの手動作業を一瞬で自動化する無料アドオン `Shape Keys Util` の右クリックメニュー |
| 16 | 10:30 | [fusako37_16_blender_separate_shapekey_left_right_oneclick.jpg](./fusako37_16_blender_separate_shapekey_left_right_oneclick.jpg) | Separate Shape Key Left and Rightワンポチ分割 | `Separate Shape Key Left and Right`（Duplicate: ON）で左右のキーを一発自動生成 |
| 17 | 12:10 | [fusako37_17_blender_highlight_apply_all_transforms_split.jpg](./fusako37_17_blender_highlight_apply_all_transforms_split.jpg) | 瞳ハイライトのトランスフォーム全適用と分割 | 原点がずれている場合の `Ctrl+A > All Transforms` 適用と、ハイライトの左右個別分割 |
| 18 | 13:20 | [fusako37_18_blender_backup_duplicate_before_subsurf_apply.jpg](./fusako37_18_blender_backup_duplicate_before_subsurf_apply.jpg) | Subsurf適用前の安全バックアップ複製 | 不可逆な細分化適用前に、`Shift+D` で顔メッシュを完全複製して別コレクションに退避 |
| 19 | 13:40 | [fusako37_19_blender_keep_shapekeys_subsurf_apply_exec.jpg](./fusako37_19_blender_keep_shapekeys_subsurf_apply_exec.jpg) | Subdivision Surfaceの確定適用実行 | `Apply Modifier Keep Shapekeys` でSubsurfを適用。中心結合エラー時の原因と対処 |
| 20 | 14:45 | [fusako37_20_blender_gg_edge_slide_mouth_crease_smoothing.jpg](./fusako37_20_blender_gg_edge_slide_mouth_crease_smoothing.jpg) | Subsurf適用後の口角えぐれ・影線スムージング | 増えた頂点を活かし、左右対称XミラーONで `G G`（エッジスライド）を使い口角のシワを解消 |
| 21 | 16:30 | [fusako37_21_blender_blend_from_shape_update_all_expressions.jpg](./fusako37_21_blender_blend_from_shape_update_all_expressions.jpg) | 修正口角のBlend From Shape部分統合 | 直した口角ループを選択し、`all_angry` や `all_joy` 等の複合キーへ部分反映 |
| 22 | 17:45 | [fusako37_22_blender_mouth_outline_uv_editor_alignment.jpg](./fusako37_22_blender_mouth_outline_uv_editor_alignment.jpg) | 口輪郭テクスチャ途切れのUVエディター修正 | 開口時にテクスチャ線が途切れる問題を、UVエディター上で頂点を微移動して綺麗に繋ぐ |
| 23 | 19:20 | [fusako37_23_blender_all_surprise_full_facial_combo_sync.jpg](./fusako37_23_blender_all_surprise_full_facial_combo_sync.jpg) | びっくり顔（all_surprise）の合成と全連動 | 見開き目＋驚き眉＋「お」の口を合成した `all_surprise`。顔・歯・瞳の完全シンクロ確認 |
| 24 | 21:05 | [fusako37_24_blender_ear_emotional_bounce_3d_cursor_pivot.jpg](./fusako37_24_blender_ear_emotional_bounce_3d_cursor_pivot.jpg) | 耳の感情連動（3Dカーソルピボット跳ね＆タレ耳） | 耳の付け根に3Dカーソルを配置し、喜怒哀楽に合わせて耳がぴょこんと動く極上アニメーション |
