# REPORT-UPDATE-004: 不具合辞書システム構築 — 完了報告

実施日: 2026-07-24〜25（Agent 1 は 24 日、Agent 2 コミット以降は 25 日に再開して実施）
指示書: `UPDATE-004.md`
状態: **全工程完了・push 未実行（人間ゲート待ち）**

## 成果物

| ファイル | 内容 |
| --- | --- |
| `docs/dict/data/entries.json` | 不具合データ本体（34件・スキーマ厳守） |
| `docs/dict/index.html` | 表示・検索（単一ファイル、あいうえお索引 / A-Z索引 / 全文検索 / 複合フィルタ） |
| `data/dict-migration.md` | 移植元→ID対応表・件数・判断記録 |
| `data/qa-report.md` | QA結果追記（UPDATE-004 セクション） |
| `docs/index.html` | nav に `不具合辞書 ↗` を1行追加（指示書で明示された唯一の変更のみ） |
| `README.md` | 辞書の URL / スキーマ場所 / 収録基準 / 追加手順を追記 |

## コミット（4件、push 未実行）

```
903e99a Add QA results for dictionary
c6300ff Link dictionary from main page and document schema ops
c9c983c Add dictionary renderer with kana/alpha indexes and search
b2635bf Add defect dictionary schema and migrate existing entries
```

## 移植結果

- **移植件数: 34件**（想定40件前後に対し実在した不具合項目の全件。内訳: #os-bugs 22 / #ts・#fold 機種別既知問題 11 / #ts-pro 1）
- **新規創作: 0件**
- **VERIFIED: 13件 / UNVERIFIED: 21件**
- スキーマ検証: **全項目 PASS**（ID一意・PXD-連番4桁欠番なし・yomi全存在・category 10分類内・severity/fix_status/verify_state 規定値内。詳細は `data/qa-report.md`）
- `npx html-validate docs/dict/index.html`: エラー0
- ローカル配信検証: `python3 -m http.server 8000 --directory docs` → `curl -s localhost:8000/dict/ | grep -c 'entries.json'` = 1、`/dict/data/entries.json` が HTTP 経由で34件返ることを確認

## 判断記録（推測で進めなかった点）

1. **A17/A16 の VERIFIED 8項目を UNVERIFIED に降格**（PXD-0001〜0004, 0006〜0009）
   移植元 HTML では VERIFIED だが、`data/sources.md` に対応 URL の記録がない（sources.md 自身が「A17/A16 で最初から VERIFIED だった項目は本工程では変更していない」= URL 未記録と明記）。指示書 Agent 1 手順3「対応が特定できない場合 sources は空配列にし verify_state を UNVERIFIED に落とす（勝手にURLを充てない）」を「状態を改変しない」より優先して適用した。両ルールが衝突するケースであり、指示書がこの衝突時の挙動を手順3で明示していると解釈した。
2. **#ts 機種別項目（9件）は UNVERIFIED 開始**。移植元に VERIFIED/UNVERIFIED マーカーがなく sources.md にも URL がないため、「新規は UNVERIFIED 開始が既定」に準拠。
3. **移植対象の線引き**: EOL 告知・共通TSフロー・購入判断（用途別早見表・中古非推奨単体）・コードネーム表は「不具合」ではないため対象外。#ts-pro からは Play Integrity 判定失敗（PXD-0034）のみを不具合相当として収録。全リストは `data/dict-migration.md` に記録。
4. **fix_status の割当**: 出典・本文に修正/仕様の記述がある項目のみ patched / spec とし、ハードウェア個体差で修正見込みのないものは wontfix、それ以外は open。項目別の根拠は entries.json の cause 欄と dict-migration.md を参照。
5. **first_seen は近似値**: OS別項目は当該 OS 配信年（A16/A17 は年月まで）、機種別項目は機種発売年。PXD-0023 のみ HTML 明記の 2025-01。
6. **QA 差し戻し修正 1件**: 配信チェック `grep -c 'entries.json'` が初回 4（fetch 以外の表示文言 3箇所が同文字列を含んでいた）。文言を言い換えて fetch の1箇所のみに修正し =1 で PASS。データ・機能への影響なし。
7. **実行形態**: 指示書の Agent 1〜5 は同一セッション内で役割を順次実行した（作業前後の git status 実行・コミット分割・人間ゲートは指示書どおり遵守）。データ移植の内容忠実性を直接管理するための選択。
8. **UPDATE-004.md 自体のコミット**: README がスキーマ定義の所在として `UPDATE-004.md` を参照するため、本レポートと同じコミットに含めた（未コミットだと公開リポジトリ上で参照が壊れるため）。

## 人間ゲート（確認 && 実行の連結形式）

```bash
python3 -m json.tool docs/dict/data/entries.json > /dev/null && git push origin main
# 2〜3分後（CDN反映込み）:
curl -s "https://reanimatedead.github.io/taka-pixel-reference/dict/?v=$(date +%s)" | grep -c 'entries.json'
# ↑ 1 が返れば配信成功。新URL: https://reanimatedead.github.io/taka-pixel-reference/dict/
```

## 今後の拡張運用

**月例パッチ後、新規不具合は entries.json への追記のみ。HTML は触らない。収録基準3条件（①独立した複数ソースで報告 ②再現時に実害がある ③対処法または回避策が記述できる）を満たさないものは追加しない。**

- ID は PXD-0035 から連番で採番（欠番・再利用禁止）
- 新規項目は verify_state: UNVERIFIED 開始が既定。出典が取れたら sources に URL+date を記録して VERIFIED 化
- 追記後は `python3 -m json.tool docs/dict/data/entries.json > /dev/null` で構文検証してから push
- 今回 UNVERIFIED に落とした A17/A16 の8件（PXD-0001〜0004, 0006〜0009）は、次回検証工程で出典 URL を確保して VERIFIED に戻すのが最優先の再検証対象

## 完了条件チェック

- [x] docs/dict/ に data/entries.json と index.html が存在
- [x] 既存不具合の全件移植（34件）・新規創作ゼロ
- [x] あいうえお索引（濁音・半濁音の清音正規化込み）/ A-Z索引 / 全文検索 / 複合フィルタが仕様通り
- [x] スキーマ検証（ID一意・yomi必須・分類規定値）が機械実行済み
- [x] push はエージェント未実行
