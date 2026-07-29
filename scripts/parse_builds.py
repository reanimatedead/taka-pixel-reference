#!/usr/bin/env python3
"""parse_builds.py — Pixel ビルド番号辞書のデータ層生成 (Agent 2: Build Collector)

入力 (一次スナップショット):
  data/raw/2026-07-30/ota.html            (developers.google.com/android/ota)
  data/raw/2026-07-30/images.html         (developers.google.com/android/images)
  data/raw/2026-07-30/pixel-bulletin.html (source.android.com/docs/security/bulletin/pixel)

出力 (派生物・再生成可能):
  docs/dict/data/builds.json

スコープ: Android 16 世代以降 (2025-06 〜 2026-07)。
  プレフィックス BP2A/BP3A/BP4A/CP1A/CP2A (メインライン) と
  BD1A/BD3A/BD6A (Pixel 10 系デバイスローンチ列)。
判断の詳細は data/build-dict-decisions.md の「## Agent 2」節を参照。
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW_ROOT = REPO / "data" / "raw"
OUT = REPO / "docs" / "dict" / "data" / "builds.json"


def _resolve_raw_dir():
    """引数 (YYYY-MM-DD) 指定があればそのスナップショット、無ければ最新の日付ディレクトリ。"""
    if len(sys.argv) > 1:
        d = RAW_ROOT / sys.argv[1]
        if not d.is_dir():
            sys.exit(f"raw snapshot dir not found: data/raw/{sys.argv[1]}")
        return d
    dated = sorted(p for p in RAW_ROOT.iterdir()
                   if p.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", p.name))
    if not dated:
        sys.exit("no dated snapshot dir under data/raw/")
    return dated[-1]


RAW = _resolve_raw_dir()

URL_OTA = "https://developers.google.com/android/ota"
URL_IMAGES = "https://developers.google.com/android/images"
URL_BULLETIN = "https://source.android.com/docs/security/bulletin/pixel"

BUILD_RE = re.compile(r"^[A-Z]{2}[0-9A-Z]{2}\.[0-9]{6}\.[0-9]{3}(\.[A-Z][0-9])?$")
VARIANT_SUFFIX_RE = re.compile(r"\.[A-Z][0-9]$")

# スコープ対象プレフィックス (Android 16 世代 2025-06 以降)
SCOPE_PREFIXES = ("BP2A", "BP3A", "BP4A", "CP1A", "CP2A", "BD1A", "BD3A", "BD6A")

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
MONTH_FULL = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"])}

# track 判定: (プレフィックス, ビルド年月) -> track
# 根拠: タスク確定値 (BP2A.2506=stable初版, BP3A.2509=QPR1, BP4A.2512=QPR2,
#        CP2A.2606=A17 stable, CP2A.2607=monthly) から系列を外挿。
#        各プレフィックスの初月 = リリース (stable/qpr)、以降の月 = monthly。
TRACK_TABLE = {
    ("BP2A", "2025-06"): "stable",   # Android 16 初版
    ("BP2A", "2025-07"): "monthly",
    ("BP2A", "2025-08"): "monthly",
    ("BP3A", "2025-09"): "qpr",      # Android 16 QPR1
    ("BP3A", "2025-10"): "monthly",
    ("BP3A", "2025-11"): "monthly",
    ("BP4A", "2025-12"): "qpr",      # Android 16 QPR2
    ("BP4A", "2026-01"): "monthly",
    ("BP4A", "2026-02"): "monthly",
    ("CP1A", "2026-03"): "qpr",      # Android 16 QPR 系 3番目 (ソースに QPR3 の呼称なし)
    ("CP1A", "2026-04"): "monthly",
    ("CP1A", "2026-05"): "monthly",
    ("CP2A", "2026-06"): "stable",   # Android 17 初版
    ("CP2A", "2026-07"): "monthly",
    # Pixel 10 系デバイスローンチ列 (メインライン合流前のデバイス専用ビルド)
    ("BD1A", "2025-08"): "stable",   # Pixel 10/10 Pro/10 Pro XL ローンチ
    ("BD3A", "2025-08"): "stable",
    ("BD3A", "2025-09"): "monthly",
    ("BD3A", "2025-10"): "monthly",
    ("BD3A", "2025-11"): "monthly",
    ("BD6A", "2026-03"): "stable",   # Pixel 10a (stallion) ローンチ
}

# ---- タスク3: 既知の確定値 (アンカー) ----
# release_date / os / track はオーナー提供の確定値。パース結果と矛盾したら
# human_review + conflict_note を付けて両方残す (make_record 内で照合)。
ANCHORS = {
    "CP2A.260705.006":    {"release_date": "2026-07-07", "os": "Android 17", "track": "monthly"},
    "CP2A.260705.006.A1": {"release_date": "2026-07-07", "os": "Android 17", "track": "monthly"},
    "CP2A.260605.012":    {"release_date": "2026-06-16", "os": "Android 17", "track": "stable"},
    "CP2A.260605.012.A1": {"release_date": "2026-06-16", "os": "Android 17", "track": "stable",
                           "region_claim": "AT&T"},
    "CP2A.260605.012.B1": {"release_date": "2026-06-16", "os": "Android 17", "track": "stable",
                           "region_claim": "AU"},
    "CP2A.260605.012.C1": {"release_date": "2026-06-16", "os": "Android 17", "track": "stable",
                           "region_claim": "Rogers"},
    "BP4A.251205.006":    {"release_date": "2025-12-02", "os": "Android 16 QPR2", "track": "qpr"},
    "BP4A.251205.006.A1": {"release_date": "2025-12-02", "os": "Android 16 QPR2", "track": "qpr",
                           "region_claim": "EMEA"},
    "BP4A.251205.006.C1": {"release_date": "2025-12-02", "os": "Android 16 QPR2", "track": "qpr",
                           "region_claim": "Japan"},
    "BP4A.251205.006.B1": {"release_date": "2025-12-02", "os": "Android 16 QPR2", "track": "qpr",
                           "region_claim": "Verizon"},  # Verizon Pixel 9a (tegu)
    "BP3A.250905.014":    {"release_date": "2025-09-03", "os": "Android 16 QPR1", "track": "qpr"},
    "BP2A.250705.008":    {"release_date": "2025-07-08", "os": "Android 16", "track": "monthly"},
    "BP2A.250705.008.A1": {"release_date": "2025-07-08", "os": "Android 16", "track": "monthly"},
    "BP2A.250605.031.A2": {"release_date": "2025-06-10", "os": "Android 16", "track": "stable"},
}

# region_claim (オーナー確定値) とソース表記の同義判定
REGION_SYNONYMS = {
    "AT&T": {"AT&T"},
    "AU": {"Australia", "AU"},
    "Rogers": {"Rogers"},
    "EMEA": {"EMEA"},
    "Japan": {"Japan"},
    "Verizon": {"Verizon", "VZW"},
}

# anti-rollback 最重要フラグ: Pixel 10 系の 2026年5月更新ビルド
ANTI_ROLLBACK_BUILDS = {"CP1A.260505.005", "CP1A.260505.005.A1"}
ANTI_ROLLBACK_NOTE = (
    "Android 16ビルドへの巻き戻し不可。ブートローダーのanti-rollbackカウンタ増加のため、"
    "これ以前のファクトリーイメージ書き込みは文鎮化リスク"
    "（対象: Pixel 10系 frankel/mustang/blazer/rango/stallion。"
    "ソース上は2026年5月の全デバイス共通ビルドとして掲載）"
)


def parse_device_tables(html: str):
    """devsite の OTA / factory image ページからビルド行を抽出する。

    構造: <h2 id="<codename>">"<codename>" for <marketing name></h2> の後に
    行 <td>VERSION (BUILD_ID, Mon YYYY[, REGION])</td> が続く。
    戻り値: [(codename, version, build_id, month "YYYY-MM", region or None), ...]
    """
    rows = []
    sections = re.split(r'<h2[^>]*id="([a-z]+)"[^>]*>', html)
    for i in range(1, len(sections) - 1, 2):
        codename, body = sections[i], sections[i + 1]
        if codename in ("legal", "instructions"):
            continue
        for ver, bid, qual in re.findall(
                r'<td>([0-9.]+) \(([A-Z0-9.]+)(?:, ([^)]+))?\)</td>', body):
            if not BUILD_RE.match(bid):
                continue
            month = None
            region = None
            if qual:
                parts = [p.strip() for p in re.split(r",", qual)]
                rest = []
                for p in parts:
                    m = re.match(r"([A-Z][a-z]{2}) (20[0-9]{2})$", p)
                    if m and m.group(1) in MONTHS:
                        month = f"{m.group(2)}-{MONTHS[m.group(1)]:02d}"
                    elif p:
                        rest.append(p.replace("&amp;", "&"))
                if rest:
                    region = ", ".join(rest)
            rows.append((codename, ver, bid, month, region))
    return rows


def parse_bulletin(html: str):
    """Pixel Update Bulletin 一覧から {"YYYY-MM": {"published": ..., "patch_level": ...}}"""
    out = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) < 4:
            continue
        m = re.match(r"([A-Z][a-z]+) (20[0-9]{2})", cells[0])
        pub = re.match(r"([A-Z][a-z]+) ([0-9]{1,2}), (20[0-9]{2})", cells[2])
        patch = re.match(r"(20[0-9]{2}-[0-9]{2}-[0-9]{2})", cells[3])
        if not (m and m.group(1) in MONTH_FULL and patch):
            continue
        key = f"{m.group(2)}-{MONTH_FULL[m.group(1)]:02d}"
        pub_date = None
        if pub and pub.group(1) in MONTH_FULL:
            pub_date = f"{pub.group(3)}-{MONTH_FULL[pub.group(1)]:02d}-{int(pub.group(2)):02d}"
        out[key] = {"published": pub_date, "patch_level": patch.group(1)}
    return out


def main():
    ota_html = (RAW / "ota.html").read_text(encoding="utf-8", errors="replace")
    img_html = (RAW / "images.html").read_text(encoding="utf-8", errors="replace")
    bul_html = (RAW / "pixel-bulletin.html").read_text(encoding="utf-8", errors="replace")

    bulletins = parse_bulletin(bul_html)

    # build_id -> aggregate
    agg = {}
    for src_url, html in ((URL_OTA, ota_html), (URL_IMAGES, img_html)):
        for codename, ver, bid, month, region in parse_device_tables(html):
            if not bid.startswith(SCOPE_PREFIXES):
                continue
            a = agg.setdefault(bid, {
                "devices": set(), "versions": set(), "months": set(),
                "regions": set(), "sources": set()})
            a["devices"].add(codename)
            a["versions"].add(ver)
            if month:
                a["months"].add(month)
            if region:
                a["regions"].add(region)
            a["sources"].add(src_url)

    builds = []
    for bid in sorted(agg):
        a = agg[bid]
        anchor = ANCHORS.get(bid)
        month = min(a["months"]) if a["months"] else None
        prefix = bid[:4]

        # os: ソースの version 列 (16.0.0 -> Android 16)。アンカーは QPR 呼称を優先。
        majors = sorted({v.split(".")[0] for v in a["versions"]})
        parsed_os = "Android " + "/".join(majors) if majors else None
        os_val = anchor["os"] if anchor else parsed_os

        # track: 規則表。アンカー値があれば照合。
        parsed_track = TRACK_TABLE.get((prefix, month))
        track = anchor["track"] if anchor else parsed_track

        # release_date: アンカーは確定日。それ以外はソースの月精度 (YYYY-MM)。
        release_date = anchor["release_date"] if anchor else month

        # security_patch: 該当月の Pixel bulletin の patch level。
        sec = bulletins.get(month, {}).get("patch_level") if month else None

        rec = {
            "build_id": bid,
            "os": os_val,
            "track": track,
            "release_date": release_date,
            "security_patch": sec,
            "devices": sorted(a["devices"]),
            "region_scope": "; ".join(sorted(a["regions"])) if a["regions"] else "global",
        }
        if VARIANT_SUFFIX_RE.search(bid):
            rec["parent_build_id"] = bid.rsplit(".", 1)[0]

        rec["anti_rollback"] = {
            "incremented": bid in ANTI_ROLLBACK_BUILDS,
            "note": ANTI_ROLLBACK_NOTE if bid in ANTI_ROLLBACK_BUILDS else "",
        }
        rec["official_fixes"] = []  # 4ソースいずれも機能修正の列挙なし (decisions.md 参照)

        srcs = sorted(a["sources"])
        if sec:
            srcs.append(URL_BULLETIN)
        rec["sources"] = srcs

        # verify_state: アンカー確定値 + anti-rollback 指定ビルドは VERIFIED。
        # それ以外は track / release_date(月精度) が推定を含むため UNVERIFIED。
        rec["verify_state"] = ("VERIFIED" if (anchor or bid in ANTI_ROLLBACK_BUILDS)
                               else "UNVERIFIED")
        if not rec["devices"]:
            rec["verify_state"] = "UNVERIFIED"

        # ---- アンカーとパース結果の照合 (食い違いは両方残す) ----
        conflicts = []
        if anchor:
            # 月の整合
            if month and not anchor["release_date"].startswith(month):
                conflicts.append(
                    f"release_date: anchor={anchor['release_date']} / source_month={month}")
                rec["release_date_source_month"] = month
            # os メジャーの整合 (QPR 呼称差は矛盾扱いしない)
            if parsed_os and anchor["os"].split(" QPR")[0] != parsed_os:
                conflicts.append(f"os: anchor={anchor['os']} / parsed={parsed_os}")
                rec["os_parsed"] = parsed_os
            # track の整合
            if parsed_track and parsed_track != anchor["track"]:
                conflicts.append(f"track: anchor={anchor['track']} / parsed={parsed_track}")
                rec["track_parsed"] = parsed_track
            # region の整合
            claim = anchor.get("region_claim")
            if claim:
                syn = REGION_SYNONYMS.get(claim, {claim})
                if a["regions"] and not (a["regions"] & syn):
                    conflicts.append(
                        f"region_scope: anchor={claim} / parsed={sorted(a['regions'])}")
        if conflicts:
            rec["human_review"] = True
            rec["conflict_note"] = " | ".join(conflicts)

        builds.append(rec)

    # 全件がビルドID正規表現に一致することを保証
    bad = [b["build_id"] for b in builds if not BUILD_RE.match(b["build_id"])]
    if bad:
        sys.exit(f"build_id regex violation: {bad}")

    # アンカー・anti-rollback ビルドがソースから取れなかった場合は既知情報で投入
    present = {b["build_id"] for b in builds}
    for bid, anchor in ANCHORS.items():
        if bid in present:
            continue
        rec = {
            "build_id": bid,
            "os": anchor["os"],
            "track": anchor["track"],
            "release_date": anchor["release_date"],
            "security_patch": None,
            "devices": [],
            "region_scope": anchor.get("region_claim", "global"),
            "anti_rollback": {"incremented": False, "note": ""},
            "official_fixes": [],
            "sources": [],
            "verify_state": "UNVERIFIED",
            "human_review": True,
            "conflict_note": "ソースHTMLに未出現。オーナー提供の既知確定値のみで投入",
        }
        if VARIANT_SUFFIX_RE.search(bid):
            rec["parent_build_id"] = bid.rsplit(".", 1)[0]
        builds.append(rec)
    for bid in sorted(ANTI_ROLLBACK_BUILDS - present):
        builds.append({
            "build_id": bid,
            "os": "Android 16",
            "track": "monthly",
            "release_date": "2026-05",
            "security_patch": bulletins.get("2026-05", {}).get("patch_level"),
            "devices": [],
            "region_scope": "global",
            "anti_rollback": {"incremented": True, "note": ANTI_ROLLBACK_NOTE},
            "official_fixes": [],
            "sources": [],
            "verify_state": "UNVERIFIED",
            "human_review": True,
            "conflict_note": "ソースHTMLに未出現。既知情報から anti-rollback フラグ目的で投入",
        })

    builds.sort(key=lambda b: b["build_id"])  # 表示順契約: build_id ASC (tests/test_contract.py で固定)
    out = {"generated_at": RAW.name, "builds": builds}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n_parent = sum(1 for b in builds if "parent_build_id" not in b)
    n_hr = sum(1 for b in builds if b.get("human_review"))
    n_ar = [b["build_id"] for b in builds if b["anti_rollback"]["incremented"]]
    print(f"total={len(builds)} parents={n_parent} variants={len(builds)-n_parent} "
          f"human_review={n_hr} anti_rollback={n_ar}")


if __name__ == "__main__":
    main()
