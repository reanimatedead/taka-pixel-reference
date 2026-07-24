# REPORT-UPDATE-001: Foldシリーズ追加

作成日: 2026-07-24
対象: `public/index.html` に Fold 系 3 機種（Pixel Fold 初代 / 9 Pro Fold / 10 Pro Fold）の独立セクション `#fold` を追加。

---

## 追加コミット（5件）

| # | ハッシュ | メッセージ | 担当 |
| --- | --- | --- | --- |
| 1 | 6b1bc13 | Add Fold series section (Fold / 9 Pro Fold / 10 Pro Fold) | content-builder |
| 2 | 6c6652c | Verify Fold section entries and append sources | research-verifier |
| 3 | ee5574d | Integrate Fold references into decision table and footer | consistency-checker |
| 4 | aef75ea | Add QA results for Fold section | qa-verifier |
| 5 | （本コミット） | Add update report | git-reporter |

## 変更点

**`public/index.html`（指示3箇所 + 判断表1行 + footer）**
- nav: `#support` の直後に `<li><a href="#fold">Fold系</a></li>` を追加。
- lede: 「歴代 a シリーズ全 8 機種の」→「歴代 a シリーズ全 8 機種 + Fold 系 3 機種の」。
- 本体: `<section id="links">` 直前に付録B（`#fold` セクション）を一字一句そのまま挿入。
- 判断表: `今買った端末は即Android 17` 行の直前に Fold系の1行を追加。
- footer: 出典行末尾に ` / Fold系は2025年8月発表時報道` を追記。
- nav 7リンク ⇔ section 7 ID の対応 全一致を確認。

**`data/sources.md`**（追記）: `#fold` の検証ログ。UNVERIFIED 2項目を VERIFIED に更新した根拠、発売日/価格/保証期限の出典を追記（既存記録は保持）。

**`data/linkcheck.md` / `data/qa-report.md`**（追記）: 新規URL死活確認と機械検証結果。

## 検証結果

- **UNVERIFIED → VERIFIED（2件）**: 初代Fold内側ディスプレイ破損（複数ソース）／保護レイヤーは自己剥離しない仕様（androidpolice・tomsguide）。
- **既存VERIFIED裏取り**: 10 Pro Fold の IP68・ギアレスヒンジ。
- **数値確認（修正不要）**: 初代Fold 日本発売 2023/7/27・¥253,000／保証年数は一次ソース(support.google.com/pixelphone/answer/4457705)で 5年・7年・7年を確認、到達年月は US発売月+年数と整合。事実誤りなし（`data/corrections.md` 記録なし）。
- **html-validate**: エラー0（exit 0）。
- **リンク**: BROKEN 0件（phonearena 403 はボット保護の偽陰性、主ソース健在）。
- **wrangler dev**: `id="fold"` = 1 / HTTP 200 を確認。

## UNVERIFIED 残存

- `#fold` セクション内に **残存 UNVERIFIED: 0件**（新規2項目は VERIFIED 化済み）。

## 注意事項（環境）

- ローカルの workerd バイナリの最新対応 compatibility date が `2026-06-24` のため、`wrangler.jsonc` の `2026-07-01` ではローカル dev がそのままでは起動しなかった（本番 Cloudflare ランタイムでは問題なし）。加えて既定 `.wrangler` state キャッシュが破損していた。配信確認は `--compatibility-date=2026-06-24` と新規 `--persist-to` で回避して実施。**`wrangler.jsonc` は未変更**。デプロイ時にこの回避策は不要。
- リポジトリ直下の `UPDATE-001.md`（指示書）は未追跡のまま。指示外のため commit していない。

---

## 人間ゲート（未実行・要人間確認）

以下2コマンドは**エージェントは実行していない**。内容確認後、人間が実行:

```bash
git push origin main
npx wrangler deploy
```

**停止**: 本レポート commit をもって作業を停止する。
