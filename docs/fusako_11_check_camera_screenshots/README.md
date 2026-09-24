# ふさこ氏チュートリアル第11話 重要シーン・スクリーンショットカタログ
## 『チェックカメラを使った印象合わせ 〜初級から中級者向けチュートリアル〜』

本ディレクトリは、ふさこ氏によるBlenderキャラクターモデリング講座第11話（[YouTube動画リンク](https://www.youtube.com/watch?v=oxADq6ZLCuQ)）から、チェックカメラの構築（中望遠80mm・正方形解像度）、立ち絵リファレンスの半透明重ね合わせ、アウトライナー誤操作防止ロック、頭頂部ボリューム・小顔化・目元角度のカメラ越し微調整、劇的ビフォーアフター比較などの決定的シーン（全17枚）を高解像度で抽出・整理した画像リファレンス集です。

詳細な操作手順やトポロジー設計の解説は、以下の仕様書を参照してください：
- 📘 **詳細手順・トポロジー仕様書**: [`../../.agents/handoffs/2026-09-24_fusako_check_camera_11_steps.md`](../../.agents/handoffs/2026-09-24_fusako_check_camera_11_steps.md)

---

### 📸 スクリーンショット一覧（全17枚）

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー） | 主な内容・重要操作・トポロジーのポイント |
|:---:|:---:|:---|:---|
| 01 | 00:00:15 | [./01_c1_intro_impression_mismatch.jpg](./01_c1_intro_impression_mismatch.jpg) | **印象合わせの必要性**: 直交投影（正射影）とイラストの間に生じる「印象の乖離」を説明し、Jump! Jun 3D ch直伝のチェックカメラ技法を導入。 |
| 02 | 00:00:35 | [./02_c1_add_camera_focal_length_80mm.jpg](./02_c1_add_camera_focal_length_80mm.jpg) | **カメラ追加と焦点距離80mm設定**: `Shift + A` でカメラを追加、`Alt + R` / `Alt + G` で初期化後、焦点距離を歪みの少ない中望遠 `80mm` に設定。 |
| 03 | 00:00:55 | [./03_c1_rx90_face_front_placement.jpg](./03_c1_rx90_face_front_placement.jpg) | **RX90による正面向き配置**: `R X 90` でカメラを正面に向け、横ビュー（テンキー3）を見ながら顔の真正面に配置。 |
| 04 | 00:01:10 | [./04_c1_split_window_numpad_0.jpg](./04_c1_split_window_numpad_0.jpg) | **ウィンドウ分割とカメラビュー表示**: 画面を左右に2分割し、左側でテンキー `0` を押して常時チェックカメラビューに切り替え。 |
| 05 | 00:01:25 | [./05_c1_resolution_square_1080.jpg](./05_c1_resolution_square_1080.jpg) | **正方形解像度（1080x1080）設定**: 出力プロパティ（プリンターアイコン）で解像度を正方形 `1080 x 1080` に設定し、顔のフィッティング枠を最適化。 |
| 06 | 00:01:45 | [./06_c1_duplicate_reference_stand_image.jpg](./06_c1_duplicate_reference_stand_image.jpg) | **立ち絵リファレンスの複製配置**: 立ち絵画像エンプティを `Shift + D` で複製し、`Y` 軸でカメラの手前（顔の前）へ移動。 |
| 07 | 00:02:40 | [./07_c1_overlay_reference_scale_fit.jpg](./07_c1_overlay_reference_scale_fit.jpg) | **カメラ越し半透明スケール合わせ**: カメラビューを見ながら、下絵の顎ライン・目のサイズが3Dモデルとおおむね重なるよう `S` キーで拡大縮小アライン。 |
| 08 | 00:03:30 | [./08_c1_outliner_selection_lock_arrow.jpg](./08_c1_outliner_selection_lock_arrow.jpg) | **アウトライナーでの下絵選択不可ロック**: 誤操作を防ぐため、フィルター（漏斗アイコン）の矢印をONにし、参考画像を選択不可にロック。 |
| 09 | 00:04:15 | [./09_c1_proportional_top_hair_lift_gz.jpg](./09_c1_proportional_top_hair_lift_gz.jpg) | **頭頂部＆ツインテール根元の引き上げ**: プロポーショナル編集（接続制限オフ）を使い、頭頂部の髪とツインテール根元を `G + Z` で持ち上げてボリュームUP。 |
| 10 | 00:04:55 | [./10_c1_cheek_hair_inward_gx_gy.jpg](./10_c1_cheek_hair_inward_gx_gy.jpg) | **頬沿い毛束の内側寄せ＆手前出し**: 頬の横の髪を `G + X` で内側へ寄せて小顔化し、`G + Y` で手前に出して立体感と陰影を強調。 |
| 11 | 00:05:25 | [./11_c1_side_hair_inward_gx.jpg](./11_c1_side_hair_inward_gx.jpg) | **サイドヘアの内側引き締め**: サイドの髪を `G + X` で内側に絞り込み、シルエットの広がりすぎを抑制。 |
| 12 | 00:05:50 | [./12_c1_ear_kemomimi_outer_placement.jpg](./12_c1_ear_kemomimi_outer_placement.jpg) | **耳・ケモ耳の外側張り出し**: 正面から見たときに耳とケモ耳の毛束がしっかり見えるよう、外側へ張り出し配置。 |
| 13 | 00:06:30 | [./13_c1_eye_contour_adjust_inward.jpg](./13_c1_eye_contour_adjust_inward.jpg) | **目の輪郭・アイラインの調整**: 下絵の切れ長・直線的な目元ラインに合わせ、目の内側輪郭をグイッと寄せる。 |
| 14 | 00:07:05 | [./14_c1_eye_scale_and_gy_depth.jpg](./14_c1_eye_scale_and_gy_depth.jpg) | **白目露出防止の目拡大＆奥配置**: 白目が不自然に露出しないよう、目オブジェクトを `S` 拡大し、`G + Y` で奥へ押し込んで肌と自然に交差。 |
| 15 | 00:07:35 | [./15_c1_eyelash_tilt_angle_shape.jpg](./15_c1_eyelash_tilt_angle_shape.jpg) | **まつ毛・目の傾き調整**: 単純な正円・楕円から、イラストの表情に合わせた微妙な角度傾き（ツリ目/タレ目）を成形。 |
| 16 | 00:08:10 | [./16_c1_before_after_comparison_split.jpg](./16_c1_before_after_comparison_split.jpg) | **調整前後のビフォーアフター比較**: 調整前（左）と調整後（右）の画面比較。頭部の豊かなボリュームと洗練された小顔・愛らしい目元の劇的変化。 |
| 17 | 00:08:25 | [./17_c1_completed_impression_fit_view.jpg](./17_c1_completed_impression_fit_view.jpg) | **チェックカメラ印象合わせ完成ビュー**: 立ち絵イラストと完全一致したプロ品質のキャラクターシルエットが完成。 |

---

### 💡 画像プレビューのコツ
各行のリンク `[./画像名.jpg](./画像名.jpg)` をクリックすると、Blender / VS Code / 各種Markdownビューア上で即座に高解像度画像が展開されます。
モデリング作業中、該当するトポロジーや操作UIの確認に直接ご活用ください。
