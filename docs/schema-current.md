# 現行スキーマ調査: docs/dict/data/entries.json

- 調査日: 2026-07-30
- 対象: `docs/dict/data/entries.json`（1383行・トップレベルは配列・37件）
- 調査方法: 全件読解 + Python による全キー・全値域の機械集計

## 1. トップレベル構造

ファイル全体は **不具合レコードの JSON 配列**。1要素 = 1不具合エントリ。

## 2. 全キー一覧（型・出現率）

| キー | 型 | 出現率 | 必須性 | 備考 |
|---|---|---|---|---|
| `id` | string | 37/37 | 必須 | `PXD-0001`〜`PXD-0037` |
| `title_ja` | string | 37/37 | 必須 | 日本語タイトル |
| `title_en` | string | 37/37 | 必須 | 英語タイトル |
| `yomi` | string | 37/37 | 必須 | ひらがな読み（ソート用） |
| `category` | string | 37/37 | 必須 | 日本語ラベル9種（下記） |
| `severity` | string | 37/37 | 必須 | `critical` / `high` / `medium` / `low` |
| `affected_models` | string[] | 37/37 | 必須 | 空配列なし |
| `affected_os` | string[] | 37/37 | 必須 | **空配列 12件あり**（OS非依存のHW問題等） |
| `symptom` | string | 37/37 | 必須 | 症状の説明文 |
| `cause` | string | 37/37 | 必須 | 原因の説明文 |
| `workaround` | string[] | 37/37 | 必須 | 対処手順の配列 |
| `fix_status` | string | 37/37 | 必須 | `open` / `patched` / `spec` / `wontfix` |
| `first_seen` | string | 37/37 | 必須 | `YYYY` または `YYYY-MM`（粒度混在） |
| `last_checked` | string | 37/37 | 必須 | `YYYY-MM-DD` |
| `verify_state` | string | 37/37 | 必須 | 値域は §3 |
| `sources` | object[] | 37/37 | 必須 | **空配列 4件あり**（UNVERIFIED の4件と一致） |
| `layer` | string | 19/37 | 任意 | `cloud` / `framework` / `hardware` / `kernel` / `modem_fw` |
| `mechanism` | object | 21/37 | 任意 | 形は §4 |
| `diagram` | string | 5/37 | 任意 | Mermaid flowchart のソース文字列 |

キーの記載順は全件でほぼ固定（id → タイトル群 → 分類 → 影響範囲 → 症状/原因/対処 → 状態/日付 → verify_state → sources → layer → mechanism → diagram）。`layer` は sources の後に置かれる。

## 3. `verify_state` の実際の値域

全37件のユニーク値は **2値のみ**:

- `VERIFIED` — 33件（sources が1件以上ある）
- `UNVERIFIED` — 4件（PXD-0004, 0005, 0010, 0013。いずれも `sources: []`）

大文字 SCREAMING_SNAKE 形式。`sources` 空配列 ⇔ `UNVERIFIED` が完全に対応している（暗黙の整合規則）。

## 4. 入れ子構造

### 4.1 `mechanism`（21/37）

```json
"mechanism": {
  "text": "機序の説明文（string）",
  "confidence": "confirmed | inferred | unknown"
}
```

- キーは全件 `text` + `confidence` の2つのみ。追加キーなし。
- `confidence` 実値域: `confirmed`（6件相当）/ `inferred` / `unknown`。小文字。
- 注意: **エントリ側 `mechanism.confidence` の値域は `confirmed|inferred|unknown` であり、build_link 案の `official|inferred|estimated|unknown` とは異なる語彙**（`inferred` と `unknown` のみ共通）。

### 4.2 `sources`（37/37、空配列あり）

```json
"sources": [
  { "url": "https://...", "date": "2026-07-24" }
]
```

- 要素キーは全件 `url` + `date` の2つのみ。`date` は `YYYY-MM-DD`（確認日）。

### 4.3 `layer`（19/37、フラット文字列）

入れ子ではなく単一文字列。実値域: `cloud` / `framework` / `hardware` / `kernel` / `modem_fw`。snake_case。

### 4.4 `diagram`（5/37）

Mermaid `flowchart TD` のソースを `\n` 込みの1文字列で格納。

## 5. ID体系

- 形式: `PXD-` + 4桁ゼロ埋め連番（正規表現 `PXD-\d{4}` に全件一致）
- `PXD-0001`〜`PXD-0037` まで**欠番なしの連番**（配列順 = ID順）
- 相互参照はテキスト内に ID を直書きする方式（例: PXD-0037 の workaround/cause 中に「PXD-0030」への言及）。専用の参照フィールドは存在しない。

## 6. 列挙値まとめ

- `category`（9種・日本語）: 画面・タッチ / 通信 / 電源・起動 / OS更新起因 / バッテリー・充電・発熱 / アプリ挙動 / 生体認証 / 物理・破損 / 音・通話
- `severity`: critical / high / medium / low（小文字）
- `fix_status`: open / patched / spec / wontfix（小文字）
- `affected_models`: 4a, 4a5g, 5a, 6a, 7a, 8a, 9a, 10a, fold, 9profold, 10profold（小文字・ハイフンなし）
- `affected_os`: "11"〜"17"（メジャーバージョンの文字列）

## 7. 命名規則

- **キー名は全て snake_case**（`title_ja`, `affected_models`, `first_seen`, `verify_state`, `last_checked`）。camelCase は 1 つもない。
- 値の規則: 状態系は小文字（severity, fix_status, layer, confidence）だが、**`verify_state` の値だけ大文字**（VERIFIED/UNVERIFIED）。
- 日付は文字列: 精密日は `YYYY-MM-DD`、発生時期は `YYYY` または `YYYY-MM` の可変粒度。

## 8. 実データ例（PXD-0002 全文引用）

```json
{
  "id": "PXD-0002",
  "title_ja": "通信不能（5G→LTE落ち・モバイル接続不可・eSIM消滅）",
  "title_en": "Mobile network failure and eSIM loss",
  "yomi": "つうしんふのう",
  "category": "通信",
  "severity": "high",
  "affected_models": ["6a", "7a", "8a", "9a", "10a"],
  "affected_os": ["17"],
  "symptom": "5GからLTEへの落ち込み、モバイル接続不可、eSIM消滅。6a / 8a を含む広範な機種で報告。",
  "cause": "Android 17 初期版のシステム側不具合。",
  "workaround": [
    "機内モードON/OFF",
    "SIM再挿入",
    "ネットワーク設定リセット",
    "eSIM消滅時は端末側で復旧不可のケースがありキャリア窓口で再発行"
  ],
  "fix_status": "open",
  "first_seen": "2026-06",
  "last_checked": "2026-07-24",
  "verify_state": "VERIFIED",
  "sources": [
    { "url": "https://www.androidauthority.com/android-17-knocks-off-5g-3679536/", "date": "2026-07-24" },
    { "url": "https://www.androidcentral.com/apps-software/android-os/android-17-woes-continue-with-pixel-users-losing-5g-connectivity", "date": "2026-07-24" },
    { "url": "https://www.phonearena.com/news/after-installing-android-17-some-pixels-lose-5g_id181265", "date": "2026-07-24" }
  ],
  "layer": "modem_fw",
  "mechanism": {
    "text": "無線プロファイルの破損（\"scrambled cellular radio profiles\"）によるものと Android Authority が推定。eUICC/無線プロファイル層の問題。",
    "confidence": "inferred"
  }
}
```
