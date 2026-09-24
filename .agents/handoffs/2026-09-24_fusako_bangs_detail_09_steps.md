# ふさこ式 3Dキャラモデリング手順書 09【前髪＆横髪の作り込み・板ポリ透過＆裏面張り立体化編】

本ドキュメントは、3Dモデラー・ふさこ氏のYouTubeチュートリアル動画：
**『Blenderでキャラクターモデル制作！09 | 前髪の作り込み 〜初級から中級者向けチュートリアル〜』**
（動画URL: https://www.youtube.com/watch?v=ZOSArnNsbrY / 収録時間: 39分08秒）
の全工程を、トポロジー構造・ショートカットキー・解剖学的＆アニメ的デフォルメの黄金律・ゲームエンジン（Unity/VRM）最適化規約に沿って完全体系化した実践仕様書です。

各手順の直下に、高解像度スクリーンショット集（`docs/fusako_09_bangs_detail_screenshots/`）への相対リンクを配置しています。

---

## 📑 目次

1. [全体の前提知識と使用ツール・アドオン](#1-全体の前提知識と使用ツールアドオン)
2. [第1章: 前髪大ラフのSubsurf確定適用とメッシュ整地](#第1章-前髪大ラフのsubsurf確定適用とメッシュ整地)
3. [第2章: 前髪の毛束切り裂き（Rip）と左右非対称化](#第2章-前髪の毛束切り裂きripと左右非対称化)
4. [第3章: EdgeFlowによる流線平滑化と「板ポリ前髪」の重要性](#第3章-edgeflowによる流線平滑化と板ポリ前髪の重要性)
5. [第4章: 重なり毛束の追加とノンマニホールド（T字ポリゴン）エラー回避](#第4章-重なり毛束の追加とノンマニホールドt字ポリゴンエラー回避)
6. [第5章: 横髪（サイドヘア）のハイディテール化と裏面張り立体化](#第5章-横髪サイドヘアのハイディテール化と裏面張り立体化)
7. [第6章: シェーディング最適化とメッシュエラー総点検](#第6章-シェーディング最適化とメッシュエラー総点検)
8. [第9話の成果と次工程への展望](#第9話の成果と次工程への展望)

---

## 1. 全体の前提知識と使用ツール・アドオン

- **前工程のベースモデル**: 第3話『髪の作り方 大ラフ編』で作成した、平面（Plane）＋Subdivision Surface（レベル2）ベースの「前髪」および「横髪」オブジェクト。
- **使用アドオン**:
  - `Edge Flow`: 選択エッジループを周囲の曲面に沿った滑らかなフローに一発補正する必須アドオン（無料）。
  - `LoopTools`: 円形化・リラックス（均等分散）用。
  - `Check Tool Box (Mesh Detection)`: T字ポリゴン（ノンマニホールド）や多角形（N-gon）を自動検出する検品アドオン。
  - `AutoMirror` / `Mirror Modifier`: 左右対称作業の基盤。
- **推奨ショートカット割り当て（著者の実務セッティング）**:
  - `Ctrl + W`: 細分化（Subdivide）
  - `Shift + F`: Edge Flow の `Set Flow`（曲率自動平滑化）

---

## 第1章: 前髪大ラフのSubsurf確定適用とメッシュ整地

### 1-1. 形状の最終確認とバックアップ退避
- 前髪大ラフ（第3話で作成したローポリケージ＋Subsurf）のシルエットが下絵に合致しているかを最終点検する。
- 編集モードに入る前に、オブジェクトモードで `Shift + D` $\to$ `Esc` で前髪オブジェクトを複製し、`M` キーで「Backup」コレクションへ退避させておく。
  - [📸 参考: 01_c1_hair_rough_before_subsurf.jpg](../../docs/fusako_09_bangs_detail_screenshots/01_c1_hair_rough_before_subsurf.jpg)

### 1-2. Subsurfの確定適用（Ctrl + A）とクリース初期化
- 前髪オブジェクトを選択し、モディファイアスタックの Subdivision Surface の上で `Ctrl + A`（確定適用）を押す。
  - [📸 参考: 02_c1_backup_and_apply_subsurf.jpg](../../docs/fusako_09_bangs_detail_screenshots/02_c1_backup_and_apply_subsurf.jpg)
- これにより滑らかなハイポリゴンケージ（実メッシュ）に変換される。
- **エッジクリースの初期化**:
  - 編集モード（`Tab`）に入り、全選択（`A`）。
  - `N` キーでサイドバーを開き、`Item > Edge Data > Mean Crease` を `0.0` に設定する。大ラフ時のクリースが残っていると、今後の変形で不要な折り目がついてしまうため完全にリセットする。
  - [📸 参考: 03_c1_reset_crease_to_zero.jpg](../../docs/fusako_09_bangs_detail_screenshots/03_c1_reset_crease_to_zero.jpg)

### 1-3. エッジリング選択と細分化（Subdivide）
- 毛束を追加したい箇所の縦エッジを `Ctrl + 左クリック` でリング選択（または最短パス選択）する。
- 右クリック $\to$ `Subdivide`（細分化）を実行し、滑らかさを損なわずに縦ループを1本追加する。
  - [📸 参考: 04_c1_ctrl_click_ring_subdivide.jpg](../../docs/fusako_09_bangs_detail_screenshots/04_c1_ctrl_click_ring_subdivide.jpg)

---

## 第2章: 前髪の毛束切り裂き（Rip）と左右非対称化

### 2-1. Vキー切り裂き（Rip）による独立毛束の分離
- 細い毛束に分岐させたいエッジを選択し、`V` キー（切り裂き / Rip）を押す。
- 即座に `X` キーを押して横方向にわずかにスライドさせ、隣接メッシュと切り離された独立毛束を形成する。
  - [📸 参考: 05_c1_rip_v_key_separate_bundle.jpg](../../docs/fusako_09_bangs_detail_screenshots/05_c1_rip_v_key_separate_bundle.jpg)

### 2-2. Xミラー編集のオフ（左右非対称化）
- 手前のメイン前髪はキャラクターデザイン上、左右非対称（片側への流し髪）となっている。
- 3Dビューポート右上の `X`（メッシュ対称編集）をオフにし、片側のみの変形・調整モードに切り替える。
  - [📸 参考: 06_c1_turn_off_x_mirror_asymmetry.jpg](../../docs/fusako_09_bangs_detail_screenshots/06_c1_turn_off_x_mirror_asymmetry.jpg)

### 2-3. プロポーショナル編集を用いた毛束の流線調整
- `O` キーでプロポーショナル編集を有効化（フォールオフ: スムーズ）。
- マウスホイールで影響範囲を調整しながら、`G` キーで毛束を外側へ引き出し、自然なS字カーブを描かせる。
  - [📸 参考: 07_c1_proportional_edit_bundle_curve.jpg](../../docs/fusako_09_bangs_detail_screenshots/07_c1_proportional_edit_bundle_curve.jpg)

### 2-4. 毛先の二股割れ（Split）の成形
- 毛先の先端部分で細かな枝毛（二股の割れ目）を作る。
- 毛先付近のエッジを細分化（Subdivide）し、先端頂点を `V` キーで切り離して左右に広げる。
  - [📸 参考: 08_c1_tip_split_subdivide.jpg](../../docs/fusako_09_bangs_detail_screenshots/08_c1_tip_split_subdivide.jpg)

---

## 第3章: EdgeFlowによる流線平滑化と「板ポリ前髪」の重要性

### 3-1. EdgeFlow（Set Flow）による曲率自動平滑化
- 毛束を切り裂いたりループカットを追加したりすると、エッジが直線的に角張ってしまう。
- 修正したいエッジループを選択し、右クリック $\to$ `Set Flow`（アドオン `Edge Flow`）を実行。
- 周囲の曲率（曲がり具合）を自動計算し、滑らかで自然なカーブへと一発補正する。
  - [📸 参考: 09_c1_edgeflow_set_flow_addon.jpg](../../docs/fusako_09_bangs_detail_screenshots/09_c1_edgeflow_set_flow_addon.jpg)

### 3-2. Jキー頂点接続による四角面トポロジー化
- ループ追加や切り裂きによって生じた5角形以上の多角面（N-gon）を解消する。
- 分割したい2頂点を選択し、`J` キー（頂点のパスを連結 / Connect Vertex Path）を押してエッジを走らせ、全て綺麗な四角面（Quad）に整流する。
  - [📸 参考: 10_c1_j_key_vertex_connect_quads.jpg](../../docs/fusako_09_bangs_detail_screenshots/10_c1_j_key_vertex_connect_quads.jpg)

### 3-3. Unity/VRM向け「板ポリ前髪」の重要性（眉毛透過表現）
- **なぜ前髪に厚みをつけないのか？（業界黄金律）**:
  - アニメ調モデルをUnity（VRM/UniVRM）に持ち込み、MToonシェーダーの「眉毛透過（前髪の上から眉毛を描画するセルアニメ演出）」を設定する際、前髪に厚み（Solidify等）があると、前髪の側面や裏面メッシュが変に遮蔽・屈折して不自然なフチ線や描画破綻が発生する。
  - そのため、**正面から見える前髪部分はあえてペラペラの「板ポリゴン（厚みゼロ）」のまま仕上げる** のがプロの実務標準である。
  - [📸 参考: 11_c1_shade_smooth_flat_bangs.jpg](../../docs/fusako_09_bangs_detail_screenshots/11_c1_shade_smooth_flat_bangs.jpg)

---

## 第4章: 重なり毛束の追加とノンマニホールド（T字ポリゴン）エラー回避

### 4-1. 既存面の複製（Shift + D）と法線浮かせ（Alt + S）
- ベース前髪の上に重なる、少し太めのアクセント毛束を作成する。
- 重ねたい位置の面を選択し、`Shift + D` で複製。
- `Alt + S`（法線方向に収縮/膨張）を使い、ベース前髪の手前側にわずかに浮かせて配置する。
  - [📸 参考: 12_c1_overlapping_bundle_duplicate.jpg](../../docs/fusako_09_bangs_detail_screenshots/12_c1_overlapping_bundle_duplicate.jpg)
  - [📸 参考: 13_c1_alt_s_offset_floating_bundle.jpg](../../docs/fusako_09_bangs_detail_screenshots/13_c1_alt_s_offset_floating_bundle.jpg)

### 4-2. 【超重要】T字ポリゴン（ノンマニホールド）の危険性と回避技法
- **T字ポリゴンとは**:
  - 1つの辺（エッジ）から「3面以上」のポリゴンが接続されている状態（Non-Manifold 幾何エラー）。
  - これが存在すると、Subdivision Surfaceの適用、UV展開、法線ベイク、ゲームエンジンエクスポートで重大な黒ずみや描画クラッシュを引き起こす。
  - [📸 参考: 14_c1_t_junction_non_manifold_warning.jpg](../../docs/fusako_09_bangs_detail_screenshots/14_c1_t_junction_non_manifold_warning.jpg)
- **ふさこ式・T字エラー回避テクニック**:
  1. 重なり毛束をベースメッシュに直接溶接（Merge）せず、接続部のエッジを `V` キーで切り離してメッシュに「穴」を開ける。
  2. 穴の周囲の3頂点を選択し、`J` キーまたは `M`（Merge）で繋ぎ、四角面または三角面として閉じる。
  3. これにより、すべてのエッジが「最大2面」で共有される正常なマニホールド構造が維持される。
  - [📸 参考: 15_c1_rip_and_hole_resolution.jpg](../../docs/fusako_09_bangs_detail_screenshots/15_c1_rip_and_hole_resolution.jpg)

### 4-3. アクティブ要素ピボットによる毛先のすぼめ成形
- ピボットポイントを「アクティブ要素（Active Element）」に切り替える。
- 毛先の頂点を最後に選択（白くハイライト）した状態で `S` キーを押して縮小し、先端に向かって綺麗に尖るテーパー形状を作る。
  - [📸 参考: 16_c1_active_element_tip_taper.jpg](../../docs/fusako_09_bangs_detail_screenshots/16_c1_active_element_tip_taper.jpg)

### 4-4. 頂点スナップによる隙間埋め
- センター前髪とサイド髪の間に隙間が空いていると、カメラを動かした際におでこが不自然に露出する。
- `Shift + Tab` でスナップをON（スナップ先: 頂点）にし、境界の頂点を隣接パーツの頂点にスナップ吸着させて隙間を完全に塞ぐ。
  - [📸 参考: 17_c1_vertex_snapping_close_gap.jpg](../../docs/fusako_09_bangs_detail_screenshots/17_c1_vertex_snapping_close_gap.jpg)

---

## 第5章: 横髪（サイドヘア）のハイディテール化と裏面張り立体化

### 5-1. 横髪ベースパーツの配置とSubsurf適用
- 頬のラインに沿った横髪大ラフ（水色パーツ）を選択。
- 下端の不要面を整理し、`Shift + D` でバックアップ退避後、Subsurfを `Ctrl + A` で確定適用する。
  - [📸 参考: 18_c2_side_hair_base_plane.jpg](../../docs/fusako_09_bangs_detail_screenshots/18_c2_side_hair_base_plane.jpg)
  - [📸 参考: 19_c2_side_hair_apply_subsurf.jpg](../../docs/fusako_09_bangs_detail_screenshots/19_c2_side_hair_apply_subsurf.jpg)

### 5-2. 側頭毛束のすぼめ成形＆Set Flow整流
- 側頭部に沿って伸びる長い毛束を `V` キーで切り離し、先端を `S` キーで細く絞る。
- ループカット（`Ctrl + R`）を追加し、`Set Flow`（Shift + F）をかけて滑らかな流線に整える。
  - [📸 参考: 20_c2_side_bundle_taper_and_set_flow.jpg](../../docs/fusako_09_bangs_detail_screenshots/20_c2_side_bundle_taper_and_set_flow.jpg)

### 5-3. カール毛束の押し出し・カーブ成形
- 横髪の途中から外側にピョンと跳ねる「カール毛束」を作成する。
- 該当するエッジを選択し、`E` キーで押し出し $\to$ `R` キーで回転させながら跳ねるカーブを成形する。
  - [📸 参考: 21_c2_curl_hair_extrude.jpg](../../docs/fusako_09_bangs_detail_screenshots/21_c2_curl_hair_extrude.jpg)

### 5-4. 【神技】裏面張りによる三角形断面立体化（断面おにぎり化）
- **前髪と横髪の違い**:
  - 前髪は正面からしか見えないため板ポリで良いが、横髪は斜め・真横・後ろから見られるため、板ポリのままだとペラペラで裏側がスカスカに見えてしまう。
- **裏面張り立体化の手順**:
  1. 横髪の表面メッシュの中央に、細分化（Subdivide）で縦ループを追加。
  2. 中央ループを選択し、`Alt + S` で**内側（頭部側）へ向けてグイッと膨らませる**。
  3. これにより、正面の平坦面に対して裏側が三角形の山（頂点）になる「三角形（おにぎり型）断面」の骨格ができる。
  - [📸 参考: 22_c2_triangular_cross_section_alt_s.jpg](../../docs/fusako_09_bangs_detail_screenshots/22_c2_triangular_cross_section_alt_s.jpg)

### 5-5. 面の向き（Face Orientation）確認とFキーによる裏面密閉
- ビューポートオーバーレイから `Face Orientation`（面の向き）をONにする。表面が青色、裏面が赤色で表示される。
- 膨らませた稜線と両端エッジの「4辺」を選択し、`F` キーを押して裏面を四角面で順次塞いでいく（密閉ソリッド化）。
- 面の法線が反転して赤くなった場合は、`Alt + N` $\to$ `Recalculate Outside`（面の向きを外側に揃える）を実行。
  - [📸 参考: 23_c2_face_orientation_and_f_key_filling.jpg](../../docs/fusako_09_bangs_detail_screenshots/23_c2_face_orientation_and_f_key_filling.jpg)

### 5-6. 後頭部・側頭部のスカスカ解消
- 斜め後ろから見た時に頭部と横髪の間に大きな隙間が空いている箇所を塞ぐ。
- 横髪の後部エッジループを選択し、`Ctrl + R` でループを追加した上で `Alt + S` で頭皮側に膨らませ、頭の丸みにフィットさせる。
- 歪みが出たループは `LoopTools > Relax` で滑らかに均等化する。
  - [📸 参考: 24_c2_fill_gap_behind_head_alt_s.jpg](../../docs/fusako_09_bangs_detail_screenshots/24_c2_fill_gap_behind_head_alt_s.jpg)

---

## 第6章: シェーディング最適化とメッシュエラー総点検

### 6-1. Shade Auto Smooth と Mark Sharp によるメリハリ
- 裏面に面を張って立体化したことで、稜線部分が黒ずんだりぼやけたりする問題が発生する。
- **解決策**:
  1. オブジェクト右クリック $\to$ `Shade Auto Smooth`（自動スムーズ）を適用し、角度（Angle）を広げる（35°〜45°程度）。急激に角度が変わる稜線だけがパキッとした陰影になる。
  2. 特にエッジを際立たせたい稜線エッジを選択し、`Ctrl + E` $\to$ `Mark Sharp`（シャープをマーク）を付与（シアン色で表示）。
  - [📸 参考: 25_c2_shade_auto_smooth_and_mark_sharp.jpg](../../docs/fusako_09_bangs_detail_screenshots/25_c2_shade_auto_smooth_and_mark_sharp.jpg)

### 6-2. Check Tool Box による Non-Manifold / N-gon 検出と修正
- アドオン `Check Tool Box (Mesh Detection)` を起動。
- `Display` / `Refresh` を押し、`Select Non-Manifold` を実行。
  - T字ポリゴン等の致命的エラーが存在する場合は自動で頂点が選択されるため、手動で溶解（Dissolve）または切り離しで修正する。
- `Select N-Gons (5角形以上)` を実行し、多角面を検出して `J` キーで四角面/三角面に分割。
  - [📸 参考: 26_c2_check_toolbox_non_manifold_detection.jpg](../../docs/fusako_09_bangs_detail_screenshots/26_c2_check_toolbox_non_manifold_detection.jpg)

---

## 第9話の成果と次工程への展望

- **完成した部位**:
  - **前髪**: 左右非対称の流線型・二股毛先・眉毛透過用板ポリゴン仕様。
  - **横髪**: くるんと跳ねるカール毛束・裏面張りによる肉厚な三角形断面・頭皮密着トポロジー。
  - **エラーゼロ**: ノンマニホールド・多角形なしの完全クリーンメッシュ。
- **次回（第10話）への展望**:
  - 後ろ髪（ロングヘア / ツインテール / お団子）の作り込みと結び目・髪飾りアクセサリーのモデリングへと進みます。
