#!/usr/bin/env python3
"""sources URL 生存確認スクリプト。

builds.json / entries.json 内の全 sources URL のユニーク集合に対し
HEAD（失敗時 GET フォールバック）でアクセスし、死んでいるリンクを報告する。
死リンクが 1 件でもあれば exit code 1。

実行: python3 scripts/verify_sources_alive.py
依存: python3 標準ライブラリのみ。ネットワークアクセスは軽く
（ユニークURLのみ・順次・リクエスト間隔 0.5s）。

他リポの同名スクリプトの思想（ソースURL失効の定期検出）を踏襲した
本リポジトリ向け新規実装。
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO / "docs" / "dict" / "data" / "builds.json"
ENTRIES_PATH = REPO / "docs" / "dict" / "data" / "entries.json"

TIMEOUT = 15  # seconds
INTERVAL = 0.5  # seconds between requests
UA = "taka-pixel-reference-linkcheck/1.0 (+https://github.com/reanimatedead/taka-pixel-reference)"
# 4xx でも「ページ自体は応答している」ものは生存とみなす閾値: 200-399 を生存、
# 401/403 は認証壁（devsite の同意壁等）の可能性があるため警告扱い（死とはしない）。
SOFT_ALIVE = {401, 403}


def collect_urls():
    # sources の要素は builds.json では string、entries.json では {url, date} object。
    raw = []
    builds_doc = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))
    for b in builds_doc.get("builds", []):
        raw.extend(b.get("sources", []))
    for e in json.loads(ENTRIES_PATH.read_text(encoding="utf-8")):
        raw.extend(e.get("sources", []))
    # 順序保存のユニーク化
    seen = set()
    uniq = []
    for s in raw:
        u = s.get("url") if isinstance(s, dict) else s
        if isinstance(u, str) and u.startswith("http") and u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def probe(url, method):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status


def check(url):
    """(status, note) を返す。status=None は接続不能。"""
    for method in ("HEAD", "GET"):
        try:
            return probe(url, method), method
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (405, 501):
                continue  # HEAD 非対応サーバは GET で再試行
            return e.code, method
        except Exception as e:  # URLError / timeout / SSL etc.
            if method == "HEAD":
                continue  # 接続レイヤの失敗も GET で一度だけ再試行
            return None, f"{type(e).__name__}: {e}"
    return None, "unreachable"


def main():
    urls = collect_urls()
    print(f"checking {len(urls)} unique source URLs (timeout={TIMEOUT}s, interval={INTERVAL}s)")
    dead = []
    warned = []
    for i, url in enumerate(urls):
        if i:
            time.sleep(INTERVAL)
        status, note = check(url)
        if status is not None and 200 <= status < 400:
            print(f"[ OK ] {status} {url}")
        elif status in SOFT_ALIVE:
            print(f"[WARN] {status} {url} (auth/consent wall? treated as alive)")
            warned.append((status, url))
        else:
            print(f"[DEAD] {status if status is not None else note} {url}")
            dead.append((status, note, url))
    print("---")
    print(f"total={len(urls)} ok={len(urls) - len(dead) - len(warned)} warn={len(warned)} dead={len(dead)}")
    if dead:
        print("DEAD LINKS:")
        for status, note, url in dead:
            print(f"  {status if status is not None else note}  {url}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
