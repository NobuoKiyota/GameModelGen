# ふさこ氏チュートリアル第12話 重要シーン・スクリーンショットカタログ
## 『ドロワーズとワンピースのモデリング 〜初級から中級者向けチュートリアル〜』

本ディレクトリは、ふさこ氏によるBlenderキャラクターモデリング講座第12話（[YouTube動画リンク](https://www.youtube.com/watch?v=NLLfkYDR0_g)）から、ドロワーズ（かぼちゃパンツ）の素体面複製（Shift+D）・法線膨らみ（Alt+S）・配列＆カーブによるフリル生成・LoopTools Bridgeギャザー接合、ワンピースの12頂点サークル押し出し・アームホール開口＆To Sphere真円化・襟ぐりインセット＆ベベル・素体頂点スナップ貫通防止・スカート裾スカラップ（半円フリル）自動巻きつけ・丈の微調整などの決定的シーン（全26枚）を高解像度で抽出・整理した画像リファレンス集です。

詳細な操作手順やトポロジー設計の解説は、以下の仕様書を参照してください：
- 📘 **詳細手順・トポロジー仕様書**: [`../../.agents/handoffs/2026-09-24_fusako_dress_drawers_12_steps.md`](../../.agents/handoffs/2026-09-24_fusako_dress_drawers_12_steps.md)

---

### 📸 スクリーンショット一覧（全26枚）

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー） | 主な内容・重要操作・トポロジーのポイント |
|:---:|:---:|:---|:---|
| 01 | 00:00:25 | [./01_c1_body_faces_duplicate_drawers.jpg](./01_c1_body_faces_duplicate_drawers.jpg) | **素体からパンツ面の複製分離**: 素体の骨盤・太もも周りの面を選択し、`Shift + D` で複製 $\to$ `P` キーで別オブジェクトに分離。 |
| 02 | 00:00:45 | [./02_c1_alt_s_bulge_pumpkin_pants.jpg](./02_c1_alt_s_bulge_pumpkin_pants.jpg) | **Alt+Sによる法線膨らみ**: ウエスト以外を選択し、`Alt + S` で外側に膨らませてふっくらとしたかぼちゃパンツ形状を形成。 |
| 03 | 00:01:10 | [./03_c1_shear_hem_leveling.jpg](./03_c1_shear_hem_leveling.jpg) | **シアー（Shear）による裾の水平化**: 斜めにカットされた太もも裾のエッジループを、シアー機能を使って床面と平行に水平レベリング。 |
| 04 | 00:03:30 | [./04_c1_frill_unit_plane_base.jpg](./04_c1_frill_unit_plane_base.jpg) | **フリル1ユニットの平面作成**: `Shift + A` で平面（Plane）を追加し、小さく縮小してループカット3本を追加。 |
| 05 | 00:04:15 | [./05_c1_frill_cross_section_curve.jpg](./05_c1_frill_cross_section_curve.jpg) | **Vキー切り裂きと立体カーブ断面**: 前側頂点を `V` キーで切り裂いて引き上げ、波打つフリルの立体的な断面カーブを成形。 |
| 06 | 00:05:15 | [./06_c1_array_modifier_merge.jpg](./06_c1_array_modifier_merge.jpg) | **Arrayモディファイア（Merge有効）**: 配列モディファイアを追加し、マージ（Merge）にチェックを入れて横方向に連続複製。 |
| 07 | 00:06:05 | [./07_c1_proportional_step_offset.jpg](./07_c1_proportional_step_offset.jpg) | **フリルの前後段差オフセット**: プロポーショナル編集を使い、フリルの波を前後にわずかにずらして立体的なひらひら感を付与。 |
| 08 | 00:07:30 | [./08_c1_hem_subdivide_relax.jpg](./08_c1_hem_subdivide_relax.jpg) | **パンツ裾ループの細分化＆三角化**: フリルの頂点数（1波5頂点）に合わせ、裾ループを細分化（Subdivide）し、`Ctrl + T` で四角面をV字三角化して整流。 |
| 09 | 00:08:50 | [./09_c1_convert_hem_to_curve.jpg](./09_c1_convert_hem_to_curve.jpg) | **裾エッジのカーブ変換**: パンツ裾エッジループを `P` で分離し、右クリック `Convert to > Curve` でカーブオブジェクトに変換。 |
| 10 | 00:09:20 | [./10_c1_curve_modifier_wrap.jpg](./10_c1_curve_modifier_wrap.jpg) | **Curveモディファイアによる巻きつけ**: フリルに `Curve` モディファイアを追加し、裾カーブを指定してパンツの足回りに沿ってぐるっと一周配置。 |
| 11 | 00:10:10 | [./11_c1_curve_tilt_ctrl_t.jpg](./11_c1_curve_tilt_ctrl_t.jpg) | **カーブ編集でのティルト（Ctrl + T）**: カーブの全頂点を選択し、`Ctrl + T`（Tilt）でフリルの向きを外側斜め下へ自然に広げる。 |
| 12 | 00:12:15 | [./12_c1_apply_modifiers_merge_ends.jpg](./12_c1_apply_modifiers_merge_ends.jpg) | **モディファイア適用と末端マージ**: Array・Curveモディファイアを確定適用し、1周の継ぎ目頂点を `M`（Merge at Center）で溶接。 |
| 13 | 00:13:55 | [./13_c1_looptools_bridge_gather.jpg](./13_c1_looptools_bridge_gather.jpg) | **LoopTools Bridgeによるギャザー接合**: ドロワーズ裾とフリル上端ループを `LoopTools > Bridge` で架橋し、クシュッとしたギャザーゴム感を表現。 |
| 14 | 00:15:55 | [./14_c1_drawers_completed_view.jpg](./14_c1_drawers_completed_view.jpg) | **ドロワーズ完成外観**: ふっくらとしたシルエットと裾のフリルが美しく一体化したインナーパンツの完成。 |
| 15 | 00:16:45 | [./15_c2_onepiece_reference_overlay.jpg](./15_c2_onepiece_reference_overlay.jpg) | **ワンピース立ち絵リファレンスの配置**: 正面・側面の下絵にワンピース着用状態の画像を読み込み、半透明配置。 |
| 16 | 00:17:55 | [./16_c2_circle_12verts_waist_base.jpg](./16_c2_circle_12verts_waist_base.jpg) | **Circle 12頂点からの胴体開始**: 素体の胴体12頂点トポロジーに合わせ、`Circle`（頂点数12）を追加してウエスト・脇下へ配置。 |
| 17 | 00:18:45 | [./17_c2_extrude_skirt_and_chest.jpg](./17_c2_extrude_skirt_and_chest.jpg) | **フレアスカート＆胸元の押し出し**: 下へ `E + Z` 押し出し $\to$ `S` 拡大でスカートを広げ、上へ `E + Z` で胸元・肩口まで押し出し。 |
| 18 | 00:20:10 | [./18_c2_armhole_extrude_delete_faces.jpg](./18_c2_armhole_extrude_delete_faces.jpg) | **アームホール（袖ぐり）の開口**: 腕の付け根の4面を `E + X` で外側に少し押し出し、選択面を `X` で削除して腕を通す穴を開口。 |
| 19 | 00:20:30 | [./19_c2_to_sphere_armhole_rounding.jpg](./19_c2_to_sphere_armhole_rounding.jpg) | **Shift+Alt+Sによるアームホール真円化**: 開口部エッジループを選択し、`Shift + Alt + S`（To Sphere: 1.0）で綺麗な円形に整流。 |
| 20 | 00:22:45 | [./20_c2_collar_inset_and_bevel.jpg](./20_c2_collar_inset_and_bevel.jpg) | **首元の襟インセット＆ベベル**: 首元を真上に押し出し、`I`（インセット、Boundaryオフ）で襟の厚みを付与、`Ctrl + B` で角を面取りベベル。 |
| 21 | 00:26:15 | [./21_c2_neck_arm_skin_snapping.jpg](./21_c2_neck_arm_skin_snapping.jpg) | **素体への頂点スナップによる肌貫通防止**: 首元・アームホールの内側エッジループを素体メッシュに頂点スナップさせ、服と肌の境界を密閉。 |
| 22 | 00:29:45 | [./22_c2_scallop_unit_circle_16.jpg](./22_c2_scallop_unit_circle_16.jpg) | **スカート裾スカラップ（半円フリル）ユニット作成**: `Circle`（16頂点）の上半分を使用し、インセットと面削除で平らな半円スカラップを作成。 |
| 23 | 00:32:30 | [./23_c2_skirt_curve_wrap_scallop.jpg](./23_c2_skirt_curve_wrap_scallop.jpg) | **裾カーブへのスカラップ12枚自動巻きつけ**: ワンピース裾の12辺に合わせて、スカラップを `Array`（数12）＋ `Curve` で裾全周に沿って等間隔配置。 |
| 24 | 00:34:30 | [./24_c2_scallop_vertex_snapping_merge.jpg](./24_c2_scallop_vertex_snapping_merge.jpg) | **スカラップとスカート裾の一体化**: モディファイア適用後、`Ctrl + J` で統合し、裾頂点にスナップ吸着 $\to$ `Merge by Distance` で完全溶接。 |
| 25 | 00:38:30 | [./25_c2_drawers_length_adjustment_gz.jpg](./25_c2_drawers_length_adjustment_gz.jpg) | **ドロワーズのチラ見せ丈調整**: ワンピース裾からドロワーズのフリルが可愛らしく覗くよう、ドロワーズ裾を `G + Z` で引き下げ、`Alt + S` で膨らみ微調整。 |
| 26 | 00:39:25 | [./26_c2_drawers_and_dress_complete.jpg](./26_c2_drawers_and_dress_complete.jpg) | **ドロワーズ＆ワンピース完成プレビュー**: かぼちゃパンツとインナーワンピースが完璧に組み合わさった可憐な衣装ベースの完成。 |

---

### 💡 画像プレビューのコツ
各行のリンク `[./画像名.jpg](./画像名.jpg)` をクリックすると、Blender / VS Code / 各種Markdownビューア上で即座に高解像度画像が展開されます。
モデリング作業中、該当するトポロジーや操作UIの確認に直接ご活用ください。
