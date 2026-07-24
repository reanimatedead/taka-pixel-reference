# 不具合辞書 移植記録（UPDATE-004 / Agent 1: schema-and-data）

移植日: 2026-07-24
移植元: `docs/index.html`（#os-bugs / #ts / #fold の既知問題 / #ts-pro）
移植先: `docs/dict/data/entries.json`

## 件数

| 区分 | 件数 |
| --- | --- |
| **総件数** | **34** |
| #os-bugs（A11〜A17） | 22 |
| #ts / #fold 機種別既知問題 | 11 |
| #ts-pro（不具合として扱える項目） | 1 |
| VERIFIED | 13 |
| UNVERIFIED | 21 |
| 新規創作 | 0 |

## 移植元 → ID 対応表

### #os-bugs — Android 17（対象: 6a/7a/8a/9a/10a）

| ID | 移植元項目 | 元の状態 | 移植後 | sources |
| --- | --- | --- | --- | --- |
| PXD-0001 | タッチ操作異常 | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0002 | 通信不能（5G→LTE落ち・モバイル接続不可・eSIM消滅） | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0003 | Wi-Fi接続時のみ一部アプリが通信不可 | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0004 | 再起動ループ・文鎮化 | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0005 | アプリ起動遅延 | UNVERIFIED | UNVERIFIED | 空 |

### #os-bugs — Android 16（対象: 6a〜10a）

| ID | 移植元項目 | 元の状態 | 移植後 | sources |
| --- | --- | --- | --- | --- |
| PXD-0006 | Wi-Fi突発切断・「接続済みだが通信不可」 | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0007 | バッテリー異常消費（6a世代で顕著報告） | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0008 | 通知が届かない | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0009 | 戻る操作無反応・画面ホワイトアウト | VERIFIED | **UNVERIFIED** ※1 | 空 |
| PXD-0010 | 位置情報の一時的ズレ（省電力切替直後） | UNVERIFIED | UNVERIFIED | 空 |

### #os-bugs — Android 15 / 14 / 13 / 12 / 11

| ID | 移植元項目 | 元の状態 | 移植後 | sources |
| --- | --- | --- | --- | --- |
| PXD-0011 | A15 プライベートスペース有効化後のアプリ検索不整合 | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0012 | A15 更新直後のアプリフリーズ・再起動ループ報告 | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0013 | A15 自動明るさの挙動変化 | UNVERIFIED | UNVERIFIED | 空 |
| PXD-0014 | A14 複数ユーザー設定時のストレージアクセス不能・データロック | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0015 | A14 戻るジェスチャーの予測アニメーション不安定 | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0016 | A13 通知権限が既定OFFでアプリ通知が来ない | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0017 | A13 一部機種でワイヤレス充電の断続 | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0018 | A12 Material You 刷新直後のバッテリードレイン | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0019 | A12 ウィジェット表示崩れ | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0020 | A12 指紋センサー反応低下（12L含む） | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0021 | A11 特定壁紙設定でのブートループ（クラッシュ画像問題） | VERIFIED | VERIFIED | sources.md の URL |
| PXD-0022 | A11 通話録音の制限開始 | VERIFIED | VERIFIED | sources.md の URL |

※ A14 の「5a はこのバージョンでアップデート終了」・A13 の「4a はこのバージョンでアップデート終了」は EOL 情報であり不具合ではないため移植対象外。

### #ts / #fold 機種別既知問題

| ID | 移植元項目 | 元の状態 | 移植後 | sources |
| --- | --- | --- | --- | --- |
| PXD-0023 | 4a バッテリー容量・充電速度の意図的制限（2025/1 最終アップデート） | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0024 | 5a 電源ボタン陥没・バッテリー膨張 | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0025 | 6a 画面内指紋の精度が低い | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0026 | 6a 発熱・電池持ち | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0027 | 6a 通信が不安定（モデム個体差） | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0028 | 7a 充電中の発熱（ワイヤレス充電停止） | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0029 | 7a 画面のちらつき報告 | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0030 | 8a 画面の緑かぶり報告 | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0031 | 9a 一部ロットのバッテリー出荷前対策 | 記載なし ※2 | UNVERIFIED | 空 |
| PXD-0032 | Fold初代 内側ディスプレイの破損・表示不良報告（#fold） | VERIFIED | VERIFIED | sources.md の URL（3件） |
| PXD-0033 | Fold初代 保護レイヤー剥がれ（#fold） | VERIFIED | VERIFIED | sources.md の URL（2件） |

※ #ts の「共通TSフロー」「4a5G/5a EOL 共通の判断」「8a〜10a 現役世代の一般案内（修復モード等）」「用途別早見表」は手順・判断情報であり個別不具合ではないため移植対象外。Fold初代の「中古購入は非推奨」は購入判断であり不具合ではないため PXD-0032/0033 の情報に含めず対象外。

### #ts-pro

| ID | 移植元項目 | 元の状態 | 移植後 | sources |
| --- | --- | --- | --- | --- |
| PXD-0034 | Lv3 caveat: ブートローダーアンロックで Play Integrity 判定失敗（銀行・決済アプリ使用不能） | UNVERIFIED | UNVERIFIED | 空 |

※ #ts-pro のコードネーム表（UNVERIFIED）・通信テストメニュー（UNVERIFIED）は不具合ではなく参照情報のため移植対象外。

## 判断記録

- **※1: VERIFIED → UNVERIFIED への降格（8件）** — PXD-0001〜0004（A17）と PXD-0006〜0009（A16）は移植元 HTML で VERIFIED だが、`data/sources.md` に対応 URL が存在しない（sources.md 注記「A17/A16 で最初から VERIFIED だった項目は本工程では変更していない」= URL 記録なし）。UPDATE-004 Agent 1 手順 3「対応が特定できない場合 sources は空配列にし verify_state を UNVERIFIED に落とす（勝手にURLを充てない）」に従い降格した。
- **※2: #ts 項目の元状態** — #ts セクションの機種別項目には VERIFIED/UNVERIFIED マーカーが付与されていない。sources.md にも URL がないため、スキーマ規約「新規はUNVERIFIED開始が既定」に準じ UNVERIFIED + sources 空とした。
- **first_seen** — OS別項目は当該 OS の配信年（月が判明する A16/A17 は年月）。機種別ハードウェア項目は機種の発売年を充てた近似値（PXD-0023 のみ 2025-01 と HTML に明記）。
- **affected_os 空配列** — ハードウェア起因・OS非依存の項目（PXD-0024〜0034 の一部）は affected_os を空配列とした。
- **カテゴリ割当** — 症状の主領域で1分類を選択（例: A17再起動ループ=電源・起動、A14ストレージロック=OS更新起因、位置情報ズレ=通信）。
- **機種キー** — 4a / 4a5g / 5a / 6a / 7a / 8a / 9a / 10a / fold / 9profold / 10profold の11キーを使用。
