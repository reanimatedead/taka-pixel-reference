# taka-pixel-reference

Pixel a シリーズ（4a → 10a）の個人用リファレンスページ「**Pixel 整備手帳**」。スペック比較・サポート期限・公式ヘルプリンク・電話/Gmail 機能・OS別不具合マトリクス・トラブルシューティング・専門TS（ADB / fastboot / コードネーム / 復旧手順）を 1 枚の静的 HTML に集約したもの。

判断基準は「今日、その端末を安全に使えるか」。EOL（アップデート提供終了）判定と、Android 各バージョンの定番不具合→対策を手元で即引けるようにするのが目的。

公開URL: `https://reanimatedead.github.io/taka-pixel-reference/`

## 構成

```
.
├── docs/
│   ├── index.html      # 本体（静的1ページ）
│   ├── dict/           # 不具合辞書（データと表示を分離した別ページ）
│   │   ├── index.html          # 表示・検索（entries.json を fetch して描画）
│   │   └── data/entries.json   # 不具合データ本体（スキーマは UPDATE-004.md）
│   └── .nojekyll        # GitHub Pages の Jekyll 処理を無効化
├── data/               # 検証ログ（sources / linkcheck / qa-report など）
├── README.md
├── INSTRUCTION.md      # 自走用の完結型指示書
└── .gitignore
```

## 配信方式

GitHub Pages（`main` ブランチの `/docs`）で配信する。**`git push` = 自動デプロイ**。別途のビルドやデプロイコマンド（旧 `wrangler deploy` 工程）は不要で、push の 1〜2 分後に自動反映される。

`docs/.nojekyll` を置くことで GitHub Pages の Jekyll 処理を無効化している（処理されると表示崩れの原因になるため）。

## ローカル確認

`docs/index.html` は依存のない静的1ページ。ブラウザで直接開くか、任意の静的サーバで確認できる：

```bash
python3 -m http.server -d docs 8000   # http://localhost:8000 で index.html が返る
```

## 月例更新運用

Android の月例セキュリティパッチ配信後に、以下を回す：

1. `git pull` で最新化する
2. Claude Code で `INSTRUCTION.md` の Agent 2 手順により `docs/index.html` の `#os-bugs` を更新する（新規に確認された不具合・対策を追記し、出典が取れた項目は `UNVERIFIED` → `VERIFIED` に更新。出典 URL は `data/sources.md` に記録）
3. ページ冒頭および `#os-bugs` の `last verified:` 日付、サポート期限（`#specs` / `#support`）の変化を反映する
4. 人間が `git push` を実行 → 1〜2 分で自動反映される

出典は Google 公式ヘルプ（support.google.com 系）を一次ソースとし、国内報道は補助として扱う。

## 不具合辞書（dict/）

整備手帳とは別ページの「不具合 × 対処法 辞書」。1000件を書くのではなく、1000件が貯まって腐らない構造（データ JSON と表示 HTML の分離）を先に作るという思想で運用する。

- **URL**: `https://reanimatedead.github.io/taka-pixel-reference/dict/`
- **データ本体**: `docs/dict/data/entries.json`（スキーマ定義は `UPDATE-004.md` を参照。`id` は PXD-連番4桁で欠番・再利用禁止、`yomi` はあいうえお索引の生成キー、`category` は10分類のみ、`severity` = critical/high/medium/low、`fix_status` = patched/open/wontfix/spec、`verify_state` は新規 UNVERIFIED 開始が既定）
- **表示**: `docs/dict/index.html`（単一ファイル。あいうえお索引 / A-Z 索引 / 全文検索 / カテゴリ・重要度・修正状況・機種フィルタ。ビルド工程なし）
- **収録基準（3条件をすべて満たすもののみ収録）**: ①独立した複数ソースで報告 ②再現時に実害がある ③対処法または回避策が記述できる。満たさない情報は件数が欲しくても入れない
- **項目の追加手順**: `docs/dict/data/entries.json` に追記 → `python3 -m json.tool docs/dict/data/entries.json > /dev/null` で構文検証 → push。**HTML は触らない**

## 移行履歴

- 2026-07-24 Cloudflare Workers から移行（実名サブドメイン廃止のため）。旧URLは Worker 削除後に無効。
