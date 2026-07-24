# UPDATE-003: 専門TSセクション追加 + タイトル変更 — 完結型指示書

作成日: 2026-07-24
対象リポジトリ: ~/taka-pixel-reference（GitHub Pages 配信中: main /docs）
目的: ①タイトルを「整備手帳」に変更 ②ナビ「トラブルシューティング」の隣に新セクション「専門TS」を追加（Lv0基本→Lv3専門の段階構造。ADB / fastboot / コードネーム / 復旧手順を含む）
配信: push = 自動デプロイ（wrangler工程なし）

---

## 絶対ルール（全エージェント共通）

1. 各エージェント作業前後に `git status`、開始前に `git pull origin main`
2. コミットは小さく安全に、メッセージは英語
3. **`git push` は人間ゲート。エージェントは実行しない**
4. 付録CのHTMLは一字一句そのまま挿入。既存本文の変更は本指示書で明示した箇所のみ
5. 検証できない項目は `UNVERIFIED` のまま残す。偽の検証成功を報告しない
6. `.env` 系への接触禁止

---

## Agent 1: content-builder（挿入担当）

1. `git pull origin main` → `git status`
2. `docs/index.html` に以下の変更:
   - **変更1（title）**: `<title>Pixel a-series 個人リファレンス | 4a → 10a</title>` → `<title>Pixel 整備手帳 | 4a → 10a</title>`
   - **変更2（h1）**: `<span class="thin">/ 個人運用ノート</span>` → `<span class="thin">/ 整備手帳</span>`
   - **変更3（nav）**: `<li><a href="#ts">トラブルシューティング</a></li>` の直後に `<li><a href="#ts-pro">専門TS</a></li>` を追加
   - **変更4（CSS）**: `</style>` の直前に以下を追加:
     ```
     pre{background:#2B2F2C;color:#E8EAE5;font-family:var(--mono);font-size:12px;border-radius:10px;padding:14px 16px;overflow-x:auto;margin:8px 0;line-height:1.6}
     pre .c{color:#8FA894}
     .lv{display:inline-block;font-family:var(--mono);font-size:10px;color:#fff;background:#4a5f8a;border-radius:99px;padding:1px 8px;margin-right:8px}
     .lv.danger{background:var(--alert)}
     ```
   - **変更5（本体）**: `</main>` の直前（= #ts セクションの後）に付録Cを丸ごと挿入
3. コミット: `Add advanced troubleshooting section and rename to Seibi-Techo`
4. `git status`

## Agent 2: research-verifier（検証担当）

1. `git status`
2. `#ts-pro` 内の `UNVERIFIED` を検証し `data/sources.md` に追記:
   - **最優先**: Pixel 10a のコードネーム（Google factory images ページ https://developers.google.com/android/images を一次ソースに）
   - Pixel 10 Pro Fold のコードネーム
   - コードネーム表の既存記載（sunfish〜tegu, felix, comet）に誤りがないか同ページで照合
   - ブートローダーアンロックで Play Integrity 判定が失敗し決済系アプリが使えなくなる旨
3. 誤り発見時のみ本文修正し `data/corrections.md` に記録
4. コミット: `Verify codenames and advanced TS entries`
5. `git status`

## Agent 3: consistency-checker（整合担当）

1. `git status`
2. 確認・修正:
   - nav 8リンク ⇔ 8セクションIDの全一致
   - `#ts` 冒頭の sec-note 末尾に「ADB・復旧などPC接続を伴う手順は次の専門TSへ。」を追記
   - README.md のページ名記載を「Pixel 整備手帳」に更新
3. コミット: `Align navigation, TS cross-reference and README title`
4. `git status`

## Agent 4: qa-verifier（機械検証）

1. `git status`
2. `npx html-validate docs/index.html` 構文エラー0
3. `grep -c 'id="ts-pro"' docs/index.html` = 1、`grep -c '整備手帳' docs/index.html` >= 2
4. `#ts-pro` 内の新規URL死活（GET+ブラウザUA）→ `data/linkcheck.md` 追記
5. `data/qa-report.md` 追記、コミット: `Add QA results for advanced TS`
6. `git status`

## Agent 5: git-reporter（統括・停止）

1. `git status` + `git log --oneline -6`
2. `REPORT-UPDATE-003.md` 作成。人間ゲート（**確認と実行を&&で連結し、失敗時に止まる形式**）:
   ```bash
   grep -q 'id="ts-pro"' docs/index.html && git push origin main
   # 1〜2分後:
   curl -s "https://reanimatedead.github.io/taka-pixel-reference/?v=$(date +%s)" | grep -c 'id="ts-pro"'
   ```
3. コミット: `Add update report` → **停止**

## 完了条件

- [ ] 5コミット存在 / nav 8=8 / タイトル2箇所変更
- [ ] `#ts-pro` に Lv0〜Lv3 + コードネーム表が存在
- [ ] 10a コードネームが VERIFIED 化 or 理由付き UNVERIFIED
- [ ] push はエージェント未実行

---

# 付録C: 挿入するHTMLセクション（一字一句そのまま）

```html
<section id="ts-pro">
  <h2>専門TS（基本 → 診断 → ADB → 復旧）</h2>
  <p class="sec-note">レベル順に並べた実務手順集。Lv2以降はPC（Mac）接続が前提。<strong class="lv danger">DATA LOSS</strong> 付きの操作はデータ消去を伴うため、実行前にバックアップ必須。</p>

  <details>
    <summary><span><span class="lv">Lv0</span>基本（端末単体で完結）</span></summary>
    <div class="body">
      <p>強制再起動・セーフモード・キャッシュ削除・ネットワークリセットは上の「トラブルシューティング → 基本TSフロー」を参照。ここでは重複させない。迷ったら必ずLv0から順に試す。</p>
    </div>
  </details>

  <details>
    <summary><span><span class="lv">Lv1</span>診断（root不要・無害）</span></summary>
    <div class="body">
      <ul>
        <li><strong>開発者オプション有効化:</strong> 設定 → デバイス情報 → <kbd>ビルド番号を7回タップ</kbd>。以降のLvで前提になる</li>
        <li><strong>バッテリー状態:</strong> 設定 → バッテリー → <kbd>バッテリーの状態</kbd>（対応世代）。劣化度と充電回数の目安を確認</li>
        <li><strong>通信テストメニュー:</strong> 電話アプリで <kbd>*#*#4636#*#*</kbd> — 電波強度・優先ネットワーク・Wi-Fi詳細 <span class="vstate u">UNVERIFIED</span></li>
        <li><strong>IMEI確認:</strong> <kbd>*#06#</kbd>（中古売却・キャリア問い合わせ時に必要）</li>
        <li><strong>バグレポート取得（端末単体）:</strong> 開発者オプション → <kbd>バグレポートを取得</kbd> → 通知から共有。サポート問い合わせ時の添付用</li>
      </ul>
    </div>
  </details>

  <details>
    <summary><span><span class="lv">Lv2</span>ADB（PC接続・非破壊）</span></summary>
    <div class="body">
      <p><strong>準備（Mac側・初回のみ）:</strong></p>
      <pre>brew install android-platform-tools
<span class="c"># 端末側: 開発者オプション → USBデバッグ ON → ケーブル接続 → 「許可」</span></pre>
      <p><strong>基本診断コマンド:</strong></p>
      <pre>adb devices                                    <span class="c"># 接続確認（deviceと出ればOK）</span>
adb shell getprop ro.build.version.release     <span class="c"># OSバージョン</span>
adb shell getprop ro.build.version.security_patch  <span class="c"># セキュリティパッチ日付</span>
adb shell getprop ro.product.device            <span class="c"># コードネーム確認</span>
adb shell dumpsys battery                      <span class="c"># バッテリー詳細</span>
adb bugreport ~/Desktop/bugreport.zip          <span class="c"># 完全ログ取得</span></pre>
      <p><strong>実務ユーティリティ:</strong></p>
      <pre>adb shell pm list packages | grep -i 対象名    <span class="c"># パッケージ名の特定</span>
adb shell pm uninstall --user 0 パッケージ名   <span class="c"># プリインアプリの無効化(復元可)</span>
adb pull /sdcard/DCIM ~/Desktop/pixel-photos   <span class="c"># 写真一括退避</span>
adb shell screenrecord /sdcard/rec.mp4         <span class="c"># 画面録画（Ctrl+Cで停止）</span></pre>
    </div>
  </details>

  <details>
    <summary><span><span class="lv danger">Lv3</span>復旧（リカバリー / sideload / Factory Image）</span></summary>
    <div class="body">
      <div class="alert-band">この階層は操作を誤るとデータ消去・文鎮化に直結する。実行前フルバックアップと、下のコードネーム表で機種一致の確認を必須とする。</div>
      <p><strong>A. リカバリーモード起動（起動不能時の入口）:</strong></p>
      <pre>電源OFF → <span class="c">電源 + 音量下</span> 長押し → bootloader画面
音量キーで「Recovery mode」選択 → 電源キーで決定
「No command」表示 → <span class="c">電源を押しながら音量上を一回</span></pre>
      <p><strong>B. OTA sideload — データを消さずにOSを上書き修復（ブートループ時の第一選択）:</strong></p>
      <pre>リカバリー画面で「Apply update from ADB」を選択
<span class="c"># Mac側: 機種のOTAイメージを https://developers.google.com/android/ota から取得</span>
adb devices        <span class="c"># sideload と表示されることを確認</span>
adb sideload ota_image.zip</pre>
      <p><strong>C. Factory Image 全書き込み <span class="lv danger">DATA LOSS</span> — 最終手段:</strong></p>
      <pre><span class="c"># https://developers.google.com/android/images から機種コードネーム一致の版を取得</span>
adb reboot bootloader
fastboot devices
./flash-all.sh     <span class="c"># 全データ消去して工場出荷状態に</span></pre>
      <p class="caveat">警告: ブートローダーアンロック（fastboot flashing unlock）は全データ消去に加え、Play Integrity 判定が失敗し銀行・決済・一部ゲームアプリが恒久的に使用不能になる <span class="vstate u">UNVERIFIED</span>。実施してよいのはEOL検証機（4a）のみ。メイン機では絶対に行わない。</p>
    </div>
  </details>

  <details open>
    <summary><span><span class="lv">表</span>コードネーム / Factory Image 対応表</span></summary>
    <div class="body">
      <p>復旧イメージは機種の<strong>コードネーム</strong>で配布される。取り違えると文鎮化するため、この表と <kbd>adb shell getprop ro.product.device</kbd> の出力一致を必ず確認する。</p>
      <ul>
        <li>4a = <kbd>sunfish</kbd> <span class="vstate u">UNVERIFIED</span> / 4a (5G) = <kbd>bramble</kbd> <span class="vstate u">UNVERIFIED</span> / 5a = <kbd>barbet</kbd> <span class="vstate u">UNVERIFIED</span></li>
        <li>6a = <kbd>bluejay</kbd> <span class="vstate u">UNVERIFIED</span> / 7a = <kbd>lynx</kbd> <span class="vstate u">UNVERIFIED</span> / 8a = <kbd>akita</kbd> <span class="vstate u">UNVERIFIED</span></li>
        <li>9a = <kbd>tegu</kbd> <span class="vstate u">UNVERIFIED</span> / 10a = <kbd>要確認</kbd> <span class="vstate u">UNVERIFIED</span></li>
        <li>Fold = <kbd>felix</kbd> <span class="vstate u">UNVERIFIED</span> / 9 Pro Fold = <kbd>comet</kbd> <span class="vstate u">UNVERIFIED</span> / 10 Pro Fold = <kbd>要確認</kbd> <span class="vstate u">UNVERIFIED</span></li>
      </ul>
      <p>配布元（公式のみ使用）: <a href="https://developers.google.com/android/images" target="_blank" rel="noopener">Factory Images</a> / <a href="https://developers.google.com/android/ota" target="_blank" rel="noopener">Full OTA Images</a></p>
    </div>
  </details>
</section>
```
