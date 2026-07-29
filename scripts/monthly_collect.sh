#!/usr/bin/env bash
# monthly_collect.sh — Pixel ビルド辞書の月次収集パイプライン（launchd から毎月10日 03:00 に起動）
#
#   1. 4ソースを data/raw/$(date +%F)/ にスナップショット
#   2. scripts/parse_builds.py で docs/dict/data/builds.json を再生成
#   3. tests/test_contract.py + scripts/decay_warning.py で検証
#
# git 操作は一切含めない（収集のみ。commit/push は人間が検証ゲートを通して行う）。
# ログは data/logs/monthly-collect-YYYY-MM-DD.log に常に残す。失敗時は非0で終了。
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TODAY="$(date +%F)"
RAW="$REPO/data/raw/$TODAY"
LOGDIR="$REPO/data/logs"
LOG="$LOGDIR/monthly-collect-$TODAY.log"

mkdir -p "$RAW" "$LOGDIR"
exec >>"$LOG" 2>&1
echo "=== monthly_collect start $(date '+%Y-%m-%d %H:%M:%S') repo=$REPO ==="

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) taka-pixel-reference-collector/1.0"
CURL=(curl -fsSL --retry 3 --retry-delay 5 --max-time 120 -A "$UA")
JAR="$(mktemp)"
trap 'rm -f "$JAR"' EXIT

# --- 1. スナップショット取得 -------------------------------------------------
# ota / images はライセンス同意壁があるため devsite_wall_acks cookie を付与（Agent 2 判断ログ準拠）
"${CURL[@]}" -b "devsite_wall_acks=nexus-ota-tos" \
  "https://developers.google.com/android/ota" -o "$RAW/ota.html"
sleep 1
"${CURL[@]}" -b "devsite_wall_acks=nexus-image-tos" \
  "https://developers.google.com/android/images" -o "$RAW/images.html"
sleep 1
# bulletin は cookie jar なしだと silent sign-in のリダイレクトループになる（同上）
"${CURL[@]}" -c "$JAR" -b "$JAR" \
  "https://source.android.com/docs/security/bulletin/pixel" -o "$RAW/pixel-bulletin.html"
sleep 1
"${CURL[@]}" \
  "https://support.google.com/pixelphone/answer/4457705?hl=en" -o "$RAW/pixel-update-help.html"

# --- 取得内容の妥当性チェック（同意壁ページ等の縮退検知） ---------------------
check_min_bytes() { # file min_bytes
  local sz
  sz="$(wc -c <"$1" | tr -d ' ')"
  if [ "$sz" -lt "$2" ]; then
    echo "ERROR: $1 too small ($sz bytes < $2). consent wall / bot block の可能性"
    exit 1
  fi
  echo "ok: $1 ($sz bytes)"
}
check_min_bytes "$RAW/ota.html" 200000
check_min_bytes "$RAW/images.html" 200000
check_min_bytes "$RAW/pixel-bulletin.html" 100000
check_min_bytes "$RAW/pixel-update-help.html" 100000
if ! grep -qE '[A-Z]{2}[0-9A-Z]{2}\.[0-9]{6}\.[0-9]{3}' "$RAW/ota.html"; then
  echo "ERROR: ota.html にビルドIDパターンが見つからない（同意壁の素ページ疑い）"
  exit 1
fi

# --- 2. パース（builds.json 再生成） -----------------------------------------
python3 "$REPO/scripts/parse_builds.py" "$TODAY"

# --- 3. 検証 -----------------------------------------------------------------
python3 "$REPO/tests/test_contract.py"
python3 "$REPO/scripts/decay_warning.py"

echo "=== monthly_collect done $(date '+%Y-%m-%d %H:%M:%S') ==="
