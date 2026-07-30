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
# MIN_LINES_BUILDS 1860→1960: Agent 3 (2nd iteration: Schema Fixer) が
# base_month を全67件に追加 (2026-07-30)。行数非減少の思想は維持。
# MIN_LINES_BUILDS 1960→2286: Agent 4 (2nd iteration: Cross-Validator) が
# confidence / confidence_sources を全67件に追加 (2026-07-30)。
MIN_LINES_ENTRIES = 1764
MIN_LINES_BUILDS = 2286
MIN_LINES_INDEX = 727

# ---- 値域 ----
BUILD_REQUIRED = [
    "build_id", "os", "track", "release_date", "security_patch",
    "devices", "region_scope", "sources", "verify_state",
]
TRACKS = {"stable", "qpr", "monthly", "drop"}
VERIFY_STATES = {"VERIFIED", "UNVERIFIED"}
# Agent 4 (2nd iteration: Cross-Validator): 外部独立ソース照合の確度
CONFIDENCE_LEVELS = {"OFFICIAL", "MULTI_SOURCE", "SINGLE_SOURCE"}

ENTRY_REQUIRED = [
    "id", "title_ja", "title_en", "yomi", "category", "severity",
    "affected_models", "affected_os", "symptom", "cause", "workaround",
    "fix_status", "first_seen", "last_checked", "verify_state", "sources",
]
EVIDENCE_LEVELS = {"OFFICIAL", "MULTI_SOURCE", "REPORTED_ONLY"}
LINK_CONFIDENCES = {"official", "inferred", "estimated", "unknown"}

BUILD_ID_RE = re.compile(r"^[A-Z]{2}[0-9A-Z]{2}\.[0-9]{6}\.[0-9]{3}(\.[A-Z][0-9])?$")
BASE_MONTH_RE = re.compile(r"^[0-9]{4}-[0-9]{2}$")

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

    # ---- 7. base_month（Agent 3 2nd iteration: Schema Fixer）----
    # base_month = build_id 埋め込み日付 (XXXX.YYMMDD.NNN) の月。release_date
    # (実配信月・ソース掲載月ベース) との分離スキーマ。全件必須。
    bm_missing = [b["build_id"] for b in builds if "base_month" not in b]
    check("builds: base_month present (all records)", not bm_missing, str(bm_missing[:10]))

    bad_bm = [(b["build_id"], b.get("base_month")) for b in builds
              if not BASE_MONTH_RE.match(str(b.get("base_month", "")))]
    check("builds: base_month matches ^[0-9]{4}-[0-9]{2}$", not bad_bm, str(bad_bm[:10]))

    bm_mismatch = [
        (b["build_id"], b.get("base_month"))
        for b in builds
        if b.get("base_month") != f"20{b['build_id'][5:7]}-{b['build_id'][7:9]}"
    ]
    check("builds: base_month == build_id date part (YYMMDD -> 20YY-MM)",
          not bm_mismatch, str(bm_mismatch[:10]))

    # ---- 8. confidence（Agent 4 2nd iteration: Cross-Validator）----
    # 外部独立ソース照合の確度。全件必須・3値域・confidence_sources は URL 配列。
    conf_missing = [b["build_id"] for b in builds if "confidence" not in b]
    check("builds: confidence present (all records)", not conf_missing, str(conf_missing[:10]))

    bad_conf_b = [(b["build_id"], b.get("confidence")) for b in builds
                  if b.get("confidence") not in CONFIDENCE_LEVELS]
    check("builds: confidence in OFFICIAL/MULTI_SOURCE/SINGLE_SOURCE",
          not bad_conf_b, str(bad_conf_b[:10]))

    bad_cs = [b["build_id"] for b in builds
              if not isinstance(b.get("confidence_sources"), list)
              or any(not (isinstance(u, str) and u.startswith("https://"))
                     for u in b.get("confidence_sources", []))]
    check("builds: confidence_sources is a list of https URLs (all records)",
          not bad_cs, str(bad_cs[:10]))

    # ---- 9. anti_rollback（Agent 5 2nd iteration: Ops & Shipper）----
    # 既知の ARB 対象ビルド（Agent 1 が公式警告文から収載）に incremented=true が
    # 立っていること。ARB 例外の取りこぼし回帰をここで固定する。
    ARB_KNOWN = ["BP1A.250505.005", "CP1A.260505.005", "CP1A.260505.005.A1"]
    by_id = {b["build_id"]: b for b in builds}
    arb_missing = [
        bid for bid in ARB_KNOWN
        if not (by_id.get(bid, {}).get("anti_rollback") or {}).get("incremented")
    ]
    check("builds: known ARB builds have anti_rollback.incremented=true %s" % ARB_KNOWN,
          not arb_missing, str(arb_missing))

    # incremented=true の全レコードに scope / effect（Agent 1 追記フィールド）が
    # 非空 string で存在すること。
    arb_bad = [
        b["build_id"] for b in builds
        if (b.get("anti_rollback") or {}).get("incremented")
        and not all(isinstance(b["anti_rollback"].get(k), str) and b["anti_rollback"][k]
                    for k in ("scope", "effect"))
    ]
    check("builds: ARB records (incremented=true) have non-empty scope/effect",
          not arb_bad, str(arb_bad))

    # ---- 10. recheck_at（Agent 5 2nd iteration: Ops & Shipper）----
    # 運用マーカー。存在する場合のみ ^[0-9]{4}-[0-9]{2}$（YYYY-MM）を要求。
    bad_recheck = [(e["id"], e.get("recheck_at")) for e in entries
                   if "recheck_at" in e
                   and not BASE_MONTH_RE.match(str(e.get("recheck_at", "")))]
    check("entries: recheck_at matches ^[0-9]{4}-[0-9]{2}$ (when present)",
          not bad_recheck, str(bad_recheck[:10]))

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
