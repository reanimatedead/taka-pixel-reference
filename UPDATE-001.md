# UPDATE-001: Foldシリーズ追加 — 完結型指示書

作成日: 2026-07-24
対象リポジトリ: ~/taka-pixel-reference（クローン済み・デプロイ済み）
目的: 公開中のページに Fold 系 3 機種（Pixel Fold / 9 Pro Fold / 10 Pro Fold）の独立セクションを追加する。aシリーズの表・タイムラインには混ぜない。

---

## 絶対ルール（全エージェント共通・前回と同一）

1. 各エージェントは作業前後に `git status` を実行し記録
2. 作業開始前に必ず `git pull origin main` を実行（マシン切替プロトコル）
3. コミットは小さく安全に、メッセージは英語
4. **`git push` と `wrangler deploy` は実行禁止。REPORT-UPDATE-001.md 作成後に停止**
5. 付録BのHTMLは一字一句そのまま挿入。既存セクションの改変は本指示書で明示した3箇所のみ
6. 検証できない項目は `UNVERIFIED` のまま残す。偽の検証成功を報告しない
7. `.env` 系への接触禁止

---

## Agent 1: content-builder（挿入担当）

1. `git pull origin main` → `git status`
2. `public/index.html` に対し以下の3変更のみ行う:
   - **変更1（nav）**: `<li><a href="#support">サポート期限</a></li>` の直後に次の1行を追加:
     `<li><a href="#fold">Fold系</a></li>`
   - **変更2（lede）**: `歴代 a シリーズ全 8 機種の` を `歴代 a シリーズ全 8 機種 + Fold 系 3 機種の` に置換
   - **変更3（本体）**: `<section id="links">` の直前に付録Bのセクションを丸ごと挿入
3. コミット: `Add Fold series section (Fold / 9 Pro Fold / 10 Pro Fold)`
4. `git status`

## Agent 2: research-verifier（検証担当）

1. `git status`
2. `#fold` 内の `UNVERIFIED` 項目をWeb検索で検証。出典確認できたものを `VERIFIED` に更新し、`data/sources.md` に「項目 / URL / 確認日」を**追記**（既存記録は消さない）
3. 特に必ず検証すること: ①初代Foldの内側画面破損・保護レイヤー問題 ②Pixel Fold(初代)の日本発売日と価格 ③各機種の保証期限（support.google.com/pixelphone/answer/4457705 を一次ソースとする）
4. 事実誤りを発見した場合のみ本文修正し `data/corrections.md` に記録
5. コミット: `Verify Fold section entries and append sources`
6. `git status`

## Agent 3: consistency-checker（整合担当）

1. `git status`
2. ページ全体の整合を確認・修正:
   - `#ts` 内「判断表」に次の1行を追加（`<li><strong>今買った端末は即Android 17` の行の直前）:
     `<li><strong>Fold系:</strong> 価格はaシリーズ約3台分。大画面が業務要件でない限り優先度は下げる（詳細は上のFold系セクション）</li>`
   - footer の出典行末尾に ` / Fold系は2025年8月発表時報道` を追記
   - nav リンクとセクションIDの対応が全て一致しているか確認
3. コミット: `Integrate Fold references into decision table and footer`
4. `git status`

## Agent 4: qa-verifier（機械検証）

1. `git status`
2. `npx html-validate public/index.html`（前回作成の .htmlvalidate.json 設定で構文エラー0を確認）
3. `#fold` 内の新規URLのみ死活確認（GET + ブラウザUA、前回の偽陰性教訓を適用）→ `data/linkcheck.md` に追記
4. `npx wrangler dev` 起動 → `curl -s localhost:8787 | grep -c "id=\"fold\""` が 1 を返すことを確認 → 終了
5. `data/qa-report.md` に追記、コミット: `Add QA results for Fold section`
6. `git status`

## Agent 5: git-reporter（統括・停止）

1. `git status` + `git log --oneline -6`
2. `REPORT-UPDATE-001.md` 作成: 変更点 / UNVERIFIED残存 / 人間ゲート:
   ```bash
   git push origin main
   npx wrangler deploy
   ```
3. コミット: `Add update report` → **停止**

## 完了条件

- [ ] 追加コミット5件が git log に存在
- [ ] `#fold` セクションが3機種を含み、既存セクションの変更は指示3箇所+判断表1行+footerのみ
- [ ] wrangler dev で `id="fold"` の存在確認済み
- [ ] REPORT-UPDATE-001.md に人間ゲート2つ明記

---

# 付録B: 挿入するHTMLセクション（一字一句そのまま）

```html
<section id="fold">
  <h2>Fold系（折りたたみ・参考情報）</h2>
  <p class="sec-note">aシリーズとは別系統のフラッグシップ折りたたみ。価格はaシリーズ約3台分のため、本ページでは<strong>購入候補ではなく情報収集対象</strong>として掲載。判断基準は同じ「サポート期限」。</p>
  <div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>項目</th>
        <th>Pixel Fold（初代）</th>
        <th>9 Pro Fold</th>
        <th>10 Pro Fold</th>
      </tr>
    </thead>
    <tbody>
      <tr><th>発売（日本）</th><td>2023/7</td><td>2024/9</td><td>2025/10/9</td></tr>
      <tr><th>SoC</th><td>Tensor G2</td><td>Tensor G4</td><td>Tensor G5</td></tr>
      <tr><th>RAM / ROM</th><td>12GB / 256–512GB</td><td>16GB / 256–512GB</td><td>16GB / 256GB–1TB</td></tr>
      <tr><th>メイン画面</th><td>7.6" 120Hz</td><td>8" 120Hz</td><td>8" 120Hz（最大輝度向上）</td></tr>
      <tr><th>カバー画面</th><td>5.8"</td><td>6.3"</td><td>6.4"</td></tr>
      <tr><th>バッテリー</th><td>4,821mAh</td><td>4,650mAh</td><td>5,015mAh（歴代Fold最大・30時間+）</td></tr>
      <tr><th>防水防塵</th><td>IPX8（防塵なし）</td><td>IPX8（防塵なし）</td><td class="hero">IP68（折りたたみ初の防塵対応）</td></tr>
      <tr><th>特記</th><td>初代・重量重め</td><td>大幅軽量化・薄型化</td><td>ギアレスヒンジ（10年動作の耐久設計）・Pixelsnap磁気/Qi2充電</td></tr>
      <tr><th>発売時価格</th><td>¥253,000</td><td>¥257,500</td><td>¥267,500 (256GB)<br>¥287,500 (512GB)</td></tr>
      <tr><th>アップデート保証</th><td class="hero">2028/6 まで <span class="badge ok">5年</span></td><td class="hero">2031/9 まで <span class="badge ok">7年</span></td><td class="hero">2032/10 まで <span class="badge ok">7年</span></td></tr>
    </tbody>
  </table>
  </div>

  <details>
    <summary><span><span class="ts-tag warn">初代</span>Pixel Fold（初代）— 既知問題</span></summary>
    <div class="body">
      <ul>
        <li><strong>内側ディスプレイの破損・表示不良報告</strong> <span class="vstate u">UNVERIFIED</span> — ヒンジ付近への微細な異物混入で内側画面が損傷する報告が発売直後から多数。画面を閉じる前にゴミを払う運用が必須</li>
        <li><strong>保護レイヤー剥がれ</strong> <span class="vstate u">UNVERIFIED</span> — 内側画面の保護層は剥がしてはいけない仕様。端が浮いても自分で剥がさず正規修理へ</li>
        <li><strong>中古購入は非推奨</strong> — 折りたたみ機構の劣化状態が外観から判定できず、保証も2028/6まで。同予算なら9a複数台の方が合理的</li>
      </ul>
    </div>
  </details>

  <details>
    <summary><span><span class="ts-tag">9/10</span>9 Pro Fold / 10 Pro Fold — 現役世代</span></summary>
    <div class="body">
      <ul>
        <li><strong>9 Pro Fold:</strong> 初代の弱点（重量・画面耐久）を大幅改善した世代。防塵は非対応（IPX8）のまま</li>
        <li><strong>10 Pro Fold:</strong> 折りたたみ初のIP68防塵防水 <span class="vstate v">VERIFIED</span>。ギアレスヒンジで10年以上の折りたたみ動作に耐える設計 <span class="vstate v">VERIFIED</span>。Android 17 の不具合マトリクス（上）は本機にも適用される</li>
        <li><strong>資金判断:</strong> 10 Pro Fold は ¥267,500〜 = 9a 約3.3台分。大画面2画面が業務生産性に直結する要件（例: 移動中の資料同時参照）がない限り、判定D（現時点購入非推奨・ウォッチのみ）</li>
      </ul>
    </div>
  </details>
</section>
```
