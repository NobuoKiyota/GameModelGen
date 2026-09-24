# ふさこ式 3Dキャラモデリング手順書 12【ドロワーズ＆ワンピースのモデリング・フリル配列＆貫通防止編】

本ドキュメントは、3Dモデラー・ふさこ氏のYouTubeチュートリアル動画：
**『Blenderでキャラクターモデル制作！12 | ドロワーズとワンピースのモデリング〜初級から中級者向けチュートリアル〜』**
（動画URL: https://www.youtube.com/watch?v=NLLfkYDR0_g / 収録時間: 39分42秒）
の全工程を、衣装トポロジー構造・ショートカットキー・解剖学的＆アニメ的デフォルメの黄金律・ゲームエンジン（Unity/VRM）最適化規約に沿って完全体系化した実践仕様書です。

各手順の直下に、高解像度スクリーンショット集（`docs/fusako_12_dress_drawers_screenshots/`）への相対リンクを配置しています。

---

## 📑 目次

1. [全体の前提知識と使用ツール・アドオン](#1-全体の前提知識と使用ツールアドオン)
2. [第1章: ドロワーズ（かぼちゃパンツ）のベースモデリング](#第1章-ドロワーズかぼちゃパンツのベースモデリング)
3. [第2章: 配列（Array）＋カーブ（Curve）によるフリルの自動生成](#第2章-配列arrayカーブcurveによるフリルの自動生成)
4. [第3章: LoopTools Bridge によるギャザー接合と完成](#第3章-looptools-bridge-によるギャザー接合と完成)
5. [第4章: ワンピース本体のモデリング（12頂点サークルベース）](#第4章-ワンピース本体のモデリング12頂点サークルベース)
6. [第5章: アームホール＆ネックライン開口と肌スナップ貫通防止](#第5章-アームホールネックライン開口と肌スナップ貫通防止)
7. [第6章: スカート裾スカラップ（半円フリル）の配置と丈調整](#第6章-スカート裾スカラップ半円フリルの配置と丈調整)
8. [第12話の成果と次工程への展望](#第12話の成果と次工程への展望)

---

## 1. 全体の前提知識と使用ツール・アドオン

- **前工程のベースモデル**: 第8話で完成した「手足統合済み素体（Headless Body）」および第11話で調整完了した「頭部・髪型」。
- **衣装制作の基本思想**:
  - 服をゼロから作ると素体との干渉（貫通）や体型のズレが起きやすい。そのため、**素体の既存メッシュから面を複製（Shift + D）して開始する**のが最も安全かつ効率的。
  - 胴体ループが1周12頂点であるため、服も「12頂点」またはその倍数で設計し、頂点の対応関係をシンプルに保つ。
- **使用アドオン**:
  - `LoopTools`: `Bridge`（フリルと裾のギャザー架橋）、`Relax`（均等平滑化）。
  - `AutoMirror`: 左右対称作業の半自動化。
  - 標準モディファイア: `Array`（配列）、`Curve`（カーブ追従）、`Mirror`。
- **重要なショートカット**:
  - `Shift + Ctrl + Alt + S`: シアー（Shear / エッジの傾斜補正）。
  - `Shift + Alt + S`: 球形化（To Sphere / アームホールの真円化）。
  - `Ctrl + T`（カーブ編集モード）: ティルト（Tilt / カーブに沿ったフリルの傾き・広がり制御）。
  - `Ctrl + B`: ベベル（面取り）。

---

## 第1章: ドロワーズ（かぼちゃパンツ）のベースモデリング

### 1-1. 素体からの面複製とオブジェクト分離
- 素体オブジェクトを選択し、編集モードに入る。
- 骨盤・股下・太もも上部にかけてのドロワーズに相当する面を選択。
- `Shift + D` $\to$ `Esc` で複製し、`P` キー $\to$ `Selection`（選択物）で別オブジェクトに分離する。
  - [📸 参考: 01_c1_body_faces_duplicate_drawers.jpg](../../docs/fusako_12_dress_drawers_screenshots/01_c1_body_faces_duplicate_drawers.jpg)

### 1-2. 法線膨らみ（Alt + S）によるかぼちゃパンツ化
- 分離したドロワーズを選択し、編集モードに入る。
- ウエストの最上段ループを選択し、`Ctrl + I`（選択反転）でウエスト以外の全頂点を選択。
- `Alt + S` で外側（法線方向）へグッと膨らませる。
- さらに上部を段階的に選択解除しながら `Alt + S` を重ね、腰回りがふっくらと丸く膨らんだ「かぼちゃパンツ」のボリュームを作る。
  - [📸 参考: 02_c1_alt_s_bulge_pumpkin_pants.jpg](../../docs/fusako_12_dress_drawers_screenshots/02_c1_alt_s_bulge_pumpkin_pants.jpg)

### 1-3. 裾エッジのシアー（Shear）水平レベリング
- 太もも裾のエッジループが斜めに傾いていると、フリルを付けた際に不自然になる。
- 裾エッジループを選択し、`Shift + Ctrl + Alt + S`（シアー / Shear）を実行。
- マウス移動でエッジループを床面と平行（水平）に整流する。
  - [📸 参考: 03_c1_shear_hem_leveling.jpg](../../docs/fusako_12_dress_drawers_screenshots/03_c1_shear_hem_leveling.jpg)

---

## 第2章: 配列（Array）＋カーブ（Curve）によるフリルの自動生成

### 2-1. フリル1ユニットの平面メッシュ作成
- `Shift + A` $\to$ `Mesh > Plane`（平面）を追加。
- 編集モードで小さく縮小し、`Ctrl + R` で縦ループカットを3本追加（4分割）。
  - [📸 参考: 04_c1_frill_unit_plane_base.jpg](../../docs/fusako_12_dress_drawers_screenshots/04_c1_frill_unit_plane_base.jpg)

### 2-2. 立体的なフリル断面カーブの成形
- 手前側の2頂点を選択し、`V` キーで切り裂き（Rip）つつ上方に持ち上げる。
- `F` キーで面を張り、S字状に波打つ立体的なフリルの1周期（1ユニット）を成形。
  - [📸 参考: 05_c1_frill_cross_section_curve.jpg](../../docs/fusako_12_dress_drawers_screenshots/05_c1_frill_cross_section_curve.jpg)

### 2-3. Array（配列）モディファイアの設定
- フリルオブジェクトに `Array` モディファイアを追加。
- `Merge`（マージ）にチェックを入れる（隣り合うユニットの端点頂点を自動溶接）。
- 繰り返し数を設定し、横方向に帯状に連続複製される状態を作る。
  - [📸 参考: 06_c1_array_modifier_merge.jpg](../../docs/fusako_12_dress_drawers_screenshots/06_c1_array_modifier_merge.jpg)
- プロポーショナル編集で正面の波に前後の段差オフセットをつけ、自然なひらひら感を付与。
  - [📸 参考: 07_c1_proportional_step_offset.jpg](../../docs/fusako_12_dress_drawers_screenshots/07_c1_proportional_step_offset.jpg)

### 2-4. パンツ裾エッジのカーブ変換
- フリルの頂点数（1波5頂点）に合わせ、パンツ裾ループを右クリック $\to$ `Subdivide`（細分化）し、`Ctrl + T` で四角面を三角面（V字）に分割整流。
  - [📸 参考: 08_c1_hem_subdivide_relax.jpg](../../docs/fusako_12_dress_drawers_screenshots/08_c1_hem_subdivide_relax.jpg)
- 裾エッジループを選択し、`P` キーで別オブジェクトに分離。
- オブジェクトモードで右クリック $\to$ `Convert to > Curve`（カーブに変換）を実行。
  - [📸 参考: 09_c1_convert_hem_to_curve.jpg](../../docs/fusako_12_dress_drawers_screenshots/09_c1_convert_hem_to_curve.jpg)

### 2-5. Curveモディファイアによる巻きつけ＆ティルト調整
- フリルオブジェクトに `Curve` モディファイアを追加し、ターゲットに裾カーブオブジェクトを指定。
- 裾カーブに沿ってフリルがぐるりと一周巻きつく。
  - [📸 参考: 10_c1_curve_modifier_wrap.jpg](../../docs/fusako_12_dress_drawers_screenshots/10_c1_curve_modifier_wrap.jpg)
- カーブオブジェクトの編集モードに入り、全選択して `Ctrl + T`（Tilt）を実行。
- フリルの角度を外側斜め下へ自然に広げ、ふわっとしたスカート状の開きを演出。
  - [📸 参考: 11_c1_curve_tilt_ctrl_t.jpg](../../docs/fusako_12_dress_drawers_screenshots/11_c1_curve_tilt_ctrl_t.jpg)

---

## 第3章: LoopTools Bridge によるギャザー接合と完成

### 3-1. モディファイア確定適用と末端マージ
- フリルの `Array` と `Curve` モディファイアを上から順に `Ctrl + A` で確定適用。
- 編集モードで全選択し、`M` $\to$ `By Distance` で重なり頂点を溶接。1周の継ぎ目端点も `M`（Merge at Center）で綺麗に繋ぐ。
  - [📸 参考: 12_c1_apply_modifiers_merge_ends.jpg](../../docs/fusako_12_dress_drawers_screenshots/12_c1_apply_modifiers_merge_ends.jpg)

### 3-2. LoopTools Bridge によるギャザー成形
- ドロワーズ本体とフリルを選択し、`Ctrl + J` で統合。
- パンツ裾ループとフリル上端ループを同時に選択。
- 右クリック $\to$ `LoopTools > Bridge` を実行。
- フリル側が少し外側に広がっているため、接合部がキュッと絞られたリアルなゴムギャザー（しわ・クシュ感）が非破壊的に生成される。
  - [📸 参考: 13_c1_looptools_bridge_gather.jpg](../../docs/fusako_12_dress_drawers_screenshots/13_c1_looptools_bridge_gather.jpg)
- 両面描画（Two-Sided Shader）を前提とするため裏面は張らず、ペラペラの軽量仕様で完成。
  - [📸 参考: 14_c1_drawers_completed_view.jpg](../../docs/fusako_12_dress_drawers_screenshots/14_c1_drawers_completed_view.jpg)

---

## 第4章: ワンピース本体のモデリング（12頂点サークルベース）

### 4-1. 立ち絵リファレンスと12頂点サークル開始
- 正面・側面にワンピース着用状態の立ち絵画像を読み込み、半透明配置。
  - [📸 参考: 15_c2_onepiece_reference_overlay.jpg](../../docs/fusako_12_dress_drawers_screenshots/15_c2_onepiece_reference_overlay.jpg)
- 素体の胴体トポロジー（12頂点）に合わせ、`Shift + A` $\to$ `Mesh > Circle`（頂点数: `12`）を追加。
- 脇下の高さに配置し、`S + Y` で前後の厚みを少し平たく調整。
  - [📸 参考: 16_c2_circle_12verts_waist_base.jpg](../../docs/fusako_12_dress_drawers_screenshots/16_c2_circle_12verts_waist_base.jpg)

### 4-2. フレアスカート＆胸元の押し出し
- 下方向へ `E + Z` で押し出しつつ、`S` キーで拡大してAラインのフレアスカートを裾（ドロワーズの少し上）まで伸ばす。
- 上方向へ `E + Z` で押し出し、胸元・肩口・首元へ向けて徐々に広げながら立ち上げる。
  - [📸 参考: 17_c2_extrude_skirt_and_chest.jpg](../../docs/fusako_12_dress_drawers_screenshots/17_c2_extrude_skirt_and_chest.jpg)

---

## 第5章: アームホール＆ネックライン開口と肌スナップ貫通防止

### 5-1. アームホールの開口とTo Sphere真円化
- 腕の付け根（側面の4面）を選択し、`E + X` で外側にわずかに押し出す。
- 押し出した4面を `X` $\to$ `Faces` で削除し、腕を通すアームホールを開口。
  - [📸 参考: 18_c2_armhole_extrude_delete_faces.jpg](../../docs/fusako_12_dress_drawers_screenshots/18_c2_armhole_extrude_delete_faces.jpg)
- 開口部エッジループを選択し、`Shift + Alt + S`（球形化 / To Sphere）を押して `1.0` を入力。
- ガタついた四角い開口部が綺麗な円形・楕円形に整流される。
  - [📸 参考: 19_c2_to_sphere_armhole_rounding.jpg](../../docs/fusako_12_dress_drawers_screenshots/19_c2_to_sphere_armhole_rounding.jpg)

### 5-2. 首元の襟インセット＆ベベル
- 首元の開口部を `E + Z` で上へ押し出し。
- `I`（インセット）を実行。このとき `Boundary`（境界）のチェックを外すことで、中央シームに不要な面を作らずに襟の厚みを付与。
- 襟の角エッジを選択し、`Ctrl + B`（ベベル）で角を丸めて布の折り返し厚みを表現。
  - [📸 参考: 20_c2_collar_inset_and_bevel.jpg](../../docs/fusako_12_dress_drawers_screenshots/20_c2_collar_inset_and_bevel.jpg)

### 5-3. 素体頂点スナップによる貫通防止
- 首元とアームホールの奥側エッジループを選択。
- `Shift + Tab` でスナップをON（スナップ先: 頂点）にし、素体の首・肩の頂点にスナップ吸着させる。
- これにより服と肌の間に隙間や食い込みが一切なくなり、後から素体の隠れた面を削除しても貫通しない完全密閉構造が完成する。
  - [📸 参考: 21_c2_neck_arm_skin_snapping.jpg](../../docs/fusako_12_dress_drawers_screenshots/21_c2_neck_arm_skin_snapping.jpg)

---

## 第6章: スカート裾スカラップ（半円フリル）の配置と丈調整

### 6-1. スカラップ1ユニット（Circle 16）の作成
- `Shift + A` $\to$ `Circle`（頂点数: `16`）を追加。
- 面を張り（F）、インセット（I）を入れてから下半分を削除し、半円形のスカラップ（ホタテ貝状フリル）ユニットを作成。
  - [📸 参考: 22_c2_scallop_unit_circle_16.jpg](../../docs/fusako_12_dress_drawers_screenshots/22_c2_scallop_unit_circle_16.jpg)

### 6-2. 裾カーブへの自動巻きつけ（数12）
- ワンピース裾のエッジループを分離してカーブに変換。
- スカラップユニットに `Array`（数: `12`、ワンピースの12辺に対応）＋ `Curve` モディファイアを追加。
- 裾カーブに沿って12枚のスカラップが等間隔にぐるっと一周配置される。
  - [📸 参考: 23_c2_skirt_curve_wrap_scallop.jpg](../../docs/fusako_12_dress_drawers_screenshots/23_c2_skirt_curve_wrap_scallop.jpg)

### 6-3. スカラップの一体化とドロワーズ丈調整
- モディファイア確定後、ワンピース本体と `Ctrl + J` で統合。
- 頂点スナップでワンピース裾の頂点とスカラップ端点を吸着させ、`Merge by Distance` で完全溶接。
  - [📸 参考: 24_c2_scallop_vertex_snapping_merge.jpg](../../docs/fusako_12_dress_drawers_screenshots/24_c2_scallop_vertex_snapping_merge.jpg)
- **丈の黄金比率調整**:
  - ワンピース裾からドロワーズの裾フリルがチラリと可愛らしく覗くよう、ドロワーズ裾を `G + Z` で引き下げ、`Alt + S` でふっくら感を微調整。
  - [📸 参考: 25_c2_drawers_length_adjustment_gz.jpg](../../docs/fusako_12_dress_drawers_screenshots/25_c2_drawers_length_adjustment_gz.jpg)
  - [📸 参考: 26_c2_drawers_and_dress_complete.jpg](../../docs/fusako_12_dress_drawers_screenshots/26_c2_drawers_and_dress_complete.jpg)

---

## 第12話の成果と次工程への展望

- **完成した部位**:
  - **ドロワーズ**: 素体面複製 $\to$ かぼちゃパンツ膨らみ $\to$ 配列・カーブによるフリル一周 $\to$ Bridgeギャザー接合。
  - **ワンピース**: 12頂点円柱ベース $\to$ フレアスカート押し出し $\to$ To Sphereアームホール $\to$ 肌スナップ密閉 $\to$ 裾スカラップ12枚接合。
  - **重ね着バランス**: ワンピースの裾からドロワーズのフリルが絶妙に覗くプロポーション。
- **次回（第13話以降）への展望**:
  - インナー衣装が完成したため、上から羽織るアウター（パーカー・カーディガン・上着）や靴・ソックスのモデリングへと進みます。
