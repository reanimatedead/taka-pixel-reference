# REPORT-UPDATE-003: 専門TSセクション追加 + タイトル改称

実行日: 2026-07-24
対象: `~/taka-pixel-reference`（GitHub Pages: main /docs）
状態: **全4作業コミット + 本レポートコミット完了。`git push` 未実行（人間ゲートで停止）**

---

## 実行サマリ（5エージェント構成）

| Phase | 役割 | コミット | 結果 |
| --- | --- | --- | --- |
| Agent 1 | content-builder（挿入） | `Add advanced troubleshooting section and rename to Seibi-Techo` | 変更1〜5すべて適用。付録Cは `diff` で一字一句一致確認済み |
| Agent 2 | research-verifier（検証） | `Verify codenames and advanced TS entries` | 一次ソースの動的テーブル非取得のため全コードネーム UNVERIFIED 据え置き（理由を `data/sources.md` に記録） |
| Agent 3 | consistency-checker（整合） | `Align navigation, TS cross-reference and README title` | nav 8=8 全一致・#ts 誘導文追記・README 改称 |
| Agent 4 | qa-verifier（機械検証） | `Add QA results for advanced TS` | html-validate 0エラー・grep全一致・新規リンク2件 200 |
| Agent 5 | git-reporter（統括） | `Add update report`（本コミット） | レポート作成 → 停止 |

各エージェントは作業前後に `git status` を実行・記録済み。

---

## 変更内容（Agent 1）

- **変更1（title）**: `Pixel a-series 個人リファレンス | 4a → 10a` → `Pixel 整備手帳 | 4a → 10a`
- **変更2（h1）**: `<span class="thin">/ 個人運用ノート</span>` → `<span class="thin">/ 整備手帳</span>`
- **変更3（nav）**: `#ts` の直後に `<li><a href="#ts-pro">専門TS</a></li>` 追加（nav 7→8リンク）
- **変更4（CSS）**: `</style>` 直前に `pre` / `pre .c` / `.lv` / `.lv.danger` の4ルール追加
- **変更5（本体）**: `</main>` 直前に付録C（`#ts-pro`：Lv0/Lv1/Lv2/Lv3 + コードネーム表）を**一字一句そのまま**挿入

---

## 検証結果（Agent 2 / Agent 4）

### 機械検証（Agent 4）
- `npx html-validate docs/index.html` → **exit 0（構文エラー0）**
- `grep -c 'id="ts-pro"'` = **1** / `grep -c '整備手帳'` = **2**（>=2）
- nav href(#) ⇔ `<section id>` = **8=8 全一致**（specs / support / fold / links / features / os-bugs / ts / ts-pro）
- 新規URL死活（curl GET + Chrome UA + リダイレクト追従）:
  - `https://developers.google.com/android/images` → **200**
  - `https://developers.google.com/android/ota` → **200**

### コードネーム検証（Agent 2）— ⚠️ 全項目 UNVERIFIED 据え置き
一次ソース指定 `https://developers.google.com/android/images` のコードネーム表は、
利用規約同意後に **JavaScript で動的挿入**される構造で、今回の取得系（JS非実行）では
本文としてテーブルを取得できず、ページ上でコードネーム文字列を一件も確認できなかった。

絶対ルール「確認できない項目は UNVERIFIED のまま残す／推測で埋めない／偽の検証成功を報告しない」に従い、
既存記載（sunfish, bramble, barbet, bluejay, lynx, akita, tegu, felix, comet）を含め**全エントリを UNVERIFIED に維持**。
一般流通値とは一致しているが、指定一次ソース上での実照合が取れないため昇格させていない。

- **Pixel 10a**: `要確認` / UNVERIFIED（ページ上で存在確認できず）→ 完了条件「VERIFIED化 or 理由付きUNVERIFIED」を**理由付きUNVERIFIEDで満たす**
- **Pixel 10 Pro Fold**: `要確認` / UNVERIFIED
- Play Integrity 記述（ブートローダーアンロックで決済系不可）も一次ソース未照合のため UNVERIFIED 維持
- 誤りを一次ソース上で確認できなかったため**本文修正なし**（`data/corrections.md` 記録事項なし）

詳細ログ: `data/sources.md`（末尾セクション） / `data/linkcheck.md` / `data/qa-report.md`

---

## 完了条件チェック

- [x] 5コミット存在（Agent1〜4 + 本レポート）
- [x] nav 8=8 / タイトル2箇所変更
- [x] `#ts-pro` に Lv0〜Lv3 + コードネーム表が存在
- [x] 10a コードネームは **理由付き UNVERIFIED** で確定
- [x] push はエージェント未実行

---

## 人間ゲート（push は人間が実行）

エージェントは `git push` を実行しない。下記は**確認と実行を `&&` で連結**しており、
`#ts-pro` が存在しなければ push しない（失敗時に止まる）形式：

```bash
# 1) 検証が通ったときだけ push する（grep 失敗なら push しない）
cd ~/taka-pixel-reference && grep -q 'id="ts-pro"' docs/index.html && git push origin main

# 2) push の 1〜2 分後、本番反映を確認（1 が返れば反映済み）
curl -s "https://reanimatedead.github.io/taka-pixel-reference/?v=$(date +%s)" | grep -c 'id="ts-pro"'
```

以上で UPDATE-003 の全工程を完了し、**push 直前で停止**する。
