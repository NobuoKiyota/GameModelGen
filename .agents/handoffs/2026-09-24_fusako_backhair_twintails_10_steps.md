# ふさこ式 3Dキャラモデリング手順書 10【後ろ髪とツインテールの作り込み・立体化＆結び目編】

本ドキュメントは、3Dモデラー・ふさこ氏のYouTubeチュートリアル動画：
**『Blenderでキャラクターモデル制作！10 | 後ろ髪とツインテールの作り込み〜初級から中級者向けチュートリアル〜』**
（動画URL: https://www.youtube.com/watch?v=3db96pczrPs / 収録時間: 40分11秒）
の全工程を、トポロジー構造・ショートカットキー・解剖学的＆アニメ的デフォルメの黄金律・ゲームエンジン（Unity/VRM）最適化規約に沿って完全体系化した実践仕様書です。

各手順の直下に、高解像度スクリーンショット集（`docs/fusako_10_backhair_twintails_screenshots/`）への相対リンクを配置しています。

---

## 📑 目次

1. [全体の前提知識と使用ツール・アドオン](#1-全体の前提知識と使用ツールアドオン)
2. [第1章: 後ろ髪の肉厚化・外側ロック・毛束分割](#第1章-後ろ髪の肉厚化外側ロック毛束分割)
3. [第2章: Subsurf確定適用・AutoMirror・襟足成形](#第2章-subsurf確定適用automirror襟足成形)
4. [第3章: ツインテールの二層立体化と裏面張り密閉](#第3章-ツインテールの二層立体化と裏面張り密閉)
5. [第4章: ツインテール結び目（シュシュ・ゴム）の彫り込み](#第4章-ツインテール結び目シュシュゴムの彫り込み)
6. [第5章: 生え際・もみあげの肌見え防止と最終検品](#第5章-生え際もみあげの肌見え防止と最終検品)
7. [第10話の成果と次工程への展望](#第10話の成果と次工程への展望)

---

## 1. 全体の前提知識と使用ツール・アドオン

- **前工程のベースモデル**: 第3話『髪の作り方 大ラフ編』で作成した「後ろ髪」「お団子・ツインテール」の大ラフメッシュ。
- **使用アドオン**:
  - `Hide Only Vertex`: 指定した頂点をロックし、プロポーショナル編集や拡大縮小の影響を受けなくする（非表示にせず固定できる）神アドオン（無料）。
  - `LoopTools`: `Relax`（エッジの均等平滑化）に多用（著者は `Shift + Y` にショートカット設定）。
  - `AutoMirror`: Subsurf適用後の中央の歪みを防ぐため、半分カットしてMirrorモディファイアを再設定する。
  - `Check Tool Box (Mesh Detection)`: T字ポリゴン・多角形の自動検出。
- **重要なショートカット**:
  - `Shift + V`: 頂点スライド（面が張られていないオープン境界でもエッジに沿ってスライド可能）。
  - `Shift + E`: エッジクリース（毛先や折り目を鋭利に保つ）。
  - `Shift + Ctrl + H`: Hide Only Vertex のロック実行。
  - `Alt + H`: ロック解除・再表示。

---

## 第1章: 後ろ髪の肉厚化・外側ロック・毛束分割

### 1-1. 後ろ髪の法線内側押し出し（Alt + S）
- 第3話の後ろ髪大ラフを選択。お団子・ツインテール部分は `P` キーで分離して非表示（`H`）にしておく。
- 編集モード（`Tab`）に入り、全選択（`A`）。
- `E` $\to$ `Esc`（押し出しを確定キャンセル）を押した後、`Alt + S` で**法線内側（頭部側）へ向けてグイッと縮小**する。
- これにより、後頭部を包み込む均一な肉厚シェルが生成される。
  - [📸 参考: 01_c1_back_hair_alt_s_extrude.jpg](../../docs/fusako_10_backhair_twintails_screenshots/01_c1_back_hair_alt_s_extrude.jpg)

### 1-2. 外側シェルのシーム分離と「Hide Only Vertex」ロック
- 外側の形状を壊さずに、内側のシェルだけを頭部に沿わせて拡大したい。
- 外側の境界エッジを選択し、`Ctrl + E` $\to$ `Mark Seam`（シームをマーク）を付与。
  - [📸 参考: 02_c1_mark_seam_outer_shell.jpg](../../docs/fusako_10_backhair_twintails_screenshots/02_c1_mark_seam_outer_shell.jpg)
- 面選択モード（`3`）で外側メッシュの上にカーソルを置き、`L` キーを押して外側シェルのみを一発選択。
- アドオン `Hide Only Vertex` のショートカット `Shift + Ctrl + H` を押す。
- **効果**: 見た目はそのままだが外側頂点に「ロック」がかかり、移動・拡大ツールの影響を一切受けなくなる。
  - [📸 参考: 03_c1_hide_only_vertex_lock.jpg](../../docs/fusako_10_backhair_twintails_screenshots/03_c1_hide_only_vertex_lock.jpg)

### 1-3. 内側頂点の頭部フィッティングとLoopTools Relax
- 外側がロックされた状態で、内側の頂点を選択。
- `Alt + S` やプロポーショナル編集（`O`）を使って、後頭部が露出しないように内側シェルを大きく広げる。
  - [📸 参考: 04_c1_proportional_inner_fit.jpg](../../docs/fusako_10_backhair_twintails_screenshots/04_c1_proportional_inner_fit.jpg)
- `Alt + S` の多用でエッジが歪んだ箇所は、ループ選択して `LoopTools > Relax`（Shift + Y）を実行し、綺麗に均等平滑化する。
  - [📸 参考: 05_c1_looptools_relax_smoothing.jpg](../../docs/fusako_10_backhair_twintails_screenshots/05_c1_looptools_relax_smoothing.jpg)

### 1-4. 不要な内側面の削除と法線再計算
- 内側の上部など、頭皮に埋まりゲームやアニメーションで絶対に見えない面を選択し、`X` $\to$ `Faces` で削除する（軽量化）。
  - [📸 参考: 06_c1_delete_inner_unseen_faces.jpg](../../docs/fusako_10_backhair_twintails_screenshots/06_c1_delete_inner_unseen_faces.jpg)
- `Alt + H` で外側のロックを解除。
- 全選択（`A`）し、`Shift + N`（面の向きを外側に揃える）を実行して反転した法線を正常化。
  - [📸 参考: 07_c1_recalculate_outside_normals.jpg](../../docs/fusako_10_backhair_twintails_screenshots/07_c1_recalculate_outside_normals.jpg)

### 1-5. Vキー切り裂きと頂点スライド（Shift + V）
- 後ろ髪の毛束を分割したいエッジを選択し、`V` キーで切り裂く。
- 開口部を `F` キーで面張りして閉じる。
  - [📸 参考: 08_c1_rip_v_key_bundle_split.jpg](../../docs/fusako_10_backhair_twintails_screenshots/08_c1_rip_v_key_bundle_split.jpg)
- 面が張られていないオープン境界の頂点は `GG` が効かないため、`Shift + V`（頂点スライド）を使用して既存エッジに沿って滑らかに移動させる。
  - [📸 参考: 09_c1_shift_v_vertex_slide.jpg](../../docs/fusako_10_backhair_twintails_screenshots/09_c1_shift_v_vertex_slide.jpg)
- 外側にカールする毛先エッジを選択し、`Shift + E` でクリース（Crease: 1.0）をかけて鋭い毛先を成形。
  - [📸 参考: 10_c1_crease_curl_tip.jpg](../../docs/fusako_10_backhair_twintails_screenshots/10_c1_crease_curl_tip.jpg)

---

## 第2章: Subsurf確定適用・AutoMirror・襟足成形

### 2-1. Subsurf確定適用とAutoMirrorによる再ミラー化
- 大ラフの形状が整ったら、`Shift + D` でバックアップコレクションへ退避。
- モディファイアスタックで、まず Mirror を適用し、続いて Subdivision Surface を `Ctrl + A` で確定適用する。
- 確定適用後、中央シームの微小なズレを防ぎ左右対称編集を続けるため、Nパネルの `Tool > Edit > AutoMirror` を実行。
- メッシュの左半分が自動削除され、クリッピングが有効化された Mirror モディファイアが再追加される。
  - [📸 参考: 11_c1_automirror_split_and_mirror.jpg](../../docs/fusako_10_backhair_twintails_screenshots/11_c1_automirror_split_and_mirror.jpg)

### 2-2. 平面的側頭部の丸み補正
- クリースや切り裂きによって側頭部が平坦になってしまった箇所を選択。
- 上下の端点を除外して中央ループを選択し、`Alt + S` で外側にふっくらと丸みを持たせる。
  - [📸 参考: 12_c1_planar_sides_alt_s_soften.jpg](../../docs/fusako_10_backhair_twintails_screenshots/12_c1_planar_sides_alt_s_soften.jpg)

### 2-3. 襟足（首の後ろ）毛束の押し出し＆整流
- 後頭部下端の不要な内側面を `X` で削除。
- 襟足の境界エッジを選択し、`E + Y` で前方へ押し出し $\to$ `G + Z` で下方へ引き下げ。
- ピボットポイントをアクティブ要素（`.`）にし、`S + X` で幅を絞り、`S + Y` で厚みを調整。
  - [📸 参考: 13_c1_nape_hair_extrude_down.jpg](../../docs/fusako_10_backhair_twintails_screenshots/13_c1_nape_hair_extrude_down.jpg)
- `LoopTools > Relax` で均等化し、毛先を `M`（Merge at Center）で閉じる。
  - [📸 参考: 14_c1_nape_bundle_smoothing.jpg](../../docs/fusako_10_backhair_twintails_screenshots/14_c1_nape_bundle_smoothing.jpg)

---

## 第3章: ツインテールの二層立体化と裏面張り密閉

### 3-1. ツインテールのS字カーブ調整
- 非表示にしていたツインテール大ラフを再表示（`Alt + H`）。
- プロポーショナル編集を使い、横から見て自然に跳ね上がり、毛先が内側へ巻き込む美しいS字カーブを形成する。
  - [📸 参考: 15_c2_twintail_proportional_curve.jpg](../../docs/fusako_10_backhair_twintails_screenshots/15_c2_twintail_proportional_curve.jpg)

### 3-2. 重なり毛束の複製と巻きつき立体配置（螺旋二層化）
- ツインテールの本体面を選択し、`Shift + D` で複製。
- `Alt + S` で外側に少し浮かせつつ、`R` キーで回転させて本体にコロンと巻きつくような螺旋状のレイヤーを配置する。
  - [📸 参考: 16_c2_overlapping_bundle_rotation.jpg](../../docs/fusako_10_backhair_twintails_screenshots/16_c2_overlapping_bundle_rotation.jpg)
- 小毛束の中央にループを追加し、`Alt + S` で中央を膨らませて肉厚な立体感を付与。
  - [📸 参考: 17_c2_center_loop_alt_s_bulge.jpg](../../docs/fusako_10_backhair_twintails_screenshots/17_c2_center_loop_alt_s_bulge.jpg)

### 3-3. ツインテールのSubsurf確定適用と頂点整流
- ツインテールを `Shift + D` でバックアップ退避後、Subsurfを `Ctrl + A` で確定適用。
  - [📸 参考: 18_c2_apply_subsurf_twintail.jpg](../../docs/fusako_10_backhair_twintails_screenshots/18_c2_apply_subsurf_twintail.jpg)
- 重なり毛束と本体の交差部にある余分なエッジを溶解（Dissolve Edges）し、下端の隙間を三角面で綺麗にマージする。
  - [📸 参考: 19_c2_resolve_overlapping_faces.jpg](../../docs/fusako_10_backhair_twintails_screenshots/19_c2_resolve_overlapping_faces.jpg)

### 3-4. 【神技】三角形断面化のための裏面張り（全方位立体化）
- ツインテールは360度全方位から見られるため、裏側が空洞（板ポリ）では成立しない。
- ツインテール裏面の中央ループを `Alt + S` で内側（芯方向）へ盛り上げる。
- 両側の境界エッジと中央ループの「4辺」を選択し、`F` キーを連続打鍵して裏面を四角面で完全に塞ぎ、断面がおにぎり型（三角形〜丸三角）の肉厚ソリッドに仕上げる。
  - [📸 参考: 20_c2_triangular_back_faces_f_key.jpg](../../docs/fusako_10_backhair_twintails_screenshots/20_c2_triangular_back_faces_f_key.jpg)
- `Shade Auto Smooth`（自動スムーズ）を適用し、不自然な黒ずみや影の段差がないか確認する。
  - [📸 参考: 21_c2_shade_auto_smooth_check.jpg](../../docs/fusako_10_backhair_twintails_screenshots/21_c2_shade_auto_smooth_check.jpg)

---

## 第4章: ツインテール結び目（シュシュ・ゴム）の彫り込み

### 4-1. アノテーション（サーフェスペン）による下書き
- オブジェクトモードで、Tパネル（ツールバー）の「アノテーション（ペンツール）」を選択。
- 配置基準を `Surface`（サーフェス）に設定。
- ツインテール根元のメッシュ表面に、髪がゴムでキュッと束ねられたしわや結び目のラインを直接手描きで下書きする。
  - [📸 参考: 22_c3_annotate_hair_tie_guide.jpg](../../docs/fusako_10_backhair_twintails_screenshots/22_c3_annotate_hair_tie_guide.jpg)

### 4-2. ナイフカット（Kキー）とインセット（Iキー）による隆起成形
- 編集モードに入り、`K` キー（ナイフツール）を起動。
- アノテーションの下書き線に沿ってメッシュをカットする。
- カットした結び目領域の面を選択し、`I` キーで面を差し込み（インセット）。
- `Alt + S` で外側にグッと押し出して隆起させる。
  - [📸 参考: 23_c3_knife_cut_and_inset.jpg](../../docs/fusako_10_backhair_twintails_screenshots/23_c3_knife_cut_and_inset.jpg)

### 4-3. Mark Sharp による結び目のシャープな引き締め
- 結び目の境界エッジループを選択し、`Ctrl + E` $\to$ `Mark Sharp`（シャープをマーク）を付与（シアン色で表示）。
- これにより、SubsurfやAuto Smooth環境下でも、髪留めゴムでギュッと締め付けられたメリハリのあるシャープな陰影が演出される。
  - [📸 参考: 24_c3_mark_sharp_hair_tie.jpg](../../docs/fusako_10_backhair_twintails_screenshots/24_c3_mark_sharp_hair_tie.jpg)

---

## 第5章: 生え際・もみあげの肌見え防止と最終検品

### 5-1. 面スナップ（Face Snapping）による生え際の密着延長
- カメラを動かした際、後ろ髪ともみあげ・生え際の隙間から頭皮や肌が不自然に露出するのを防止する。
- `Shift + Tab` でスナップをONにし、スナップ先を `Face`（面）に設定。
- 後ろ髪の境界エッジを選択し、`E` キーで押し出しながら頭皮メッシュの表面に吸着させる。
  - [📸 参考: 25_c3_face_snap_hairline_extrude.jpg](../../docs/fusako_10_backhair_twintails_screenshots/25_c3_face_snap_hairline_extrude.jpg)
- 生え際の内側まで十分に延長することで、あらゆる角度から見ても地肌が見えない完全密閉ヘアスタイルが完成する。

### 5-2. 最終確認とクリーンアップ
- 前髪・横髪・後ろ髪・ツインテールの全コレクションを表示。
- 全オブジェクトに対して `Check Tool Box` を実行し、ノンマニホールドや多角面エラーがゼロであることを確認。
- 各パーツの接続部、重なり感、シルエットを360度回転させて検品完了。
  - [📸 参考: 26_c3_complete_hair_preview.jpg](../../docs/fusako_10_backhair_twintails_screenshots/26_c3_complete_hair_preview.jpg)

---

## 第10話の成果と次工程への展望

- **完成した部位**:
  - **後ろ髪**: 肉厚シェル化・外側ロックによる頭部フィット・襟足成形・AutoMirror対称化。
  - **ツインテール**: 豊かなS字カーブ・重なり小毛束の巻きつき二層化・360度裏面張り密閉（三角形断面）。
  - **結び目**: アノテーション下書き $\to$ ナイフカット $\to$ インセット $\to$ Mark Sharpによる髪留めのリアルな彫り込み。
  - **生え際**: 面スナップによる地肌露出の完全防止。
- **次回（第11話以降）への展望**:
  - 頭部・体素体・髪型の全ベースパーツが完成。いよいよ衣装（服・靴・アクセサリー）のモデリング、またはUV展開・テクスチャリング工程へと進みます。
