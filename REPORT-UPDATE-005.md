# REPORT-UPDATE-005 — 図解・原因構造の追加（UPDATE-005R 完了報告）

作業日: 2026-07-25 / 指示書: taka-pixel-reference-UPDATE-005R.md（初版UPDATE-005は破棄、R版のみ使用）
一次参照: 付録E（`data/research-2026-07.md` として一字一句そのまま保存済み）。再検索は行わず、付録Eに無い機序は書いていない。

## コミット（4件・すべて未push、origin/main より ahead 4）

| Agent | コミット | 内容 |
|---|---|---|
| 1 data-updater | 40dacc0 | 付録E保存・entries.json 機序/昇格/新規・変更一覧 |
| 2 codename-fixer | f71d116 | コードネーム表確定・sources.md 追記 |
| 3 renderer-extender | e40594a | layer/機序/Mermaid 表示・図解5件データ |
| 4 qa-verifier | 2890611 | QA全件PASSの記録 |

## 昇格件数（UNVERIFIED → VERIFIED）

- **合計 17件**。うち降格8件からの復帰は **7件**（PXD-0001/0002/0003/0006/0007/0008/0009、すべて付録EのURLを sources に転記）
- **PXD-0004 は昇格見送り**: 付録Eのブートループは「2026年3〜5月の月例更新起因」で、本項目の主張（A17初期版起因・first_seen 2026-06）と対応が明確でないため。「対応が明確なもののみ昇格」ルールに従った。当該事象は新規 PXD-0036 として収録
- その他の昇格10件: PXD-0023/0024/0025/0026/0027/0028/0029/0030/0031/0034
- 最終: VERIFIED 33 / UNVERIFIED 4（PXD-0004/0005/0010/0013）・全37件

## confidence 内訳（mechanism 21件）

**confirmed : inferred : unknown = 7 : 11 : 3**

- confirmed（7）: PXD-0003 / 0014 / 0021 / 0023 / 0025 / 0030 / 0034 — いずれも付録Eに Google声明・Issue Tracker番号・ソース差分解析の明記あり
- inferred（11）: PXD-0002 / 0007 / 0008 / 0017 / 0026 / 0027 / 0029 / 0031 / 0032 / 0035 / 0037
- unknown（3）: PXD-0001 / 0009 / 0036 — Google認知あり・機序非公開
- 付録Eの判定をそのまま使用し格上げなし。unknown は画面上で「機序未解明（Google認知あり）」として表示される

## 新規追加: 3件（上限8以内）と見送り理由

| 候補 | 処置 |
|---|---|
| ② A16 GNSS非スリープドレイン | **新規 PXD-0035**（inferred） |
| ③ 2026年3〜5月ブートループ | **新規 PXD-0036**（unknown） |
| ④ 8a 緑の縦ライン（ハード故障） | **新規 PXD-0037**（inferred）。ソフト起因の緑ティント（PXD-0030、confirmed・2024-03修正）と分離し相互参照を明記 |
| ① 4aバッテリー制限の詳細版 | 見送り＝**既存 PXD-0023 の機序拡張で実施**（dtbo差分・セル判別QR番号・ACCC文書をすべて mechanism に収録。同一不具合の重複項目を作らないため） |
| ⑤ A13ワイヤレス充電断続 | 見送り＝既存 PXD-0017 の拡張（Issue 242836221 転記） |
| ⑥ A12 Pixel6指紋低速 | 見送り＝既存 PXD-0025（6a）の拡張。付録E「Pixel 6世代」の公式声明を同世代の 6a 項目に適用 |
| ⑦ A11壁紙ブートループ機序詳細化 | 指示書どおり既存 PXD-0021 の拡張 |
| ⑧ Fold内側画面機序詳細化 | 指示書どおり既存 PXD-0032 の拡張 |

新規3件は付録Eの出典転記済みのため VERIFIED で収録（「新規はUNVERIFIED開始」は出典なし項目の規約と解釈）。

## 図解件数

- **5件**（上限10以内・全件 mechanism 保有項目）: PXD-0003（A17仕事用プロファイルWi-Fi）/ PXD-0014（A14ストレージ）/ PXD-0021（A11壁紙: RGB合計→index256超過フロー）/ PXD-0023（4a: クラウド判定→dtbo書換→制限の連鎖）/ PXD-0034（Play Integrity連鎖）— 指示書のパイロット5候補どおり
- 共通構造図（付録D）は辞書冒頭に一字一句そのまま静的埋め込み
- Mermaid は cdnjs 10.9.1（SRI付き）。読込失敗時は図解のみ非表示・本文正常のフォールバック実装
- Mermaid 構文検証: mermaid@10.9.1 の parse() で全6件 PASS（手段は qa-report.md に記録）

## コードネーム表

- 10a = **stallion** VERIFIED（9to5Google Factory Image 公開記事）
- 既存9件（sunfish/bramble/barbet/bluejay/lynx/akita/tegu/felix/comet）VERIFIED（Android Police + LineageOS wiki + AOSP build docs の community 照合。注記は sources.md）
- 10 Pro Fold = **rango（リーク段階・公式Factory Image未掲載）** UNVERIFIED 維持

## 迷った判断の記録

1. **複合層の layer 単一値化**: 付録Eの「modem_fw+hardware」等は先頭（主因）を採用し、複合の実態は mechanism.text に残した（0007/0023/0025/0026/0027/0031/0034）
2. **「〜疑い」「未特定」の層**: layer 未付与（スキーマ「不明は付けない」）— 0001/0006/0009/0029/0036
3. **mechanism の付与基準**: 付録Eに機序記述（unknown は認知状況）があるもののみ。confidence マーカーだけのもの（0006/0024/0028）は layer・出典のみで mechanism なし
4. **PXD-0029 の confidence**: 付録E表記「unknown/inferred」→ コミュニティ推定（両説）が実在するため定義に合う inferred を採用し、text に「両説併存・未確定」を明記
5. **PXD-0018（A12ドレイン）は無変更**: 付録Eの機序は Exynos（Pixel 6）前提で、本項目の対象機種（4a/4a5g/5a＝Snapdragon）に適用不能なため
6. **PXD-0034 の cause 文言**: 「指定一次ソースでの照合は未実施」の注記が VERIFIED 化と矛盾するため削除（既存フィールドの唯一の文言変更として記録）
7. **エージェント実行形態**: 5エージェントは同一セッション内で逐次フェーズとして実行（各フェーズで git status 確認・役割どおりのコミットを分離）
8. リポジトリ直下の旧 `UPDATE-005.md`（未追跡）は破棄対象のため放置・未コミット。削除は人間判断に委ねる

## 完了条件チェック

- [x] data/research-2026-07.md がリポジトリに存在（付録Eと diff 一致を確認済み）
- [x] confidence 3値運用・unknown が画面表示される（PXD-0001/0009/0036）
- [x] 降格8件のうち付録Eで裏付く7件が sources 付きで VERIFIED 復帰（0004 は理由付き見送り）
- [x] コードネーム表: 10a=stallion VERIFIED、10 Pro Fold=rango UNVERIFIED維持
- [x] 新規3件（≤8）・図解5件（≤10）・Mermaid全件構文PASS
- [x] push はエージェント未実行

## 人間ゲート（push 手順）

```bash
python3 -m json.tool docs/dict/data/entries.json > /dev/null && git push origin main
# 2〜3分後:
curl -s "https://reanimatedead.github.io/taka-pixel-reference/dict/?v=$(date +%s)" | grep -c 'mermaid'
```
