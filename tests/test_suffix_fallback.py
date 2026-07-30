#!/usr/bin/env python3
"""結合テスト: SUFFIX_MONTH_MAP フォールバック経路 (2026-07-31 凍結時に追加)

実行: python3 tests/test_suffix_fallback.py
依存: python3 標準ライブラリのみ。

背景: scripts/parse_builds.py の SUFFIX_MONTH_MAP フォールバックは実データ
(data/raw/2026-07-30) で発動 0 件 = 本番未検証だった。本テストは注記
(月・地域) を欠落させた合成HTMLフィクスチャ (tests/fixtures/suffix_fallback/)
を parse_builds.main() に実際に通し、フォールバック経路を結合レベルで固定する。

固定する契約:
  1. 注記欠落の 2025-12 .C1 -> SUFFIX_MONTH_MAP により region=Japan
  2. 注記欠落の 2026-06 .C1 -> SUFFIX_MONTH_MAP により region=Rogers
     (同一サフィックス .C1 が月で意味が変わることの結合レベル検証)
  3. 注記欠落かつマップに無い月×サフィックス (2026-08 .Z9) ->
     region_scope="unknown" + human_review=true。"global" 等での推測禁止。
  4. 「月注記あり・地域トークンなし」は devsite の正常表記 (= 地域限定なし) で
     あり global のまま (フォールバック・unknown の対象外)。実データの外部照合済み
     global 変異版 18 件と同じ表記のため、ここを unknown にする実装は誤り。

注意: parse_builds.main() は module グローバル RAW / OUT を参照するため、
本テストはそれらをフィクスチャ/一時ファイルに差し替えてから main() を呼ぶ。
実データ (docs/dict/data/builds.json) には一切書き込まない。
"""
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import parse_builds  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "suffix_fallback"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main():
    out_path = Path(tempfile.mkdtemp(prefix="suffix-fallback-")) / "builds.json"

    # module グローバルの差し替え (実データへの書き込み防止 + フィクスチャ注入)
    parse_builds.RAW = FIXTURE
    parse_builds.OUT = out_path
    parse_builds.main()

    doc = json.loads(out_path.read_text(encoding="utf-8"))
    builds = {b["build_id"]: b for b in doc["builds"]}

    # ---- 1. 2025-12 の .C1 (注記欠落) -> Japan ----
    b = builds.get("BP4A.251215.001.C1")
    check("fallback: 2025-12 .C1 (注記欠落) region_scope == 'Japan'",
          b is not None and b["region_scope"] == "Japan",
          f"actual {b['region_scope'] if b else 'MISSING'}")
    check("fallback: 2025-12 .C1 に region_scope_source (フォールバック発動の証跡)",
          b is not None and "SUFFIX_MONTH_MAP" not in str(b.get("conflict_note", ""))
          and bool(b.get("region_scope_source")),
          f"actual {b.get('region_scope_source') if b else 'MISSING'}")
    check("fallback: 2025-12 .C1 は human_review なし",
          b is not None and not b.get("human_review"),
          f"actual {b.get('human_review') if b else 'MISSING'}")

    # ---- 2. 2026-06 の .C1 (注記欠落) -> Rogers (同一サフィックスが月で変わる) ----
    b2 = builds.get("CP2A.260615.001.C1")
    check("fallback: 2026-06 .C1 (注記欠落) region_scope == 'Rogers'",
          b2 is not None and b2["region_scope"] == "Rogers",
          f"actual {b2['region_scope'] if b2 else 'MISSING'}")
    check("fallback: 結合レベルでも .C1 は月非依存でない (Japan != Rogers)",
          b is not None and b2 is not None
          and b["region_scope"] != b2["region_scope"])

    # ---- 3. マップに無い月×サフィックス (2026-08 .Z9) -> unknown + human_review ----
    b3 = builds.get("CP2A.260805.001.Z9")
    check("fallback-miss: 2026-08 .Z9 region_scope == 'unknown' (推測で埋めない)",
          b3 is not None and b3["region_scope"] == "unknown",
          f"actual {b3['region_scope'] if b3 else 'MISSING'}")
    check("fallback-miss: 2026-08 .Z9 human_review == true",
          b3 is not None and b3.get("human_review") is True,
          f"actual {b3.get('human_review') if b3 else 'MISSING'}")
    check("fallback-miss: 2026-08 .Z9 conflict_note に SUFFIX_MONTH_MAP 未登録の根拠",
          b3 is not None and "SUFFIX_MONTH_MAP" in str(b3.get("conflict_note", "")),
          f"actual {b3.get('conflict_note') if b3 else 'MISSING'}")

    # ---- 4. 月注記あり・地域トークンなし = devsite 正常表記の global (unknown 対象外) ----
    b4 = builds.get("CP2A.260615.002.B9")
    check("month-only note: 2026-06 .B9 region_scope == 'global' (devsite 正常表記)",
          b4 is not None and b4["region_scope"] == "global",
          f"actual {b4['region_scope'] if b4 else 'MISSING'}")
    check("month-only note: 2026-06 .B9 は human_review なし",
          b4 is not None and not b4.get("human_review"),
          f"actual {b4.get('human_review') if b4 else 'MISSING'}")

    # ---- 5. 結合の周辺検証 (bulletin / 出力形式) ----
    # (注記欠落行は月が取れず bulletin 照合不能のため、月注記ありの b4 で検証)
    check("integration: security_patch は bulletin フィクスチャ由来 (2026-06-05)",
          b4 is not None and b4.get("security_patch") == "2026-06-05",
          f"actual {b4.get('security_patch') if b4 else 'MISSING'}")
    check("integration: generated_at == フィクスチャディレクトリ名",
          doc.get("generated_at") == FIXTURE.name,
          f"actual {doc.get('generated_at')}")
    check("integration: 実データ builds.json には書き込んでいない (出力先は一時ファイル)",
          out_path != REPO / "docs" / "dict" / "data" / "builds.json"
          and out_path.is_file())

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
