# UPDATE-004: 不具合辞書システム構築 — 完結型指示書

作成日: 2026-07-24
対象リポジトリ: ~/taka-pixel-reference（GitHub Pages: main /docs）
目的: 整備手帳とは別ページとして「不具合×対処法 辞書」を新設する。**思想: 1000件を書くのではなく、1000件が貯まって腐らない構造を先に作る。** データ(JSON)と表示(HTML)を分離し、A-Z索引・あいうえお索引・全文検索・カテゴリ/重要度フィルタを備える。既存の整備手帳の不具合項目（#os-bugs / #ts / #ts-pro）を初期データとして全件移植する。
新URL: `https://reanimatedead.github.io/taka-pixel-reference/dict/`

---

## 絶対ルール（全エージェント共通）

1. 各エージェント作業前後に `git status`、開始前に `git pull origin main`
2. コミットは小さく安全に、メッセージは英語
3. **`git push` は人間ゲート。エージェントは実行しない**
4. 既存の `docs/index.html`（整備手帳）は本指示書で明示した1箇所以外変更しない
5. データ移植時、**元の記述内容・VERIFIED/UNVERIFIED状態・出典を改変しない**。要約可、創作禁止
6. 新規項目の追加は本指示書ではゼロ件。件数を増やすのは今後の月例運用（収録基準に従う）
7. `.env` 系への接触禁止

---

## データスキーマ（この定義が本プロジェクトの本体。厳守）

`docs/dict/data/entries.json` — 配列。1項目:

```json
{
  "id": "PXD-0001",
  "title_ja": "タッチ操作異常（スワイプ方向逆転・無反応）",
  "title_en": "Touch input anomaly",
  "yomi": "たっちそうさいじょう",
  "category": "画面・タッチ",
  "severity": "high",
  "affected_models": ["6a","7a","8a","9a","10a"],
  "affected_os": ["17"],
  "symptom": "上下スワイプの方向逆転、タップ無反応、入力の過剰認識/欠落がシステム全体で突発する。",
  "cause": "Android 17 初期版のシステム側バグ。画面ハードの故障ではない。",
  "workaround": [
    "アクセシビリティのトリプルタップ(拡大操作)をOFF",
    "Pixel Launcher のキャッシュ削除",
    "改善なければ修正パッチ待ち。修理に出さない"
  ],
  "fix_status": "open",
  "first_seen": "2026-06",
  "last_checked": "2026-07-24",
  "verify_state": "VERIFIED",
  "sources": [{"url": "https://...", "date": "2026-07-24"}]
}
```

フィールド規約:
- `id`: PXD-連番4桁。欠番禁止・再利用禁止
- `yomi`: title_ja のひらがな読み。**あいうえお索引の生成キー**。長音・記号は除去、英字始まりの項目は読みを充てる（例: Wi-Fi → わいふぁい）
- `category`: 次の10分類のみ使用可 — 電源・起動 / 画面・タッチ / 通信 / バッテリー・充電・発熱 / 音・通話 / カメラ / 生体認証 / アプリ挙動 / OS更新起因 / 物理・破損
- `severity`: critical（データ喪失・文鎮） / high（主要機能停止） / medium（機能低下） / low（軽微）
- `fix_status`: patched / open / wontfix / spec（仕様であり不具合でない）
- `verify_state`: 移植元の状態を維持。新規はUNVERIFIED開始が既定

**収録基準（辞書冒頭にも表示する）**: ①独立した複数ソースで報告 ②再現時に実害がある ③対処法または回避策が記述できる — 3条件を満たすもののみ収録。満たさない情報は件数が欲しくても入れない。

---

## Agent 1: schema-and-data（データ移植担当）

1. `git pull origin main` → `git status`
2. `docs/dict/data/entries.json` を新規作成し、既存 `docs/index.html` の以下から**全不具合項目を移植**:
   - `#os-bugs`（A11〜A17 全項目）
   - `#ts` の機種別既知問題（4aバッテリー制限、5a電源ボタン、6a指紋/発熱/モデム、7a発熱/ちらつき、8a緑かぶり、9aバッテリーロット、Fold初代の画面/保護層 等）
   - `#ts-pro` 内で不具合として扱える項目
3. 各項目の sources は `data/sources.md` の対応URLを転記。対応が特定できない場合 sources は空配列にし verify_state を UNVERIFIED に落とす（勝手にURLを充てない）
4. `python3 -m json.tool docs/dict/data/entries.json > /dev/null` で構文検証
5. `data/dict-migration.md` に「移植元→ID対応表」と件数を記録
6. コミット: `Add defect dictionary schema and migrate existing entries`
7. `git status`

## Agent 2: renderer-builder（表示・検索担当）

1. `git status`
2. `docs/dict/index.html` を新規作成（単一ファイル、外部依存はGoogle Fontsのみ）:
   - デザイントークンは整備手帳と同一（CSS変数・Zen Kaku Gothic New + IBM Plex Mono をコピー）
   - fetch で `./data/entries.json` を読み描画（ビルド工程なし・GitHub Pagesでそのまま動く）
   - **必須UI**:
     a. 全文検索ボックス（title_ja / title_en / symptom / workaround を対象、入力即時絞り込み）
     b. **あいうえお索引**: あ〜わ行タブ。yomi の頭文字で分類（濁音・半濁音は清音に正規化: が→か）
     c. **A-Z索引**: title_en の頭文字タブ
     d. カテゴリ（10分類）・severity・fix_status・機種のフィルタ（複合適用可）
     e. 各項目カード: ID / タイトル / severity色帯（critical=--alert） / 対象機種・OS / 症状 / 原因 / 対処（番号付き） / fix_status / verify_state / 出典リンク / last_checked
     f. ヒット件数と総件数の常時表示（例: 42 / 47 件）
   - localStorage 等のブラウザストレージは使用しない
   - 冒頭に収録基準3条件と「網羅は目的でない。基準を満たす項目が貯まる構造が目的」の1文を表示
3. コミット: `Add dictionary renderer with kana/alpha indexes and search`
4. `git status`

## Agent 3: integration（整備手帳との接続）

1. `git status`
2. `docs/index.html` への唯一の変更: nav の `<li><a href="#ts-pro">専門TS</a></li>` の直後に `<li><a href="dict/">不具合辞書 ↗</a></li>` を追加
3. `docs/dict/index.html` のヘッダーに整備手帳へ戻るリンク `← 整備手帳` を配置
4. `README.md` に辞書の説明（URL / スキーマ場所 / 収録基準 / 追加手順: entries.json に追記→json.tool検証→push）を追記
5. コミット: `Link dictionary from main page and document schema ops`
6. `git status`

## Agent 4: qa-verifier（機械検証）

1. `git status`
2. 検証:
   - `python3 -m json.tool docs/dict/data/entries.json > /dev/null`（構文）
   - `python3` ワンライナーで: ID重複ゼロ / 全項目に yomi 存在 / category が10分類内 / severity・fix_status が規定値内 — 違反があれば Agent 1 に差し戻し修正
   - `npx html-validate docs/dict/index.html` エラー0
   - `npx wrangler` は使わない。`python3 -m http.server 8000 --directory docs` をバックグラウンド起動 → `curl -s localhost:8000/dict/ | grep -c 'entries.json'` = 1 → 終了
   - 移植件数が `data/dict-migration.md` の記録と JSON の実件数で一致
3. `data/qa-report.md` に追記、コミット: `Add QA results for dictionary`
4. `git status`

## Agent 5: git-reporter（統括・停止）

1. `git status` + `git log --oneline -6`
2. `REPORT-UPDATE-004.md` 作成:
   - 移植件数 / UNVERIFIED件数 / スキーマ検証結果
   - 人間ゲート（確認&&実行の連結形式）:
     ```bash
     python3 -m json.tool docs/dict/data/entries.json > /dev/null && git push origin main
     # 2〜3分後（CDN反映込み）:
     curl -s "https://reanimatedead.github.io/taka-pixel-reference/dict/?v=$(date +%s)" | grep -c 'entries.json'
     ```
   - 今後の拡張運用の明記: 「月例パッチ後、新規不具合は entries.json への追記のみ。HTMLは触らない。収録基準3条件を満たさないものは追加しない」
3. コミット: `Add dictionary build report` → **停止**

## 完了条件

- [ ] docs/dict/ に data/entries.json と index.html が存在
- [ ] 既存不具合の全件移植（想定40件前後）・新規創作ゼロ
- [ ] あいうえお索引 / A-Z索引 / 検索 / フィルタが仕様通り
- [ ] スキーマ検証（ID一意・yomi必須・分類規定値）が機械実行済み
- [ ] push はエージェント未実行
