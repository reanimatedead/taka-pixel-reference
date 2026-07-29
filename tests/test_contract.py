#!/usr/bin/env python3
"""契約テスト: docs/dict/data/builds.json / entries.json / docs/dict/index.html

実行: python3 tests/test_contract.py
依存: python3 標準ライブラリのみ。
方針: データ改変は一切しない。契約違反は FAIL として報告するのみ。
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO / "docs" / "dict" / "data" / "builds.json"
ENTRIES_PATH = REPO / "docs" / "dict" / "data" / "entries.json"
INDEX_PATH = REPO / "docs" / "dict" / "index.html"

# ---- 基準値（2026-07-30 時点。行数非減少ゲート）----
MIN_LINES_ENTRIES = 1764
MIN_LINES_BUILDS = 1860
MIN_LINES_INDEX = 727

# ---- 値域 ----
BUILD_REQUIRED = [
    "build_id", "os", "track", "release_date", "security_patch",
    "devices", "region_scope", "sources", "verify_state",
]
TRACKS = {"stable", "qpr", "monthly", "drop"}
VERIFY_STATES = {"VERIFIED", "UNVERIFIED"}

ENTRY_REQUIRED = [
    "id", "title_ja", "title_en", "yomi", "category", "severity",
    "affected_models", "affected_os", "symptom", "cause", "workaround",
    "fix_status", "first_seen", "last_checked", "verify_state", "sources",
]
EVIDENCE_LEVELS = {"OFFICIAL", "MULTI_SOURCE", "REPORTED_ONLY"}
LINK_CONFIDENCES = {"official", "inferred", "estimated", "unknown"}

BUILD_ID_RE = re.compile(r"^[A-Z]{2}[0-9A-Z]{2}\.[0-9]{6}\.[0-9]{3}(\.[A-Z][0-9])?$")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main():
    builds_doc = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))
    entries = json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    builds = builds_doc["builds"] if isinstance(builds_doc, dict) else builds_doc

    # ---- 1. builds.json 必須キー・値域 ----
    missing = [
        (b.get("build_id", f"#index{i}"), k)
        for i, b in enumerate(builds)
        for k in BUILD_REQUIRED
        if k not in b
    ]
    check("builds: required keys present (all %d records)" % len(builds),
          not missing, str(missing[:10]))

    bad_track = [(b["build_id"], b.get("track")) for b in builds
                 if b.get("track") not in TRACKS]
    check("builds: track in %s" % sorted(TRACKS), not bad_track, str(bad_track[:10]))

    bad_vs = [(b["build_id"], b.get("verify_state")) for b in builds
              if b.get("verify_state") not in VERIFY_STATES]
    check("builds: verify_state in VERIFIED/UNVERIFIED", not bad_vs, str(bad_vs[:10]))

    # ---- 3. build_id 正規表現 ----
    bad_id = [b["build_id"] for b in builds if not BUILD_ID_RE.match(b["build_id"])]
    check("builds: build_id matches ^[A-Z]{2}[0-9A-Z]{2}\\.[0-9]{6}\\.[0-9]{3}(\\.[A-Z][0-9])?$",
          not bad_id,
          "%d 件不一致 %s（データは改変しない。正規表現の適否は人間確認）" % (len(bad_id), bad_id[:10]))

    dup = len(builds) - len({b["build_id"] for b in builds})
    check("builds: build_id unique", dup == 0, "%d duplicates" % dup)

    # ---- 2. entries.json 必須16キー・値域 ----
    check("entries: record count == 44", len(entries) == 44, "actual %d" % len(entries))

    e_missing = [
        (e.get("id", f"#index{i}"), k)
        for i, e in enumerate(entries)
        for k in ENTRY_REQUIRED
        if k not in e
    ]
    check("entries: required 16 keys present (all records)", not e_missing, str(e_missing[:10]))

    bad_ev = [(e["id"], e.get("evidence_level")) for e in entries
              if e.get("evidence_level") not in EVIDENCE_LEVELS]
    check("entries: evidence_level in OFFICIAL/MULTI_SOURCE/REPORTED_ONLY",
          not bad_ev, str(bad_ev[:10]))

    # build_link.confidence 値域（first_seen / fixed_in は object 形、
    # still_open_as_of は string も許容 = schema-proposal.md 1.1 準拠）
    bad_conf = []
    for e in entries:
        bl = e.get("build_link")
        if not bl:
            continue
        for key, val in bl.items():
            if isinstance(val, dict) and "confidence" in val:
                if val["confidence"] not in LINK_CONFIDENCES:
                    bad_conf.append((e["id"], key, val["confidence"]))
    check("entries: build_link.confidence in official/inferred/estimated/unknown",
          not bad_conf, str(bad_conf[:10]))

    # ---- 4. 参照整合 ----
    bids = {b["build_id"] for b in builds}
    dangling = []
    for e in entries:
        bl = e.get("build_link") or {}
        for key, val in bl.items():
            bid = val.get("build_id") if isinstance(val, dict) else val
            if bid and bid not in bids:
                dangling.append((e["id"], key, bid))
    check("entries: build_link build_ids exist in builds.json", not dangling, str(dangling[:10]))

    # ---- 5. 行数非減少 ----
    def lines(p):
        return p.read_text(encoding="utf-8").count("\n") + (
            0 if p.read_text(encoding="utf-8").endswith("\n") else 1)

    n_e = lines(ENTRIES_PATH)
    n_b = lines(BUILDS_PATH)
    n_i = lines(INDEX_PATH)
    check("lines: entries.json >= %d" % MIN_LINES_ENTRIES, n_e >= MIN_LINES_ENTRIES, "actual %d" % n_e)
    check("lines: builds.json >= %d" % MIN_LINES_BUILDS, n_b >= MIN_LINES_BUILDS, "actual %d" % n_b)
    check("lines: index.html >= %d" % MIN_LINES_INDEX, n_i >= MIN_LINES_INDEX, "actual %d" % n_i)

    # ---- 6. ソート順（build_id ASC = scripts/parse_builds.py L322 の既存規則を固定）----
    ids = [b["build_id"] for b in builds]
    check("builds: sorted by build_id ASC (parse_builds.py の既存ソート規則)",
          ids == sorted(ids),
          "first mismatch: %s" % next(
              (f"index {i}: {a} > {b_}" for i, (a, b_) in enumerate(zip(ids, ids[1:])) if a > b_),
              ""))

    # ---- 出力 ----
    n_fail = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            n_fail += 1
        line = f"[{mark}] {name}"
        if not ok and detail:
            line += f"  -> {detail}"
        print(line)
    print(f"---\n{len(results) - n_fail}/{len(results)} passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
