# ふさこ氏 Blenderキャラクター制作 #26『アウターのUV展開』スクリーンショットカタログ

YouTube動画: [Blenderでキャラクターモデル制作！#26 | アウターのUV展開 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=pueKgjxwIyI)  
詳細仕様書: [2026-09-24_fusako_uv_outer_26_steps.md](../../.agents/handoffs/2026-09-24_fusako_uv_outer_26_steps.md)

---

## スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル（クリックで拡大） | 主な解説・操作内容 |
|:---:|:---:|:---|:---|
| 01 | 00:20 | [fusako26_01_outer_overview.jpg](./fusako26_01_outer_overview.jpg) | アウター全体の確認とUV展開の基本方針（フード・袖・身頃・裏地） |
| 02 | 00:50 | [fusako26_02_hood_seam_marking.jpg](./fusako26_02_hood_seam_marking.jpg) | フードのシーム設定（外側と内側の色の切り替わりラインにマークシーム） |
| 03 | 01:30 | [fusako26_03_hood_unwrap_check.jpg](./fusako26_03_hood_unwrap_check.jpg) | フードの初期展開と猫耳パーツの表裏分割・展開確認 |
| 04 | 02:10 | [fusako26_04_string_rectify.jpg](./fusako26_04_string_rectify.jpg) | フード中央・直線部分のTexTools Rectify（長方形格子化）による歪み解消 |
| 05 | 02:45 | [fusako26_05_string_pin_relax.jpg](./fusako26_05_string_pin_relax.jpg) | 直線化部分のピン留め（P）と再展開（U）によるテクスチャ描きやすさ向上 |
| 06 | 03:30 | [fusako26_06_body_shoulder_side_seam.jpg](./fusako26_06_body_shoulder_side_seam.jpg) | 猫耳パーツの厚み歪み対策（選択縮小＋ピン留め再展開テクニック） |
| 07 | 04:15 | [fusako26_07_sleeve_seam_unwrap.jpg](./fusako26_07_sleeve_seam_unwrap.jpg) | フード内側（裏地）のRectify展開とピン留め再展開 |
| 08 | 05:00 | [fusako26_08_material_color_assign.jpg](./fusako26_08_material_color_assign.jpg) | パックアイランド仮配置とアウター用UV確認マテリアル（黄色系）のアサイン |
| 09 | 05:45 | [fusako26_09_rib_cuff_unwrap.jpg](./fusako26_09_rib_cuff_unwrap.jpg) | アウターへのマテリアルリンク（Ctrl+L > Link Materials）と模様の歪み確認 |
| 10 | 06:30 | [fusako26_10_solidify_distortion_check.jpg](./fusako26_10_solidify_distortion_check.jpg) | 身頃の展開（前身頃・後身頃のシーム入れ）と袖の厚み付け適用前の形状確認 |
| 11 | 07:15 | [fusako26_11_solidify_rim_seam.jpg](./fusako26_11_solidify_rim_seam.jpg) | 袖のSolidifyモディファイア適用と厚み境界・色分けラインへのシーム入れ |
| 12 | 08:00 | [fusako26_12_pocket_seam_marking.jpg](./fusako26_12_pocket_seam_marking.jpg) | 袖の上下色分け境界（紫・白の切り替え）へのマークシーム |
| 13 | 08:45 | [fusako26_13_pocket_unwrap_relax.jpg](./fusako26_13_pocket_unwrap_relax.jpg) | 袖展開時の厚み歪み発生と選択縮小法による修正（Ctrl+NumMinus） |
| 14 | 09:30 | [fusako26_14_inner_shrink_pin_unwrap.jpg](./fusako26_14_inner_shrink_pin_unwrap.jpg) | 袖の表面ピン留め $\to$ 厚み含めた再展開で完全な歪み解消 |
| 15 | 09:44 | [fusako26_15_uv_island_rotation_align.jpg](./fusako26_15_uv_island_rotation_align.jpg) | 袖裏地（インナー面）のS 0.5縮小と向き揃え、Pack Islands（Rotateオフ） |
| 16 | 11:00 | [fusako26_16_zipper_seam_unwrap.jpg](./fusako26_16_zipper_seam_unwrap.jpg) | 前立て・ファスナー境界のシーム入れと重なり部分のトポロジー確認 |
| 17 | 11:45 | [fusako26_17_zipper_straighten_grid.jpg](./fusako26_17_zipper_straighten_grid.jpg) | エッジ回転（Rotate Edge CW）と頂点結合（J）によるメッシュ流れの修正 |
| 18 | 12:30 | [fusako26_18_hood_lining_unwrap.jpg](./fusako26_18_hood_lining_unwrap.jpg) | 重なりフチの曲がり角にシーム追加し縦横ラインを独立展開 |
| 19 | 13:15 | [fusako26_19_textools_rectify_relax.jpg](./fusako26_19_textools_rectify_relax.jpg) | 前立て・フチパーツのTexTools Rectifyと目視歪み微調整 |
| 20 | 14:00 | [fusako26_20_average_island_scale.jpg](./fusako26_20_average_island_scale.jpg) | 全アイランドのUV Average Island Scale（テクセル実寸統一） |
| 21 | 14:45 | [fusako26_21_uv_pack_layout_init.jpg](./fusako26_21_uv_pack_layout_init.jpg) | 各原点（Individual Origins）基準での裏地50%縮小（S 0.5）と初期パッキング |
| 22 | 15:30 | [fusako26_22_symmetry_overlap_prep.jpg](./fusako26_22_symmetry_overlap_prep.jpg) | 左右非対称パーツ（柄・厚み）の分離と左右対称パーツのUV重ね方針 |
| 23 | 16:30 | [fusako26_23_symmetry_overlap_align.jpg](./fusako26_23_symmetry_overlap_align.jpg) | UV同期選択を活用した対称アイランドの結合・TexTools整列（左右・下寄せ） |
| 24 | 17:30 | [fusako26_24_final_outer_uv_layout.jpg](./fusako26_24_final_outer_uv_layout.jpg) | セーター柄パーツの拡大調整とアウター全体の最終UVパッキング完成 |
