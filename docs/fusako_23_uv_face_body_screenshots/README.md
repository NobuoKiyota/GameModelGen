# ふさこ氏『Blenderでキャラクターモデル制作！#23』重要シーン・スクリーンショット集

本ディレクトリには、YouTubeチュートリアル動画 **『【Blender】顔・体のUV展開！【キャラクターモデル制作！#23】』**（講師: ふさこ氏、時間: 27分29秒、URL: `https://www.youtube.com/watch?v=hwDyavPRVNE`）の解説工程に対応する高解像度スクリーンショット（全24枚）を保存しています。

本動画に対応する詳細な手順解説・トラブルシューティングは、以下の仕様書を参照してください。
👉 **[UV展開編 第1回 詳細技術仕様書（ステップバイステップ解説）](../../.agents/handoffs/2026-09-24_fusako_uv_face_body_23_steps.md)**

---

## 収録スクリーンショット一覧（全24枚）

### Chapter 1: UV展開の事前準備と口内モデリング (00:00〜07:05)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:25 | [01_c1_uv_material_separation_plan.jpg](./01_c1_uv_material_separation_plan.jpg) | **マテリアル・テクスチャ分割計画**: 顔、髪、肌、インナー、アウター、アクセ、透過（チーク等）の単位設計。 |
| 02 | 00:02:05 | [02_c1_apply_scale_and_cleanup_mesh.jpg](./02_c1_apply_scale_and_cleanup_mesh.jpg) | **展開前チェック**: 全オブジェクトのスケール適用（`Ctrl + A > Scale`）と服の中の不可視面削除。 |
| 03 | 00:03:30 | [03_c1_teeth_upper_model_plane_extrude.jpg](./03_c1_teeth_upper_model_plane_extrude.jpg) | **上の歯のモデリング**: 平面からインセット、中央削除、ミラー＋サブサーフ、押し出しでアーチ形成。 |
| 04 | 00:04:25 | [04_c1_teeth_lower_duplicate_sz_minus1.jpg](./04_c1_teeth_lower_duplicate_sz_minus1.jpg) | **下の歯の反転配置**: 上の歯を `Shift + D` 複製し、`S Z -1` で上下反転させて配置。 |
| 05 | 00:05:15 | [05_c1_tongue_model_cube_subsurf.jpg](./05_c1_tongue_model_cube_subsurf.jpg) | **舌のモデリング**: 立方体から奥面削除、ミラー＋サブサーフ、押し出しでシンプルな舌を作成。 |
| 06 | 00:06:25 | [06_c1_mouth_parts_scale_fit_in_head.jpg](./06_c1_mouth_parts_scale_fit_in_head.jpg) | **口内パーツの配置・整理**: 歯と舌を小型化して口内ソケットへ収め、ヘッドコレクションへ移動。 |

---

### Chapter 2: 顔肌（Face）のUV展開と歪み解消・ピン留め (07:05〜17:30)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 07 | 08:05 | [07_c2_face_project_from_view.jpg](./07_c2_face_project_from_view.jpg) | **正面投影（Project from View）**: テンキー1の正面視点から顔前面メッシュをUV投影。 |
| 08 | 08:35 | [08_c2_checker_texture_shader_setup.jpg](./08_c2_checker_texture_shader_setup.jpg) | **チェッカーテクスチャ接続**: シェーダーで UV $\to$ Mapping $\to$ Checker Texture を接続し歪み確認環境を構築。 |
| 09 | 09:00 | [09_c2_checker_stretch_display_issue.jpg](./09_c2_checker_stretch_display_issue.jpg) | **側面伸びの確認**: 正面投影では側頭部・耳周りのチェッカーが激しく引き伸ばされる課題を確認。 |
| 10 | 09:40 | [10_c2_pin_center_vertices_p_key.jpg](./10_c2_pin_center_vertices_p_key.jpg) | **中心頂点のピン留め (P)**: 歪みのない顔面中央の主要頂点を `P` キーで赤くピン留め固定。 |
| 11 | 10:10 | [11_c2_pin_unwrap_side_expand.jpg](./11_c2_pin_unwrap_side_expand.jpg) | **ピン留め状態での再展開**: `U > Unwrap` を実行し、中心を固定したまま側面を自然に広げて歪み解消。 |
| 12 | 11:15 | [12_c2_compress_side_temple_uv_space.jpg](./12_c2_compress_side_temple_uv_space.jpg) | **側頭部UVの圧縮**: 塗り込みの少ないこめかみ・耳周りのUV幅を手動で縮小しテクセル解像度を節約。 |
| 13 | 12:00 | [13_c2_align_center_axis_sx0_cursor.jpg](./13_c2_align_center_axis_sx0_cursor.jpg) | **中心軸の垂直一直線化**: 2Dカーソルをピボットにし、正中線頂点を `S X 0` で完全に垂直揃え。 |
| 14 | 12:40 | [14_c2_flatten_mouth_lip_line_sy0.jpg](./14_c2_flatten_mouth_lip_line_sy0.jpg) | **口元リップラインの水平直線化**: リップのアウトラインを `S Y 0` で水平に揃えテクスチャ歪みを防止。 |
| 15 | 13:25 | [15_c2_clear_back_head_seam_unwrap.jpg](./15_c2_clear_back_head_seam_unwrap.jpg) | **後頭部シームのクリア**: 前後分割シームを解除し、頭部全体を一体化した状態で再展開。 |
| 16 | 14:25 | [16_c2_compress_back_head_half_size.jpg](./16_c2_compress_back_head_half_size.jpg) | **後頭部UVの半分圧縮**: 髪で隠れる後頭部の頂点をピン留め併用で約50%の幅に圧縮。 |
| 17 | 15:10 | [17_c2_display_stretch_overlay_heat_map.jpg](./17_c2_display_stretch_overlay_heat_map.jpg) | **Display Stretch オーバーレイ**: UVエディタの歪みヒートマップを表示し、青〜シアンの適正値を確認。 |
| 18 | 17:05 | [18_c2_mirror_u_modified_edges_display.jpg](./18_c2_mirror_u_modified_edges_display.jpg) | **Mirror U による左右展開**: ミラーモディファイアの「Mirror U」ON、2DカーソルX=0.5へ中心スナップ。 |

---

### Chapter 3: 目・口内・まつ毛・歯・舌のUV展開と配置 (17:30〜27:30)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 19 | 18:40 | [19_c3_sclera_white_eye_project_view.jpg](./19_c3_sclera_white_eye_project_view.jpg) | **白目の正面投影**: 白目（Sclera）メッシュをテンキー1から `U > Project from View` で展開。 |
| 20 | 20:05 | [20_c3_mouth_interior_rectify_straight.jpg](./20_c3_mouth_interior_rectify_straight.jpg) | **口内ソケットの直線格子展開**: TexTools Rectify または手動 `S X 0`/`S Y 0` で綺麗な長方形に展開。 |
| 21 | 22:00 | [21_c3_eyelashes_mark_seam_front_back.jpg](./21_c3_eyelashes_mark_seam_front_back.jpg) | **まつ毛の表裏シーム分割**: エッジに `Mark Seam` を入れ、前面と背面に綺麗に2分割展開。 |
| 22 | 24:00 | [22_c3_eyelashes_layout_order_matching_3d.jpg](./22_c3_eyelashes_layout_order_matching_3d.jpg) | **まつ毛の3D整列レイアウト**: 3Dビューの並び（左・中・右）に合わせてUV島を並べ直観的描画を確保。 |
| 23 | 25:10 | [23_c3_separate_eye_highlight_iris_uv.jpg](./23_c3_separate_eye_highlight_iris_uv.jpg) | **瞳とハイライトの分離**: ハイライトを別オブジェクトに分離し、瞳の島を右上に巨大確保。 |
| 24 | 26:55 | [24_c3_teeth_tongue_join_head_uv_layout.jpg](./24_c3_teeth_tongue_join_head_uv_layout.jpg) | **歯・舌の統合と顔UV仮レイアウト**: 歯・舌を統合（`Ctrl + J`）し、1枚の正方形テクスチャ内に集約完了。 |
