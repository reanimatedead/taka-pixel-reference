#!/usr/bin/env python3
"""sources URL 生存確認スクリプト。

builds.json / entries.json 内の全 sources URL のユニーク集合に対し
HEAD（失敗時 GET フォールバック）でアクセスし、死んでいるリンクを報告する。
死リンクが 1 件でもあれば exit code 1。

実行: python3 scripts/verify_sources_alive.py
依存: python3 標準ライブラリのみ。ネットワークアクセスは軽く
（ユニークURLのみ・順次・リクエスト間隔 0.5s）。

Obsidian-Public-Vault 版とは別実装。将来共通化検討。
（思想＝ソースURL失効の定期検出は同じだが、コードは本リポジトリ向け新規実装）

判定ロジック（2026-07-30 Agent 5 改修）:
- HEAD が 4xx でも GET で必ず再確認する。support.google.com は HEAD に
  404 を返す（GET では 200）ことが実測で確認済みのため（HEAD 偽陰性）。
- support.google.com 系で GET も失敗した場合は hl=ja を付与して再試行。
- それでも失敗した場合は 1 回だけリトライ（一過性のネットワーク失敗対策）。
"""
import json
import sys
import time
import urllib.error
import urllib.parse
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


def get_once(url):
    """GET 1回。(status, note) を返す。status=None は接続不能。"""
    try:
        return probe(url, "GET"), "GET"
    except urllib.error.HTTPError as e:
        return e.code, "GET"
    except Exception as e:  # URLError / timeout / SSL etc.
        return None, f"{type(e).__name__}: {e}"


def is_alive(status):
    return status is not None and (200 <= status < 400 or status in SOFT_ALIVE)


def with_hl_ja(url):
    return url + ("&hl=ja" if "?" in url else "?hl=ja")


def check(url):
    """(status, note) を返す。status=None は接続不能。

    HEAD 成功(2xx/3xx)以外は必ず GET で再確認する。support.google.com は
    HEAD に 404 を返すが GET では 200 の HEAD 偽陰性が実測されているため、
    旧実装（HEAD の 4xx を即 dead 判定）は誤検出していた。
    """
    try:
        status = probe(url, "HEAD")
        if 200 <= status < 400:
            return status, "HEAD"
    except Exception:
        pass  # HEAD の失敗理由によらず GET で確認する
    status, note = get_once(url)
    if is_alive(status):
        return status, note
    # support.google.com 系: hl 未指定が原因のことがあるため hl=ja を付与して再試行
    host = urllib.parse.urlsplit(url).hostname or ""
    if host == "support.google.com":
        s2, n2 = get_once(with_hl_ja(url))
        if is_alive(s2):
            return s2, f"{n2} +hl=ja"
    # 一過性のネットワーク失敗対策のリトライ（1回のみ）
    time.sleep(1.0)
    s3, n3 = get_once(url)
    if is_alive(s3):
        return s3, f"{n3} retry"
    return status if status is not None else s3, note if status is not None else n3


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
