# ふさこ氏 Blenderキャラモデリング #35 スクリーンショットカタログ
## 【シェイプキー編01】あいうえお口の形のシェイプキー (Blender 3D)

本フォルダには、YouTube動画「【Blender】キャラクターモデル制作！シェイプキー編01 口のシェイプキー【3Dモデリング講座】」（動画ID: `A6vy0tfvAzA`）から抽出した高解像度解説スクリーンショット（全24枚）を収録しています。

対応する詳細手順仕様書: [2026-09-25_fusako_shapekey_mouth_35_steps.md](../../.agents/handoffs/2026-09-25_fusako_shapekey_mouth_35_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像リンク（クリックで表示） | 場面・操作内容の解説 |
|:---:|:---:|:---|:---|
| 01 | 00:15 | [fusako35_01_blender_shapekey_overview_vroid.jpg](./fusako35_01_blender_shapekey_overview_vroid.jpg) | **【シェイプキー全体設計】** 喜怒哀楽・あいうえお・瞬きなど制作する必須シェイプキーの構造概要 |
| 02 | 01:25 | [fusako35_02_blender_vertex_count_freeze_basis_check.jpg](./fusako35_02_blender_vertex_count_freeze_basis_check.jpg) | **【鉄則: 頂点数不変】** シェイプキー作成後の頂点増減厳禁ルールと、まつ毛・口のBasis（初期状態）めり込み事前点検 |
| 03 | 01:50 | [fusako35_03_blender_split_window_solid_rendered.jpg](./fusako35_03_blender_split_window_solid_rendered.jpg) | **【作業環境の構築】** ウィンドウを分割し、マテリアルビュー（最終ルック）とソリッドビュー（ポリゴン破綻診断）を並行表示 |
| 04 | 02:55 | [fusako35_04_blender_vroid_vrm_reference_shapekeys.jpg](./fusako35_04_blender_vroid_vrm_reference_shapekeys.jpg) | **【VRoidリファレンス】** VRMインポートした公式モデルのシェイプキー一覧を参照し、標準的な命名規則を把握 |
| 05 | 03:50 | [fusako35_05_blender_brow_pre_subsurf_workflow.jpg](./fusako35_05_blender_brow_pre_subsurf_workflow.jpg) | **【眉毛の先行作成】** SubsurfやMirrorを適用する前のシンプルなトポロジー状態で眉シェイプキーを作成する方針 |
| 06 | 04:15 | [fusako35_06_blender_add_basis_new_shapekey.jpg](./fusako35_06_blender_add_basis_new_shapekey.jpg) | **【Basisと新規キー追加】** オブジェクトデータプロパティから「Basis」を作成後、新規キー（Key 1）を追加してValue操作 |
| 07 | 05:25 | [fusako35_07_blender_brow_angry_offset_penetration.jpg](./fusako35_07_blender_brow_angry_offset_penetration.jpg) | **【brow_angry（怒り眉）】** 眉頭を斜め下に下げつつ、顔面へのめり込みを防ぐためわずかに手前に引き出して配置 |
| 08 | 05:45 | [fusako35_08_blender_intermediate_value_penetration_test.jpg](./fusako35_08_blender_intermediate_value_penetration_test.jpg) | **【中間値貫通テスト】** Valueスライダーを0〜1へ動かし、中間地点（0.5）でメッシュが顔面に埋没しないか動的確認 |
| 09 | 06:10 | [fusako35_09_blender_brow_sorrow_sad_down.jpg](./fusako35_09_blender_brow_sorrow_sad_down.jpg) | **【brow_sorrow（困り眉）】** 眉頭を上げて眉尻を下げるハの字変形を作成 |
| 10 | 07:10 | [fusako35_10_blender_brow_surprise_upward.jpg](./fusako35_10_blender_brow_surprise_upward.jpg) | **【brow_surprise（驚き眉）】** 眉全体を上方に大きく引き上げ、目を見開いた表情に連動させるキーを作成 |
| 11 | 07:45 | [fusako35_11_blender_mouth_diagonal_open_principle.jpg](./fusako35_11_blender_mouth_diagonal_open_principle.jpg) | **【口の開口理論】** 真下ではなく、顔・頬のカーブに沿って「斜め上・斜め下」に広げるセルルック口の変形黄金律 |
| 12 | 08:35 | [fusako35_12_blender_gg_edge_slide_mouth_open.jpg](./fusako35_12_blender_gg_edge_slide_mouth_open.jpg) | **【G Gエッジスライド変形】** 口周りのエッジループを `G G` でスライドさせ、自然なアニメ口輪筋の形状を形成 |
| 13 | 09:45 | [fusako35_13_blender_teeth_tongue_shapekey_mouth_a.jpg](./fusako35_13_blender_teeth_tongue_shapekey_mouth_a.jpg) | **【口内・歯のシェイプキー】** 歯・舌オブジェクト側にも新規キーを作成し、上の歯を上へ、下の歯・舌を斜め下へ退避 |
| 14 | 10:50 | [fusako35_14_blender_separate_objects_sync_problem.jpg](./fusako35_14_blender_separate_objects_sync_problem.jpg) | **【別オブジェクトの非同期問題】** 顔と歯が別オブジェクトのため、スライダーを動かしても連動しないBlenderの課題 |
| 15 | 11:25 | [fusako35_15_blender_mio3_shapekey_addon_setup.jpg](./fusako35_15_blender_mio3_shapekey_addon_setup.jpg) | **【神アドオン Mio3 Shapekey】** オブジェクトプロパティで同期対象のコレクション（Head.001）を指定 |
| 16 | 11:55 | [fusako35_16_blender_mth_a_auto_sync_face_teeth.jpg](./fusako35_16_blender_mth_a_auto_sync_face_teeth.jpg) | **【完全自動連動の実現】** 顔と歯に同一のキー名 `mth_A` を付与することで、顔の操作に追従して口内も完全自動シンクロ！ |
| 17 | 12:45 | [fusako35_17_blender_basis_fix_workflow_socket.jpg](./fusako35_17_blender_basis_fix_workflow_socket.jpg) | **【Basis後修正の神技法①】** 口腔奥が小さすぎた問題に対し、修正用シェイプキーを新規作成 |
| 18 | 13:05 | [fusako35_18_blender_select_loop_inner_region_alt_s.jpg](./fusako35_18_blender_select_loop_inner_region_alt_s.jpg) | **【Basis後修正の神技法②】** `Select Loop Inner-Region` で口内を一発全選択し、`Alt + S` で奥のソケットを大きく拡張 |
| 19 | 13:40 | [fusako35_19_blender_vertex_blend_from_shape_basis.jpg](./fusako35_19_blender_vertex_blend_from_shape_basis.jpg) | **【Basis後修正の神技法③】** Basis上で `Blend From Shape` を実行し、既存のmth_Aキーを壊さずに口腔拡張を反映 |
| 20 | 15:15 | [fusako35_20_blender_new_shape_from_mix_workflow.jpg](./fusako35_20_blender_new_shape_from_mix_workflow.jpg) | **【New Shape from Mix】** mth_Aを弱めに開いた状態から、下矢印「New Shape from Mix」で派生口を複製 |
| 21 | 15:45 | [fusako35_21_blender_mth_i_horizontal_spread_teeth.jpg](./fusako35_21_blender_mth_i_horizontal_spread_teeth.jpg) | **【mth_I（い）の造形】** 口角を横に引き広げ、上の歯がチラリと覗く位置に歯のシェイプを調整 |
| 22 | 16:45 | [fusako35_22_blender_mth_u_active_element_pucker.jpg](./fusako35_22_blender_mth_u_active_element_pucker.jpg) | **【mth_U（う）の造形】** ピボットを Active Element に変更し、唇のエッジを内側へ縮小しておちょぼ口を形成 |
| 23 | 18:45 | [fusako35_23_blender_mth_e_pin_preview_toggle.jpg](./fusako35_23_blender_mth_e_pin_preview_toggle.jpg) | **【mth_E（え）とピン留め】** 「あ」と「い」の中間的な開き口を作成。ピン留めアイコンでValue=1のプレビューを確認 |
| 24 | 20:15 | [fusako35_24_blender_mth_o_vertical_oval_aiueo_done.jpg](./fusako35_24_blender_mth_o_vertical_oval_aiueo_done.jpg) | **【mth_O（お）とあいうえお完結】** 縦長のオーバル形状を作成し、リップシンク対応の「あいうえお」基本口が全完成 |

---
*Generated by Antigravity AI Learning Automation Engine*
