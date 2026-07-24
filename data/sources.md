# OS別不具合マトリクス 出典記録（#os-bugs）

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
