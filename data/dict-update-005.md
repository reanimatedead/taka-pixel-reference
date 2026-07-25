# dict-update-005 — 変更一覧（UPDATE-005R Agent 1: data-updater）

作業日: 2026-07-25 / 一次参照: `data/research-2026-07.md`（付録E・2026-07-24調査）。付録Eに無い機序は書いていない。

## サマリ

| 指標 | 前 | 後 |
|---|---|---|
| 項目数 | 34 | 37（新規3件） |
| VERIFIED | 13 | 33 |
| UNVERIFIED | 21 | 4（PXD-0004 / 0005 / 0010 / 0013） |
| mechanism 保有 | 0 | 21（confirmed 7 / inferred 11 / unknown 3） |
| layer 保有 | 0 | 19 |

## UNVERIFIED降格8件の処置

| ID | 処置 |
|---|---|
| PXD-0001 タッチ操作異常 | VERIFIED 復帰（出典3件転記）+ mechanism unknown |
| PXD-0002 通信不能・eSIM消滅 | VERIFIED 復帰（3件）+ layer modem_fw + mechanism inferred |
| PXD-0003 仕事用プロファイルWi-Fi | VERIFIED 復帰（3件）+ layer framework + mechanism confirmed（Google声明引用）。fix_status は open のまま（修正表明あり・時期未定） |
| PXD-0004 再起動ループ（A17起因とする既存項目） | **昇格見送り**。付録Eのブートループは「2026年3〜5月の月例更新起因」であり、本項目の主張（A17初期版起因・first_seen 2026-06）と対応が明確でないため。当該事象は新規 PXD-0036 として収録 |
| PXD-0006 Wi-Fi突発切断 | VERIFIED 復帰（1件）。層は「framework疑い」のため layer 未付与、付録Eに機序記述が無いため mechanism 未付与 |
| PXD-0007 バッテリー異常消費 | VERIFIED 復帰（3件）+ layer modem_fw + mechanism inferred |
| PXD-0008 通知が届かない | VERIFIED 復帰（1件）+ layer framework + mechanism inferred |
| PXD-0009 戻る無反応・ホワイトアウト | VERIFIED 復帰（1件）+ mechanism unknown（層未特定のため layer 未付与） |

## その他の既存項目更新

- PXD-0014（A14ストレージ）: layer kernel + mechanism confirmed（Issue 305766503）+ 出典2件追加。fix_status は patched のまま（2023-11 パッチ、機序文に明記）
- PXD-0017（A13ワイヤレス充電）: layer framework + mechanism inferred（Issue 242836221）+ 出典2件追加 ※付録E新規候補⑤は本項目の拡張で対応
- PXD-0021（A11壁紙ブートループ）: layer framework + mechanism confirmed（配列index256超過の詳細）+ 出典2件追加 ※新規候補⑦は拡張で対応
- PXD-0023（4aバッテリー制限）: VERIFIED 昇格 + layer cloud + mechanism confirmed（dtbo差分・セル判別番号・ACCC文書）※新規候補①「詳細版」は本項目の機序拡張として実施（重複項目回避）
- PXD-0024（5a膨張）: VERIFIED 昇格 + layer hardware（付録Eに機序記述なし）
- PXD-0025（6a指紋精度）: VERIFIED 昇格 + layer hardware + mechanism confirmed（Google公式声明。付録E「Pixel 6世代」を同世代の 6a 項目に適用）※新規候補⑥は本項目の拡張で対応
- PXD-0026 / PXD-0027（6a発熱・モデム）: VERIFIED 昇格 + layer modem_fw + mechanism inferred（付録E「6aモデム不安定・発熱」が両項目に対応）
- PXD-0028（7a充電中発熱）: VERIFIED 昇格 + layer hardware（機序記述なし）
- PXD-0029（7aちらつき）: VERIFIED 昇格 + mechanism inferred（ソフト説/ハード説併存を明記。付録E表記 unknown/inferred のうち「コミュニティ推定あり」の実態に合う inferred を採用、格上げではない）
- PXD-0030（8a緑かぶり）: VERIFIED 昇格 + layer framework + mechanism confirmed（2024-03修正）。縦ライン（ハード故障）は PXD-0037 に分離
- PXD-0031（9aロット）: VERIFIED 昇格 + layer hardware + mechanism inferred（延期事実は confirmed だが過熱原因はリーク推定のため全体を inferred）
- PXD-0032（Fold内側画面）: layer hardware + mechanism inferred（4経路）+ 出典2件追加 ※新規候補⑧は拡張で対応
- PXD-0034（Play Integrity）: VERIFIED 昇格 + layer cloud + mechanism confirmed + 出典2件。cause 内の「指定一次ソースでの照合は未実施」注記は VERIFIED 化と矛盾するため削除（唯一の既存フィールド文言変更）

## 新規追加（3件・上限8件以内）

| ID | 内容 | confidence |
|---|---|---|
| PXD-0035 | A16 GNSS非スリープドレイン（新規候補②） | inferred |
| PXD-0036 | 2026年3〜5月 月例更新ブートループ（新規候補③） | unknown |
| PXD-0037 | 8a 恒久縦ライン＝ハード故障（新規候補④・PXD-0030から分離） | inferred |

新規候補①⑤⑥⑦⑧は既存項目（0023/0017/0025/0021/0032）の機序拡張で対応し、辞書の重複を避けた。新規はいずれも付録Eの出典を転記済みのため VERIFIED で収録（UPDATE-004の「新規はUNVERIFIED開始」は出典なし項目の規約と解釈）。

## 判断メモ（迷った点）

- **複合層の layer 表記**: スキーマは単一値のため、付録Eの「A+B」表記は先頭（主因）を採用し、複合である旨は mechanism.text に残した（例: 0007 modem_fw+hardware → modem_fw）
- **「〜疑い」の層**: 確定でないため layer 未付与（0001 / 0006 / 0009 / 0029 / 0036）。スキーマ「不明は付けない」に準拠
- **mechanism の付与基準**: 付録Eに機序の記述（または unknown の認知状況）があるもののみ。confidence マーカーだけで機序記述の無いもの（0006 / 0024 / 0028）は mechanism を付けず layer・出典のみ
- **PXD-0018（A12ドレイン）**: 付録Eの機序は Exynos（Pixel 6）前提で、本項目の対象機種（4a/4a5g/5a＝Snapdragon）に適用できないため付与見送り。出典追加もせず無変更
- **PXD-0035 の workaround**: 付録Eに対処記述が無いため、機序（GNSS常時稼働）から導いた最小限の運用回避＋パッチ待ちのみ記載
