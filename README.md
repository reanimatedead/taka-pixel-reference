# taka-pixel-reference

Pixel a シリーズ（4a → 10a）の個人用リファレンスページ。スペック比較・サポート期限・公式ヘルプリンク・電話/Gmail 機能・OS別不具合マトリクス・トラブルシューティングを 1 枚の静的 HTML に集約したもの。

判断基準は「今日、その端末を安全に使えるか」。EOL（アップデート提供終了）判定と、Android 各バージョンの定番不具合→対策を手元で即引けるようにするのが目的。

## 構成

```
.
├── public/
│   └── index.html      # 本体（静的1ページ）
├── data/               # 検証ログ（sources / linkcheck / qa-report など）
├── wrangler.jsonc      # Cloudflare Workers（静的アセット配信）設定
├── README.md
├── INSTRUCTION.md      # 自走用の完結型指示書
└── .gitignore
```

Cloudflare Workers の静的アセット機能のみを使う構成（`main` ワーカースクリプトなし）。`public/` 配下をそのまま配信する。

## ローカル確認

```bash
npx wrangler dev
```

起動後、表示された URL（デフォルト `http://localhost:8787`）をブラウザで開くと `public/index.html` が返る。

## デプロイ（人間のみ実行）

```bash
npx wrangler login    # 初回のみ（ブラウザ認証）
npx wrangler deploy   # ← 人間ゲート。自動実行しない
```

デプロイは**人間が明示的に実行する**。エージェント・スクリプトからの自動 `wrangler deploy` は禁止。

公開 URL 想定: `https://taka-pixel-reference.<account>.workers.dev`

## 月例更新運用

Android の月例セキュリティパッチ配信後に、以下を回す：

1. `public/index.html` の `#os-bugs` セクションを確認する
2. 新規に確認された不具合・対策があれば追記し、出典が取れた項目は `UNVERIFIED` → `VERIFIED` に更新する（出典 URL は `data/sources.md` に記録）
3. ページ冒頭および `#os-bugs` の `last verified:` 日付を更新する
4. サポート期限（`#specs` / `#support`）に変化があれば反映する

出典は Google 公式ヘルプ（support.google.com 系）を一次ソースとし、国内報道は補助として扱う。
