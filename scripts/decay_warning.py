#!/usr/bin/env python3
"""収集鮮度の監視スクリプト。

builds.json の generated_at（無ければ data/raw/ の最新日付ディレクトリ）を
最終収集日とみなし、30日以上収集が止まっていたら警告を出して exit code 1。
併せて docs/dict/data/status.json に
{"last_collected": "YYYY-MM-DD", "days_since": N, "stale": bool} を出力する
（ページ側の警告バナーが fetch する）。

実行: python3 scripts/decay_warning.py
依存: python3 標準ライブラリのみ。ネットワークアクセスなし。

他リポの同名スクリプトの思想（データ収集停止の腐敗検知）を踏襲した
本リポジトリ向け新規実装。
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO / "docs" / "dict" / "data" / "builds.json"
RAW_DIR = REPO / "data" / "raw"
STATUS_PATH = REPO / "docs" / "dict" / "data" / "status.json"

STALE_DAYS = 30
DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def last_collected():
    """(date, source) を返す。特定できなければ (None, reason)。"""
    try:
        doc = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))
        g = doc.get("generated_at")
        if g:
            return datetime.strptime(str(g)[:10], "%Y-%m-%d").date(), "builds.json generated_at"
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    if RAW_DIR.is_dir():
        dirs = sorted(d.name for d in RAW_DIR.iterdir()
                      if d.is_dir() and DATE_DIR_RE.match(d.name))
        if dirs:
            return datetime.strptime(dirs[-1], "%Y-%m-%d").date(), "data/raw/ latest dir"
    return None, "no generated_at and no dated dir under data/raw/"


def main():
    today = date.today()  # ローカル日付（収集も同一マシンのローカル日付ディレクトリで行う）
    last, source = last_collected()
    if last is None:
        print(f"ERROR: last collection date unknown ({source})")
        return 1
    days = max(0, (today - last).days)  # タイムゾーン揺れによる負値は 0 に丸める
    stale = days >= STALE_DAYS
    status = {"last_collected": last.isoformat(), "days_since": days, "stale": stale}
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"last_collected={last.isoformat()} ({source}) days_since={days} stale={stale}")
    print(f"wrote {STATUS_PATH.relative_to(REPO)}")
    if stale:
        print(f"WARNING: build collection has been stalled for {days} days (>= {STALE_DAYS})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
