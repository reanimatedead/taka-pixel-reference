# OS別不具合マトリクス 出典記録（#os-bugs）

## 2026-08-05 — Pixel標準 / Pro 諸元追加（#pixel-lineup / dict #model-specs）

| 項目 | URL | 確認日 | メモ |
| --- | --- | --- | --- |
| Pixel phone hardware tech specs | https://support.google.com/pixelphone/answer/7158570 | 2026-08-05 | Pixel 6/6 Pro、7/7 Pro、8/8 Pro、9/9 Pro/9 Pro XL、10/10 Pro/10 Pro XL の公式ハードウェア諸元。 |
| Pixel phone hardware tech specs（earlier models） | https://support.google.com/pixelphone/answer/16043605 | 2026-08-05 | Pixel 5 の公式ハードウェア諸元。 |
| Learn when you'll get software updates on Google Pixel phones | https://support.google.com/pixelphone/answer/4457705 | 2026-08-05 | Pixel 5a以前はEOL、Pixel 6/7/Foldは5年、Pixel 8以降は7年の更新ポリシー。 |

## 2026-08-02 — 開発者オプション詳細（#dev-options）

| 項目 | URL | 確認日 | メモ |
| --- | --- | --- | --- |
| Android Developers: Configure on-device developer options | https://developer.android.com/studio/debug/dev-options | 2026-08-02 | 開発者オプションの有効化、USB/Wi-Fi debugging、General/Input/Drawing/GPU/Apps 項目の一次ソース。 |
| Android 17 CDD: Developer Options | https://source.android.com/docs/compatibility/17/android-17-cdd#6_2_developer_options | 2026-08-02 | Developer Options を標準UIとして提供し、既定で隠す要件の一次ソース。 |

Agent 2 (research-verifier) による検証ログ。`public/index.html` の `#os-bugs` セクションで `UNVERIFIED` だった項目を Web 検索・実ページ取得で検証し、出典が確認できたものを `VERIFIED` に更新した。

確認日は全て **2026-07-24**。

## VERIFIED に更新した項目（11件）

| 項目 / URL / 確認日 |
| --- |
| **A11 特定壁紙設定でのブートループ（クラッシュ画像問題）** / https://www.androidauthority.com/android-wallpaper-crash-1124577/ / 2026-07-24 — 非sRGB壁紙画像が ImageProcessorHelper の色空間輝度オーバーフローを誘発しクラッシュ/ブートループ。Android 11 は自動色空間変換で回避。 |
| **A11 通話録音の制限開始** / https://www.androidpolice.com/google-ends-call-recording-apps-accessibility-services/ / 2026-07-24 — アクセシビリティAPI経由の通話録音を Google が制限。Android 10/11 で通話音声アクセスが外れた流れ。 |
| **A12 Material You 刷新直後のバッテリードレイン** / https://www.tomsguide.com/news/android-12-is-draining-some-google-pixel-batteries-what-you-need-to-know / 2026-07-24 — Android 12（Material You 版）で複数 Pixel にバッテリードレイン報告。 |
| **A12 ウィジェット表示崩れ** / https://www.androidpolice.com/android-12-fixes-material-you-glitches-when-previewing-widgets/ / 2026-07-24 — ウィジェットのプレビュー崩れ・非表示・角丸クロップ等をアップデートで修正。 |
| **A12 指紋センサー反応低下（12L含む）** / https://www.androidpolice.com/google-details-why-pixel-6-fingerprint-sensor-is-slow-but-were-not-satisfied-with-the-explanation/ / 2026-07-24 — Pixel 6 / Android 12 の画面内指紋の低速・不安定を Google が公式に認める。 |
| **A13 通知権限が既定OFFでアプリ通知が来ない** / https://developer.android.com/develop/ui/compose/notifications/notification-permission / 2026-07-24 — Android 13 (API 33) で POST_NOTIFICATIONS ランタイム権限を導入、新規アプリは既定OFF。公式ドキュメント。 |
| **A13 一部機種でワイヤレス充電の断続** / https://www.androidauthority.com/wireless-charging-android-13-3198736/ / 2026-07-24 — Android 13 更新後に一部 Pixel でワイヤレス充電が断続（Not charging 表示）。後にパッチ提供。 |
| **A14 複数ユーザー設定時のストレージアクセス不能・データロック（重大）** / https://9to5google.com/2023/10/17/android-14-pixel-6-storage-problems/ / 2026-07-24 — 複数ユーザープロファイル端末でストレージアクセス喪失（"Structure needs cleaning"）・ブートループ・データ喪失。Google が認め修復ツールを提供。 |
| **A14 戻るジェスチャーの予測アニメーション不安定** / https://docs.flutter.dev/release/breaking-changes/android-predictive-back / 2026-07-24 — Android 14 の予測型戻るアニメーションがジェスチャー確定前に開始し、戻るをキャンセルするアプリで不安定化・クラッシュ。 |
| **A15 プライベートスペース有効化後のアプリ検索不整合** / https://www.tomsguide.com/phones/android-phones/private-space-on-android-15-has-an-annoying-glitch-but-android-15-beta-21-can-fix-it / 2026-07-24 — プライベートスペースのアプリが検索で見えてしまう不整合。beta 2.1 で修正。Google サポートスレッドでも裏取り。 |
| **A15 更新直後のアプリフリーズ・再起動ループ報告** / https://9to5google.com/2026/06/11/google-pixel-updates-left-phones-useless-bootlooping-for-some-a-fix-is-now-in-sight/ / 2026-07-24 — 更新後の再起動ループ/フリーズ報告（Pixel 6〜10、Issue Tracker 約800件）。Google が認め復旧ツールを提供。 |

## UNVERIFIED のまま残した項目（3件・偽の検証成功を報告しない方針）

| 項目 | 判断理由 |
| --- | --- |
| **A15 自動明るさの挙動変化** | 汎用的な自動明るさ不満（自動復帰・屋外視認性）はどのバージョンにも存在するが、Android 15 固有の「挙動変化」として認知された一次ソースを確認できず。 |
| **A16 位置情報の一時的ズレ（省電力切替直後）** | 「省電力切替直後の位置ズレ/精度低下」に一致する一次ソースなし。Android 16 には Google 認定の GNSS モジュール非スリープ不具合（2026/3）が存在するが、これは*バッテリードレイン*であり位置精度の不具合ではないため、混同を避け UNVERIFIED を維持。 |
| **A17 アプリ起動遅延** | Android 17 には実在の不具合（タッチ/スクロール、ブートループ、GPU性能低下、Wi-Fi等）があるが、「更新後の再インデックスによるアプリ起動遅延」を defect として記す一次ソースは確認できず。ART 再最適化の一般論のみで Android 17 固有と特定できない。 |

## 補足（Agent 2 の注記）

- **A12 Material You バッテリー**: 出典はバッテリードレインを Android 12 リリースそのものに紐づけている。「Material You」はそのリリースのブランド名であり、UI コード単独が原因という厳密解釈までは支持しない（症状の存在は支持）。
- `#os-bugs` の A17 / A16 で最初から `VERIFIED` だった項目（タッチ操作異常・通信不能・Wi-Fi・再起動ループ / Wi-Fi突発切断・バッテリー異常消費・通知が届かない・戻る操作無反応）は付録A原文の判定を尊重し、本工程では変更していない。

---

# Fold系セクション 出典記録（#fold）— UPDATE-001

Agent 2 (research-verifier) による `#fold` セクションの検証ログ。`UNVERIFIED` だった2項目を Web 検索・実ページ取得で検証し `VERIFIED` に更新した。確認日は全て **2026-07-24**。

## VERIFIED に更新した項目（2件）

| 項目 / URL / 確認日 |
| --- |
| **初代Pixel Fold 内側ディスプレイの破損・表示不良報告** / https://www.tomsguide.com/news/google-pixel-fold-display-breaks-already-and-this-could-be-the-cause / 2026-07-24 — ベゼルと画面保護層の間に生の内側ディスプレイが露出する隙間があり、ヒンジ付近に入った微細な異物が折りたたみ時にOLEDを突き破る設計上の脆弱性。発売直後から複数の破損報告。裏取り: https://www.androidpolice.com/google-pixel-fold-common-problems-and-how-to-solve-them/ , https://www.phonearena.com/news/screen-issue-affects-new-pixel-fold_id148509 |
| **初代Pixel Fold 保護レイヤー剥がれ（自分で剥がさない仕様）** / https://www.androidpolice.com/google-pixel-fold-common-problems-and-how-to-solve-them/ / 2026-07-24 — 内側画面のプリインストール保護層は一体構造であり自己剥離は非推奨。Google サポート指示で剥がしたユーザーがラミネート浮き・中央からのクモの巣状クラックを経験した報告あり。裏取り: https://www.tomsguide.com/news/google-pixel-fold-display-breaks-already-and-this-could-be-the-cause |

## 既に本文で VERIFIED だった項目の裏取り（変更なし・出典追記のみ）

| 項目 / URL / 確認日 |
| --- |
| **10 Pro Fold 折りたたみ初のIP68防塵防水** / https://en.wikipedia.org/wiki/Pixel_10_Pro_Fold / 2026-07-24 — Pixel 10 Pro Fold で折りたたみ機として初の IP68 到達（従来 Fold は IPX8 で防塵非対応）。 |
| **10 Pro Fold ギアレスヒンジ 10年動作耐久設計** / https://android.gadgethacks.com/news/pixel-10-pro-fold-gets-7-years-of-updates-through-2032/ / 2026-07-24 — ギアレスヒンジ採用と長期耐久設計。 |

## 発売日・価格・保証期限の検証（本文は正しく、修正不要）

| 項目 / URL / 確認日 |
| --- |
| **初代Pixel Fold 日本発売日 2023/7/27・価格 ¥253,000（税込）** / https://k-tai.watch.impress.co.jp/docs/news/1519260.html / 2026-07-24 — 本文「発売（日本）2023/7」「発売時価格 ¥253,000」を確認。裏取り: https://blog.google/intl/ja-jp/products/devices-services/2023_07_pixelfoldlaunch/ , https://ascii.jp/elem/000/004/136/4136589/ |
| **アップデート保証期限（一次ソース）** / https://support.google.com/pixelphone/answer/4457705 / 2026-07-24 — 一次ソースはUS Google Store 販売開始日から起算の年数（初代Fold=5年 / 9 Pro Fold=7年 / 10 Pro Fold=7年）を規定。本文の到達年月（初代=2028/6・9 Pro Fold=2031/9・10 Pro Fold=2032/10）は各US発売月（2023/6・2024/9・2025/10）+年数と整合。durationは一次ソースで直接 VERIFIED、到達年月は算出値として整合を確認。裏取り: https://android.gadgethacks.com/news/pixel-10-pro-fold-gets-7-years-of-updates-through-2032/ , https://www.androidauthority.com/google-pixel-software-update-policy-3482984/ |

## 補足（Agent 2 の注記 / UPDATE-001）

- 事実誤りは発見されなかったため本文の数値・日付修正は行っていない（`data/corrections.md` への記録なし）。UNVERIFIED→VERIFIED の状態更新のみ実施。
- 保証到達年月は一次ソースが「販売開始日+年数」で規定するため、月単位の値は算出値。年数（duration）自体は一次ソースで直接確認できるため VERIFIED とした。

---

# 専門TS（#ts-pro）コードネーム検証ログ — UPDATE-003 / Agent 2

検証日: **2026-07-24**。一次ソース指定: `https://developers.google.com/android/images`（Factory Images）。

## 検証結果サマリ: 全項目 UNVERIFIED のまま据え置き

**理由（重要・偽の検証成功を出さないための記録）:**
一次ソースに指定された Factory Images ページ（`https://developers.google.com/android/images`）は、
コードネーム→ダウンロードリンクの本体テーブルが、利用規約への同意（acknowledgement）後に
JavaScript で動的挿入される構造。今回利用した取得系（HTML→Markdown 変換・JS非実行）では
当該テーブルが本文として取得できず、ページ本文からコードネーム文字列を一件も確認できなかった。

- 取得試行1: `WebFetch` で当該ページ本文取得 → 導入文・警告・規約のみ。ダウンロード表は本文に含まれず（NOT LISTED）。
- 取得試行2: `WebSearch`（allowed_domains=developers.google.com）→ ページの存在は確認できるが個別コードネームは列挙されず。

指示書の絶対ルール「確認できない項目は UNVERIFIED のまま残す／推測で埋めない／偽の検証成功を報告しない」に従い、
**既存記載（sunfish, bramble, barbet, bluejay, lynx, akita, tegu, felix, comet）を一次ソースで照合できなかったため、
これらを VERIFIED に昇格させない。** 一般に流通している値と一致はしているが、
指定された一次ソース上での実照合が取れていない以上、UNVERIFIED を維持する。

## 各項目の状態

| デバイス | HTML記載 | 一次ソース照合 | 状態 |
| --- | --- | --- | --- |
| Pixel 4a | sunfish | 未取得（JS-gated table） | UNVERIFIED |
| Pixel 4a (5G) | bramble | 未取得 | UNVERIFIED |
| Pixel 5a | barbet | 未取得 | UNVERIFIED |
| Pixel 6a | bluejay | 未取得 | UNVERIFIED |
| Pixel 7a | lynx | 未取得 | UNVERIFIED |
| Pixel 8a | akita | 未取得 | UNVERIFIED |
| Pixel 9a | tegu | 未取得 | UNVERIFIED |
| **Pixel 10a（最優先）** | 要確認 | 未取得（そもそもページで存在確認できず） | **UNVERIFIED** |
| Pixel Fold（初代） | felix | 未取得 | UNVERIFIED |
| Pixel 9 Pro Fold | comet | 未取得 | UNVERIFIED |
| **Pixel 10 Pro Fold** | 要確認 | 未取得 | **UNVERIFIED** |

## Play Integrity（ブートローダーアンロックで決済系アプリ不可）

- HTML記載: `#ts-pro` Lv3 C の caveat に UNVERIFIED 付きで記載。
- 一次ソース照合: 決済/銀行アプリの Play Integrity(旧SafetyNet) 判定はデバイス完全性(MEETS_DEVICE_INTEGRITY)を要求し、
  ブートローダーアンロック端末では当該判定が通らない、という挙動は Play Integrity API の一般的仕様として広く知られる。
  ただし本 UPDATE で指定された一次ソース（Factory Images ページ）はこの事項の出典ではなく、
  Google Play Integrity 公式ドキュメントでの実照合を今回実施していないため **UNVERIFIED を維持**。

## 結論

- 本文修正なし（誤りを一次ソース上で確認できていないため、修正の根拠がない = `data/corrections.md` への記録事項なし）。
- 10a / 10 Pro Fold を含む全コードネームは UNVERIFIED のまま。完了条件「10a コードネームが VERIFIED 化 or 理由付き UNVERIFIED」→ **理由付き UNVERIFIED で確定**。

---

# UPDATE-005R Agent 2 (codename-fixer) 追記 — 2026-07-25

コードネーム表（`docs/index.html` #ts-pro）を付録E（`data/research-2026-07.md`）の確定情報で更新した。

## 確定内容

| 機種 | コードネーム | 状態 | 出典 |
| --- | --- | --- | --- |
| Pixel 10a | **stallion**（STA5） | **VERIFIED** | https://9to5google.com/2026/03/05/pixel-10a-factory-images/ （9to5Google・Factory Image公開記事） |
| 4a=sunfish / 4a(5G)=bramble / 5a=barbet / 6a=bluejay / 7a=lynx / 8a=akita / 9a=tegu / Fold=felix / 9 Pro Fold=comet | 既存9件 | **VERIFIED** | https://www.androidpolice.com/google-pixel-codename-list/ + https://wiki.lineageos.org/devices/ + https://source.android.com/docs/setup/build/building-pixel-kernels |
| Pixel 10 Pro Fold | rango（リーク段階・公式Factory Image未掲載） | **UNVERIFIED 維持** | https://www.xda-developers.com/google-pixel-10-leaks-codenames/ |

## 注記

- 既存9件の VERIFIED は Google 公式一次ソース単独ではなく、Android Police 一覧・LineageOS wiki・AOSP build docs の**community 照合**（3ソース一致）による。
- 10 Pro Fold = rango はリーク段階のため表に名称は記載しつつ UNVERIFIED を維持した。
