# リンク死活チェック（Agent 4: qa-verifier）

対象: `public/index.html` 内の全 `https://` URL（重複除外後 17件）。実施日: 2026-07-24

判定基準: 200/301/302 = OK / 403 = MANUAL_CHECK / 404/000 = BROKEN。

## 手順と注意

1. 指示書どおり `curl -s -o /dev/null -w "%{http_code}" -I <URL>`（HEAD）で一次判定。
2. `support.google.com` 系は HEAD/UA無しリクエストに対して **404 を返す**（SPA + ボット弾き）。これは死リンクではなく偽陰性のため、`GET + ブラウザ UA + リダイレクト追従` で再判定した。
3. 再判定で全て 200 を確認。

## 結果一覧

| 最終判定 | HEAD | GET+UA | URL | 備考 |
| --- | --- | --- | --- | --- |
| OK | 200 | 200 | https://developers.google.com/android/images | |
| OK(preconnect) | 404 | 404 | https://fonts.googleapis.com | `<link rel="preconnect">` のホストヒント。パス無しの素のホストは元々404を返すが、実際にfetchされる資源ではなく接続の事前確立用。ページ機能上は正常。**修正不要**（原文改変も不可） |
| OK | 200 | 200 | https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap | 実際に読み込むCSS。200 |
| OK | 200 | 200 | https://store.google.com/jp/product/pixel_10a_specs?hl=ja | |
| OK | 404→200 | 200 | https://support.google.com/accounts/answer/185833 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/assistant | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/gemini | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/mail | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/mail/answer/6579 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/mail/answer/7126229 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/messages | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/phoneapp | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/phoneapp/answer/9118387 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/pixelphone | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/pixelphone/answer/4457705 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/pixelphone/answer/7158570 | HEADは偽陰性 |
| OK | 404→200 | 200 | https://support.google.com/pixelphone/answer/7173456 | HEADは偽陰性 |

## まとめ

- **BROKEN: 0件**（HTML の URL 修正は不要）。
- **MANUAL_CHECK: 0件**（403 なし）。
- `https://fonts.googleapis.com`（素のホスト）は GET でも 404 だが、これは preconnect 用ホストヒントであり実リソースではないため機能上 OK と判定。原文（付録A）の一字一句保持ルールにより HTML は改変しない。
- `support.google.com` 系 13件は HEAD で 404 に見えるが GET+UA では全て 200。ページ内リンクとしては全て有効。

## UPDATE-001: Fold系セクション（#fold）の新規URL死活確認 — 2026-07-24

`#fold` セクション本体（付録B HTML）には `<a href>` リンクは **0件**（表と details のみ、外部リンクなし）。よって死活確認対象は Agent 2 が `data/sources.md` に追記した新規出典URLとした。方式: `GET -L` + ブラウザUA（前回の HEAD 偽陰性教訓を適用）。

| 判定 | HTTP(GET+UA) | URL | 備考 |
| --- | --- | --- | --- |
| OK | 200 | https://www.tomsguide.com/news/google-pixel-fold-display-breaks-already-and-this-could-be-the-cause | 初代Fold内側画面破損 主ソース |
| OK | 200 | https://www.androidpolice.com/google-pixel-fold-common-problems-and-how-to-solve-them/ | 保護層/既知問題 主ソース |
| MANUAL_CHECK | 403 | https://www.phonearena.com/news/screen-issue-affects-new-pixel-fold_id148509 | サーバ側ボット保護による偽陰性。裏取り用の副ソースで、内容はWeb検索で確認済み。主ソース(200)が別途あるため影響なし |
| OK | 200 | https://en.wikipedia.org/wiki/Pixel_10_Pro_Fold | IP68/ヒンジ |
| OK | 200 | https://android.gadgethacks.com/news/pixel-10-pro-fold-gets-7-years-of-updates-through-2032/ | 保証7年/ヒンジ |
| OK | 200 | https://k-tai.watch.impress.co.jp/docs/news/1519260.html | 初代Fold日本発売日/価格 |
| OK | 200 | https://blog.google/intl/ja-jp/products/devices-services/2023_07_pixelfoldlaunch/ | Google公式 発売 |
| OK | 200 | https://ascii.jp/elem/000/004/136/4136589/ | 価格¥253,000 裏取り |
| OK | 200 | https://support.google.com/pixelphone/answer/4457705 | 保証期限 一次ソース |
| OK | 200 | https://www.androidauthority.com/google-pixel-software-update-policy-3482984/ | 保証年数 裏取り |

- **BROKEN: 0件**。**MANUAL_CHECK: 1件**（phonearena 403＝ボット保護の偽陰性、主ソース健在のため実害なし）。
