# UPDATE-002: GitHub Pages 移行 — 完結型指示書

作成日: 2026-07-24
対象リポジトリ: ~/taka-pixel-reference
目的: 配信先を Cloudflare Workers から GitHub Pages に移行し、実名入りURL（yamadatakahiro63.workers.dev）を廃止する。新URL: `https://reanimatedead.github.io/taka-pixel-reference/`
重要な順序原則: **新URLの配信確認が取れるまで、旧Worker（Cloudflare）は削除しない。**

---

## 絶対ルール（全エージェント共通）

1. 各エージェントは作業前後に `git status` を実行し記録
2. 作業開始前に `git pull origin main`
3. コミットは小さく安全に、メッセージは英語
4. **以下は全て人間ゲート。エージェントは絶対に実行しない:**
   - `git push`
   - リポジトリの公開化（visibility変更）
   - GitHub Pages の有効化
   - `wrangler delete`（Worker削除 = 破壊的操作）
5. `docs/index.html` の**本文内容は一切変更しない**（移動のみ）
6. `.env` 系への接触禁止

---

## Agent 1: restructure（構成変更）

1. `git pull origin main` → `git status`
2. `git mv public docs` を実行（Pages が参照できるのは ルート or /docs のため）
3. `docs/.nojekyll` を空ファイルとして作成（GitHub Pages の Jekyll 処理を無効化。処理されると表示崩れの原因になる）
4. `wrangler.jsonc` を削除（配信は Pages に一本化。Cloudflare構成の履歴は git log に残る）
5. コミット: `Move assets to docs/ for GitHub Pages and drop wrangler config`
6. `git status`

## Agent 2: docs-updater（運用文書の書き換え）

1. `git status`
2. `README.md` を全面更新:
   - 公開URL: `https://reanimatedead.github.io/taka-pixel-reference/`
   - 配信方式: GitHub Pages（main ブランチ /docs）。**push = 自動デプロイ**（wrangler deploy 工程は廃止）
   - 月例更新手順: `git pull` → Claude Code で INSTRUCTION.md の Agent 2 手順により #os-bugs 更新 → 人間が `git push` → 1〜2分で自動反映
   - 移行履歴: 「2026-07-24 Cloudflare Workers から移行（実名サブドメイン廃止のため）。旧URLは Worker 削除後に無効」の1行
3. コミット: `Update README for GitHub Pages operations`
4. `git status`

## Agent 3: qa-verifier（ローカル機械検証）

1. `git status`
2. `npx html-validate docs/index.html` で構文エラー0を確認（パス変更後も設定が効くか確認、必要なら .htmlvalidate.json のパスを修正）
3. `grep -c 'id="fold"' docs/index.html` が 1 を返すことを確認
4. `ls docs/.nojekyll` で存在確認
5. `grep -rn "public/" README.md INSTRUCTION.md UPDATE-001.md` を実行し、旧パス参照が残る箇所を `data/qa-report.md` に列挙（歴史的文書 INSTRUCTION.md / UPDATE-001.md は**修正しない**。当時の記録として保持し、report に「historical」と注記）
6. 結果を `data/qa-report.md` に追記、コミット: `Add QA results for Pages migration`
7. `git status`

## Agent 4: consistency-checker（整合確認）

1. `git status`
2. リポジトリ全体を確認:
   - `docs/index.html` が UPDATE-001 適用後の内容と同一（`git diff HEAD~3 -- docs/index.html public/index.html` 相当で本文変更ゼロを確認。rename のみであること）
   - `.gitignore` に `.wrangler/` 等の残置があっても害はないため削除しない（将来Cloudflareを再利用する可能性を排除しない）
   - リポジトリ直下に配信を妨げるファイルがないこと
3. 確認結果を `data/qa-report.md` に追記、コミット: `Confirm content integrity after restructure`
4. `git status`

## Agent 5: git-reporter（統括・停止）

1. `git status` + `git log --oneline -6`
2. `REPORT-UPDATE-002.md` を作成。**人間ゲートを以下の順序で明記（順序厳守）:**
   ```bash
   # Gate 1: push（ローカル変更を反映）
   git push origin main

   # Gate 2: リポジトリ公開化（実行前に中身に秘密情報がないこと最終確認）
   gh repo edit reanimatedead/taka-pixel-reference --visibility public --accept-visibility-change-consequences

   # Gate 3: GitHub Pages 有効化（main /docs）
   gh api -X POST repos/reanimatedead/taka-pixel-reference/pages -f "source[branch]=main" -f "source[path]=/docs"

   # Gate 4: 新URL配信確認（1〜2分待ってから。1 が返るまで次に進まない）
   curl -s https://reanimatedead.github.io/taka-pixel-reference/ | grep -c 'id="fold"'

   # Gate 5: 旧Worker削除（Gate 4 で 1 を確認した後のみ。破壊的操作）
   npx wrangler delete --name taka-pixel-reference

   # Gate 6: 旧URLの死亡確認（404等が返ればOK）
   curl -s -o /dev/null -w "%{http_code}\n" https://taka-pixel-reference.yamadatakahiro63.workers.dev/
   ```
   - 注記も記載: 「Pixel 4a のブックマークを新URLへ更新」「Gate 3 が 409 を返した場合は既に有効化済みなので Gate 4 へ進む」
3. コミット: `Add migration report` → **停止**

## 完了条件

- [ ] docs/ 移行・.nojekyll・README更新・QA・整合確認の5コミットが存在
- [ ] index.html の本文は無変更（リネームのみ）
- [ ] REPORT-UPDATE-002.md に人間ゲート6つが順序付きで明記
- [ ] wrangler delete がエージェントにより実行されていない
