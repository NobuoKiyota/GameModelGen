# ふさこ氏チュートリアル第09話 重要シーン・スクリーンショットカタログ
## 『前髪の作り込み 〜初級から中級者向けチュートリアル〜』

本ディレクトリは、ふさこ氏によるBlenderキャラクターモデリング講座第9話（[YouTube動画リンク](https://www.youtube.com/watch?v=ZOSArnNsbrY)）から、前髪・横髪のハイディテール化、毛束の切り裂き（Vキー）、左右非対称調整、EdgeFlowによる曲率自動整流、ノンマニホールド（T字ポリゴン）エラー回避、横髪の裏面張り立体化（三角形断面）、Check Tool Boxによるエラー検出などの決定的シーン（全26枚）を高解像度で抽出・整理した画像リファレンス集です。

詳細な操作手順やトポロジー設計の解説は、以下の仕様書を参照してください：
- 📘 **詳細手順・トポロジー仕様書**: [`../../.agents/handoffs/2026-09-24_fusako_bangs_detail_09_steps.md`](../../.agents/handoffs/2026-09-24_fusako_bangs_detail_09_steps.md)

---

### 📸 スクリーンショット一覧（全26枚）

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー） | 主な内容・重要操作・トポロジーのポイント |
|:---:|:---:|:---|:---|
| 01 | 00:00:20 | [./01_c1_hair_rough_before_subsurf.jpg](./01_c1_hair_rough_before_subsurf.jpg) | **前髪大ラフの最終確認**: 第3話で作成したローポリケージとSubsurfモディファイアによる前髪の初期形状。 |
| 02 | 00:00:45 | [./02_c1_backup_and_apply_subsurf.jpg](./02_c1_backup_and_apply_subsurf.jpg) | **バックアップ退避＆Subsurf確定適用**: `Shift + D` で複製してバックアップコレクションへ退避後、`Ctrl + A` でSubsurfを確定適用。 |
| 03 | 00:01:25 | [./03_c1_reset_crease_to_zero.jpg](./03_c1_reset_crease_to_zero.jpg) | **エッジクリースの初期化**: 全選択（A）し、Nパネルの `Item > Edge Data > Mean Crease` を 0.0 にリセットして均一化。 |
| 04 | 00:01:45 | [./04_c1_ctrl_click_ring_subdivide.jpg](./04_c1_ctrl_click_ring_subdivide.jpg) | **エッジリング選択＆細分化**: `Ctrl + クリック` でリング選択し、右クリック `Subdivide`（細分化）で滑らかな縦ループを追加。 |
| 05 | 00:02:05 | [./05_c1_rip_v_key_separate_bundle.jpg](./05_c1_rip_v_key_separate_bundle.jpg) | **Vキー切り裂き（Rip）による毛束分離**: `V` キーでメッシュを切り裂き、`X` 軸（横）に少しずらして独立した細い毛束を生成。 |
| 06 | 00:02:35 | [./06_c1_turn_off_x_mirror_asymmetry.jpg](./06_c1_turn_off_x_mirror_asymmetry.jpg) | **Xミラー編集のオフ（左右非対称化）**: 手前のメイン前髪は左右非対称デザインのため、右上のメッシュ対称（X Mirror）をオフにして個別編集。 |
| 07 | 00:03:00 | [./07_c1_proportional_edit_bundle_curve.jpg](./07_c1_proportional_edit_bundle_curve.jpg) | **プロポーショナル編集による流線調整**: `O` キーでプロポーショナル編集を有効化し、自然なS字・流線カーブを形成。 |
| 08 | 00:04:15 | [./08_c1_tip_split_subdivide.jpg](./08_c1_tip_split_subdivide.jpg) | **毛先の二股割れ（Split）モデリング**: 毛先のポリゴン不足を補うため細分化を追加し、枝毛・毛先のニュアンスを成形。 |
| 09 | 00:05:25 | [./09_c1_edgeflow_set_flow_addon.jpg](./09_c1_edgeflow_set_flow_addon.jpg) | **EdgeFlow（Set Flow）アドオン活用**: ループカット追加で角張ったエッジを、`Set Flow`（右クリック）で曲率に沿った滑らかカーブへ一発自動補正。 |
| 10 | 00:06:10 | [./10_c1_j_key_vertex_connect_quads.jpg](./10_c1_j_key_vertex_connect_quads.jpg) | **Jキー頂点接続による四角面整流**: 5角形以上が発生した箇所を `J` キー（頂点のパスを連結）で繋ぎ、綺麗な四角面トポロジーを構築。 |
| 11 | 00:07:45 | [./11_c1_shade_smooth_flat_bangs.jpg](./11_c1_shade_smooth_flat_bangs.jpg) | **板ポリ前髪のシェードスムース確認**: Unity/VRMでの「前髪から眉毛が透けて見える（MToon透過）」演出のため、前髪は意図的に薄い板ポリのまま仕上げる。 |
| 12 | 00:09:40 | [./12_c1_overlapping_bundle_duplicate.jpg](./12_c1_overlapping_bundle_duplicate.jpg) | **重なる大毛束の面複製**: 上に重なる毛束を作るため、既存の面を選択して `Shift + D` で複製。 |
| 13 | 00:10:45 | [./13_c1_alt_s_offset_floating_bundle.jpg](./13_c1_alt_s_offset_floating_bundle.jpg) | **Alt+Sによる法線浮かせ配置**: 複製した面を `Alt + S` で法線方向に少し浮かせ、奥行き感のある毛束レイヤーを配置。 |
| 14 | 00:11:45 | [./14_c1_t_junction_non_manifold_warning.jpg](./14_c1_t_junction_non_manifold_warning.jpg) | **【警告】T字ポリゴン（ノンマニホールド）**: 1辺から3面分岐する「T字ポリゴン」はゲームエンジンやSubsurfで破綻する重大エラーであることを解説。 |
| 15 | 00:12:10 | [./15_c1_rip_and_hole_resolution.jpg](./15_c1_rip_and_hole_resolution.jpg) | **Vキー穴あけによるT字回避**: 接続部をあらかじめ `V` キーで切り離して穴を開け、3頂点マージ（Jキー）で四角面/三角面として正しく閉じる解決策。 |
| 16 | 00:13:10 | [./16_c1_active_element_tip_taper.jpg](./16_c1_active_element_tip_taper.jpg) | **アクティブ要素ピボットによる毛先のすぼめ**: ピボットポイントをアクティブ要素に設定し、先端頂点に向かって均一に細身化。 |
| 17 | 00:15:35 | [./17_c1_vertex_snapping_close_gap.jpg](./17_c1_vertex_snapping_close_gap.jpg) | **頂点スナップによる隙間埋め**: `Shift + Tab` で頂点スナップを有効化し、センター前髪とサイド髪の間の不自然な隙間を吸着密閉。 |
| 18 | 00:16:40 | [./18_c2_side_hair_base_plane.jpg](./18_c2_side_hair_base_plane.jpg) | **横髪ベース（水色パーツ）の配置**: 頬のラインに沿った横髪の初期平面メッシュ（Subsurf適用前）の形状確認。 |
| 19 | 00:18:15 | [./19_c2_side_hair_apply_subsurf.jpg](./19_c2_side_hair_apply_subsurf.jpg) | **横髪のSubsurf適用と大毛束分離**: バックアップ退避後、Subsurfを確定適用して長い側頭毛束を `V` キーで切り離し押し出し。 |
| 20 | 00:20:00 | [./20_c2_side_bundle_taper_and_set_flow.jpg](./20_c2_side_bundle_taper_and_set_flow.jpg) | **側頭毛束のすぼめ成形＆Set Flow**: 先端を細く絞り、追加ループを `Set Flow` で整流して美しい流線を作成。 |
| 21 | 00:25:30 | [./21_c2_curl_hair_extrude.jpg](./21_c2_curl_hair_extrude.jpg) | **カール毛束の押し出し・カーブ成形**: くるんと外側に跳ねるカール毛束を `E` 押し出しと回転（R）で立体成形。 |
| 22 | 00:27:00 | [./22_c2_triangular_cross_section_alt_s.jpg](./22_c2_triangular_cross_section_alt_s.jpg) | **三角形断面化のためのAlt+S内側膨らみ**: 横髪裏面張り用の中央ループを細分化で追加し、`Alt + S` で内側へ膨らませて肉厚な三角形断面の骨格を形成。 |
| 23 | 00:28:15 | [./23_c2_face_orientation_and_f_key_filling.jpg](./23_c2_face_orientation_and_f_key_filling.jpg) | **面の向き確認＆Fキー裏面張り**: `Face Orientation` で表面が青色であることを確認しながら、4辺を選択して `F` キーで裏面を順次密閉。 |
| 24 | 00:30:20 | [./24_c2_fill_gap_behind_head_alt_s.jpg](./24_c2_fill_gap_behind_head_alt_s.jpg) | **後頭部・側頭部のスカスカ解消**: 斜め後ろから見た時に頭皮との隙間が空かないよう、側面にループを追加して `Alt + S` で頭部に沿わせる。 |
| 25 | 00:32:30 | [./25_c2_shade_auto_smooth_and_mark_sharp.jpg](./25_c2_shade_auto_smooth_and_mark_sharp.jpg) | **Shade Auto Smooth＆Mark Sharp**: 稜線が黒ずむのを防ぐため、自動スムーズの角度を広げ、エッジに `Mark Sharp`（Ctrl+E）を付与してパキッとした陰影を両立。 |
| 26 | 00:35:15 | [./26_c2_check_toolbox_non_manifold_detection.jpg](./26_c2_check_toolbox_non_manifold_detection.jpg) | **Check Tool Boxによるエラー自動検出＆完成**: `Select Non-Manifold` や `Select N-Gons` を実行してエラーゼロを確認。前髪・横髪ハイディテール完成。 |

---

### 💡 画像プレビューのコツ
各行のリンク `[./画像名.jpg](./画像名.jpg)` をクリックすると、Blender / VS Code / 各種Markdownビューア上で即座に高解像度画像が展開されます。
モデリング作業中、該当するトポロジーや操作UIの確認に直接ご活用ください。
