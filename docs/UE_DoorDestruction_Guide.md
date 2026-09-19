# 扉の破壊アニメを Unreal Engine 5 で再生する手順（レベルシーケンスで任意タイミング破壊）

> **状態**: Blender側の出力は再インポートで検証済み。**UE 5.3.2 では実機検証済み**（FBXインポート→スケルタルメッシュ/AnimSequence/スケルトン生成、扉の高さ約334cm＝スケール正常、アニメ長1.67秒・ボーントラック66本、`BP_<扉名>` の3コンポーネント構成と設定値をPython経由で読み戻して確認）。
> **検証済み(UE 5.3.2, Simulate)**: レベルシーケンスの Event トラック → Director BP（Set Visibility ×2 → Play）で、無傷扉が非表示・破壊メッシュが表示され、1.67秒のアニメが最後まで再生されることをPIEワールド内で確認。
> **未検証**: `BP_<扉名>` 内の `Break` カスタムイベント経由の呼び出し、`setup_door_destruction_sequence.py`（そのレベル専用シーケンス）。
> Blueprintのグラフノードは UE 5.3 の Python から作れないため `Break` / Director BP のグラフは手動です。

## 仕組み（全体像）
- 破壊の計算（Cell Fracture＋Rigid Body）は**すべてBlender側で事前に計算・焼き付け済み**。UEはそれを再生するだけ。
- 破片ごとに1ボーンのスケルタルメッシュ＋ボーンアニメ(毎フレーム)なので、回転しながら飛ぶ破片も歪みません。
- 破壊メッシュの初期姿勢(rest)は「破片が組み上がった状態」で、破片の隙間がヒビ状に見えます。
  そのため **破壊前は別の無傷メッシュ(LeavesIntact)を表示し、破壊時刻に入れ替える**構成にしています。

## 0. 推奨方式: Blueprintアクター（どのレベルでも使える）
扉一式を **1つのBlueprintアクター `BP_<扉名>`** にまとめ、`Break` を呼ぶと破壊されます。レベルに置くだけで使え、
ゲームプレイ(トリガー/レベルBP)からもレベルシーケンスからも同じ `Break` で破壊できます。
（§2 のシーケンス自動スクリプトは「そのレベルのアクターに結びつく」ため他レベルでは動きません。**通常は本方式を使ってください**）

### 0-1. Blueprintの作成
1. §1 でBlenderからFBX3点を出力
2. `ue_scripts/create_door_blueprint.py` の先頭（`FBX_DIR`, `NAME`, `CONTENT_DIR`）を編集し、`File > Execute Python Script...` で実行
   - FBXインポート＋ `BP_<NAME>`（Frame / LeavesIntact / Destruction の3コンポーネント）を自動作成
   - Destruction は最初 **非表示**、アニメは **Single Node・非ループ・停止** に設定済み
3. 自動作成に失敗した場合の手動手順: Actor継承のBlueprintを作り、コンポーネントを追加
   - `Frame`(StaticMesh) / `LeavesIntact`(StaticMesh) / `Destruction`(SkeletalMesh)
   - Destruction: `Visible` をOFF、Animation Mode = *Use Animation Asset*、Anim to Play = インポートしたAnimSequence、Looping = OFF

### 0-2. `Break` 関数（Blueprintのグラフは手動、ノード4つ）
BlueprintのグラフノードはPythonから作れないため、ここだけ手作業です。`BP_<NAME>` を開き、イベントグラフで:
1. **Custom Event `Break`** を作成（または関数 `Break` を作成）
2. `LeavesIntact` → **Set Visibility**（New Visibility = OFF）
3. `Destruction` → **Set Visibility**（New Visibility = ON, Propagate = ON）
4. `Destruction` → **Play**（Looping = OFF）
   - Break を実行順に 2 → 3 → 4 とつなぐ
5. （任意）**Custom Event `ResetDoor`**: LeavesIntact Visible=ON、Destruction Visible=OFF、Destruction `Stop` → `Set Position`(0.0)
6. コンパイル・保存

### 0-2b. 爆発・煙・埃・音（BPのコンポーネント、起動ノードは手動）
`BP_<NAME>` に次のコンポーネントを追加してある（すべて Auto Activate=OFF、位置は扉の中央 (0,0,150)cm）。スクリプト: 手順は下記のとおり `Activate` を呼ぶだけ。
| コンポーネント | 中身 | 用途 |
|---|---|---|
| `FX_Dust` | Niagara `/Game/Dungeon/FBX/NSdust` | 埃 |
| `FX_Explosion` | Cascade `P_Explosion`（スケール0.6） | 爆発 |
| `FX_Smoke` | Cascade `P_Smoke`（スケール0.8、位置は足元寄り） | 煙 |
| `SFX_Explosion` / `SFX_Collapse` | `Explosion_Cue` / `Collapse_Cue` | 爆発音／崩落音 |
- **起動**: `Break`（または Director BP）で、`Destruction` の `Play` の後ろに各コンポーネントの **`Activate`（Reset=ON）** をつなぐ（Targetは各コンポーネント）。
- `FX_Smoke` / `FX_Dust` は放っておくと出続けるので、`Delay`(2〜3秒) → `Deactivate` を付けるか、Niagara/Cascade 側の寿命を短くする。
- 中身は Details の Asset/Template/Sound を差し替えれば別のエフェクトに変えられる（位置・スケールも同じ場所で調整）。Niagara標準の `RadialBurst` は Activate しても動かなかったため外した。
- 共通の演出はBP側、そのカット専用の演出はSequencer側、と分けると管理しやすい。

### 0-3. 使い方
- **ゲームプレイ**: `BP_<NAME>` の参照から `Break` を呼ぶ（トリガーボリューム/レベルBP/他Blueprintなど）
- **レベルシーケンスで任意のタイミング破壊**:
  1. `BP_<NAME>` をレベルに置き、Sequencerへ追加
  2. そのバインディングに `+ Track > Event`（Event Track）を追加
  3. 破壊したい時刻にキーを打ち、キーを右クリック → **Quick Binding**（または Properties で Function）で **`Break`** を選ぶ
  4. 時刻を動かせばタイミング変更。シーケンス再生（PIE/Cinematic再生）で発火します
     （エディタのスクラブでは発火しないことがあります。PIEまたは Sequencer の再生で確認）
  - シーケンスを別レベルで使う場合: 該当レベルに `BP_<NAME>` を置いて再バインド、
    またはバインディングを右クリック → **Convert to Spawnable** にすると、シーケンスが扉を自動生成するので
    レベルに何も置かなくても動きます（どのレベルでも再生可）

---

## 1. Blenderでの出力
1. DOORカテゴリで扉を生成 → `Door_Frame`（または `Door_Leaf_L/R`）を選択
2. 「💥 破壊アニメーション」ボックスの `破片数/枚` と `フレーム数` を調整
3. **「💥 木っ端微塵に破壊してUE用FBX一括出力」** を押す
4. 出力先: `<出力タブのexport_folder>/<扉名>_UE/`（既存なら `_UE_01` …）
   - `<扉名>_Frame.fbx` … 石枠（Static Mesh）
   - `<扉名>_LeavesIntact.fbx` … 無傷の扉（Static Mesh）
   - `<扉名>_Destruction.fbx` … 破壊アニメ（Skeletal Mesh＋ボーンアニメ）
   - 3つとも **Door_Frame のローカル原点基準**（Blender上で扉を動かしていても原点・直立で出力されます）

## 2. UEで自動セットアップ（そのレベル専用のシーケンスを作るPythonスクリプト）
※ 作成されるシーケンスは**実行時に開いていたレベルのアクター**に結びつくため、他レベルでは動きません。汎用には §0 の Blueprint 方式を使ってください。
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
- **UV（2026-09-19〜）**: 3つのFBXすべてに UV0 が入っています。組み上がった扉(Door_Frameローカル空間)を基準に **1UV=1m のボックス投影**（前後面=X,Z／左右面=Y,Z／上下面=X,Y）で、破壊メッシュ・無傷の扉・石枠が同じ規則です。破片に割れても木目・石目が連続し、無傷の扉との継ぎ目も出ません。タイリングする木目・石のテクスチャをそのまま貼れます（大きさは UVTiling / TexCoord のスケールで調整）。ベイクしたテクスチャ用の重ならない一意UVではありません（必要なら別途対応）。
- 取り込み直すとき: Frame / LeavesIntact は同じパスへ上書き取り込みで更新できますが、Destruction（スケルタル）は同パス上書きだとAnimSequenceが更新されないため、新しいフォルダへ取り込んでBPの参照を切り替える（BPテンプレートとレベル上のインスタンス両方。インスタンスは旧形式の `skeletal_mesh` も含めて更新し、保存する）。

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
| PIEで何も起きない（エラーも出ない） | ①**Level Sequence Actor の Auto Play がOFF**（Details > 再生 > 自動プレイ をON。既定はOFFで、シーケンスがPIEで再生されない）。②**World Partition レベルで扉がプレイヤーから遠い**（Is Spatially Loaded=ON のアクターは約256m以遠だとPIEでロードされず、Level Sequence Actor だけ再生されてバインド先が無く空振りする）→ 扉の Details > `Spatially` で **Is Spatially Loaded をOFF**、または PlayerStart を扉の近くへ |
| 破壊時に破片がほとんど見えない／原点付近で点のように潰れる | **旧FBX(2026-09-19以前)の不具合**: `FBX_SCALE_NONE` だとArmature/Meshノードに100倍スケールが付き、UEはメッシュ頂点にだけ反映して**ボーン位置(メートル値)には反映しない**ため、骨が1/100になり破片が原点を軸に回って潰れる。現行の出力はメッシュ・ボーン・アニメを実寸(cm)に焼き込み、ノードスケール1で出力するので発生しない。古いFBXを取り込んでいたら**Blenderで再出力→UEで再インポート**（同じパスへの再インポートはアニメが更新されないので、既存のSkeletalMesh/Skeleton/AnimSequenceを削除してから取り込む）。確認: Skeletal Meshのバウンドが扉と同寸(高さ約334cm)で、ボーン(`Shard_###`)の位置が扉全体に散らばっていること |
| 破壊アニメで破片が数十m飛んで消える／アニメの途中で止まる | **旧版(2026-09-19以前)**は衝撃が強すぎ(破片の速度中央値約10m/s・飛距離中央値25m)、床が20m四方で外へ落ち続けたため。現行は飛距離中央値が約1.4m・約2秒で静止する。**アニメ長(フレーム数)が短いと飛行中に止まる**ので、実物の扉では Blender パネルの「フレーム数」を60以上(既定70)にする。派手にしたい/大人しくしたい場合はパネルの **「飛散の強さ」**(既定1.0。0.5=ほぼその場に崩れる、2.0=派手に飛び散る)を変えて再出力 |
| 「質量がない」ように軽く飛ぶ | 質量は設定済み(木片0.25〜0.55kg、鉄金具3.2kg)。ただし衝撃はフォースフィールドで与えるため、加速度=力÷質量で**軽い破片ほど速く飛ぶ**。現行は力の届く距離を制限し(0.8〜4m)、小さい破片ほど空気抵抗(減衰)を強くしている |
| アセットを差し替えたのにPIEで古い見た目のまま | レベル上のBP実体(インスタンス)が古いメッシュ/アニメへの参照を持っていることがある。BPテンプレートだけでなく、レベル上のインスタンスの Destruction コンポーネントの Skeletal Mesh / Anim to Play も新アセットになっているか確認 |
| Director BP の Set Visibility/Play が効かない | Set Visibility は **Scene Component 版**（Widget版ではない）。Targets は `self` のままにせず、イベントの `BP Op Door` ピンから `Get Destruction` / `Get LeavesIntact` をつなぐ。最初の Set Visibility にも実行ピンをつなぐ |

## 6. Blender側パラメータ
- `破片数/枚`（既定16。実際は目安より多く生成される）、`フレーム数`（既定70。UEでのアニメ長に直結）
- ボーン数 = 破片数(左右合計)+鉄部2+root。多くても数百ボーン程度で、UEは問題なく扱えます。
