# ふさこ氏『Blenderでキャラクターモデル制作！』第38話 スクリーンショットカタログ
## 04 | ハート目・キラキラ目・青ざめなどの特殊シェイプキー【シェイプキー編 完結】

本カタログは、YouTubeチュートリアル動画 **ふさこ氏『04 | ハート目・キラキラ目・青ざめなどの特殊シェイプキー』**（動画ID: `GC37bbvRjqU`）から抽出した高解像度スクリーンショット（全24枚）のインデックスです。

詳細な操作手順、ショートカットキー、設定パラメータ、理論的背景については、以下の仕様書を参照してください：
- **詳細技術仕様書**: [`.agents/handoffs/2026-09-25_fusako_special_shapekey_38_steps.md`](../../.agents/handoffs/2026-09-25_fusako_special_shapekey_38_steps.md)

---

### スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル名（クリックで表示） | 場面・工程タイトル | 主な解説・技術ポイント |
|:---:|:---:|:---|:---|:---|
| 01 | 00:15 | [fusako38_01_blender_special_shapekeys_concept_overview.jpg](./fusako38_01_blender_special_shapekeys_concept_overview.jpg) | 特殊シェイプキーの全体構想 | ハート目・キラキラ目・青ざめ等、追加メッシュと透過テクスチャによる特殊演出の設計 |
| 02 | 00:55 | [fusako38_02_inkscape_vector_assets_heart_star_aozame.jpg](./fusako38_02_inkscape_vector_assets_heart_star_aozame.jpg) | ベクターソフトInkscapeでのテクスチャ作成 | 無料ベクターソフトInkscapeで描画したハート・星・青ざめグラデーションアセット |
| 03 | 01:25 | [fusako38_03_inkscape_texture_export_resolution_path.jpg](./fusako38_03_inkscape_texture_export_resolution_path.jpg) | テクスチャのPNG書き出し設定 | 選択範囲を指定し、`Shift+Ctrl+E` でプロジェクトのテクスチャフォルダへPNGエクスポート |
| 04 | 01:50 | [fusako38_04_blender_face_texture_swap_plane_add.jpg](./fusako38_04_blender_face_texture_swap_plane_add.jpg) | Blenderでのテクスチャ差し替えと平面追加 | 顔マテリアルに新テクスチャを差し替え、ハート目メッシュ用の平面（Plane）を追加 |
| 05 | 01:60 | [fusako38_05_blender_plane_uv_map_to_heart_area.jpg](./fusako38_05_blender_plane_uv_map_to_heart_area.jpg) | 平面メッシュのUV展開とハートへの配置 | UVエディター上で平面の頂点をテクスチャのハート領域にフィットするように配置 |
| 06 | 04:50 | [fusako38_06_blender_center_vertex_merge_s0_uv_fix.jpg](./fusako38_06_blender_center_vertex_merge_s0_uv_fix.jpg) | 中央頂点マージ（S 0）とUV歪み解消 | メッシュ中央の頂点を `S 0` で一点に集約し、3Dビューでのテクスチャ歪みを防止 |
| 07 | 05:25 | [fusako38_07_blender_heart_align_pupil_mirror_setup.jpg](./fusako38_07_blender_heart_align_pupil_mirror_setup.jpg) | ハート目を瞳前に配置・ミラー適用 | `RX 90` で正対させ、縮小して瞳直前に配置。ミラーモディファイア（対象: 顔）を付与 |
| 08 | 06:15 | [fusako38_08_blender_shapekey_basis_and_key1_pull_back.jpg](./fusako38_08_blender_shapekey_basis_and_key1_pull_back.jpg) | 出現シェイプキーの作成開始 | まず標準出現状態でBasisを作成し、`+` でKey 1を作成して編集モードへ入る |
| 09 | 06:45 | [fusako38_09_blender_gy_depth_hide_scale_zero_behind_eye.jpg](./fusako38_09_blender_gy_depth_hide_scale_zero_behind_eye.jpg) | 瞳裏への引き込み（GY）と極小縮小 | `G Y` で瞳の裏側へ押し込み、`S` で極小サイズに縮小して完全に隠す |
| 10 | 07:10 | [fusako38_10_blender_hidden_to_show_reverse_problem.jpg](./fusako38_10_blender_hidden_to_show_reverse_problem.jpg) | デフォルト出現問題と逆転の必要性 | このままだとデフォルトで表示されキーONで消えてしまうため、Basisとキーを逆転する必要がある |
| 11 | 07:30 | [fusako38_11_blender_reverse_basis_technique_delete_basis.jpg](./fusako38_11_blender_reverse_basis_technique_delete_basis.jpg) | 【神技】逆転Basis技法（元Basisの削除） | 隠れた状態で新規キーを作成後、元のBasisを削除。縮小隠蔽状態を新たなBasisへ昇格させる |
| 12 | 07:50 | [fusako38_12_blender_eye_heart_pop_out_shapekey_complete.jpg](./fusako38_12_blender_eye_heart_pop_out_shapekey_complete.jpg) | 飛び出し出現キー（eye_heart）の完成 | スライダーを上げると瞳の奥からピュッと拡大出現する完璧な `eye_heart` が完成 |
| 13 | 08:15 | [fusako38_13_blender_eye_star_kirakira_reverse_basis.jpg](./fusako38_13_blender_eye_star_kirakira_reverse_basis.jpg) | キラキラ目（eye_star）の逆転Basis作成 | 同様の手順でキラキラ星メッシュを作成し、逆転Basisで出現シェイプキーを構築 |
| 14 | 08:55 | [fusako38_14_vrm_alicia_solid_aozame_forehead_reference.jpg](./fusako38_14_vrm_alicia_solid_aozame_forehead_reference.jpg) | アリシアちゃんモデルの青ざめ構造リファレンス | VRM標準モデル「アリシア・ソリッド」のおでこに沿う板ポリ＋透過テクスチャ構造を確認 |
| 15 | 09:30 | [fusako38_15_blender_forehead_mesh_mirror_select_extend.jpg](./fusako38_15_blender_forehead_mesh_mirror_select_extend.jpg) | 額メッシュの選択（ミラー選択Extend） | 顔の肌面から額を選択し、`Shift+Ctrl+M`（Extend ON）で左右対称に額の面を一括選択 |
| 16 | 10:10 | [fusako38_16_blender_duplicate_shift_d_separate_p.jpg](./fusako38_16_blender_duplicate_shift_d_separate_p.jpg) | 額面の複製（Shift+D）と分離（P） | `Shift+D` で同一位置に複製し、`P` キーで別オブジェクトとして分離 |
| 17 | 10:30 | [fusako38_17_blender_delete_all_shapekeys_transparent_mat.jpg](./fusako38_17_blender_delete_all_shapekeys_transparent_mat.jpg) | 不要キー全削除と透過マテリアル割り当て | `Delete All Shape Keys` で既存キーを全消去し、透過マテリアルを新規割り当て |
| 18 | 11:15 | [fusako38_18_blender_alt_s_normal_offset_extrude_down.jpg](./fusako38_18_blender_alt_s_normal_offset_extrude_down.jpg) | Alt+S法線浮かせと目の上への押し出し | Zファイト防止のため `Alt+S` でわずかに浮かせ、目の直上まで下方向に面を押し出し |
| 19 | 12:40 | [fusako38_19_blender_material_alpha_hashed_blend_mode.jpg](./fusako38_19_blender_material_alpha_hashed_blend_mode.jpg) | マテリアルのブレンドモード透過設定 | マテリアル設定の `Blend Mode` を `Alpha Hashed`（または `Alpha Blend`）に設定 |
| 20 | 13:15 | [fusako38_20_blender_uv_project_from_view_forehead.jpg](./fusako38_20_blender_uv_project_from_view_forehead.jpg) | Project from Viewによる正面投影UV展開 | テンキー1正面視点から `U > Project from View` を行い、青ざめグラデーション領域へ配置 |
| 21 | 14:10 | [fusako38_21_blender_aozame_shapekey_hide_and_unity_instant_switch.jpg](./fusako38_21_blender_aozame_shapekey_hide_and_unity_instant_switch.jpg) | 青ざめ縮小隠蔽とUnity向け0/1瞬時切替思想 | 頭部内へ縮小隠蔽。中間値の歪みはUnity側で0/1瞬時切り替え（Constant）するため無問題 |
| 22 | 15:40 | [fusako38_22_blender_extra_aozame_shapekey_reverse_complete.jpg](./fusako38_22_blender_extra_aozame_shapekey_reverse_complete.jpg) | 逆転Basis適用と命名（extra_aozame） | 逆転Basisを適用して `extra_aozame` を完成。全表情シェイプキーの構築が完了！ |
| 23 | 20:25 | [fusako38_23_inkscape_heart_bezier_nodes_smooth_edit.jpg](./fusako38_23_inkscape_heart_bezier_nodes_smooth_edit.jpg) | 【付録】Inkscapeによるハートパス編集 | ベジェペンで大まかに打ったノードを「スムーズ」機能で丸みのある綺麗なハートへ整える |
| 24 | 23:05 | [fusako38_24_inkscape_linear_gradient_blue_transparent_aozame.jpg](./fusako38_24_inkscape_linear_gradient_blue_transparent_aozame.jpg) | 【付録】青ざめ線形グラデーション作成 | 濃青から透明への線形グラデーションを矩形に適用し、90度回転させて縦落ちシャドウを制作 |
