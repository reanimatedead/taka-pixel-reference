#!/usr/bin/env python3
"""回帰テスト: ビルドID変異版サフィックス→地域/キャリア導出 (Agent 2 2nd iteration)

実行: python3 tests/test_suffix_map.py
依存: python3 標準ライブラリのみ。

固定する事実: サフィックスの意味は「月ごとに」変わる。
  2025-12 .C1 = Japan   / 2026-02 .C1 = Japan / 2026-06 .C1 = Rogers
  2026-07 .A1 = Rogers  / 2025-12 .A1 = EMEA  / 2026-05 .A1 = Telia
  2026-06 .A1 = AT&T
よって「.C1 は常に日本」のようなグローバル1次元固定辞書の実装はここで FAIL する
(同一サフィックスが月によって異なる地域になることを不等式でアサート)。

データ側の補足 (2026-07-30 スナップショット時点):
  2026-02 .C1 -> BP4A.260205.001.C1 が builds.json に存在 (データ側テスト対象)。
  2026-07 .A1 -> CP2A.260705.006.A1 が builds.json に存在。ただしソース注記が
  デバイスにより Rogers / Australia の2種のため region_scope は
  "Australia; Rogers"。データ側テストは「Rogers を含む」ことをアサートする。
  存在しない組が将来出た場合はパーサ側 (SUFFIX_MONTH_MAP) テストのみが担う。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import parse_builds  # noqa: E402

BUILDS_PATH = REPO / "docs" / "dict" / "data" / "builds.json"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main():
    m = parse_builds.SUFFIX_MONTH_MAP

    # ---- 1. パーサ側: 二次元テーブル (month × suffix) の既知確定値 ----
    expected = {
        ("2025-12", "C1"): "Japan",
        ("2026-02", "C1"): "Japan",
        ("2026-06", "C1"): "Rogers",
        ("2025-12", "A1"): "EMEA",
        ("2026-05", "A1"): "Telia",
        ("2026-06", "A1"): "AT&T",
    }
    for key, region in expected.items():
        check(f"map: {key} == {region!r}",
              key in m and m[key]["region"] == region,
              f"actual {m.get(key)}")
    # 2026-07 .A1: Rogers (ソース注記はデバイスにより Australia も併記)
    key = ("2026-07", "A1")
    check("map: ('2026-07','A1') contains Rogers",
          key in m and "Rogers" in m[key]["region"].split("; "),
          f"actual {m.get(key)}")

    # ---- 2. 固定辞書 (suffix→region の1次元マップ) なら FAIL する不等式 ----
    check("map: .C1 is NOT month-invariant (2025-12 Japan != 2026-06 Rogers)",
          m[("2025-12", "C1")]["region"] != m[("2026-06", "C1")]["region"])
    a1 = [m[("2025-12", "A1")]["region"], m[("2026-05", "A1")]["region"],
          m[("2026-06", "A1")]["region"]]
    check("map: .A1 is NOT month-invariant (EMEA / Telia / AT&T pairwise distinct)",
          len(set(a1)) == 3, f"actual {a1}")
    # キーが (month, suffix) の2次元タプルであること (1次元 suffix キーの混入禁止)
    check("map: all keys are (month 'YYYY-MM', suffix) 2-tuples",
          all(isinstance(k, tuple) and len(k) == 2
              and len(k[0]) == 7 and k[0][4] == "-" for k in m))

    # ---- 3. 各対応に根拠出典があること ----
    no_src = [k for k, v in m.items() if not v.get("source")]
    check("map: every entry has a non-empty source", not no_src, str(no_src))
    bad_src = [k for k, v in m.items()
               if "data/raw/2026-07-30" not in v["source"]
               and "https://" not in v["source"]]
    check("map: source cites raw snapshot or official URL", not bad_src, str(bad_src))

    # ---- 4. データ側: builds.json の実データが既知確定値と一致 ----
    doc = json.loads(BUILDS_PATH.read_text(encoding="utf-8"))
    builds = {b["build_id"]: b for b in doc["builds"]}
    # 基準値 66→67: Agent 1 (2nd iteration: ARB Historian) が BP1A.250505.005
    # (Android 15 世代 ARB 例外収載) を追加 (2026-07-30)。件数非減少の思想は維持。
    check("data: builds.json has 67 records", len(builds) == 67,
          f"actual {len(builds)}")

    data_expected = {
        "BP4A.251205.006.C1": "Japan",     # 2025-12 .C1
        "BP4A.260205.001.C1": "Japan",     # 2026-02 .C1
        "CP2A.260605.012.C1": "Rogers",    # 2026-06 .C1
        "BP4A.251205.006.A1": "EMEA",      # 2025-12 .A1
        "CP1A.260505.005.A1": "Telia",     # 2026-05 .A1
        "CP2A.260605.012.A1": "AT&T",      # 2026-06 .A1
    }
    for bid, region in data_expected.items():
        b = builds.get(bid)
        check(f"data: {bid} region_scope == {region!r}",
              b is not None and b["region_scope"] == region,
              f"actual {b['region_scope'] if b else 'MISSING'}")
    # 2026-07 .A1 (CP2A.260705.006.A1): Rogers を含む (Australia 併記は許容)
    b = builds.get("CP2A.260705.006.A1")
    check("data: CP2A.260705.006.A1 region_scope contains Rogers",
          b is not None and "Rogers" in b["region_scope"].split("; "),
          f"actual {b['region_scope'] if b else 'MISSING'}")

    # データ側でも同一サフィックスが月で異なることを直接アサート
    check("data: .C1 2025-12 (Japan) != .C1 2026-06 (Rogers)",
          builds["BP4A.251205.006.C1"]["region_scope"]
          != builds["CP2A.260605.012.C1"]["region_scope"])
    a1_data = [builds["BP4A.251205.006.A1"]["region_scope"],
               builds["CP1A.260505.005.A1"]["region_scope"],
               builds["CP2A.260605.012.A1"]["region_scope"]]
    check("data: .A1 across 2025-12/2026-05/2026-06 pairwise distinct",
          len(set(a1_data)) == 3, f"actual {a1_data}")

    # ---- 5. 正規化: 廃止表記が region_scope に残っていないこと ----
    banned = {"VZW", "JP", "Softbank", "NA GStore", "AU"}
    leftovers = [(bid, b["region_scope"]) for bid, b in builds.items()
                 if set(b["region_scope"].split("; ")) & banned
                 or "Japan, Japan" in b["region_scope"]
                 or "except Softbank" in b["region_scope"]]
    check("data: no un-normalized tokens (VZW/JP/Softbank/NA GStore/'Japan, Japan')",
          not leftovers, str(leftovers))

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
