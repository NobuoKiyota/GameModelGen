# ふさこ氏『Blenderでキャラクターモデル制作！#24』重要シーン・スクリーンショット集

本ディレクトリには、YouTubeチュートリアル動画 **『【Blender】髪のUV展開！【キャラクターモデル制作！#24】』**（講師: ふさこ氏、時間: 28分32秒、URL: `https://www.youtube.com/watch?v=caWYi7sJmrM`）の解説工程に対応する高解像度スクリーンショット（全24枚）を保存しています。

本動画に対応する詳細な手順解説・トラブルシューティングは、以下の仕様書を参照してください。
👉 **[UV展開編 第2回 詳細技術仕様書（ステップバイステップ解説）](../../.agents/handoffs/2026-09-24_fusako_uv_hair_24_steps.md)**

---

## 収録スクリーンショット一覧（全24枚）

### Chapter 1: 髪パーツのシーム分割と表裏解像度コントロール (00:00〜12:30)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:45 | [01_c1_hair_checker_texture_setup.jpg](./01_c1_hair_checker_texture_setup.jpg) | **チェッカーマテリアル設定**: 髪用マテリアルに Checker Texture を接続し歪み・テクセル密度確認環境を構築。 |
| 02 | 00:01:15 | [02_c1_bangs_center_plane_straight_unwrap.jpg](./02_c1_bangs_center_plane_straight_unwrap.jpg) | **前髪センターの展開**: 板ポリ前髪の中央エッジを直線化し、左右均等にペイントしやすいよう配置。 |
| 03 | 00:01:38 | [03_c1_mirror_u_asymmetric_hair_coloring.jpg](./03_c1_mirror_u_asymmetric_hair_coloring.jpg) | **Mirror U による非対称対応**: 主要前髪は左右非対称塗りのため Mirror U にチェックを入れて分離。 |
| 04 | 00:02:15 | [04_c1_hair_root_and_side_seam_mark.jpg](./04_c1_hair_root_and_side_seam_mark.jpg) | **立体毛束のシーム入れ**: 生え際の根元ループと、表側・裏側を二分する側面エッジに `Mark Seam`。 |
| 05 | 00:03:10 | [05_c1_back_face_scale_down_half_s05.jpg](./05_c1_back_face_scale_down_half_s05.jpg) | **【神Tips】裏面UVの半減縮小**: 頭皮側・影側となる裏面アイランドを `S 0.5` で50%縮小し解像度を節約。 |
| 06 | 00:04:35 | [06_c1_invisible_root_faces_delete.jpg](./06_c1_invisible_root_faces_delete.jpg) | **不可視メッシュの徹底削除**: 髪内部や頭頂に埋まって絶対に見えない根元面を `X > Faces` で完全消去。 |
| 07 | 00:06:15 | [07_c1_twintails_seam_and_unwrap.jpg](./07_c1_twintails_seam_and_unwrap.jpg) | **ツインテールのシーム分割**: カールした太い毛束を表裏で綺麗に2枚に開くシーム配置と展開。 |
| 08 | 00:07:15 | [08_c1_pin_and_weld_split_hair_island.jpg](./08_c1_pin_and_weld_split_hair_island.jpg) | **毛束割れの溶接とピン留め**: 展開時に先端が裂けた箇所を `S 0` で溶接し、`P` ピン留めして再展開。 |
| 09 | 00:08:18 | [09_c1_backhair_select_similar_crease.jpg](./09_c1_backhair_select_similar_crease.jpg) | **クリースからシームへの変換**: `Shift + G > Crease` でクリースエッジを選択し `Mark Seam` に一括流用。 |
| 10 | 00:08:48 | [10_c1_clear_crease_weight_to_zero.jpg](./10_c1_clear_crease_weight_to_zero.jpg) | **クリースのクリア**: 不要になったエッジクリース値をサイドバー（Nキー）で 0 にリセット。 |
| 11 | 00:09:10 | [11_c1_backhair_lock_bundle_seam.jpg](./09_c1_backhair_select_similar_crease.jpg) | **後ろ髪ブロックシーム**: 後ろ髪の重なり合う毛束ブロックごとに外周シームを追加して分離。 |
| 12 | 00:10:15 | [12_c1_backhair_top_seam_and_unwrap.jpg](./12_c1_backhair_top_seam_and_unwrap.jpg) | **上面・側面の展開チェック**: 後ろ髪の上面と側面をシーム分割し、重なりのない展開島を生成。 |
| 13 | 00:11:05 | [13_c1_snap_and_weld_overlapping_uv.jpg](./13_c1_snap_and_weld_overlapping_uv.jpg) | **スナップによるUV頂点吸着**: UVスナップ（Vertex）をONにし、近接した不要な隙間頂点を吸着結合。 |

---

### Chapter 2: 髪UVのパズルパッキングとカーブ直線化 (12:30〜22:45)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 14 | 13:50 | [14_c2_modified_edges_overlay_check.jpg](./14_c2_modified_edges_overlay_check.jpg) | **Modified Edges 表示**: ミラー反転側のUV島を表示し、重なり・干渉をチェック。 |
| 15 | 14:25 | [15_c2_all_hair_objects_multi_edit.jpg](./15_c2_all_hair_objects_multi_edit.jpg) | **全髪パーツの一括編集**: 前髪・横髪・後ろ髪・ツインテールを全選択し、全UV島をエディタ上に同時表示。 |
| 16 | 15:38 | [16_c2_average_islands_scale_apply.jpg](./16_c2_average_islands_scale_apply.jpg) | **Average Islands Scale**: `UV > Average Islands Scale` で全パーツのテクセル密度比率を均一化。 |
| 17 | 18:20 | [17_c2_straighten_curved_hair_island_sx0.jpg](./17_c2_straighten_curved_hair_island_sx0.jpg) | **カーブ毛束の直線化 (`S X 0`)**: 三日月形に曲がった毛束を直線化＋ピン留めで専有スペースを劇的圧縮。 |
| 18 | 20:40 | [18_c2_enlarge_high_detail_bangs_islands.jpg](./18_c2_enlarge_high_detail_bangs_islands.jpg) | **主要前髪の解像度拡大**: 余白スペースを活用し、描き込みが多い主要前髪3本をスケールアップ配置。 |
| 19 | 21:55 | [19_c2_hair_uv_packing_margin_spacing.jpg](./19_c2_hair_uv_packing_margin_spacing.jpg) | **適正マージン確保とパッキング完了**: ブリード（色のにじみ）を防ぐ適正なアイランド間隔を確保して完成。 |

---

### Chapter 3: 猫耳のUV展開と顔テクスチャへの統合パズル (22:45〜28:30)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 20 | 23:15 | [20_c3_kemomimi_outer_inner_seam_mark.jpg](./20_c3_kemomimi_outer_inner_seam_mark.jpg) | **猫耳の表裏シーム分割**: 耳の外殻（表）と内耳の毛（裏）の境界エッジにシームを入れて展開。 |
| 21 | 24:20 | [21_c3_rectify_inner_ear_fluff_tufts.jpg](./21_c3_rectify_inner_ear_fluff_tufts.jpg) | **内耳毛束の Rectify 直角化**: TexTools Rectify ＋ ピン留めにより、三角形面を含む毛束を長方形に補正。 |
| 22 | 25:30 | [22_c3_sort_horizontal_align_tufts.jpg](./22_c3_sort_horizontal_align_tufts.jpg) | **Sort H による一列自動整列**: 内耳の複数毛束を島選択モードで `Sort H` を実行し横一列に整頓。 |
| 23 | 26:15 | [23_c3_face_and_ears_multi_selection.jpg](./23_c3_face_and_ears_multi_selection.jpg) | **顔と耳の一括複数選択**: 表情シェイプキー連動のため猫耳を顔マテリアルに統合し、全パーツを同時選択。 |
| 24 | 28:15 | [24_c3_final_face_and_ears_uv_layout.jpg](./24_c3_final_face_and_ears_uv_layout.jpg) | **顔・耳の最終統合パッキング完了**: 顔・白目・瞳・口内・歯・舌・猫耳を1枚のテクスチャ正方形内に配置完了。 |
