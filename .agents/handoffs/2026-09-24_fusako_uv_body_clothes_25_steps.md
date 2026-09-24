# 【ふさこ氏 3Dキャラ制作 第25回】体・服・靴のUV展開 完全技術仕様書

本ドキュメントは、YouTubeチュートリアル動画 **『【Blender】体・服・靴のUV展開！【キャラクターモデル制作！#25】』**（講師: ふさこ氏、時間: 33分10秒、URL: `https://www.youtube.com/watch?v=4EvrIHpTA2c`）の内容を、Blender 3.6+ / 4.x に対応した詳細なステップバイステップ技術仕様として完全体系化したものである。

---

## 0. 本技術仕様の全体俯瞰と核心ポイント

### 0.1 本動画で解決する課題
1. **着衣キャラクターの不可視メッシュ最適化と着せ替え対応の分岐**:
   - ワンピースやドロワーズ、靴の内部にある素体メッシュをそのまま残すと、テクスチャ領域が無駄に消費され、ポリゴン描画負荷も増大する。
   - **解決策**:
     - 下からのアオリ視点で絶対に見えない領域（胸・胴体、お尻・骨盤、靴の中の足）を `P` キーで別オブジェクトに分離退避（または削除）。
     - スカートやドロワーズの内部には、下から覗いた時の穴あきを防ぐため「お腹の高さでの内側蓋メッシュ（キャッピング）」を作成。
2. **厚み付け衣服（Solidify）のUV裾広がり歪みの解消（神Tips）**:
   - 厚みモディファイアを適用した布メッシュをそのまま展開すると、裏面・厚み面に引っ張られて裾が扇状にブワッと広がる強烈な歪みが発生する。
   - **解決策**:
     - **表面のみピン留め再展開法**: 厚み・裏面を除外した「外側表面のみ」を選択して `U > Unwrap` $\to$ 綺麗に整った表面頂点を `P` キーでピン留め $\to$ 厚み・裏面を含めて再度 `U > Unwrap`。表面の美しいプロポーションを100%保ったまま、厚み面だけが自然に追従付加される。
     - **不可視面・蓋メッシュの極小化**: 見えない内側・蓋の島は `S 0.5` 以下に縮小し、テクセル解像度を節約。
3. **湾曲パーツ（靴ストラップ・ベルト）のTexTools Rectify直角格子化**:
   - 弧を描く靴のストラップやリボンは、斜めに展開されると直線ラインやステッチを描く際に強烈なジャギー・歪みが生じる。
   - **解決策**: TexTools アドオンの **Rectify**（または手動 `S X 0` / `S Y 0`）で完全な長方形グリッドに整形し、`P` ピン留めして再展開。
4. **【神Tips】UV Grid ＋ RGB Curves によるマテリアル別カラー識別シェーダー**:
   - 全身のUV展開が進むと、3D空間上のどのポリゴンがどのUVテクスチャ（顔、髪、肌、服、靴等）に属しているか混乱が生じる。
   - **解決策**: `Texture Coordinate` $\to$ `Mapping` $\to$ `Image Texture`（2048x2048, UV Grid）の後段に **RGB Curves** を配置。マテリアルごとに R/G/B の出力比率を変更してモデル全体を色分け（顔=赤、髪=緑、肌=ピンク、服=青など）し、アサインミスを一目で視覚検出する。

---

## 1. チャプター別・詳細ステップバイステップ手順

### Chapter 1: 着衣不可視メッシュの分離・削除と服の厚み・蓋モデリング (00:00〜06:35)

#### Step 1-1: インナーワンピースへの Solidify 設定と適用
1. インナーワンピース（服）オブジェクトを選択。
2. **Solidify**（厚み付け）モディファイアを追加。
   - **Thickness**: `0.001 m`（ごく薄い厚み）
   - **Fill Rim**: チェックをOFF（裾の境界面をあらかじめ開けておく）
3. モディファイアスタックで Mirror の上（または下）に配置し、`Ctrl + A` で Apply（適用）。
4. オートミラー（Auto Mirror）を再適用してミラー構造を再構築。
   [📸 参考: 01_c1_dress_solidify_modifier_setup.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/01_c1_dress_solidify_modifier_setup.jpg)

#### Step 1-2: お腹の位置での内側蓋メッシュ作成
1. 内側のメッシュ面を選択し、下から覗いた時に見えないお腹の高さの頂点ループを選択。
2. `F` キーで面を張り、`I`（インセット）後、`M > At Center`（中心でマージ）して少し上方に持ち上げる。
3. これにより、下から見上げても中が黒い空洞にならず、自然にお腹で蓋がされた構造になる。
   [📸 参考: 02_c1_dress_inner_cap_face_inset.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/02_c1_dress_inner_cap_face_inset.jpg)

#### Step 1-3: 裾の内外境界エッジのブリッジ接続
1. 外側の裾エッジループと内側の裾エッジループを `Shift + Alt + Click` で両方選択。
2. 右クリック > **LoopTools > Bridge**（または `Ctrl + E > Bridge Edge Loops`）で面を張り、厚みメッシュを密閉。
   [📸 参考: 03_c1_dress_hem_bridge_edge_loops.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/03_c1_dress_hem_bridge_edge_loops.jpg)

#### Step 1-4: ワンピースに隠れる胸・体幹メッシュの分離退避
1. 素体（Body）オブジェクトの編集モードに入る。
2. ワンピースに完全に覆われて見えない胸部〜腹部のポリゴン面を選択。
3. `P` > **Selection** で別オブジェクトに分離し、バックアップコレクションへ退避。
   [📸 参考: 04_c1_separate_body_hidden_torso_p.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/04_c1_separate_body_hidden_torso_p.jpg)

#### Step 1-5: ドロワーズ内部の骨盤・お尻および靴内部の足の分離退避
1. ドロワーズに隠れる骨盤・お尻の面を選択し、`P` で分離。
2. 靴の内部に入り込む足首・足先の面を選択し、`P` で分離。
3. **効果**: 素体のポリゴン数およびUV面積を劇的に削減。
   [📸 参考: 05_c1_separate_body_hidden_pelvis_and_feet.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/05_c1_separate_body_hidden_pelvis_and_feet.jpg)

#### Step 1-6: ドロワーズへの厚み付けとお腹蓋メッシュ作成
1. ドロワーズオブジェクトに対しても同様に Solidify（Thickness: 0.01m、Fill Rim: OFF）を適用。
2. 内側のお腹の高さで蓋メッシュを作成し、裾エッジを Bridge で接続。
   [📸 参考: 06_c1_drawers_solidify_and_inner_cap.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/06_c1_drawers_solidify_and_inner_cap.jpg)

---

### Chapter 2: 肌（Body・Hand）のUV展開とシーム設計 (06:35〜09:35)

#### Step 2-1: 素体メッシュのシーム配置
1. 残った肌オブジェクト（首・腕・お腹・足先）の編集モードに入る。
2. 腕の下側ライン（目立たない内側）に `Ctrl + E > Mark Seam`。
3. 足の内側ライン（股下からくるぶし）に `Mark Seam`。
4. 足先は甲側と裏側（足裏）を二分するエッジに `Mark Seam`。
   [📸 参考: 07_c2_body_arm_leg_feet_seam_mark.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/07_c2_body_arm_leg_feet_seam_mark.jpg)

#### Step 2-2: 肌メッシュの展開とチェッカー歪み確認
1. 全選択 (`A`) して `U > Unwrap`。
2. 首、腕、足先が綺麗な円筒短冊状に開かれ、チェッカーテクスチャの正方形が均等であることを確認。
   [📸 参考: 08_c2_body_unwrap_checker_check.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/08_c2_body_unwrap_checker_check.jpg)

#### Step 2-3: 手の表裏シーム分割
1. 手オブジェクトの編集モードに入る。
2. 親指の外周から側面を通り、手の甲（背面）と手のひら（前面）を二分する外周エッジに `Mark Seam`。
   [📸 参考: 09_c2_hand_front_back_seam_mark.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/09_c2_hand_front_back_seam_mark.jpg)

#### Step 2-4: 手の展開とシーム漏れの修正
1. `U > Unwrap` を実行。指の間にシーム漏れがないか確認し、手の甲と手のひらが綺麗に2枚の板として展開されることを確認。
   [📸 参考: 10_c2_hand_unwrap_and_seam_fix.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/10_c2_hand_unwrap_and_seam_fix.jpg)

---

### Chapter 3: 服（Dress・Drawers）のUV展開と厚み歪み解消 (09:35〜17:45)

#### Step 3-1: ワンピースのシーム配置
1. ワンピースの襟元・裾の内外境界エッジに `Mark Seam`。
2. 体の側面（脇下から裾へ下るライン）にシームを入れ、前後2大ブロックに分割。
   [📸 参考: 11_c3_dress_outer_inner_seam_mark.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/11_c3_dress_outer_inner_seam_mark.jpg)

#### Step 3-2: 厚み面による裾広がり歪み課題の確認
1. そのまま `U > Unwrap` すると、内側の厚みメッシュに引っ張られて裾が扇状にブワッと広がり、テクスチャが激しく歪む現象を確認。
   [📸 参考: 12_c3_dress_hem_flare_distortion_issue.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/12_c3_dress_hem_flare_distortion_issue.jpg)

#### Step 3-3: 【極意】表面ピン留め再展開法
1. 厚み面や内側を含めて選択後、`Ctrl + テンキー -`（選択縮小）を数回行い、厚みを除いた「純粋な表面のみ」を選択。
2. `U > Unwrap` で表面だけを展開（裾が広がらず綺麗な縦長プロポーションが得られる）。
3. UVエディタでこの表面頂点を全選択し、`P` キーでピン留め（赤色固定）。
4. `Ctrl + L` で厚み面を含めた全メッシュを選択し、再度 `U > Unwrap`。
5. **結果**: 固定された表面の完璧なプロポーションを維持したまま、厚み面だけが自然に周囲へ展開される。
   [📸 参考: 13_c3_dress_outer_face_pin_and_reunwrap.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/13_c3_dress_outer_face_pin_and_reunwrap.jpg)

#### Step 3-4: Mirror U 有効化と前面正中線の結合 (`S X 0`)
1. ミラーモディファイアの **Mirror U** にチェック。
2. 2Dカーソルの Location X を `0.5` に設定。
3. 前面正中線の頂点を `S X 0` で 2Dカーソル（中央）に垂直結合。
   [📸 参考: 14_c3_dress_mirror_u_center_align_sx0.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/14_c3_dress_mirror_u_center_align_sx0.jpg)

#### Step 3-5: 内側・蓋メッシュの極小化 (`S 0.5`)
1. 襟元の内面、裾の内面、お腹の蓋メッシュを選択。
2. `S` > `0.5`（または `0.3`）で極小サイズに縮小し、UV領域の端へ配置。
   [📸 参考: 15_c3_dress_inner_faces_scale_down_half.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/15_c3_dress_inner_faces_scale_down_half.jpg)

#### Step 3-6: ドロワーズの足回りシーム分割と表面ピン留め展開
1. ドロワーズの内股ラインおよび足回り境界にシームをマーク。
2. 同様に表面をピン留めしてから厚み面を含めて再展開し、歪みのない綺麗な島を作成。
   [📸 参考: 16_c3_drawers_pin_and_reunwrap.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/16_c3_drawers_pin_and_reunwrap.jpg)

---

### Chapter 4: 靴（Shoes）のUV展開とTexTools四角格子化 (17:45〜25:35)

#### Step 4-1: 靴底の直線短冊展開
1. 靴底の上面エッジ、底面エッジ、およびかかとの中央1ラインにシームをマーク。
2. `U > Unwrap` で完全な直線短冊状に展開。
   [📸 参考: 17_c4_shoes_sole_straight_unwrap.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/17_c4_shoes_sole_straight_unwrap.jpg)

#### Step 4-2: ペンギン羽・リボン装飾の表裏シーム分割
1. 靴に付いているペンギン羽やリボン、ポンポン装飾の表裏境界にシームをマークして展開。
   [📸 参考: 18_c4_shoes_penguin_wings_seam.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/18_c4_shoes_penguin_wings_seam.jpg)

#### Step 4-3: 湾曲ストラップの TexTools Rectify 直角四角化
1. 湾曲した靴ストラップや甲バンドのメッシュを選択。
2. TexTools > **Rectify**（または手動 `S X 0` / `S Y 0`）で完全な長方形グリッドに直角化。
   [📸 参考: 19_c4_textools_rectify_curved_straps.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/19_c4_textools_rectify_curved_straps.jpg)

#### Step 4-4: 四角化頂点のピン留め再展開
1. 四角化した頂点を `P` でピン留めし、接続するメッシュを含めて再展開。歪みのない整然としたUV島を形成。
   [📸 参考: 20_c4_rectify_pin_and_reunwrap_smooth.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/20_c4_rectify_pin_and_reunwrap_smooth.jpg)

#### Step 4-5: 靴のライン描画用サポートループ追加
1. 靴の表面に黄色いラインテクスチャを描くため、`Ctrl + R` でループカットを追加。
2. `E` ＋ `F` で輪郭に平行なループにスナップさせ、シームを追加してUV上でも独立した帯として分離。
   [📸 参考: 21_c4_shoes_yellow_line_loopcut_add.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/21_c4_shoes_yellow_line_loopcut_add.jpg)

---

### Chapter 5: UVグリッドカラー識別シェーダーと最終パズルパッキング (25:35〜33:10)

#### Step 5-1: 【神技】マテリアル別カラー識別シェーダー構築
1. シェーダーエディタで `Texture Coordinate`（UV） $\to$ `Mapping` $\to$ `Image Texture`（2048x2048、Generated Type: **UV Grid**）を接続。
2. テクスチャの直後に **Color > RGB Curves** ノードを挿入。
3. マテリアルごとにカーブを色分け：
   - **Face（顔）**: Rカーブを上げて「赤色グリッド」
   - **Hair（髪）**: Gカーブを上げて「緑色グリッド」
   - **Skin（肌）**: RとBを上げて「ピンク色グリッド」
   - **Inner（服）**: Bカーブを上げて「青色グリッド」
4. 3Dビュー上でモデル全体を見渡し、マテリアルの割り当てミス（手のマテリアルが服になっている等）を一発で視覚検出。
   [📸 参考: 22_c5_uv_grid_color_id_shader_setup.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/22_c5_uv_grid_color_id_shader_setup.jpg)

#### Step 5-2: 肌（Body）UVアイランドのパッキング
1. 肌オブジェクトのUVを選択し、`UV > Average Islands Scale` で均一化。
2. `UV > Pack Islands`（Margin: `0.005`〜`0.01`）で自動配置後、描き込み密度の高い「手」の島を手動で少し拡大。
   [📸 参考: 23_c5_body_uv_pack_islands_margin.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/23_c5_body_uv_pack_islands_margin.jpg)

#### Step 5-3: インナー服・靴の最終統合パッキング完了
1. ワンピース、ドロワーズ、靴の全島を選択。
2. 表側の主要パーツを等倍で配置し、裏地・内側・蓋メッシュを隙間に小さくパズル配置。
3. 1枚の正方形テクスチャ（Inner 1枚）に美しく敷き詰め完了。
   [📸 参考: 24_c5_inner_dress_and_shoes_final_layout.jpg](../../docs/fusako_25_uv_body_clothes_screenshots/24_c5_inner_dress_and_shoes_final_layout.jpg)

---

## 2. 実装チェックリスト（トラブルシューティング）

| 現象 | 主な原因 | 確実な解決策 |
| :--- | :--- | :--- |
| 厚みのある服を展開すると裾が扇状にブワッと広がる | 厚み・裏面メッシュの歪み計算に引っ張られている | 表面のみ選択展開 $\to$ `P` ピン留め $\to$ 厚み面含めて再展開する。 |
| 靴のストラップに直線を描くと波打ってジャギーになる | ストラップが曲がったまま斜めに展開されている | TexTools の **Rectify** で長方形グリッドに直角化してからペイントする。 |
| どのパーツがどのテクスチャか3D上で分からなくなる | チェッカーテクスチャが全パーツ同じ白黒になっている | **UV Grid ＋ RGB Curves** でマテリアルごとに赤・緑・青・ピンクに色分けする。 |
| 下から覗いた時に服の中が空洞で突き抜けて見える | 不可視面を削除しすぎて中身が抜けている | お腹の高さで内側ループに面張り（`F`）して蓋メッシュを作成しておく。 |
| テクスチャの境界線で隣のパーツの色がにじむ | パッキング時のアイランドマージンが近すぎる | `Pack Islands` の Margin を `0.005`〜`0.01` に設定し適正な余白を確保する。 |
