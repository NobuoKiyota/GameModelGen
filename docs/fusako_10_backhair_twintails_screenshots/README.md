# ふさこ氏チュートリアル第10話 重要シーン・スクリーンショットカタログ
## 『後ろ髪とツインテールの作り込み 〜初級から中級者向けチュートリアル〜』

本ディレクトリは、ふさこ氏によるBlenderキャラクターモデリング講座第10話（[YouTube動画リンク](https://www.youtube.com/watch?v=3db96pczrPs)）から、後ろ髪の肉厚化（Alt+S）・外側頂点ロック（Hide Only Vertex）・LoopTools Relax・毛束切り裂き（Vキー）・AutoMirror再対称化・ツインテールの二層立体化・三角形断面裏面張り・アノテーションとナイフによる結び目成形・生え際肌見え防止などの決定的シーン（全26枚）を高解像度で抽出・整理した画像リファレンス集です。

詳細な操作手順やトポロジー設計の解説は、以下の仕様書を参照してください：
- 📘 **詳細手順・トポロジー仕様書**: [`../../.agents/handoffs/2026-09-24_fusako_backhair_twintails_10_steps.md`](../../.agents/handoffs/2026-09-24_fusako_backhair_twintails_10_steps.md)

---

### 📸 スクリーンショット一覧（全26枚）

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー） | 主な内容・重要操作・トポロジーのポイント |
|:---:|:---:|:---|:---|
| 01 | 00:00:25 | [./01_c1_back_hair_alt_s_extrude.jpg](./01_c1_back_hair_alt_s_extrude.jpg) | **法線内側への厚み出し**: 全選択から `E` $\to$ `Esc` $\to$ `Alt + S` で法線方向に内側へ縮小し、後頭部を覆う均一な肉厚シェルを生成。 |
| 02 | 00:00:50 | [./02_c1_mark_seam_outer_shell.jpg](./02_c1_mark_seam_outer_shell.jpg) | **外側シェルのシーム分離**: 外側の境界エッジに `Ctrl + E` $\to$ `Mark Seam`（シームをマーク）を付与し、面選択で外側のみを一発選択可能にする。 |
| 03 | 00:01:05 | [./03_c1_hide_only_vertex_lock.jpg](./03_c1_hide_only_vertex_lock.jpg) | **Hide Only Vertexによる頂点ロック**: 外側面を選択した状態で `Shift + Ctrl + H` を押し、外側シェルを編集不可にロック（非表示にせず固定）。 |
| 04 | 00:01:40 | [./04_c1_proportional_inner_fit.jpg](./04_c1_proportional_inner_fit.jpg) | **内側頂点の頭部フィッティング**: 外側をロックしたまま、内側頂点のみを `Alt + S` やプロポーショナル編集で後頭部に合わせて安全に拡大変形。 |
| 05 | 00:02:20 | [./05_c1_looptools_relax_smoothing.jpg](./05_c1_looptools_relax_smoothing.jpg) | **LoopTools Relaxによる平滑化**: `Alt + S` で歪んだエッジループを `LoopTools > Relax`（著者は `Shift + Y`）で滑らかに均等化。 |
| 06 | 00:03:05 | [./06_c1_delete_inner_unseen_faces.jpg](./06_c1_delete_inner_unseen_faces.jpg) | **見えない内側不要面の削除**: 頭皮に埋まりカメラから絶対に見えない内側上部面を選択し、`X` $\to$ `Faces` で削除して軽量化。 |
| 07 | 00:03:45 | [./07_c1_recalculate_outside_normals.jpg](./07_c1_recalculate_outside_normals.jpg) | **法線の外側再計算**: 裏面押し出しで反転した法線を、全選択して `Shift + N`（面の向きを外側に揃える）で正常化。 |
| 08 | 00:04:15 | [./08_c1_rip_v_key_bundle_split.jpg](./08_c1_rip_v_key_bundle_split.jpg) | **Vキー切り裂きによる毛束分割**: 後ろ髪の境界エッジを `V` キーで切り裂き、`F` キーで穴を塞いで独立した毛束を成形。 |
| 09 | 00:05:00 | [./09_c1_shift_v_vertex_slide.jpg](./09_c1_shift_v_vertex_slide.jpg) | **Shift+Vによる頂点スライド**: 面が張られていないオープン境界の頂点を、`Shift + V`（頂点スライド）でエッジに沿って綺麗に移動。 |
| 10 | 00:05:40 | [./10_c1_crease_curl_tip.jpg](./10_c1_crease_curl_tip.jpg) | **Shift+Eクリースによる毛先引き締め**: カール毛束の先端エッジに `Shift + E` でクリースを付与し、Subsurf下でも鋭く尖った毛先を維持。 |
| 11 | 00:08:45 | [./11_c1_automirror_split_and_mirror.jpg](./11_c1_automirror_split_and_mirror.jpg) | **Subsurf適用後のAutoMirror再設定**: Subsurf確定適用後、中央の歪みを防ぐため `AutoMirror` アドオンで半分カットしてMirrorモディファイアを再追加。 |
| 12 | 00:10:45 | [./12_c1_planar_sides_alt_s_soften.jpg](./12_c1_planar_sides_alt_s_soften.jpg) | **平面的側頭部のふっくら丸み補正**: クリース等で直線的・平面的になってしまった側頭部ループを選択し、`Alt + S` で丸みを復元。 |
| 13 | 00:15:35 | [./13_c1_nape_hair_extrude_down.jpg](./13_c1_nape_hair_extrude_down.jpg) | **襟足毛束の押し出し＆引き下げ**: 襟足（首の後ろ）のラインを選択し、`E + Y` で前へ押し出し $\to$ `G + Z` で下へ引き下げて自然な襟足を形成。 |
| 14 | 00:17:15 | [./14_c1_nape_bundle_smoothing.jpg](./14_c1_nape_bundle_smoothing.jpg) | **襟足毛束の滑らか整流**: 襟足毛束の先端をマージ（M）してまとめ、`Alt + S` で急激なエッジの黒ずみを解消。 |
| 15 | 00:21:10 | [./15_c2_twintail_proportional_curve.jpg](./15_c2_twintail_proportional_curve.jpg) | **ツインテールのプロポーショナルS字カーブ**: ツインテール大ラフを選択し、プロポーショナル編集で豊かに広がる美しいS字カーブを成形。 |
| 16 | 00:22:15 | [./16_c2_overlapping_bundle_rotation.jpg](./16_c2_overlapping_bundle_rotation.jpg) | **重なり毛束の複製＆巻きつき立体配置**: 大毛束の面を `Shift + D` で複製し、`Alt + S` で浮かせつつ `R` キーで回転させて本体に巻きつく螺旋立体感を形成。 |
| 17 | 00:23:40 | [./17_c2_center_loop_alt_s_bulge.jpg](./17_c2_center_loop_alt_s_bulge.jpg) | **重なり小毛束の中央膨らみ**: 小毛束の中央にループを追加し、`Alt + S` でふっくらと丸みを帯びた断面を作成。 |
| 18 | 00:25:10 | [./18_c2_apply_subsurf_twintail.jpg](./18_c2_apply_subsurf_twintail.jpg) | **ツインテールのSubsurf確定適用**: バックアップ退避後、Subsurfを確定適用してハイポリゴンメッシュ化。 |
| 19 | 00:26:20 | [./19_c2_resolve_overlapping_faces.jpg](./19_c2_resolve_overlapping_faces.jpg) | **重なり毛束の頂点整流と三角面マージ**: 重なり毛束と本体の交差部分の不要エッジを溶解（Dissolve）し、先端を三角面で綺麗にマージ。 |
| 20 | 00:28:40 | [./20_c2_triangular_back_faces_f_key.jpg](./20_c2_triangular_back_faces_f_key.jpg) | **三角形断面化のための裏面Fキー張り**: ツインテールの裏側中央ループを内側に膨らませた状態で、4辺を選択して `F` キーで裏面を順次密閉張り。 |
| 21 | 00:29:30 | [./21_c2_shade_auto_smooth_check.jpg](./21_c2_shade_auto_smooth_check.jpg) | **ツインテールのShade Auto Smooth確認**: 自動スムーズを適用し、突き抜けや破綻がないか360度ビューで検品。 |
| 22 | 00:34:05 | [./22_c3_annotate_hair_tie_guide.jpg](./22_c3_annotate_hair_tie_guide.jpg) | **アノテーション（サーフェスペン）下書き**: Tパネルのアノテーション（Surface配置）を使い、ツインテール根元の結び目（シュシュ・ヘアゴム）のしわ・流れを下書き。 |
| 23 | 00:34:40 | [./23_c3_knife_cut_and_inset.jpg](./23_c3_knife_cut_and_inset.jpg) | **ナイフカット＆インセット成形**: `K` キーで下書きに沿ってナイフカットを入れ、選択面を `I` キーでインセット $\to$ `Alt + S` で隆起させて結び目を立体化。 |
| 24 | 00:35:10 | [./24_c3_mark_sharp_hair_tie.jpg](./24_c3_mark_sharp_hair_tie.jpg) | **結び目エッジのMark Sharp**: 結び目の境界エッジに `Mark Sharp`（Ctrl+E）を付与し、ゴムでギュッと縛られたシャープな陰影を演出。 |
| 25 | 00:36:15 | [./25_c3_face_snap_hairline_extrude.jpg](./25_c3_face_snap_hairline_extrude.jpg) | **生え際（もみあげ）の肌露出防止面スナップ**: もみあげ・生え際から頭皮が露出するのを防ぐため、後ろ髪境界を `E` 押し出しし、頭皮の面にスナップ吸着させて密着。 |
| 26 | 00:39:45 | [./26_c3_complete_hair_preview.jpg](./26_c3_complete_hair_preview.jpg) | **後ろ髪＆ツインテール完成プレビュー**: 前髪・横髪・後ろ髪・ツインテール・結び目が全方位美しく組み合わさった完全なヘアスタイルの完成。 |

---

### 💡 画像プレビューのコツ
各行のリンク `[./画像名.jpg](./画像名.jpg)` をクリックすると、Blender / VS Code / 各種Markdownビューア上で即座に高解像度画像が展開されます。
モデリング作業中、該当するトポロジーや操作UIの確認に直接ご活用ください。
