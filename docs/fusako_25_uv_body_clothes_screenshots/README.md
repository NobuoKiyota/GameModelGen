# ふさこ氏『Blenderでキャラクターモデル制作！#25』重要シーン・スクリーンショット集

本ディレクトリには、YouTubeチュートリアル動画 **『【Blender】体・服・靴のUV展開！【キャラクターモデル制作！#25】』**（講師: ふさこ氏、時間: 33分10秒、URL: `https://www.youtube.com/watch?v=4EvrIHpTA2c`）の解説工程に対応する高解像度スクリーンショット（全24枚）を保存しています。

本動画に対応する詳細な手順解説・トラブルシューティングは、以下の仕様書を参照してください。
👉 **[UV展開編 第3回 詳細技術仕様書（ステップバイステップ解説）](../../.agents/handoffs/2026-09-24_fusako_uv_body_clothes_25_steps.md)**

---

## 収録スクリーンショット一覧（全24枚）

### Chapter 1: 着衣不可視メッシュの分離・削除と服の厚み・蓋モデリング (00:00〜06:35)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:01:05 | [01_c1_dress_solidify_modifier_setup.jpg](./01_c1_dress_solidify_modifier_setup.jpg) | **ワンピースへの Solidify 設定**: Thickness: 0.001m、Fill Rim チェックを外して内側に薄い厚みを付加。 |
| 02 | 00:02:10 | [02_c1_dress_inner_cap_face_inset.jpg](./02_c1_dress_inner_cap_face_inset.jpg) | **お腹の位置での内側蓋作成**: 内側ループに面張り（`F`）＋インセット（`I`）＋中心マージで蓋メッシュを作成。 |
| 03 | 00:02:35 | [03_c1_dress_hem_bridge_edge_loops.jpg](./03_c1_dress_hem_bridge_edge_loops.jpg) | **裾の厚み境界ブリッジ**: 外側と内側の境界エッジを `Bridge Edge Loops` で接続し厚み形状を密閉。 |
| 04 | 00:03:20 | [04_c1_separate_body_hidden_torso_p.jpg](./04_c1_separate_body_hidden_torso_p.jpg) | **ワンピース内部の体幹メッシュ分離**: 服に隠れて完全に見えない胸・腹部の素体を `P` キーで別オブジェクトに分離退避。 |
| 05 | 00:04:10 | [05_c1_separate_body_hidden_pelvis_and_feet.jpg](./05_c1_separate_body_hidden_pelvis_and_feet.jpg) | **骨盤・お尻・足のメッシュ分離**: ドロワーズ内部の腰部・お尻、靴内部の足を `P` で分離してポリゴン・UV節約。 |
| 06 | 00:06:00 | [06_c1_drawers_solidify_and_inner_cap.jpg](./06_c1_drawers_solidify_and_inner_cap.jpg) | **ドロワーズの厚み付けと内側蓋作成**: 同様に Solidify 適用とお腹の高さでの内側蓋メッシュを作成。 |

---

### Chapter 2: 肌（Body・Hand）のUV展開とシーム設計 (06:35〜09:35)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 07 | 07:35 | [07_c2_body_arm_leg_feet_seam_mark.jpg](./07_c2_body_arm_leg_feet_seam_mark.jpg) | **素体のシーム配置**: 腕の下側ライン、足の内側ライン、足先の表裏境界エッジに `Mark Seam`。 |
| 08 | 08:25 | [08_c2_body_unwrap_checker_check.jpg](./08_c2_body_unwrap_checker_check.jpg) | **肌メッシュの展開とチェッカー確認**: 首・腕・お腹・足先の展開結果とチェッカー歪みの均一性を確認。 |
| 09 | 09:05 | [09_c2_hand_front_back_seam_mark.jpg](./09_c2_hand_front_back_seam_mark.jpg) | **手の表裏シーム分割**: 親指外周から手の甲と手のひらを二分する外側エッジにシームをマーク。 |
| 10 | 09:30 | [10_c2_hand_unwrap_and_seam_fix.jpg](./10_c2_hand_unwrap_and_seam_fix.jpg) | **手の展開とシーム漏れ修正**: 指の間のシーム漏れを修正し、手の甲・手のひらを綺麗に2枚展開。 |

---

### Chapter 3: 服（Dress・Drawers）のUV展開と厚み歪み解消 (09:35〜17:45)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 11 | 10:15 | [11_c3_dress_outer_inner_seam_mark.jpg](./11_c3_dress_outer_inner_seam_mark.jpg) | **ワンピースのシーム配置**: 襟元・裾の内外境界エッジおよび前後の分割エッジにシームをマーク。 |
| 12 | 11:15 | [12_c3_dress_hem_flare_distortion_issue.jpg](./12_c3_dress_hem_flare_distortion_issue.jpg) | **厚み面による裾広がり歪み課題**: そのまま展開すると厚み部分に引っ張られて裾が扇状にブワッと広がる問題を確認。 |
| 13 | 12:10 | [13_c3_dress_outer_face_pin_and_reunwrap.jpg](./13_c3_dress_outer_face_pin_and_reunwrap.jpg) | **【神Tips】表面ピン留め再展開**: 表面のみ選択展開 $\to$ `P` ピン留め $\to$ 厚み面含めて再展開で歪みを完全根絶。 |
| 14 | 13:40 | [14_c3_dress_mirror_u_center_align_sx0.jpg](./14_c3_dress_mirror_u_center_align_sx0.jpg) | **Mirror U 有効化と前面正中線結合**: 2DカーソルX=0.5で前面正中線を `S X 0` 垂直結合し左右非対称柄に対応。 |
| 15 | 14:15 | [15_c3_dress_inner_faces_scale_down_half.jpg](./15_c3_dress_inner_faces_scale_down_half.jpg) | **内側・蓋メッシュの極小化**: 見えない内面・蓋の島を `S 0.5` 以下に縮小しテクセル解像度を節約。 |
| 16 | 15:45 | [16_c3_drawers_pin_and_reunwrap.jpg](./16_c3_drawers_pin_and_reunwrap.jpg) | **ドロワーズのピン留め展開**: 同様に足回りシーム分割後、表面をピン留めして厚み歪みを防ぎつつ展開。 |

---

### Chapter 4: 靴（Shoes）のUV展開とTexTools四角格子化 (17:45〜25:35)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 17 | 18:35 | [17_c4_shoes_sole_straight_unwrap.jpg](./17_c4_shoes_sole_straight_unwrap.jpg) | **靴底の直線短冊展開**: 靴底の上面・底面シーム、かかと中央シームで綺麗な直線状に展開。 |
| 18 | 19:45 | [18_c4_shoes_penguin_wings_seam.jpg](./18_c4_shoes_penguin_wings_seam.jpg) | **装飾パーツの表裏シーム分割**: ペンギン羽やリボン等の装飾パーツを表裏境界エッジで分割展開。 |
| 19 | 20:45 | [19_c4_textools_rectify_curved_straps.jpg](./19_c4_textools_rectify_curved_straps.jpg) | **TexTools Rectify 直角四角化**: 湾曲した靴ストラップを四角格子状に整形しペイント歪みを防止。 |
| 20 | 21:40 | [20_c4_rectify_pin_and_reunwrap_smooth.jpg](./20_c4_rectify_pin_and_reunwrap_smooth.jpg) | **四角化頂点のピン留め再展開**: Rectify した頂点をピン留めし、接続するメッシュを滑らかに追従展開。 |
| 21 | 24:55 | [21_c4_shoes_yellow_line_loopcut_add.jpg](./21_c4_shoes_yellow_line_loopcut_add.jpg) | **ライン描画用サポートループ追加**: 靴の黄色いラインに沿った平行ループカット（`Ctrl + R > E > F`）を追加。 |

---

### Chapter 5: UVグリッドカラー識別シェーダーと最終パズルパッキング (25:35〜33:10)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 22 | 26:40 | [22_c5_uv_grid_color_id_shader_setup.jpg](./22_c5_uv_grid_color_id_shader_setup.jpg) | **【神Tips】UV Grid ＋ RGB Curves 色分け**: マテリアル単位でカラーカーブを色分けし、所属パーツを一目瞭然に可視化。 |
| 23 | 29:10 | [23_c5_body_uv_pack_islands_margin.jpg](./23_c5_body_uv_pack_islands_margin.jpg) | **肌（Body）UVアイランドのパッキング**: 適正マージン（Margin: 0.005〜0.01）で自動パッキング後、手を拡大調整。 |
| 24 | 32:45 | [24_c5_inner_dress_and_shoes_final_layout.jpg](./24_c5_inner_dress_and_shoes_final_layout.jpg) | **インナー服・靴の最終統合パッキング完了**: ワンピース、ドロワーズ、靴を1枚のテクスチャ正方形内に敷き詰め完了。 |
