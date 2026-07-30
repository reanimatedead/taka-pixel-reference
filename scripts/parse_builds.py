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

import copy
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

# ---- region_scope 正規化 (Agent 2 2nd iteration: Suffix Auditor) ----
# 規則: キャリア名は正式表記 (VZW→Verizon, Softbank→SoftBank)、
#       国はISO2レターでなく英語国名 (JP→Japan, AU→Australia)、
#       複数対象は正規化トークンをソートし "; " 区切り、
#       ソース側の同一トークン重複 ("Japan, Japan") はセットで自然に排除。
REGION_NORMALIZE = {
    "VZW": "Verizon",
    "JP": "Japan",
    "AU": "Australia",
    "Softbank": "SoftBank",
    "Japan carriers except Softbank": "Japan carriers except SoftBank",
    "NA GStore": "North America (Google Store)",
}

# ---- サフィックス→地域/キャリアの二次元テーブル (base month × suffix) ----
# 重要: サフィックスの意味は月ごとに変わる (.C1: 2025-12=Japan / 2026-06=Rogers、
#       .A1: 2025-12=EMEA / 2026-05=Telia / 2026-06=AT&T / 2026-07=Rogers)。
#       グローバル1次元の固定辞書 (suffix→region) は誤りであり禁止。
# 用途: ソースHTMLの変異版キャリア注記から直接パースするのが正
#       (parse_device_tables が担当)。本テーブルは注記が欠落した場合のみの
#       フォールバック。key = (build_id 埋め込みの base month "YYYY-MM", suffix)。
# source: 生HTMLスナップショット data/raw/2026-07-30/{ota,images}.html 内の
#         該当 <td> 注記 (両ファイルに同一注記が存在することを確認済み)。
_SNAP = "data/raw/2026-07-30/{ota,images}.html"
SUFFIX_MONTH_MAP = {
    ("2025-08", "A3"): {"region": "Verizon",
                        "source": f"{_SNAP} '(BD1A.250702.001.A3, Aug 2025, Verizon)' <- {URL_OTA}"},
    ("2025-08", "A1"): {"region": "North America (Google Store)",
                        "source": f"{_SNAP} '(BD3A.250721.001.A1, Aug 2025, NA GStore)' <- {URL_OTA}"},
    ("2025-10", "A2"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP3A.251005.004.A2, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-10", "A3"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP3A.251005.004.A3, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-10", "F1"): {"region": "Japan",
                        "source": f"{_SNAP} '(BD3A.251005.003.F1, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-10", "J2"): {"region": "Japan",
                        "source": f"{_SNAP} '(BD3A.251005.003.J2, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-10", "J5"): {"region": "Japan",
                        "source": f"{_SNAP} '(BD3A.251005.003.J5, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-10", "J6"): {"region": "Japan",
                        "source": f"{_SNAP} '(BD3A.251005.003.J6, Oct 2025, Japan)' <- {URL_OTA}"},
    ("2025-11", "J1"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP3A.251105.015.J1, Nov 2025, Japan)' <- {URL_OTA}"},
    ("2025-11", "F1"): {"region": "Japan carriers except SoftBank",
                        "source": f"{_SNAP} '(BD3A.251105.010.F1, Nov 2025, Japan carriers except Softbank)' <- {URL_OTA}"},
    ("2025-11", "J3"): {"region": "SoftBank",
                        "source": f"{_SNAP} '(BD3A.251105.010.J3, Nov 2025, Softbank)' <- {URL_OTA}"},
    ("2025-12", "A1"): {"region": "EMEA",
                        "source": f"{_SNAP} '(BP4A.251205.006.A1, Dec 2025, EMEA)' <- {URL_OTA}"},
    ("2025-12", "A4"): {"region": "EMEA",
                        "source": f"{_SNAP} '(BP4A.251205.006.A4, Dec 2025, EMEA)' <- {URL_OTA}"},
    ("2025-12", "B1"): {"region": "Verizon",
                        "source": f"{_SNAP} '(BP4A.251205.006.B1, Dec 2025, VZW)' <- {URL_OTA}"},
    ("2025-12", "B3"): {"region": "Verizon",
                        "source": f"{_SNAP} '(BP4A.251205.006.B3, Dec 2025, Verizon)' <- {URL_OTA}"},
    ("2025-12", "C1"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP4A.251205.006.C1, Dec 2025, Japan)' <- {URL_OTA}"},
    ("2025-12", "C2"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP4A.251205.006.C2, Dec 2025, Japan)' <- {URL_OTA}"},
    ("2026-01", "A2"): {"region": "EMEA",
                        "source": f"{_SNAP} '(BP4A.260105.004.A2, Jan 2026, EMEA)' <- {URL_OTA}"},
    ("2026-01", "B2"): {"region": "Verizon",
                        "source": f"{_SNAP} '(BP4A.260105.004.B2, Jan 2026, Verizon)' <- {URL_OTA}"},
    ("2026-01", "C2"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP4A.260105.004.C2, Jan 2026, Japan)' <- {URL_OTA}"},
    ("2026-02", "A1"): {"region": "EMEA",
                        "source": f"{_SNAP} '(BP4A.260205.001.A1, Feb 2026, EMEA)' <- {URL_OTA}"},
    ("2026-02", "B1"): {"region": "Verizon",
                        "source": f"{_SNAP} '(BP4A.260205.001.B1, Feb 2026, VZW)' <- {URL_OTA}"},
    ("2026-02", "C1"): {"region": "Japan",
                        "source": f"{_SNAP} '(BP4A.260205.001.C1, Feb 2026, JP)' <- {URL_OTA}"},
    ("2026-03", "A1"): {"region": "Australia",
                        "source": f"{_SNAP} '(CP1A.260305.018.A1, Mar 2026, Australia)' <- {URL_OTA}"},
    ("2026-04", "A1"): {"region": "Australia",
                        "source": f"{_SNAP} '(CP1A.260405.003.A1, Apr 2026, Australia)' <- {URL_OTA}"},
    ("2026-04", "B1"): {"region": "Telia",
                        "source": f"{_SNAP} '(CP1A.260405.005.B1, Apr 2026, Telia)' <- {URL_OTA}"},
    ("2026-05", "A1"): {"region": "Telia",
                        "source": f"{_SNAP} '(CP1A.260505.005.A1, May 2026, Telia)' <- {URL_OTA}"},
    ("2026-06", "A1"): {"region": "AT&T",
                        "source": f"{_SNAP} '(CP2A.260605.012.A1, Jun 2026, AT&T)' <- {URL_OTA}"},
    ("2026-06", "B1"): {"region": "Australia",
                        "source": f"{_SNAP} '(CP2A.260605.012.B1, Jun 2026, Australia)' <- {URL_OTA}"},
    ("2026-06", "C1"): {"region": "Rogers",
                        "source": f"{_SNAP} '(CP2A.260605.012.C1, Jun 2026, Rogers)' <- {URL_OTA}"},
    # 2026-07 の .A1 はデバイスにより Rogers / Australia の両注記あり
    ("2026-07", "A1"): {"region": "Australia; Rogers",
                        "source": f"{_SNAP} '(CP2A.260705.006.A1, Jul 2026, Rogers)' + '(..., Australia)' <- {URL_OTA}"},
}


def base_month_of(bid: str) -> str:
    """build_id 埋め込み日付 (XXXX.YYMMDD.NNN) から base month 'YYYY-MM' を得る。"""
    return f"20{bid[5:7]}-{bid[7:9]}"


# ---- Agent 3 (2nd iteration: Schema Fixer): 解決済みアンカー矛盾 ----
# スキーマを base_month (ビルドID埋め込み日付の月・機械導出) と
# release_date (実際に配信された月 = ソース掲載月ベース) に分離したことで、
# 「ビルドIDの月 != 配信月」は矛盾ではなく「後月配信」として表現できる。
# release_date 起因のアンカー矛盾のうち、ソース掲載月で解決が確定したものを
# ここに登録する。該当ビルドは human_review / conflict_note を付けず、
# release_date をソース掲載月に確定し resolution_note に経緯を残す。
# release_date 以外の矛盾 (os / track / region) は従来どおり human_review。
RESOLVED_CONFLICTS = {
    "BP2A.250705.008.A1": {
        "release_date": "2025-08",  # ソース掲載月 (ota/images 両方 'Aug 2025' 注記)
        "resolution_note": (
            "base_month/release_date 分離により矛盾でないと判明。"
            "base_month=2025-07 はビルドID埋め込み日付、実配信はソース掲載月 2025-08"
            "（アンカー値 2025-07-08 はビルドID日付由来でありソース掲載月と食い違っていた）。"
            "2026-07-30 解決"
        ),
    },
}


# ---- Agent 4 (2nd iteration: Cross-Validator): 外部独立ソース照合 ----
# スクレイピング元 (developers.google.com/{ota,images} + source.android.com bulletin)
# とは独立の外部情報で build_id を照合し confidence を付与する (2026-07-30 実施)。
# 判定規則 (詳細: data/build-dict-decisions.md「## Agent 4 (2nd iteration)」):
#   OFFICIAL      = Google 公式の第二経路 (Pixel Community 公式月次投稿
#                   support.google.com/pixelphone/thread/*) で build_id 一致を確認
#   MULTI_SOURCE  = 公式第二経路では未確認だが、独立系ソース (BetaWiki / XDA /
#                   droid-life / 9to5Google / Android Police) 1つ以上で一致
#                   (= スクレイピング元と合わせ相互独立 2 経路以上)
#   SINGLE_SOURCE = 外部照合できず (スクレイピング元の1経路のみ。要再確認)
# external_conflict は外部ソースと builds.json の値の食い違い (値は書き換えず
# conflict_note に外部値を記録して両方残す)。同一月3件以上でその月全レコードに
# human_review を立てる (apply 部で機械判定)。
_C = "https://support.google.com/pixelphone/thread/"
COMMUNITY_POSTS = {  # Google Pixel Update 公式月次投稿 (Community Manager 投稿)
    "2025-06": _C + "349745083",  # June 2025 (Android 16)
    "2025-07": _C + "355981577",
    "2025-08": _C + "362911257",
    "2025-09": _C + "368006132",
    "2025-10": _C + "379076388",
    "2025-11": _C + "386109819",
    "2025-12": _C + "389367100",
    "2026-01": _C + "401468923",
    "2026-02": _C + "406938450",
    "2026-03": _C + "410784164",
    "2026-04": _C + "422905223",
    "2026-05": _C + "431077516",
    "2026-06": _C + "442096105",
    "2026-07": _C + "448470698",
}
BW = "https://betawiki.net/wiki/"
DL = "https://www.droid-life.com/"
N5 = "https://9to5google.com/"
XDA = "https://xdaforums.com/t/"
DL_P10FI = DL + "2025/08/28/google-posts-factory-image-files-for-pixel-10-series/"
DL_OCT30 = DL + "2025/10/30/google-posts-surprise-october-pixel-update-builds-doesnt-say-what-for/"
XDA_P10_OCT30 = XDA + "30oct25-new-stable-update-bd3a-251005-003-w4-or-j6-for-japan-variant.4757843/"
XDA_P10_DEC25 = XDA + "02dec25-new-stable-update-qpr2-bp4a-251205-006-also-a1-or-c1-e1-verizon-19dec25.4757843/"
XDA_P10_MAY26 = XDA + ("05-may-2026-new-stable-update-a16-qpr3-cp1a-260505-005-global-a1-telia-"
                       "warning-anti-rollback-update-included-take-care-not-to-brick-your-phone.4757843/")
XDA_RAVEN_MAR26 = XDA + "march-3-2026-cp1a-260305-018-global-18-a1-australia-root-pixel-6-pro-raven-stable-firmware.4352027/"
XDA_RAVEN_JUN26 = XDA + "june-16-2026-android-17-stable-cp2a-260605-012-global-a1-at-t-b1-au-root-pixel-6-pro-raven-stable-firmware.4352027/"
N5_DEC19 = N5 + "2025/12/19/pixel-december-2025-update-patch/"
N5_SEP02 = N5 + "2025/09/02/pixel-10-september-ota-update/"

CROSS_VALIDATION = {
    # ---- 2025-05 (スコープ外例外収載) ----
    "BP1A.250505.005": {
        "confidence": "MULTI_SOURCE",
        "confidence_sources": [
            "https://www.androidpolice.com/may-2025-google-pixel-security-update-anti-rollback-bootloader/",
            XDA + "may-6-2025-anti-rollback-bootloader-flash-both-slots-bp1a-250505-005-global-root-pixel-6-pro-raven-stable-firmware.4352027/",
        ],
        # 独立2ソース (Android Police / XDA) はロールアウト開始日を 2025-05-06 とする
        "external_conflict": ("release_date: builds.json=2025-05-05 / "
                              "外部(Android Police, XDA)=2025-05-06 (ロールアウト開始日)。値は書き換えず両方残す"),
    },
    # ---- 2025-06 ----
    "BP2A.250605.031.A2": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-06"], BW + "Android_16_build_BP2A.250605.031.A2",
        DL + "2025/06/10/android-16-download-new-features/"]},
    "BP2A.250605.031.A3": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-06"], BW + "Android_16_build_BP2A.250605.031.A3",
        DL + "2025/06/10/android-16-download-new-features/"]},
    # ---- 2025-07 ----
    "BP2A.250705.008": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-07"], N5 + "2025/07/08/android-16-july-update-pixel/"]},
    # ---- 2025-08 (BP2A.250605.031.A5 / BP2A.250705.008.A1 は8月配信分として公式投稿に掲載) ----
    "BP2A.250605.031.A5": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-08"], DL + "2025/08/05/august-2025-google-pixel-update-download/"]},
    "BP2A.250705.008.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-08"], DL + "2025/08/05/august-2025-google-pixel-update-download/"]},
    "BP2A.250805.005": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-08"], DL + "2025/08/05/august-2025-google-pixel-update-download/",
        N5 + "2025/08/05/android-16-august-update-pixel/"]},
    # ---- 2025-08 Pixel 10 ローンチ (公式月次投稿に非掲載 → 独立系で照合) ----
    "BD1A.250702.001": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        BW + "Android_16_build_BD1A.250702.001", DL_P10FI]},
    "BD1A.250702.001.A3": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        DL_P10FI, BW + "Android_16_build_BD1A.250702.001"]},
    "BD3A.250721.001": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        DL_P10FI, N5_SEP02]},
    "BD3A.250721.001.A1": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        DL_P10FI, N5_SEP02]},
    # ---- 2025-09 ----
    "BP3A.250905.014": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-09"], BW + "Android_16_build_BP3A.250905.014",
        N5 + "2025/09/03/android-16-september-update-pixel/"]},
    "BP3A.250905.014.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-09"],
        DL + "2025/09/04/heres-everything-fixed-in-pixel-september-security-patch/"]},
    "BD3A.250721.001.B7": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-09"], BW + "Android_16_build_BD3A.250721.001.B7"]},
    "BD3A.250721.001.E1": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        XDA + "16sep25-new-stable-update-critical-bug-fix-bd3a-250721-001-e1.4757843/",
        N5 + "2025/09/16/pixel-10-september-2025-ota-update/"]},
    # ---- 2025-10 (10/8 第1波は公式投稿掲載。rango 系ローンチビルドは非掲載) ----
    "BP3A.251005.004.A2": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-10"],
        DL + "2025/10/08/october-2025-android-update-available-for-google-pixel-devices/"]},
    "BP3A.251005.004.B1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-10"],
        DL + "2025/10/08/october-2025-android-update-available-for-google-pixel-devices/",
        N5 + "2025/10/08/android-16-october-update-pixel/"]},
    "BD3A.251005.003.W3": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-10"],
        DL + "2025/10/08/october-2025-android-update-available-for-google-pixel-devices/"]},
    "BD3A.251005.003.J5": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-10"],
        DL + "2025/10/08/october-2025-android-update-available-for-google-pixel-devices/"]},
    "BD3A.250808.001": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        BW + "Android_16"]},  # BetaWiki の Android 16 ビルド一覧に掲載 (rango 出荷ビルド)
    # 10/30 第2波 (公式投稿に非掲載 → droid-life / XDA / 9to5Google で照合)
    "BP3A.251005.004.A3": {"confidence": "MULTI_SOURCE", "confidence_sources": [DL_OCT30]},
    "BP3A.251005.004.B2": {"confidence": "MULTI_SOURCE", "confidence_sources": [DL_OCT30]},
    "BP3A.251005.004.B3": {"confidence": "MULTI_SOURCE", "confidence_sources": [DL_OCT30]},
    "BD3A.251005.003.E1": {"confidence": "MULTI_SOURCE", "confidence_sources": [DL_OCT30]},
    "BD3A.251005.003.F1": {"confidence": "MULTI_SOURCE", "confidence_sources": [DL_OCT30]},
    "BD3A.251005.003.J6": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        DL_OCT30, XDA_P10_OCT30]},
    "BD3A.251005.003.W4": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        DL_OCT30, XDA_P10_OCT30, N5 + "2025/11/01/new-pixel-october-2025-update/"]},
    # ---- 2025-11 ----
    "BP3A.251105.015": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    "BP3A.251105.015.J1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    "BP3A.251105.013.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    "BD3A.251105.010.E1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    "BD3A.251105.010.F1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    "BD3A.251105.010.J3": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-11"],
        DL + "2025/11/11/november-2025-android-security-update-download-google-pixel/"]},
    # ---- 2025-12 (12/2 第1波は公式投稿掲載。12/17-19 第2波は非掲載) ----
    "BP4A.251205.006": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-12"], BW + "Android_16_build_BP4A.251205.006",
        DL + "2025/12/02/download-pixel-december-update-features/"]},
    "BP4A.251205.006.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-12"], DL + "2025/12/02/download-pixel-december-update-features/"]},
    "BP4A.251205.006.B1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-12"], DL + "2025/12/02/download-pixel-december-update-features/"]},
    "BP4A.251205.006.C1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2025-12"], DL + "2025/12/02/download-pixel-december-update-features/"]},
    "BP4A.251205.006.E1": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        N5_DEC19, XDA_P10_DEC25]},
    "BP4A.251205.006.A4": {"confidence": "MULTI_SOURCE", "confidence_sources": [N5_DEC19]},
    "BP4A.251205.006.C2": {"confidence": "MULTI_SOURCE", "confidence_sources": [N5_DEC19]},
    # ---- 2026-01 ----
    "BP4A.260105.004.E1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-01"], DL + "2026/01/12/january-2026-google-pixel-update-download/"]},
    "BP4A.260105.004.A2": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-01"], DL + "2026/01/12/january-2026-google-pixel-update-download/"]},
    "BP4A.260105.004.B2": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-01"], DL + "2026/01/12/january-2026-google-pixel-update-download/"]},
    "BP4A.260105.004.C2": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-01"], DL + "2026/01/12/january-2026-google-pixel-update-download/"]},
    # ---- 2026-02 ----
    "BP4A.260205.001": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    "BP4A.260205.001.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    "BP4A.260205.001.B1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    "BP4A.260205.001.C1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    "BP4A.260205.002": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    "BP4A.260205.002.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-02"], DL + "2026/02/03/download-february-pixel-update-features/"]},
    # ---- 2026-03 ----
    "CP1A.260305.018": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-03"], XDA_RAVEN_MAR26]},
    "CP1A.260305.018.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-03"], XDA_RAVEN_MAR26]},
    "BD6A.251031.001.A4": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        N5 + "2026/03/05/pixel-10a-factory-images/"]},
    # ---- 2026-04 ----
    "CP1A.260405.005": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-04"], DL + "2026/04/07/2026-april-pixel-update-download-phone/"]},
    "CP1A.260405.003.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-04"], DL + "2026/04/07/2026-april-pixel-update-download-phone/"]},
    # ---- 2026-05 ----
    "CP1A.260505.005": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-05"], N5 + "2026/05/05/android-16-may-update-pixel/",
        XDA_P10_MAY26]},
    "CP1A.260505.005.A1": {"confidence": "MULTI_SOURCE", "confidence_sources": [
        XDA_P10_MAY26]},
    # ---- 2026-06 ----
    "CP2A.260605.012": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-06"], N5 + "2026/06/16/android-17-june-update-pixel/"]},
    "CP2A.260605.012.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-06"], N5 + "2026/06/16/android-17-june-update-pixel/",
        XDA_RAVEN_JUN26]},
    "CP2A.260605.012.B1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-06"], N5 + "2026/06/16/android-17-june-update-pixel/",
        XDA_RAVEN_JUN26]},
    "CP2A.260605.012.C1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-06"], N5 + "2026/06/16/android-17-june-update-pixel/",
        XDA + "android-17-stable-cp2a-260605-012-012-c1-16-jun-2026.4757843/"]},
    # ---- 2026-07 ----
    "CP2A.260705.006": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-07"], N5 + "2026/07/07/android-17-july-pixel-update/",
        DL + "2026/07/07/2026-july-pixel-update-available-for-your-pixel-phone/"]},
    "CP2A.260705.006.A1": {"confidence": "OFFICIAL", "confidence_sources": [
        COMMUNITY_POSTS["2026-07"],
        DL + "2026/07/07/2026-july-pixel-update-available-for-your-pixel-phone/"]},
    # ---- 外部照合できなかったもの (SINGLE_SOURCE はデフォルトのため列挙不要だが、
    #      調査済みであることを明示するため空エントリで記録) ----
    "BD3A.251005.003": {"confidence": "SINGLE_SOURCE", "confidence_sources": []},
    "BD3A.251005.003.J2": {"confidence": "SINGLE_SOURCE", "confidence_sources": []},
    "BP4A.251205.006.B3": {"confidence": "SINGLE_SOURCE", "confidence_sources": []},
    "CP1A.260405.005.B1": {"confidence": "SINGLE_SOURCE", "confidence_sources": []},
}


def apply_cross_validation(builds):
    """confidence / confidence_sources を全レコードに追記し、外部食い違いを記録する。

    - 値は書き換えない (追記のみ)。external_conflict は conflict_note に外部値を追記。
    - 同一リリース月内で外部食い違いが3件以上なら、その月の全レコードに
      human_review: true を立てる (2件以下は conflict_note のみ)。
    """
    conflict_months = {}
    for b in builds:
        cv = CROSS_VALIDATION.get(b["build_id"], {})
        b["confidence"] = cv.get("confidence", "SINGLE_SOURCE")
        b["confidence_sources"] = list(cv.get("confidence_sources", ()))
        ext = cv.get("external_conflict")
        if ext:
            b["conflict_note"] = (b["conflict_note"] + " | " + ext) if b.get("conflict_note") else ext
            month = str(b.get("release_date"))[:7]
            conflict_months[month] = conflict_months.get(month, 0) + 1
    review_months = {m for m, n in conflict_months.items() if n >= 3}
    for b in builds:
        if str(b.get("release_date"))[:7] in review_months:
            b["human_review"] = True


def with_base_month(rec):
    """全レコードに base_month (build_id 日付部から機械導出) を release_date の直前に挿入。"""
    out = {}
    for k, v in rec.items():
        if k == "release_date" and "base_month" not in out:
            out["base_month"] = base_month_of(rec["build_id"])
        out[k] = v
    return out

# anti-rollback 最重要フラグ: Pixel 10 系の 2026年5月更新ビルド
ANTI_ROLLBACK_BUILDS = {"CP1A.260505.005", "CP1A.260505.005.A1"}
ANTI_ROLLBACK_NOTE = (
    "Android 16ビルドへの巻き戻し不可。ブートローダーのanti-rollbackカウンタ増加のため、"
    "これ以前のファクトリーイメージ書き込みは文鎮化リスク"
    "（対象: Pixel 10系 frankel/mustang/blazer/rango/stallion。"
    "ソース上は2026年5月の全デバイス共通ビルドとして掲載）"
)


# ---- Agent 1 (2nd iteration: ARB Historian): anti-rollback 追記フィールド ----
# 既存2件 (CP1A.260505.005 系) への scope / effect の「追記」。note は不変で残す。
# scope はソース警告文 (data/raw/2026-07-30/images.html 内
# "Special instructions for updating Pixel devices to the May 2026 monthly release"
# 警告: "Pixel 10, 10 Pro, 10 Pro XL and 10 Pro Fold") の列挙に従う。
# 既存 note は stallion (10a) を含むが、ソース警告文は列挙していない
# (差異の判断は data/build-dict-decisions.md「## Agent 1 (2nd iteration)」参照)。
ARB_SCOPE_A16 = ("Pixel 10, 10 Pro, 10 Pro XL, 10 Pro Fold"
                 "（frankel/mustang/blazer/rango。ソース警告文の列挙。Pixel 9系以前は非対象）")
ARB_EFFECT_A16 = "これ以前のAndroid 16ビルドへ戻して起動できない"
ARB_EXTRA_FIELDS = {
    "CP1A.260505.005": {"scope": ARB_SCOPE_A16, "effect": ARB_EFFECT_A16},
    "CP1A.260505.005.A1": {"scope": ARB_SCOPE_A16, "effect": ARB_EFFECT_A16},
}

# ---- Agent 1 (2nd iteration: ARB Historian): スコープ外の例外収載レコード ----
# Android 16 世代 (SCOPE_PREFIXES) 外だが、復旧手順の正しさに直結する
# anti-rollback 履歴として例外収載する既知レコード。パースでは出現しない
# (BP1A は SCOPE_PREFIXES 外) ため、main() 末尾で builds に注入する。
# 根拠: data/raw/2026-07-30/images.html 内の警告
#   "Special instructions for updating Pixel devices to the May 2025 monthly release
#    Warning: The May 2025 update for Pixel 6 (6, 6 Pro, 6a) and Pixel 8 (8, 8 Pro, 8a)
#    devices contains a bootloader update that increments the anti-roll back version..."
# + Android Police 2025-05-06 記事 (build_id BP1A.250505.005 を明記)。
# "_bulletin_month" は security_patch を bulletin スナップショットから
# 再解決するためのヒントキー (出力前に除去)。
KNOWN_EXTRA_BUILDS = [
    {
        "build_id": "BP1A.250505.005",
        "os": "Android 15",
        "track": "stable",
        "release_date": "2025-05-05",
        "security_patch": "2025-05-05",  # フォールバック。bulletin から再解決
        "_bulletin_month": "2025-05",
        "devices": ["akita", "bluejay", "husky", "oriole", "raven", "shiba"],
        "region_scope": "global",
        "scope_note": "Android 16世代外だが、復旧手順の正しさに直結するため例外収載",
        "anti_rollback": {
            "incremented": True,
            "scope": "Pixel 6, 6 Pro, 6a, 8, 8 Pro, 8a（Pixel 7系は非対象）",
            "effect": "これ以前のAndroid 15ビルドへ戻して起動できない",
            "note": (
                "Android 15ビルドへの巻き戻し不可。ブートローダーのanti-rollbackカウンタ増加のため、"
                "これ以前のファクトリーイメージ書き込みは文鎮化リスク"
                "（対象: Pixel 6系 oriole/raven/bluejay・Pixel 8系 shiba/husky/akita。"
                "Pixel 7系は非対象）"
            ),
        },
        "official_fixes": [],
        "sources": [
            URL_IMAGES,
            URL_BULLETIN,
            "https://www.androidpolice.com/may-2025-google-pixel-security-update-anti-rollback-bootloader/",
        ],
        "verify_state": "VERIFIED",
    },
]


def parse_device_tables(html: str):
    """devsite の OTA / factory image ページからビルド行を抽出する。

    構造: <h2 id="<codename>">"<codename>" for <marketing name></h2> の後に
    行 <td>VERSION (BUILD_ID, Mon YYYY[, REGION])</td> が続く。
    REGION 注記は "," 区切りでトークン化し REGION_NORMALIZE で正規化する
    (ソース側の "Japan, Japan" 重複や VZW/JP 略記のゆれを吸収)。
    戻り値: [(codename, version, build_id, month "YYYY-MM", regions tuple), ...]
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
            rest = []
            if qual:
                parts = [p.strip() for p in re.split(r",", qual)]
                for p in parts:
                    m = re.match(r"([A-Z][a-z]{2}) (20[0-9]{2})$", p)
                    if m and m.group(1) in MONTHS:
                        month = f"{m.group(2)}-{MONTHS[m.group(1)]:02d}"
                    elif p:
                        tok = p.replace("&amp;", "&")
                        rest.append(REGION_NORMALIZE.get(tok, tok))
            rows.append((codename, ver, bid, month, tuple(rest)))
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
        for codename, ver, bid, month, regions in parse_device_tables(html):
            if not bid.startswith(SCOPE_PREFIXES):
                continue
            a = agg.setdefault(bid, {
                "devices": set(), "versions": set(), "months": set(),
                "regions": set(), "sources": set()})
            a["devices"].add(codename)
            a["versions"].add(ver)
            if month:
                a["months"].add(month)
            a["regions"].update(regions)
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

        # region_scope: ソースHTMLの変異版注記の直接パースが正。
        # devsite の正常行は必ず "(BUILD_ID, Mon YYYY[, REGION])" の月注記を持ち、
        # 「月注記あり・地域トークンなし」は地域限定なし (= global) を意味する
        # (2026-07-30 スナップショット実測: 月注記なしのスコープ内行は 0 件。
        #  外部照合済み global 変異版 18 件がこの表記。builds.json の confidence_sources 参照)。
        # 注記そのものが欠落した縮退行 (月も取れない) のみ SUFFIX_MONTH_MAP
        # (base month × suffix) でフォールバック補完する。
        # 固定辞書 (suffix→region のグローバル1次元マップ) は使用禁止。
        # フォールバックも失敗した場合 (注記欠落かつマップ外の月×サフィックス) は
        # "global" 等で推測して埋めず region_scope="unknown" + human_review を立てる
        # (2026-07-31 凍結時に確定。tests/test_suffix_fallback.py で回帰固定)。
        regions = set(a["regions"])
        region_fallback_src = None
        region_unknown = False
        if not regions and VARIANT_SUFFIX_RE.search(bid) and not a["months"]:
            fb = SUFFIX_MONTH_MAP.get((base_month_of(bid), bid.rsplit(".", 1)[1]))
            if fb:
                regions = set(fb["region"].split("; "))
                region_fallback_src = fb["source"]
            else:
                region_unknown = True

        rec = {
            "build_id": bid,
            "os": os_val,
            "track": track,
            "release_date": release_date,
            "security_patch": sec,
            "devices": sorted(a["devices"]),
            "region_scope": ("unknown" if region_unknown
                             else "; ".join(sorted(regions)) if regions else "global"),
        }
        if region_fallback_src:
            rec["region_scope_source"] = region_fallback_src
        if VARIANT_SUFFIX_RE.search(bid):
            rec["parent_build_id"] = bid.rsplit(".", 1)[0]

        arb = {
            "incremented": bid in ANTI_ROLLBACK_BUILDS,
            "note": ANTI_ROLLBACK_NOTE if bid in ANTI_ROLLBACK_BUILDS else "",
        }
        # Agent 1 (2nd iteration): scope / effect の追記 (note は不変で残す)
        extra_arb = ARB_EXTRA_FIELDS.get(bid)
        if extra_arb:
            arb = {"incremented": arb["incremented"],
                   "scope": extra_arb["scope"],
                   "effect": extra_arb["effect"],
                   "note": arb["note"]}
        rec["anti_rollback"] = arb
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
        # 変異版サフィックスの地域が注記 (欠落) からもフォールバックからも導出
        # できない場合は推測せず人間確認に回す (region_scope="unknown" のまま残す)
        if region_unknown:
            rec["human_review"] = True
            conflicts.append(
                "region_scope: 変異版サフィックスの注記欠落 (月注記も取得できず)・"
                f"SUFFIX_MONTH_MAP ({base_month_of(bid)}, {bid.rsplit('.', 1)[1]}) "
                "未登録 -> unknown")
        if conflicts:
            resolution = RESOLVED_CONFLICTS.get(bid)
            if resolution and all(c.startswith("release_date:") for c in conflicts):
                # Agent 3 (2nd iteration): base_month/release_date 分離で解決済み。
                # release_date はソース掲載月ベースに確定。release_date_source_month は残す。
                rec["release_date"] = resolution["release_date"]
                rec["resolution_note"] = resolution["resolution_note"]
            else:
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
            "region_scope": REGION_NORMALIZE.get(anchor.get("region_claim", "global"),
                                                 anchor.get("region_claim", "global")),
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

    # Agent 1 (2nd iteration): スコープ外の例外収載レコードを注入
    # (既存レコードと build_id 衝突時はソース由来を優先し注入しない)
    for extra in KNOWN_EXTRA_BUILDS:
        if extra["build_id"] in present:
            continue
        rec = copy.deepcopy(extra)
        bm = rec.pop("_bulletin_month", None)
        if bm and bulletins.get(bm, {}).get("patch_level"):
            rec["security_patch"] = bulletins[bm]["patch_level"]
        builds.append(rec)

    # Agent 4 (2nd iteration): 外部独立ソース照合 (confidence / confidence_sources /
    # 外部食い違いの conflict_note 追記。同一月3件以上で human_review)
    apply_cross_validation(builds)

    # Agent 3 (2nd iteration): 全レコードに base_month を付与 (機械導出のため全件)
    builds = [with_base_month(b) for b in builds]

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
