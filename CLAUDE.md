# GameModelGen — Claude Code 入口

どうぶつの森風ちびキャラをBlender(Python)で生成するプロジェクト。Claude Code と Antigravity(Gemini) がこのリポジトリを共有する。
このファイルは**入口のみ**。ルール本文は複製せず、下記の参照先を正とする。

## セッション開始時（この順に、これだけ読む）
1. **顔の作業なら `AnimeFace/STATE.md` と `AnimeFace/DESIGN.md`。** 現在の工程・ステップ・座標系・ゲート・下絵の使い分けがある。旧 `.blend` やアドオンは参考のみ
2. `.agents/shared_log.md` の**末尾のエントリのみ** — Geminiからの申し送り
3. 顔の背景（失敗の経緯）が必要なら `forCLAUDE.md`（Geminiの引き継ぎ）。ただし「3面が1px一致」の記述は**測定で否定済み**（DESIGN.md §3）
4. 胴体など顔以外で `Blender_HumanStudy/` を触るなら `Blender_HumanStudy/MODELING_GUIDELINE.md` の**現在の工程の節のみ**（全文は読まない）

上記以外（`handoffs/*.md`、`AI_LEARNING_RULES_FOR_GEMINI.md`、`AI_KNOWLEDGE_DB.md` 等）は、必要になった時に該当箇所だけ開く。

## 絶対ルール（モデリング作業）
1. モディファイアは Apply しない（例外: キューブスフィア化の初回 Subsurf Apply 1回のみ）
2. 頂点を動かす前に、トポロジー（段数・ループ数・頂点数）を決めて記録する。足りなければループカットが先
3. 1回の実行で1ステップ1変更。各ステップの合格ライン（頂点数・座標・シルエット差）を数値で確認してから次へ
4. 承認ゲートでユーザーの OK を得るまで次工程に進まない
5. 提出は「ケージワイヤー画像＋ソリッド画像＋頂点数・モディファイア構成」の事実のみ。「完成」「〇点」は書かない

## 検証（省略不可）
`py_compile` → `blender --background --python` → 生成物の数値検証（頂点数・スロット数）。出力を確認せず完了と言わない。

## 作業の終わりに
- `.agents/STATE.md` を更新（工程・ステップ・合否）
- Geminiへの申し送りがあれば `.agents/shared_log.md` に追記（フォーマットは `.agents/skills/ai-collaboration-protocol/SKILL.md`）
- コード差分は `git log` が正。ログには書かない

## ユーザーへの応対
- 日本語。回答は短く。ユーザーの指示は曖昧なことがあるので、重い処理の前は疑問点を先に数行で列挙する
- 意思決定（美的判断・承認）はログで済ませず必ずユーザーに確認する
