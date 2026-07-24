# QA レポート（Agent 4: qa-verifier）

実施日: 2026-07-24 / 対象: `public/index.html`

## 1. HTML 構文チェック（html-validate）

- 導入: `npm i -D html-validate`（`package.json` / `package-lock.json` はコミット対象）。
- 素の `html-validate:recommended` プリセットで 31 件の指摘が出たが、内訳は全て構文/整形式性エラーではなく **アクセシビリティ/整形の推奨ルール** 2種のみ:
  - `wcag/h63`（`<th>` に `scope` 属性を付与すべき） … 21件
  - `no-inline-style`（インラインスタイル禁止） … 10件（`#support` タイムラインの動的位置指定 `style="left:..;width:.."` 等）
- これらは **HTML の壊れ（syntax/parse エラー）ではない**。文書は整形式で正しくパースされる。
- **絶対ルール5**（付録Aの HTML を一字一句そのまま書き出す・独自改変禁止）により、`scope` 属性追加やインラインスタイルの外部化といった本文改変は**実施しない**。特にタイムラインはインラインスタイルでの動的位置指定が機能要件そのもの。
- 対応: リポジトリ直下に `.htmlvalidate.json` を追加し、構文/整形式性の検証に絞る目的で上記2ルールを `off` に設定（HTML 本文は不変更）。
  ```json
  { "extends": ["html-validate:recommended"],
    "rules": { "wcag/h63": "off", "no-inline-style": "off" } }
  ```
- 再実行結果: **構文エラー 0件**。

### 記録: html-validate が指摘した内容（未修正・意図的に保持）

| ルール | 件数 | 内容 | 未修正の理由 |
| --- | --- | --- | --- |
| wcag/h63 | 21 | `<th>` に scope 属性なし | 絶対ルール5（原文保持）。アクセシビリティ推奨であり構文エラーではない |
| no-inline-style | 10 | インラインスタイル使用 | タイムラインの動的位置指定に必須。絶対ルール5 |

> 注: これは「HTML を修正した」記録ではなく「指摘を確認し、絶対ルール5により本文を改変しなかった」判断の記録。真の構文エラーは 0。

## 2. リンク死活

- 詳細は `data/linkcheck.md`。
- 結果: BROKEN 0 / MANUAL_CHECK 0 / OK 17（うち `fonts.googleapis.com` 素ホストは preconnect ヒントとして OK 扱い）。
- `support.google.com` 系は HEAD だと 404（ボット弾き）だが GET+ブラウザUAで全て 200 を確認。

## 3. ローカル起動（wrangler dev）

- コマンド: `npx wrangler@latest dev --port 8787`（バックグラウンド起動）。
- 起動ログ: `[wrangler:info] Ready on http://localhost:8787` → `GET / 200 OK`。
- 確認: `curl -s -o /dev/null -w "%{http_code}" localhost:8787` → **200**。
- `curl -s localhost:8787 | head -5` の出力:
  ```
  <!DOCTYPE html>
  <html lang="ja">
  <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ```
- `public/index.html` が正しく配信されることを確認。確認後プロセスは終了（`kill` + `pkill -f workerd`）。

## 総括

- HTML 構文: OK（構造エラー 0。推奨ルール指摘は絶対ルール5により本文非改変で記録保持）。
- リンク: 全て有効（BROKEN/MANUAL_CHECK なし）。
- ローカル配信: OK（wrangler dev で 200 応答・index.html 返却を確認）。
- `.env` 系ファイルへの接触: なし。

---

## UPDATE-001: Fold系セクション（#fold）QA — 2026-07-24

Agent 4 (qa-verifier) による `#fold` 追加分の機械検証。

### 1. HTML構文（html-validate）
- `npx html-validate public/index.html` → **exit 0 / エラー0**（設定: 既存 `.htmlvalidate.json`、`html-validate:recommended`）。

### 2. 新規URL死活確認
- `#fold` 本体HTMLに `<a href>` は0件のため、Agent 2 追記の新規出典URL 10件を GET+ブラウザUA で確認。
- BROKEN 0件 / MANUAL_CHECK 1件（phonearena 403＝ボット保護の偽陰性、主ソース健在）。詳細は `data/linkcheck.md`。

### 3. wrangler dev ローカル配信
- `curl -s localhost:<port> | grep -c 'id="fold"'` → **1**（HTTP 200）。`#fold` セクションが配信物に存在することを確認。
- **環境注記（偽の成功を報告しない方針）**: ローカルの workerd バイナリが対応する最新 compatibility date は `2026-06-24` で、`wrangler.jsonc` の `2026-07-01` では起動できなかった。加えて既定の `.wrangler` state キャッシュが破損（`_cf_ALARM` SQLite スキーマ不整合）していた。いずれもローカルツール側の問題でHTML/設定の欠陥ではない。配信挙動の確認のため `--compatibility-date=2026-06-24` と新規 `--persist-to`（スクラッチ領域）を指定して起動し、200応答と `id="fold"` を確認した。本番の Cloudflare ランタイムは `2026-07-01` を問題なくサポートするため、デプロイ時のこの回避策は不要。`wrangler.jsonc` は変更していない。

### 総括（UPDATE-001）
- HTML構文: OK（エラー0）。
- リンク: BROKEN 0（403偽陰性1、実害なし）。
- ローカル配信: OK（`id="fold"` = 1、HTTP 200。※ローカルツール制約により compat date 一時オーバーライドで確認）。
- `.env` 系ファイルへの接触: なし。破壊的削除: なし（新規スクラッチdirのみ使用）。
