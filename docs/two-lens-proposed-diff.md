# PXL / DICT 二層テンプレ 提案 diff（本体無改変）

- **作成日**: 2026-08-25
- **作成者**: Opus 4.7 (1M context)
- **本ファイルは提案であり、本体（`docs/index.html` / `docs/dict/index.html`）は一切改変していない**
- **適用は次回の FROZEN.md 再開ゲート（条件 1 / 2 / 3 のいずれか発動時）で人間承認を経てからのみ**
- 参考実装: `internals-command-deck` の 6 ラボで既に本番稼働中の同パターン（`public/*-lab.html` の `<section id="user-view">` + `renderUserView()` + `.uv-hero` / `.qtcard` / `.glossitem`）

## 背景と動機

Deck 6 ラボ（buds / nest / home / fitbit / watch / pixel-android-issues）に「専門家視点＋ユーザー視点」の二層テンプレを導入した（Job2 / 2026-08-25 push 済み）。同じ品質基準を PXL（諸元）/ DICT（不具合辞書）にも揃えれば、リファレンス全体が「今日その端末を安全に使えるか」の一行結論を最上位に置ける。

ただし PXL / DICT は `docs/FROZEN.md` line 47 の「機能追加はしない」対象。UI 拡張・スキーマ拡張は再開ゲート案件のため、本ファイルは実装提案のみ記録する。

## 提案する二層テンプレの構造

Deck 側で既に稼働中のパターンを踏襲する:

```
[ 既存 hero / meta ]
  ↓
<section id="user-view">                    ← 新規（常時表示）
  <div class="uv-hero {green|yellow|red}">
    <span class="vb vb--{v|u|r}">今日 安全に使える / 注意 / 控える</span>
    <p>一行結論</p>
  </div>
  <h3>症状 → まず試す 3 手順（逆引き）</h3>
  <div class="uv-cards"> ... </div>
  <h3>やってはいけない</h3>
  <ul class="uv-list"> ... </ul>
  <h3>用語の一言注釈</h3>
  <div class="uv-glos"> ... </div>
</section>
  ↓
[ 既存 具体詳細（PXL: 諸元スライダー / DICT: 検索/フィルタ/辞書） ]
```

## 提案 diff 案 A: PXL (`docs/index.html`)

### データ側（新規追加・既存無改変）

PXL は現状データ実体を HTML 内に直接記述している。二層テンプレのため以下の 2 択:

- **A-1**: HTML の `<script>` 内に `PXL_USER_VIEW` 定数を新規追加。既存の諸元テーブル生成コードは不変。
- **A-2**: 新規 JSON ファイル `docs/data/pxl-user-view.json` を作成し、`docs/index.html` から fetch する。既存構造への影響最小。

A-2 推奨（データと表示の分離、Deck パターンと整合）。

### HTML/CSS/JS 差分（提案）

```diff
--- a/docs/index.html
+++ b/docs/index.html
@@ style末尾 @@
+/* two-lens: user-view (top) */
+#user-view{margin:14px 0}
+.uv-hero{border:1px solid var(--border);border-radius:14px;background:var(--panel);padding:14px;
+  display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
+.uv-hero.green{border-left:4px solid var(--good)}
+.uv-hero.yellow{border-left:4px solid var(--warn)}
+.uv-hero.red{border-left:4px solid var(--bad)}
+.uv-hero p{color:var(--text);font-size:13px;line-height:1.6;margin:0}
+.uv-h{font-weight:850;font-size:15px;margin:14px 0 8px;color:var(--text)}
+.uv-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
+.qtcard{border:1px solid var(--border);border-radius:12px;background:var(--panel);padding:12px}
+.qtcard h3{font-size:14px;margin-bottom:8px}
+.qtcard ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:5px}
+.uv-list{border-left:4px solid var(--bad);border-radius:10px;padding:12px 12px 12px 32px}
+.uv-glos{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px}
+.glossitem{border:1px solid var(--border);border-radius:8px;padding:8px 10px}
+.vb--r{border:1px solid var(--bad);color:var(--bad)}
@@ body 冒頭 <h1>Pixelの諸元</h1> の直後 @@
+<section id="user-view" aria-label="ユーザー視点"></section>
@@ script 内 @@
+function safeBadge(uv){ /* Deck 側 buds-lab.html:220-225 と同一実装 */ }
+function renderUserView(uv){ /* Deck 側 buds-lab.html:227-241 と同一実装 */ }
+// DOMContentLoaded で fetch('/taka-pixel-reference/data/pxl-user-view.json') → renderUserView(uv)
```

### 提案 userView データ内容（PXL 版）

```json
{
  "safeToUse": {
    "status": "green",
    "oneLine": "5a 以前は EOL 済 = 銀行・決済不可。6a / 7a は 5 年、8a 以降は 7 年保証。今日買うなら 8a 以降。"
  },
  "quickTriage": [
    { "symptom": "手持ちの機種の EOL を確認したい", "steps": ["諸元表の各機種の EOL 列を確認", "赤線（今日）より左で終わるバーは要更新", "8a 以降ならまだ 7 年保証"] },
    { "symptom": "コードネーム / Factory Image を探したい", "steps": ["Pixel 諸元スライドで機種を選択", "コードネーム欄を確認", "Factory / OTA は developers.google.com/android/images"] },
    { "symptom": "開発者オプションを使いたい", "steps": ["設定 > 端末情報 > ビルド番号を 7 回タップ", "開発者オプション有効化後、必要な項目のみ ON", "本ページの「開発者オプション詳細」表で分類を確認"] }
  ],
  "dontDo": [
    "サポート終了 (EOL) 済み端末を主機として使わない（銀行 / 決済 / メール 2FA が危険）",
    "Pixel 11 系のコードネーム PENDING を勝手に埋めない（Google 公式反映まで待つ）",
    "開発者オプションのフラグを本番端末で常時 ON にしない（電池 / 挙動が変わる）"
  ],
  "glossary": [
    { "term": "EOL", "note": "End of Life。ソフトウェア更新の提供終了" },
    { "term": "Factory Image", "note": "端末を出荷状態に戻すための公式イメージ" },
    { "term": "OTA", "note": "Over The Air。無線経由の更新パッケージ" },
    { "term": "コードネーム", "note": "Pixel 機種の内部識別名（例: husky = Pixel 8 Pro）" },
    { "term": "ARB", "note": "Anti-Rollback。旧ビルドへの巻き戻しをファーム側で禁止する仕組み" }
  ]
}
```

## 提案 diff 案 B: DICT (`docs/dict/index.html`)

### データ側（新規追加・既存無改変）

DICT は既に `docs/dict/data/builds.json` と `entries.json` を持つ。二層テンプレ用は別ファイル `docs/dict/data/user-view.json` に分離（既存 builds.json / entries.json は完全無改変）。

### HTML/CSS/JS 差分（提案）

```diff
--- a/docs/dict/index.html
+++ b/docs/dict/index.html
@@ style末尾 @@
+/* two-lens: user-view (top) — 上記 PXL と同一 CSS */
+#user-view{...}
+...
@@ body内 <h1>不具合辞書 ...</h1> の直後 @@
+<section id="user-view" aria-label="ユーザー視点"></section>
@@ script 内 @@
+function safeBadge(uv){ /* 同一 */ }
+function renderUserView(uv){ /* 同一 */ }
+// fetch('/taka-pixel-reference/dict/data/user-view.json') → renderUserView(uv)
```

### 提案 userView データ内容（DICT 版）

```json
{
  "safeToUse": {
    "status": "yellow",
    "oneLine": "収録は「公式修正 or 公式回避策 or 再現手順ログ」の 3 条件を満たすもののみ。噂・未検証情報は含まれない。"
  },
  "quickTriage": [
    { "symptom": "特定のビルド番号の不具合を調べたい", "steps": ["「ビルド番号で引く」セクションで番号入力", "該当ビルドの不具合エントリ一覧を確認", "confidence バッジ (OFFICIAL/MULTI_SOURCE/SINGLE_SOURCE) で信頼度確認"] },
    { "symptom": "自分の Pixel でどの層が原因か調べたい", "steps": ["共通構造図で層 (Kernel/HAL/Framework/App) を確認", "症状の分類フィルタで絞り込み", "該当エントリの primaryCauses / actions を読む"] },
    { "symptom": "ARB 影響で戻せない状況を避けたい", "steps": ["対象ビルドの anti_rollback.incremented を確認", "true なら旧ビルドへの巻き戻し不可", "更新前にバックアップと業務影響評価を実施"] }
  ],
  "dontDo": [
    "confidence=SINGLE_SOURCE のエントリだけを根拠に業務判断しない（追加ソースを求める）",
    "human_review=true のフラグを無視しない（自動判定で埋まらなかった箇所は要人間確認）",
    "凍結中の本辞書に非公式なエントリを直接追加しない（FROZEN.md line 47 違反）"
  ],
  "glossary": [
    { "term": "confidence", "note": "OFFICIAL/MULTI_SOURCE/SINGLE_SOURCE の 3 段階" },
    { "term": "evidence_level", "note": "エントリの証拠の強さ（OFFICIAL/MULTI_SOURCE/REPORTED_ONLY）" },
    { "term": "human_review", "note": "自動判定で埋められず人間による再確認が必要なフラグ" },
    { "term": "region_scope", "note": "ビルドの地域配布範囲（global / Japan / Rogers 等）" },
    { "term": "AOSP tag", "note": "Android Open Source Project のバージョンタグ。実配信ビルド ID と異なることがある" }
  ]
}
```

## 適用時の Verifier ゲート要件

- 対象ファイル実存 / 追記中心で既存 VERIFIED 行の非破壊
- JSON / JS パース成功
- 3 テストランナー全緑（test_contract 24 + test_suffix_map 23 + test_suffix_fallback 13 = **60/60 継続**）
- 既存の `builds.json` / `entries.json` は完全無改変（差分ゼロを機械確認）
- 新規トップレベル名 (`renderUserView` / `safeBadge` / `#user-view` / `.uv-*` / `.qtcard` / `.glossitem` / `.vb--r`) の grep 衝突なし
- 描画確認: ローカルプレビューで白画面なし・コンソールエラーなし
- 判断ログ (`data/build-dict-decisions.md`) への追記必須（FROZEN.md line 47 に基づく）

## 適用しない場合

「一次リファレンスとしてデータの正確性のみで十分」という判断であれば本提案は棄却で問題ない。Deck 側で二層テンプレを提供しているため、ユーザー視点導線は Deck から reference への深堀りで維持される。棄却する場合は本ファイルを削除、または `docs/two-lens-rejected-YYYYMMDD.md` にリネームして判断日を残す。
