# スキーマ拡張提案: build_link 追記 & builds.json 新設

- 作成日: 2026-07-30
- 前提: **既存キー名は一切変更しない。追記のみ。** 既存 37 件のレコードは追加フィールドなしでも valid のまま（全追加フィールドは optional）。
- 根拠となる現行スキーマ調査: `docs/schema-current.md`

## 0. 命名整合性チェック（結論）

| 観点 | 実データの規則 | 提案での採用 |
|---|---|---|
| キー命名 | **snake_case のみ**（camelCase ゼロ） | 全追加キーを snake_case とする（`build_link`, `first_seen`, `release_date`, `security_patch`, `parent_build_id`, `anti_rollback`, `official_fixes`, `region_scope`） |
| 状態値（severity, fix_status, layer, mechanism.confidence） | 小文字 | `track`, `confidence` の値は小文字（`stable`, `official` 等） |
| `verify_state` の値 | **大文字**（`VERIFIED` / `UNVERIFIED`） | `evidence_level` と builds.json の `verify_state` も大文字値で統一 |
| 日付 | 文字列 `YYYY-MM-DD`（発生時期のみ `YYYY[-MM]` 可変粒度） | `release_date` は `YYYY-MM-DD`、`security_patch` は `YYYY-MM-DD`（Android のセキュリティパッチレベル表記に一致） |
| 配列キー | 複数形（`affected_models`, `sources`） | `devices`, `official_fixes`, `sources` も複数形で整合 |

## 1. 不具合レコード（entries.json）への追記フィールド

### 1.1 `build_link`（optional, object）

```json
"build_link": {
  "first_seen": { "build_id": "BP2A.250705.008", "confidence": "official" },
  "fixed_in":   { "build_id": "BP2A.250805.005", "confidence": "inferred" },
  "still_open_as_of": "BP2A.250805.005"
}
```

- `first_seen` / `fixed_in` / `still_open_as_of` はいずれも optional。`fixed_in` と `still_open_as_of` は排他（両方あるのはデータ不整合）。
- `confidence` 値域: `official` | `inferred` | `estimated` | `unknown`（小文字、指定どおり）。
- **既存トップレベル `first_seen`（"2026-06" 等の時期文字列）とはキーが同名だが階層が違うため衝突しない**。JSON 的に問題なし。ただし読み手の混同リスクがあるので §「判断ログ」参照。既存 `first_seen` はそのまま変更しない。
- `build_id` の値は builds.json の `build_id` への外部キー。

### 1.2 `evidence_level`（optional, string）

- 値域: `OFFICIAL` | `MULTI_SOURCE` | `REPORTED_ONLY`（大文字 — 既存 `verify_state` の VERIFIED/UNVERIFIED と同じ大文字流儀）
- **既存 `verify_state` はそのまま残し併設**。互換規則:
  - `verify_state: "VERIFIED"` のレコードは `evidence_level` が `OFFICIAL` または `MULTI_SOURCE` になりうる
  - `verify_state: "UNVERIFIED"` のレコードは `evidence_level: "REPORTED_ONLY"` にのみ対応
  - `evidence_level` 未設定のレコードは従来どおり `verify_state` のみで解釈（後方互換）
- 既存 UI（index.html）は `verify_state` を読み続けられるため互換維持。

## 2. 新規ファイル `docs/dict/data/builds.json`

トップレベルは entries.json と同様に**配列**とする。1要素 = 1ビルド。

```json
[
  {
    "build_id": "BP2A.250805.005",
    "os": "16",
    "track": "monthly",
    "release_date": "2025-08-05",
    "security_patch": "2025-08-05",
    "devices": ["6a", "7a", "8a", "9a"],
    "region_scope": "global",
    "parent_build_id": "BP2A.250705.008",
    "anti_rollback": { "incremented": false, "note": "" },
    "official_fixes": ["PXD-0003"],
    "sources": [
      { "url": "https://source.android.com/docs/setup/reference/build-numbers", "date": "2026-07-30" }
    ],
    "verify_state": "VERIFIED"
  }
]
```

### フィールド仕様

| キー | 型 | 必須 | 規則 |
|---|---|---|---|
| `build_id` | string | 必須 | Google 公式ビルド番号をそのまま（例 `BP2A.250805.005`）。本ファイル内で一意。これが主キー |
| `os` | string | 必須 | 既存 `affected_os` の要素と同じ表記（`"16"` 等の文字列）。数値にしない |
| `track` | string | 必須 | `stable` \| `qpr` \| `monthly` \| `drop`（小文字） |
| `release_date` | string | 必須 | `YYYY-MM-DD` |
| `security_patch` | string | 必須 | `YYYY-MM-DD` |
| `devices` | string[] | 必須 | 既存 `affected_models` と**同一の機種トークン**（`6a`, `fold`, `9profold` 等）を使う。表記の二重管理を作らない |
| `region_scope` | string | 必須 | `global` を既定。キャリア/地域限定ビルドは `jp`, `us_verizon` 等の小文字 snake_case トークン |
| `parent_build_id` | string \| null | 任意 | 直前ビルドの `build_id`。系譜の先頭は `null` |
| `anti_rollback` | object | 任意 | `{ "incremented": boolean, "note": string }`。不明なら省略（省略 = unknown） |
| `official_fixes` | string[] | 必須（空配列可） | このビルドで公式修正が明言された不具合の `PXD-xxxx` ID 配列 |
| `sources` | object[] | 必須（空配列可） | **entries.json と同形** `{ "url", "date" }` |
| `verify_state` | string | 必須 | **既存と同じ値域 `VERIFIED` / `UNVERIFIED` を採用**（下記） |

### builds.json の `verify_state` を既存と同値域にする判断

**同じ値域（`VERIFIED` | `UNVERIFIED`）を採用する。** 理由:

1. 既存 entries.json では「`sources` 空配列 ⇔ `UNVERIFIED`」という暗黙規則が全件で成立しており、builds.json も同じ `sources` 形式を持つため同じ規則をそのまま流用できる。
2. UI・検証スクリプトが verify_state の判定ロジックを 1 本で共有できる。
3. 証拠の質の段階表現は `evidence_level`（OFFICIAL/MULTI_SOURCE/REPORTED_ONLY）側の役割であり、verify_state に第3の値を足すと責務が重複する。builds.json に将来 evidence_level を足す場合も entries 側と同じ値域を使えばよい。

### 衝突リスクの明記

- **entries.json 側**: 追加キー `build_link` / `evidence_level` は既存 19 キーのいずれとも不一致 → トップレベル衝突なし。`build_link.first_seen` はトップレベル `first_seen` と同名だが別階層で、型も異なる（object vs string）。コードで `entry.first_seen` と `entry.build_link.first_seen` を取り違えないよう注意が必要（衝突ではなく混同リスク）。
- **builds.json 側**: 新規ファイルなのでキー衝突は原理上なし。ただし語彙の再利用に注意:
  - `sources` / `verify_state` / `devices`(=affected_models のトークン) / `os`(=affected_os のトークン) は entries.json と**意図的に同形・同値域**（衝突ではなく共有）。
  - `mechanism.confidence`（confirmed/inferred/unknown）と `build_link.confidence`（official/inferred/estimated/unknown）は**同名キーで値域が異なる**。既存の `confirmed` を build_link 側で使わない・`official` を mechanism 側で使わないこと。バリデータは親キーで値域を切り替える必要がある。
  - `anti_rollback.note` は自由文。空でも `""` を許容（例示に合わせる）が、省略も可。

## 3. 後続エージェントがそのまま使う最終命名（確定）

entries.json 追記（全て optional・既存キー変更ゼロ）:

```
build_link: {
  first_seen: { build_id: string, confidence: "official"|"inferred"|"estimated"|"unknown" },
  fixed_in:   { build_id: string, confidence: "official"|"inferred"|"estimated"|"unknown" },
  still_open_as_of: string   // build_id
}
evidence_level: "OFFICIAL" | "MULTI_SOURCE" | "REPORTED_ONLY"
```

docs/dict/data/builds.json（トップレベル配列）:

```
{
  build_id: string,                  // 主キー、Google公式ビルド番号
  os: string,                        // "16" 等、affected_os と同表記
  track: "stable"|"qpr"|"monthly"|"drop",
  release_date: "YYYY-MM-DD",
  security_patch: "YYYY-MM-DD",
  devices: string[],                 // affected_models と同一トークン
  region_scope: string,              // 既定 "global"
  parent_build_id: string|null,
  anti_rollback: { incremented: boolean, note: string },   // optional
  official_fixes: string[],          // PXD-xxxx の配列
  sources: [ { url: string, date: "YYYY-MM-DD" } ],
  verify_state: "VERIFIED"|"UNVERIFIED"
}
```

## 判断ログ

1. **`build_link.first_seen` の同名問題** — 指示された仕様どおり `first_seen` を採用した。トップレベルの既存 `first_seen`（時期文字列）と別階層なので JSON 衝突はないが、混同リスクがあるため `first_seen_build` 等への改名も検討した。しかし仕様に `build_link: { first_seen: {...} }` と明記されており、既存キー変更禁止の原則は「既存を壊さない」ことであって新規キーの命名指定を覆す理由にならないため、指定どおりとした。混同リスクは本書 §2 衝突リスク節に明記して対処。
2. **`evidence_level` の値を大文字にした根拠** — 指示に OFFICIAL|MULTI_SOURCE|REPORTED_ONLY と大文字で書かれており、かつ既存で唯一の「検証状態系」キーである `verify_state` が大文字値（VERIFIED/UNVERIFIED）を使っているため、検証・証拠系は大文字、分類・状態系（severity/fix_status/track/confidence）は小文字、という既存の使い分けに沿う。
3. **builds.json のトップレベルを配列にした** — 指示は `{ build_id, ... }` とレコード形のみ指定しファイル全体の形は未指定。entries.json がトップレベル配列であり、読み込みコード（fetch → 配列走査）を揃えるため配列とした。build_id をキーにしたオブジェクトマップ案は、既存との非対称性と sources 等の並び保証の弱さから不採用。
4. **`os` を文字列にした** — 数値の方が比較は楽だが、既存 `affected_os` が `"17"` と文字列であり、entries と builds を突き合わせるコードで型変換を挟まないため文字列に統一。
5. **`devices` のトークン** — フル機種名（"Pixel 8a"）ではなく既存 `affected_models` の短縮トークン（"8a"）を採用。entries とのクロス参照が文字列一致で済む。
6. **`anti_rollback` を optional にした** — anti-rollback counter の増分有無は公式に公表されないことが多く、`incremented: false` と「不明」を区別する必要がある。必須にすると不明時に false を書く捏造圧が生じるため、省略 = unknown とした。
7. **`still_open_as_of` の型** — 指示どおり build_id 文字列の単値。`{ build_id, confidence }` 形に揃える案もあったが、「そのビルド時点でまだ open」という観測記録は confidence を持たせるほどの推定を含まない（確認したか否かだけ）ため、指定どおり単値とした。
8. **`fixed_in` と `still_open_as_of` の排他** — 仕様に明記はないが論理的に両立しないため、バリデーション規則として本書に明記した（スキーマ構造では強制しない）。
9. **verify_state の値域拡張はしない** — builds.json でも VERIFIED/UNVERIFIED の2値のまま。第3の値（例: PARTIAL）追加は既存 UI の分岐を壊すリスクがあり、証拠段階は evidence_level に責務分離できるため不要と判断。
