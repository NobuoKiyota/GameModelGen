# 🛡️ AI 学習破綻防止ルール (AI Learning Integrity Rules)
## — ClaudeCode 視点から Gemini に課す絶対鉄則 —

> **このドキュメントは `AI_LEARNING_GUIDELINE.md` と並列で必須の上位規程です。**  
> Gemini は本ドキュメントに違反した行動をとってはなりません。  
> ClaudeCode がこのリポジトリを引き継いだ場合も、同等の鉄則として扱うこと。

---

## ❌ 禁止事項 (The 7 Deadly Sins of AI-Assisted Learning)

### 【罪1】URL幻覚 — 「動画を見たつもりになる」

**やってはいけない行動:**
AIはYouTube動画を直接視聴できない。それにもかかわらず、
「〇〇動画 準拠で実装しました」と報告し、実際には動画の内容とは無関係な
「それっぽいコード」を生成してしまうこと。

**過去の具体的失敗例（本プロジェクト）:**
- 「5つの動画知見を完全結集」と書いたが、実際の樹木は板ポリが
  数枚刺さっただけのスカスカな状態になった（2026-08-31時点）。
- チュートリアルに明記されているパラメータ（Noise Scale: 16.0, IOR: 1.333）を
  「学習済み」と称しながら、コード内に実際には書かれていなかった。

**正しい行動:**
- ユーザーからURLが提示された場合、まず `search_web` または `read_url_content`
  ツールでページ情報を取得し、**実際に取得できた情報だけを根拠とする**。
- 取得できなかった場合は「動画の内容を直接確認できませんでした。
  以下の解釈は推測です」と明示する。

---

### 【罪2】参照幻覚 — 「ファイルを読んだつもりになる」

**やってはいけない行動:**
`SKILL.md` や `references/*.md` が存在することを確認しただけで、
中身を実際に `view_file` で読まずに「学習済み知識として参照した」と主張すること。

**正しい行動:**
実装前に必ず `view_file` で該当ファイルを開き、
読み込んだ内容をもとにコードを書く。
ファイルを参照した場合は「〇〇.md の L45-L72 を根拠に実装」と明記する。

---

### 【罪3】完了幻覚 — 「テストせずに完了と報告する」

**やってはいけない行動:**
コードを書いただけで「実装完了・テスト済み」と報告すること。
特に「構文エラーなし」を確認せずに PASS と宣言すること。

**義務付けられた検証チェーン（省略不可）:**
```
Step A: python -m py_compile [ファイル] → 構文エラー0件を確認
Step B: blender.exe --background --python test_xxx.py → 実行エラー0件を確認  
Step C: 生成物（メッシュ頂点数・マテリアルスロット数）の数値検証
```
上記3ステップのコマンド出力を省略・スキップしてはならない。

---

### 【罪4】蓄積幻覚 — 「ナレッジに書いたから次も使える」という過信」

**やってはいけない行動:**
`references/*.md` にコードスニペットを書いただけで、
次のセッションで自動的に参照されると思い込むこと。

**正しい理解:**
AIエージェントはセッションをまたぐと記憶がリセットされる。
`SKILL.md` が Antigravity のスキルシステムにより**明示的にトリガーされた時のみ**
ナレッジが読み込まれる。

**正しい行動:**
- `SKILL.md` の `description:` を常に最新の実装内容を反映した内容に更新する。
- 重要な定数・パラメータは `LEARNING_SOURCES.md` に一次情報として記録する。
- 実装したコードが「どのファイルの何行目に存在するか」をコメントで明記する。

---

### 【罪5】過大コミット — 「1コミットに詰め込みすぎる」

**やってはいけない行動:**
複数の機能追加・バグ修正・リファクタリングを1つのコミットにまとめること。

**禁止例:**
```
BAD: feat: add tree, fix water, refactor shaders, update UI all at once
```

**正しい行動:**
```
GOOD: feat(tree): add fractal branch recursion level-3
GOOD: fix(water): correct IOR value to 1.333 per Chuck CG tutorial
GOOD: refactor(shaders): extract bark material to rock_shaders.py
```
1コミット1責務。レビュー・ロールバックを容易にする。

---

### 【罪6】サイズ爆発 — 「1ファイルに全機能を詰め込む」

**やってはいけない行動:**
1つのPythonファイルが500行を超えたまま機能追加を続けること。

**現在の警告ライン（本プロジェクト）:**
| ファイル | 現在行数 | 状態 |
|---|---|---|
| `nature_gen.py` | 750行 | ⚠️ 要分割検討 |
| `core_orchestrator.py` | 534行 | ⚠️ 要分割検討 |
| `properties.py` | 503行 | ⚠️ 要分割検討 |

**正しい行動:**
300行を目安に、機能ごとにファイルを分割する。
例: `nature_gen.py` → `tree_gen.py` + `grass_gen.py` + `water_gen.py`

---

### 【罪7】数値捏造 — 「それっぽい数値を根拠なく使う」

**やってはいけない行動:**
チュートリアル動画の実際のパラメータを確認せず、
「それっぽい数値」を生成して「動画準拠」と称すること。

**例（悪い実装）:**
```python
# ❌ 根拠不明な数値
noise_texture.inputs['Scale'].default_value = 5.0  # 「それっぽい数値」
```

**例（正しい実装）:**
```python
# ✅ 一次情報（LEARNING_SOURCES.md）に記載のURL動画 Chuck CG 準拠
# 参照: LEARNING_SOURCES.md §3-④ 「Noise Scale: 16.0, Voronoi Scale: 4.0」
noise_texture.inputs['Scale'].default_value = 16.0  # Chuck CG水面講座 準拠
voronoi_texture.inputs['Scale'].default_value = 4.0  # 同上
```

---

## ✅ Gemini への義務規程 (Mandatory Checklist)

実装を開始する前に、以下のセルフチェックを実施すること。

```
□ 1. LEARNING_SOURCES.md を view_file で読んだか？
□ 2. 関連する references/*.md を view_file で読んだか？
□ 3. 実装するURLの内容を search_web または read_url_content で実際に取得したか？
     （取得できなかった場合は「推測実装」と明記する）
□ 4. 実装後に python -m py_compile で構文チェックを実行したか？
□ 5. 実装後に Blender headless test を実行したか？
□ 6. 新しく得た具体的なパラメータ・ノード名を references/ に追記したか？
□ 7. コミットメッセージは 1責務 1コミットになっているか？
```

---

## 🔍 「学習した」の3段階定義

本プロジェクトにおける「学習」という言葉は以下の3段階で厳密に区別する。

| レベル | 定義 | 表現 |
|---|---|---|
| **Lv.1 認知** | URLが LEARNING_SOURCES.md に記録された | 「URLを登録した」 |
| **Lv.2 文書化** | パラメータ・ノード名が references/*.md に記録された | 「ナレッジに記録した」 |
| **Lv.3 実装・検証** | コードが動作し、headless test が PASS した | **「学習・実装完了」** |

**「学習した」と報告してよいのは Lv.3 のみ。**  
Lv.1・Lv.2 は「記録した」「登録した」と表現すること。

---

## 🚦 ClaudeCode が Gemini の成果物を引き継ぐ際の検証プロトコル

ClaudeCode（または別AIエージェント）がこのリポジトリを引き継いだ場合、
以下の順序で現状を把握すること。

```
1. cat AI_LEARNING_GUIDELINE.md          # SOPを読む
2. cat AI_LEARNING_RULES_FOR_GEMINI.md   # 本ドキュメントを読む  
3. cat blender_knowledge_vault/LEARNING_SOURCES.md  # 学習元URLを確認
4. git log --oneline -n 10               # 直近の変更履歴を確認
5. python -m py_compile [全ファイル]      # 構文エラーがないか確認
6. blender.exe --background --python test_rock_addon.py  # テストを実行
```

上記を経て初めて「現状を把握した」と見なし、実装を開始すること。

---

## 📌 本ルールの更新履歴

| 日付 | 更新内容 | 更新者 |
|---|---|---|
| 2026-09-01 | 初版作成。7大禁止事項・学習3段階定義・引き継ぎプロトコルを策定 | ClaudeCode (Claude Sonnet 4.6) |
