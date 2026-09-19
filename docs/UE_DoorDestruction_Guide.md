# 扉の破壊アニメを Unreal Engine 5 で再生する手順（レベルシーケンスで任意タイミング破壊）

> **状態**: Blender側の出力（ボーン構造・アニメ・寸法・原点）は再インポートで検証済み。
> **UE側は作成環境にUEが無く未検証**です。動かない箇所があれば、UEの Output Log のエラー文を共有してください。

## 仕組み（全体像）
- 破壊の計算（Cell Fracture＋Rigid Body）は**すべてBlender側で事前に計算・焼き付け済み**。UEはそれを再生するだけ。
- 破片ごとに1ボーンのスケルタルメッシュ＋ボーンアニメ(毎フレーム)なので、回転しながら飛ぶ破片も歪みません。
- 破壊メッシュの初期姿勢(rest)は「破片が組み上がった状態」で、破片の隙間がヒビ状に見えます。
  そのため **破壊前は別の無傷メッシュ(LeavesIntact)を表示し、破壊時刻に入れ替える**構成にしています。

## 1. Blenderでの出力
1. DOORカテゴリで扉を生成 → `Door_Frame`（または `Door_Leaf_L/R`）を選択
2. 「💥 破壊アニメーション」ボックスの `破片数/枚` と `フレーム数` を調整
3. **「💥 木っ端微塵に破壊してUE用FBX一括出力」** を押す
4. 出力先: `<出力タブのexport_folder>/<扉名>_UE/`（既存なら `_UE_01` …）
   - `<扉名>_Frame.fbx` … 石枠（Static Mesh）
   - `<扉名>_LeavesIntact.fbx` … 無傷の扉（Static Mesh）
   - `<扉名>_Destruction.fbx` … 破壊アニメ（Skeletal Mesh＋ボーンアニメ）
   - 3つとも **Door_Frame のローカル原点基準**（Blender上で扉を動かしていても原点・直立で出力されます）

## 2. UEで自動セットアップ（Pythonスクリプト・推奨）
1. UE5: `Edit > Plugins` で **Python Editor Script Plugin** を有効化 → 再起動
2. `ue_scripts/setup_door_destruction_sequence.py` の先頭の設定を編集
   - `FBX_DIR`（出力フォルダ）、`NAME`（`<扉名>`）、`DESTROY_TIME_SEC`（破壊時刻）、`FPS`（Blenderのfps、既定24）
3. `File > Execute Python Script...` でそのファイルを実行
4. 完了後、`/Game/DoorDestruction/LS_DoorDestruction` を開く
5. 失敗したステップは Output Log に「手動手順」付きで表示されます → 以下の手動手順で補ってください

## 3. UEで手動セットアップ

### 3-1. FBXインポート（3ファイルとも Content Browser にドラッグ or Import）
| ファイル | Import設定 |
|---|---|
| `_Frame.fbx` / `_LeavesIntact.fbx` | Skeletal Mesh: **OFF**（Static Mesh）、Combine Meshes: ON |
| `_Destruction.fbx` | **Skeletal Mesh: ON**、**Import Animations: ON**、Skeleton: None(新規作成)、Import Morph Targets: OFF、Create Physics Asset: OFF |
共通: Import Uniform Scale = 1.0。**Convert Scene / Force Front XAxis はOFF**（Blenderは -Y forward / Z up で出力済み）。
- インポート後、Destruction の隣に `AnimSequence` が作られます（破壊アニメ本体）。
- 扉の高さが極端(100倍)に違う場合は Import Uniform Scale を 0.01 / 100 に。

### 3-2. マテリアル
- ブレンダーのプロシージャルノードはFBXでは転送されません。マテリアルスロット名は
  `<扉名>_Stone_Mat` / `_Wood_Mat` / `_Iron_Mat` です。UEで同名スロットに好みのマテリアルを割り当ててください。
- Blenderの「Auto PBR Baker」（📦出力タブ）でテクスチャをベイクして持ち込むこともできます（本機能では自動化していません）。
- LeavesIntact と Destruction は同じ Wood/Iron マテリアルを割り当てると、破壊の瞬間の入れ替わりが目立ちません。

### 3-3. レベルへ配置
1. `Frame`(Static)、`LeavesIntact`(Static)、`Destruction`(Skeletal) を**同じ位置(原点)**へ配置（回転・スケールも揃える）

### 3-4. レベルシーケンス
1. `Cinematics > Level Sequence` を作成して開く（表示レートは Blender と同じ 24fps 推奨）
2. Sequencer へ `Door_Destruction`、`Door_LeavesIntact`（必要なら `Door_Frame`）を追加
3. **Door_Destruction**
   - `+ Track > Animation` → インポートされた AnimSequence を選択
   - このアニメーションセクションを**破壊したい時刻へドラッグして移動**（= 任意のタイミング破壊）
   - セクションの右端を**シーケンス終端まで伸ばす**（アニメ終了後に組み上がった姿勢へ戻らず、最終姿勢を保持）。ループしていたらセクション詳細で Looping をOFF
4. **破壊前後の見た目の入れ替え**（Actor Hidden In Game）
   - `Door_LeavesIntact` に `+ Track > Actor Hidden In Game`（Visibility）→ 破壊時刻で **Hidden=ON**
   - `Door_Destruction` に同トラック → 最初は **Hidden=ON**、破壊時刻で **OFF**
   - 切替キーの時刻は、アニメーションセクション開始の**同じフレーム**に合わせる
5. 再生して確認

## 4. 破壊タイミングの変更
- アニメーションセクションと、2つの Visibility の切替キーを**同じ量だけ**動かせばOKです。
- スクリプトで作った場合は `DESTROY_TIME_SEC` を変え、既存の `LS_DoorDestruction`（とレベル上の3アクター）を削除してから再実行するのが簡単です（同名アセットがあるとシーケンス作成が失敗します）。

## 5. よくある不具合
| 症状 | 対処 |
|---|---|
| スケルトンに `Armature` などの余計なルートが付く | Blenderは出力時に一時的に Armature 名・原点にしています。UEのSkeleton Treeで根が `root` 以外になっていたらインポート設定（Import Meshes in Bone Hierarchy等）を確認し、共有してください |
| 扉が寝ている/向きが違う | Convert Scene / Force Front XAxis をOFFにして再インポート |
| サイズが100倍/1/100 | Import Uniform Scale を調整 |
| 破壊アニメが再生されない | AnimSequence が生成されているか、Animation トラックのセクションが破壊時刻に置かれているか確認 |
| 破壊後に組み上がった(ヒビ入り)扉に戻る | Animationセクション右端をシーケンス終端まで延長／Looping OFF |
| 破壊前の扉にヒビ線が見える | Destruction を破壊時刻まで Hidden にし、LeavesIntact を表示しているか確認 |

## 6. Blender側パラメータ
- `破片数/枚`（既定16。実際は目安より多く生成される）、`フレーム数`（既定70。UEでのアニメ長に直結）
- ボーン数 = 破片数(左右合計)+鉄部2+root。多くても数百ボーン程度で、UEは問題なく扱えます。
