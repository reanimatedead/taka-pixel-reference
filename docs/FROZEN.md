# FROZEN — Pixel ビルド番号辞書 凍結宣言

- **凍結日: 2026-07-31**
- 本リポジトリの Pixel ビルド番号辞書レイヤ（`docs/dict/data/builds.json` とその生成・検証・表示系）は本日をもって凍結する。**今後は自動収集と鮮度バナーのみで運用し、機能追加はしない。**

## 凍結時点の実測値

| 項目 | 値 |
| --- | --- |
| ビルド件数 (`docs/dict/data/builds.json`) | 67 件 |
| confidence 内訳 | OFFICIAL 44 / MULTI_SOURCE 19 / SINGLE_SOURCE 4 |
| テスト: `tests/test_contract.py` | 24 チェック |
| テスト: `tests/test_suffix_map.py` | 23 チェック |
| テスト: `tests/test_suffix_fallback.py` | 13 チェック |
| テスト合計 | 60 チェック（3 ランナーすべて自作・pytest 不使用） |
| 不具合エントリ (`docs/dict/data/entries.json`) | 44 件 |

## 月次自動収集の仕組み

実体は `scripts/monthly_collect.sh`（収集のみ。git 操作は一切含めない。commit/push は人間が検証ゲートを通して行う）。

1. **スナップショット取得**: 4 ソースを `data/raw/$(date +%F)/` に保存する。
   - `developers.google.com/android/ota` → `ota.html`（同意壁回避のため cookie `devsite_wall_acks=nexus-ota-tos` を付与）
   - `developers.google.com/android/images` → `images.html`（同 `nexus-image-tos`）
   - `source.android.com/docs/security/bulletin/pixel` → `pixel-bulletin.html`（silent sign-in のリダイレクトループ回避のため cookie jar 使用）
   - `support.google.com/pixelphone/answer/4457705` → `pixel-update-help.html`
   - curl は `-fsSL --retry 3 --retry-delay 5 --max-time 120` + 明示 User-Agent（`taka-pixel-reference-collector/1.0`）。
   - 取得後に最小バイト数チェック（ota/images 200KB・bulletin/help 100KB）と ota.html のビルドID正規表現チェックで同意壁・bot ブロックの縮退を検知し、異常時は非 0 終了。
2. **パース**: `scripts/parse_builds.py $(date +%F)` で `docs/dict/data/builds.json` を再生成。
3. **検証**: `tests/test_contract.py` → `tests/test_suffix_map.py` → `tests/test_suffix_fallback.py` → `scripts/decay_warning.py` を必ず全部実行（`set -euo pipefail` のため 1 つでも FAIL すれば非 0 終了）。
- ログは `data/logs/monthly-collect-YYYY-MM-DD.log` に常に残る。

起動は launchd（`launchd/com.taka.pixel-builds-monthly.plist`, Label `com.taka.pixel-builds-monthly`）:

- **毎月 10 日 03:00 と 20 日 03:00 の月 2 回**（StartCalendarInterval の 2 要素配列）。月 2 回化は 2026-07-30 変更で、A17 正式版 6/16・Feature Drop 11/11・QPR2 2 次更新 12/19 など 10 日単発では拾えない月中〜月末配信の取りこぼし防止が理由。
- 実行コマンドは `/bin/bash -c 'exec "$HOME/taka-pixel-reference/scripts/monthly_collect.sh"'`（launchd は StandardOutPath 等で環境変数を展開しないため、stdout/stderr は `/tmp/com.taka.pixel-builds-monthly.{out,err}.log` 固定）。
- 注意: plist の LaunchAgents への設置（`launchctl bootstrap`）は人間ゲート運用で、**凍結時点では未設置**（MEMORY: launchd 月2回版設置は人間の残タスク）。

## 鮮度バナー

- `scripts/decay_warning.py` が最終収集日から 30 日超で `docs/dict/data/status.json` に stale を立て、`docs/dict/index.html` が status.json（サーバ側判定）と builds.json の `generated_at`（クライアント側判定）の二重化で警告バナーを表示する。

## 運用方針（凍結後）

- 自動収集（月 2 回）と鮮度バナーのみで運用する。
- データは `parse_builds.py` による再生成 + 3 テストランナーの検証ゲートを通過したもののみ commit する。
- **機能追加はしない**（UI 拡張・スキーマ拡張・新ソース追加を含む）。バグ修正・データ訂正は判断ログ（`data/build-dict-decisions.md`）への記録を必須とする。

## 再開条件

以下のいずれかが起きた場合のみ凍結を解除して改修する:

1. **パース失敗が 2 ヶ月連続**（monthly_collect.sh の非 0 終了が 2 ヶ月連続 = ソース側の構造変更が恒久化したと判断）
2. **Android 18 リリース**（新プレフィックス世代の追加が必要になる）
