# ビルド番号辞書 判断ログ

## Agent 2（Build Collector, 2026-07-30）

### 取得（タスク1）
- 4URLすべて取得成功。`data/raw/2026-07-30/` に保存。FETCH-FAILURES.md は不要（最終的な失敗なし）。
  - ota.html 655,832 bytes / images.html 1,185,307 bytes / pixel-bulletin.html 330,485 bytes / pixel-update-help.html 1,458,771 bytes
- **ota / images はライセンス同意壁**: 素の取得ではビルドテーブルが含まれない（Acknowledge ボタンのみ、約70KB）。
  Cookie `devsite_wall_acks=nexus-ota-tos` / `nexus-image-tos` を付与して再取得し、フルテーブル入りHTMLを保存した。
- **pixel-bulletin は OAuth リダイレクトループ**: cookie なしで `-L` 追従すると accounts.google.com の
  silent sign-in（prompt=none）で50回リダイレクト上限に到達。リトライ時に cookie jar（-c/-b）を付けて解消（final=200, redirects=4）。
- 検証: 各ファイルの `<title>` と実コンテンツ（ビルドID・bulletin表・サポートポリシー本文）を確認済み。

### パース方針（タスク2）
- パーサ正本: `scripts/parse_builds.py`（再実行で `docs/dict/data/builds.json` を再生成可能）。
- **スコープ**: Android 16 世代以降（2025-06〜2026-07）。プレフィックス BP2A/BP3A/BP4A/CP1A/CP2A（メインライン）
  ＋ BD1A/BD3A/BD6A（Pixel 10 系ローンチのデバイス専用列）。ota ページ全体は490ユニークID（2017年〜）あるが、
  旧世代は track/security_patch の根拠が薄く誤情報混入リスクが高いため今回の初期投入から除外した。
- **構造**: devsite ページは `<h2 id="コードネーム">` 区切り＋ `<td>VERSION (BUILD_ID, Mon YYYY[, REGION])</td>` 行。
  ota と images の両方をパースし devices を統合。
- **os**: version 列（16.0.0/17.0.0）から "Android 16/17"。アンカー指定ビルドは QPR 呼称（Android 16 QPR1/QPR2）を優先。
- **track 判定規則**: 各プレフィックスの初月＝リリース（OSメジャー更新なら stable、それ以外は qpr）、以降の月＝monthly。
  アンカー確定値（BP2A.2506=stable、BP3A.2509=QPR1、BP4A.2512=QPR2、CP2A.2606=A17 stable、CP2A.2607=monthly）に整合。
  - CP1A（2026-03〜05, 16.0.0）は系列位置から QPR 第3弾と推定し 2026-03 を qpr、以降 monthly とした。
    ただし4ソースに「QPR3」の呼称は存在しないため os は "Android 16" のまま（QPR3 とは記載しない）。
  - **track=drop は未使用**: support ページに "Pixel Drops" の言及はあるが、どのビルドが Feature Drop かを
    4ソースから特定できない。QPR リリースは qpr で統一（アンカー指定に一致）。
- **release_date**: アンカーは確定日（YYYY-MM-DD）、その他はソースの月精度（YYYY-MM）。
  bulletin 公開日と各アンカー日付の一致を確認: 2026-07-07 / 2026-06-16 / 2025-12-02 / 2025-09-03 は bulletin 公開日と完全一致。
  BP2A.250705.008（2025-07-08）と BP2A.250605.031.A2（2025-06-10）は bulletin 公開日（07-07 / 06-04）と別日だが、
  bulletin 公開日 ≠ OTA 配信日のため矛盾とはしない。
- **security_patch**: pixel-bulletin の月次表（YYYY-MM-05）をビルドの掲載月にマッピング。
- **official_fixes**: 4ソースのいずれも機能修正（非セキュリティ）の列挙を持たないため全件空配列。
  補完は別ソース（リリースノート等）担当の後続エージェントに委ねる。
- **verify_state**: entries.json の値域（VERIFIED/UNVERIFIED）に合わせた。アンカー確定値ビルド＋anti-rollback 指定ビルド
  ＝VERIFIED（16件）、それ以外は track・release_date に推定を含むため UNVERIFIED（50件）。
- **parent_build_id**: サフィックス `.[A-Z][0-9]` を持つものは変異版としてベースIDを設定。
  注意: BP2A.250605.031（ベース）自体は ota/images に掲載がない（.A2/.A3/.A5 のみ出荷）。
  parent_build_id は名目上のベースIDとして記載しており、ベースの単独レコードは作っていない。

### アンカー照合結果（タスク3）
- CP2A.260605.012 変異版: ソースで .A1=AT&T（bluejay/oriole/raven）、.B1=Australia、.C1=Rogers（Pixel 9/10系）
  → オーナー確定値（AT&T / AU / Rogers）と**完全一致**。
- BP4A.251205.006 変異版: .A1=EMEA、.C1=Japan、.B1=VZW（tegu=Pixel 9a のみ）→ 確定値（EMEA/日本/Verizon Pixel 9a）と一致
  （VZW=Verizon の表記揺れは同義扱い）。ソースには追加変異版 .A4(EMEA)/.B3(Verizon)/.C2(Japan)/.E1 も存在し、レコード化した。
- **食い違い1件（human_review:true）**: BP2A.250705.008.A1 — オーナー確定値は「BP2A.250705.008 の変異版」
  （release_date 2025-07-08 系）だが、ソース（bluejay）では掲載月が **Aug 2025**。
  release_date=2025-07-08（アンカー値）を保持しつつ `release_date_source_month: "2025-08"` で両方残した。
  security_patch はソース掲載月準拠で 2025-08-05。
- CP2A.260705.006.A1 の region はデバイスにより異なる（Pixel 9/10系=Rogers、Pixel 6系=Australia）。
  ソース内部の実態であり矛盾ではないため region_scope="Australia; Rogers" として併記（human_review なし）。
- CP2A.260705.006 の「security修正なし」: 2026-07 の Pixel bulletin 自体は存在する（patch level 2026-07-05）ため、
  指示どおり security_patch=2026-07-05 を採用。official_fixes は空（ソースに列挙なし）。

### anti-rollback（最重要フラグ）
- Pixel 10 系の 2026年5月更新 = **CP1A.260505.005**（＋変異版 .A1=Telia）とソースから特定
  （frankel/mustang/blazer/rango/stallion の May 2026 行に掲載）。両ビルドに anti_rollback.incremented=true と指定文言を設定。
  パースで取得できたため human_review は不要。
- 注記: 当該ビルド自体の version 列は 16.0.0（Android 16）。指定文言の「Android 16ビルドへの巻き戻し不可」は
  「カウンタ増加以前の（古い）ビルドへの巻き戻し不可」の意で解釈し、note 末尾に対象デバイスとソース上の掲載実態を補記した。
- ソース上 CP1A.260505.005 は全デバイス共通掲載だが、anti-rollback カウンタ増加の影響が確認されているのは
  Pixel 10 系ブートローダー。他デバイスへの波及有無は4ソースからは判定不能（note に明記）。

### デバイスコードネーム（ソースで確認）
- Pixel 10 系: stallion=10a / rango=10 Pro Fold / blazer=10 Pro / frankel=10 / mustang=10 Pro XL
- 既知系はソースと一致: tegu=9a, comet=9 Pro Fold, caiman=9 Pro, komodo=9 Pro XL, tokay=9, akita=8a,
  husky=8 Pro, shiba=8, felix=Fold, tangorpro=Tablet, lynx=7a, cheetah=7 Pro, panther=7, bluejay=6a, oriole=6, raven=6 Pro

## Agent 3（Issue Curator, 2026-07-30）

### 適用範囲
- entries.json 既存37件: 全件に `evidence_level` を追記。12件に `build_link` を追記（PXD-0001〜0010, 0035, 0036）。既存キー・値の変更ゼロ（バックアップとの機械照合で diff 0 を確認）。
- 新規7件: PXD-0038〜0044 を配列末尾に追加。

### build_link 省略の方針
- schema-proposal.md には「紐付け不能時の表現」の明示規定なし（anti_rollback の「省略=unknown」規定は builds.json 側のみ）→ 指示どおり **「省略 = unknown 扱い」** を採用。null 入りのプレースホルダ形は採用しない（proposal はサブキー optional を明記しており、省略の方が既存スタイルと整合）。
- 省略25件の内訳: Android 11〜15 起因（PXD-0011〜0023 の OS 依存分）= builds.json に A11〜A15 のビルドが存在しないため参照不能。ハードウェア/仕様起因（affected_os 空の12件: PXD-0024〜0034, 0037）= ビルドに紐付かない事象。PXD-0030 は 2024-03 更新で修正だが該当ビルドが builds.json に無いため fixed_in を立てられず省略。

### 紐付けと confidence の根拠
- Android 17 初出（PXD-0001〜0005, 新規全件）: A17 初期 stable = CP2A.260605.012（2026-06-16）。報道は「Android 17 初期版」とのみ言い、ビルド番号を名指ししないため confidence=inferred（出典が初期版と明言する既存5件）/ estimated（出典なし・時期からの推定である PXD-0005 と新規7件）。
- Android 16 初出（PXD-0006〜0010）: A16 初期 stable ベース BP2A.250605.031 は builds.json 未収載（.A2/.A3/.A5 のみ出荷、Agent 2 記録）→ 実在する最初期の BP2A.250605.031.A2（2025-06-10）を採用。inferred（PXD-0010 のみ一次ソース未確認のため estimated）。
- PXD-0035/0036（2026-03 発生）: 2026-03 の A16 ビルド = CP1A.260305.018 を first_seen（inferred）。still_open_as_of=CP1A.260505.005（PXD-0035 は「2026年5月更新でも未修正」と本文明記、PXD-0036 は「統一パッチなし」かつ 3〜5月更新自体が発生窓）。
- **still_open_as_of を保守的に限定**: PXD-0006〜0009 は fix_status=open だが、mechanism/出典に「QPR3 Beta 2 で修正対象」の記述があり、最新 A16 stable 時点での継続を機械的に断定できない → still_open_as_of は付けず first_seen のみ。A17 の PXD-0001〜0003 は「7月更新の公式修正4項目（先行エージェント確定）に含まれない」+ last_checked(07-24) が 7月ビルド(07-07)より後 + 未修正の追加報告あり → still_open_as_of=CP2A.260705.006 を付与。
- fixed_in と still_open_as_of の排他は全件遵守（機械検証済み）。

### 7月更新（CP2A.260705.006）公式修正4項目の割当
- 再起動ループ → **既存 PXD-0004** に fixed_in{CP2A.260705.006, official}。既存 fix_status=open は改変禁止のため据え置き（build_link 側が新しい情報を持つ。次回人間承認更新で patched への変更を推奨）。A16 の月例更新起因ブートループ PXD-0036 とは別事象（OS・発生窓が異なる）のため PXD-0036 には立てない。
- アプリ起動失敗・強制終了 → 既存 PXD-0005 は「起動遅延」で症状が異なる（遅延≠失敗/強制終了）→ **新規 PXD-0038**。
- システムウィジェットの色・コントラスト異常 → 既存 PXD-0019 は Android 12 期の表示崩れで別事象 → **新規 PXD-0039**。
- Pixel 10 Pro Fold ナビボタン位置ずれ → 該当既存なし → **新規 PXD-0040**（affected_models=["10profold"]）。
- 修正3新規（0038〜0040）は fix_status=patched。リポジトリ内に 7月修正の出典URLが存在しない（Agent 2 記録: official_fixes はソースに列挙なし）ため sources=[]、既存の不変条件「sources 空 ⇔ UNVERIFIED」に従い verify_state=UNVERIFIED、evidence_level=REPORTED_ONLY。fixed_in.confidence=official は先行エージェント確定事項に基づく（evidence_level と confidence の役割は別: 前者はエントリの sources 品質、後者はビルド紐付けの根拠強度）。

### タスク2（A17 未修正報告5項目）の重複判定
- **タッチ無反応/ジェスチャー反転 → 新規エントリを作らず既存 PXD-0001 への追記で対応**。PXD-0001 は既に Android 17・6a〜10a・スワイプ反転/無反応を扱う同一事象（VERIFIED・出典3件）であり、複製エントリはデータ汚染になるため。still_open_as_of=CP2A.260705.006 で「7月更新後も未修正」を表現。**未反映情報**: 新報告の回避策「スムーズディスプレイOFF→ON」は既存 workaround 配列に無いが、既存値の改変禁止のため追加せず（research-2026-07.md 6行目に Smooth Display 無効化の記載あり。次回人間承認更新で追加を推奨）。なお指示の「影響: Pixel 6a〜10」は本辞書の対象機種トークン（a系+fold系）に合わせ 6a〜10a と解釈。
- Wi-Fi切断ループ（20〜30秒周期）→ PXD-0003（仕事用プロファイル限定）とも PXD-0006（A16）とも条件・OSが異なる → **新規 PXD-0041**。cause に「原因未確定」を明記、IPv6 回避策に「暫定対処・自己責任」を付記。
- 着信不可 → 既存に該当なし（音・通話は PXD-0022 のみ）→ **新規 PXD-0042**。
- ウィジェット消失・再配置不可 → PXD-0019（A12・表示崩れ）とも PXD-0039（色異常・修正済）とも別 → **新規 PXD-0043**。
- ゲーム動作不安定 → 該当なし → **新規 PXD-0044**。
- 新規5項目のうち回避策未確定のもの（0041〜0044）は workaround に「暫定対処・自己責任」を明記。全件 verify_state=UNVERIFIED・sources=[]・evidence_level=REPORTED_ONLY・still_open_as_of=CP2A.260705.006（0041〜0044）。first_seen は報告集約時期から 2026-07（トップレベル値、推定）。IssueTracker の具体URLは手元になくURL捏造を避けるため sources には入れず symptom 中の言及に留めた（PXD-0042）。

### evidence_level の判定基準と個別判断
- 規則: Google/Android 公式ドメインのソースあり=OFFICIAL / 独立した複数ソース=MULTI_SOURCE / 単一ソースまたは sources 空=REPORTED_ONLY。
- OFFICIAL 5件: PXD-0008, 0023, 0031（support.google.com）、PXD-0016（developer.android.com）、**PXD-0015（docs.flutter.dev）— flutter.dev は Google 公式プロダクトドメインと判断して OFFICIAL 扱い**（異論余地あり・要レビュー）。
- **PXD-0034 は出典2件だが両方 xdaforums.com（同一サイトの別スレッド）で独立性なし → REPORTED_ONLY**。
- PXD-0001 は 9to5google×2 + androidcentral = 独立2媒体 → MULTI_SOURCE。
- 集計: OFFICIAL 5 / MULTI_SOURCE 17 / REPORTED_ONLY 22（新規7件含む全44件）。

### 検証結果（機械照合）
- python3 -m json.tool: valid。行数 1383 → 1764（非減少）。
- バックアップ（スクラッチ領域 entries.backup.json、リポジトリ外）との照合: 既存37件の全既存キー・値の diff = 0、ID順序維持、追加キーは build_link / evidence_level のみ。
- build_link 内の全 build_id（CP2A.260605.012 / CP2A.260705.006 / BP2A.250605.031.A2 / CP1A.260305.018 / CP1A.260505.005）は builds.json に実在することを機械確認。
- 新規7件は必須16キー完備・category/severity/fix_status/affected_models が既存値域内・yomi ひらがなのみ、を機械確認。

## Agent 4（Renderer: docs/dict/index.html への「ビルド番号で引く」UI追加, 2026-07-30）

### 既存コードとの共存方針
- 変更は **追記のみ3箇所**（head 末尾に bx 専用 `<style>` ブロック / `</main>` と `<footer>` の間に `#bx-section` / 既存 `</script>` の後に bx 専用 `<script>`）。既存の style・HTML・IIFE には1文字も触れていない。diff は挿入4ハンクのみ・削除0行（機械確認済み）。441行 → 727行（+286、行数非減少）。
- 名前空間: 新規の ID/class/関数はすべて `bx-` / `bx` 接頭辞（bx-section, bx-input, bx-build, bx-result, bxClassify 等）。既存IDとの衝突なし。JSは独立IIFEで、既存IIFEの内部関数（esc/render/init等）とはスコープも分離。
- fetch は bx 側で entries.json + builds.json を **独自に Promise.all で取得**（既存 fetch の流用は既存 init への介入になるため不採用）。同一URLなのでHTTPキャッシュで実質二重取得コストは無視できる。
- 表示スタイルは既存トーン踏襲（CSS変数 --sage-deep/--alert 等・IBM Plex Mono・カード様式）。severity バッジのみ既存 class（tag sev-t-*）を「参照」して再利用（既存ルールの変更ではない）。
- エントリ表示は「id + title_ja + severity + confidence/evidence_level バッジ + 判定理由」。既存カードは `id` 属性を持たない（既存 card() を変更しない制約のため）ので、アンカーリンクではなく仕様許容のフォールバック（最低限表示）を採用。

### 3分類ロジックと時系列比較の扱い
- 比較軸は builds.json の release_date。**"YYYY-MM" と "YYYY-MM-DD" が混在**（52件/14件）するため bxCmpDate は「月が異なれば月で比較 → 同月で両方に日があれば日で比較 → 同月で日が欠ける場合は null（比較不能）」を返す。
- **① 修正済み**: fixed_in.build_id が入力と完全一致（大文字化して比較）、または fixed_in ビルドの release_date が入力ビルドより**厳密に前**（cmp = -1）の場合のみ。同日（cmp = 0）・比較不能（null）・入力未収載は①に入れない = 安全側。
- **② 未修正**: (a) fixed_in が入力より新しい、(b) still_open_as_of が入力と一致 or 入力以降、(c) still_open_as_of が入力より前（以降の状況未確認）、(d) fixed_in/still_open との比較根拠なし、(e) build_link はあるが first_seen のみで修正記録なし——(c)(d)(e) はいずれも**安全側で②に倒す**（「修正済み」と誤答して回避策を捨てさせるより「未修正扱い」の方が実害が小さい）。理由文を各行に明示し、機械的判定と安全側判定を区別できるようにした。
- first_seen のみの entry で、入力ビルドが first_seen より前の場合は「このビルドでは未発生の可能性あり」を注記（分類は②のまま。発生前判定を独立バケットにするのは仕様の3分類を崩すため不採用）。
- **③ 不明**: build_link 省略のもののみ（現データで25件）。③件数は「不明 N件（44件中）」形式で常時表示、①②も件数表示。①+②+③ = 全件を smoke test で保証。
- 未収載ビルド入力時は「辞書未収載のビルド」と明示し、時系列比較なし・文字列完全一致のみで判定（①は fixed_in 文字列一致のみ）。前方一致候補をボタン表示（クリックで完全一致検索に切替 = 完全一致優先）。大文字小文字ゆらぎは入力を大文字化して吸収。
- ARB: anti_rollback.incremented=true のビルドは「⚠ これ以前のAndroid 16へ戻せません」+ note を赤枠で常時表示（トグル等に隠さない）。incremented=false は「増加なし」、キー省略は「記載なし」と区別表示。

### 検証結果
- npx html-validate docs/dict/index.html: PASS。
- diff（オリジナルをスクラッチ領域に退避して照合）: 削除0・変更0・挿入4ハンクのみ → 既存JS関数・イベントリスナ・DOM ID 無変更。
- node smoke（実HTMLから bx スクリプトを抽出し、DOMスタブ + 実JSONで実行）: 18アサーション全PASS。代表値: CP2A.260705.006 → ①4/②15/③25、CP1A.260505.005（ARB） → ①0/②19/③25 + ARB警告表示、未収載ID → ①0/②19/③25、小文字入力・前方一致・空入力クリアも確認。
- python3 -m http.server + curl: index.html / entries.json / builds.json すべて 200。
- entries.json / builds.json / docs/index.html は無変更。git commit/push なし（指示どおり）。

## Agent 5（Verifier & Shipper, 2026-07-30）

### 契約テスト（tests/test_contract.py, 標準ライブラリのみ）
- 14項目: builds 必須9キー / track 値域（stable|qpr|monthly|drop = schema-proposal.md 準拠。drop は現データ未使用だが値域として許容）/ verify_state 値域 / build_id 正規表現 / build_id ユニーク / entries 44件 / 必須16キー / evidence_level 値域 / build_link.confidence 値域 / 参照整合 / 行数非減少3件 / ソート順。全 PASS。
- **build_id 正規表現**: `^[A-Z]{2}[0-9A-Z]{2}\.[0-9]{6}\.[0-9]{3}(\.[A-Z][0-9])?$` に全66件一致（不一致0件）。2桁サフィックス（.A11 等）の変異版は現データに存在せず、正規表現の変更・人間確認は不要。将来2桁版が出現したらテストが FAIL で検知する（データ改変はしない設計）。
- **build_link.confidence の階層**: schema-proposal.md 1.1 のとおり confidence は first_seen / fixed_in の object 内にネスト。still_open_as_of は string 形（confidence なし）も valid としてテストした。
- **ソート順**: builds.json には既存規則あり = **build_id ASC**（parse_builds.py L322 の `builds.sort(key=build_id)`）。全66件がこの順で並んでいることを機械確認したため、release_date DESC への再ソートは行わず既存規則をテストで固定した。release_date は "YYYY-MM" と "YYYY-MM-DD" の混在で日付ソートは粒度曖昧になるのに対し、build_id ASC は決定的・冪等で、ID内の日付部（250702等）により概ね時系列にもなる。parse_builds.py に既にソートがあるため冪等性も確保済み（再生成して byte-diff ゼロを確認）。
- 行数基準値: entries.json ≥1764 / builds.json ≥1860 / index.html ≥727 をテスト内に定数化。

### 鮮度監視（新規実装）
- このリポジトリには verify_sources_alive.py / decay_warning.py は元々存在しない。他リポの同名スクリプトの思想（ソースURL失効検出・収集停止の腐敗検知）を踏襲した**本リポ向け新規実装**として scripts/ に作成した。
- verify_sources_alive.py: builds+entries の sources からユニーク57 URL を抽出（entries 側は {url,date} object 形に対応）。HEAD→GET フォールバック、UA・timeout 15s・間隔0.5s。401/403 は同意壁/bot対策の可能性があるため WARN（生存扱い）。
- **初回実行結果: ok=41 / warn=12 / dead=4**。死リンク: support.google.com の answer 2件 + thread 1件（404。ブラウザでは生きている可能性もあるが curl では404）、wiki.rossmanngroup.com（DNS 解決不能）。リンク死活は push ゲート対象外（監視ツールであり、データ修正は別エージェントの担当）。次回データ更新時に sources 差し替えを検討。
- decay_warning.py: builds.json の generated_at（フォールバック: data/raw/ 最新日付ディレクトリ）から days_since を計算、30日以上で警告+exit 1。docs/dict/data/status.json（last_collected/days_since/stale）を常時出力。日付はローカル日付基準・TZ揺れの負値は0に丸め。今回実行: last_collected=2026-07-30, days_since=0, stale=false。
- **ページバナー**: index.html の bx 名前空間内に #bx-stale（既定 hidden）を追加。status.json fetch（404/不正 JSON は catch して無視 = 既存機能非干渉）と、既存 Promise.all が取得済みの builds.json generated_at からのクライアント側30日判定の**二重化**。既存ロジックへの変更は Promise.all の then 内に判定2行を足したのみ（bx ブロック内・削除0行）。html-validate PASS、727→751行。

### parse_builds.py の小改修
- RAW ディレクトリ固定（2026-07-30）を「argv[1] 指定 or data/raw/ 最新日付ディレクトリ」に変更し、generated_at をそのディレクトリ名から取るようにした（月次自動収集の前提整備）。現行データで再生成し **byte-diff ゼロ**を確認（冪等・出力不変）。

### 月次収集（launchd）
- scripts/monthly_collect.sh: set -euo pipefail。4ソース取得（ota/images は devsite_wall_acks cookie、bulletin は cookie jar = Agent 2 の取得手順を踏襲）→ サイズ・ビルドID存在の縮退チェック → parse → 契約テスト → decay_warning。ログは data/logs/monthly-collect-YYYY-MM-DD.log に常時保存、失敗時非0。**git 操作なし**（commit/push は人間ゲート経由）。
- pixel-update-help の取得URL は support.google.com/pixelphone/answer/4457705?hl=en（保存済みスナップショットの `<title>` と docs/index.html 内カードリンクから同定）。
- launchd/com.taka.pixel-builds-monthly.plist: StartCalendarInterval Day=10 Hour=3 Minute=0。ProgramArguments は `/bin/bash -c 'exec "$HOME/..."'` で **$HOME を bash に展開させ、個人の絶対パスを plist に埋め込まない**。launchd は StandardOutPath 等の環境変数を展開しないため、そこは /tmp/com.taka.pixel-builds-monthly.{out,err}.log 固定（詳細ログは script 側で data/logs/ に残るため /tmp 側は起動失敗時の diagnostics 用）。plutil -lint OK。**設置（cp / launchctl bootstrap）は未実行**（人間が実行）。
- data/logs/ を .gitignore に追加（実行ログはリポジトリに含めない）。

### 出荷判断
- data/raw/2026-07-30/ は合計 4.5MB（<10MB）のため **gzip 圧縮せず素の .html のまま commit**（一次資産・再現性最優先。10MB 超過時に圧縮検討のルールは維持）。
- forbidden terms スキャン: 新規・変更ファイル全て + data/raw/ 生HTML（自分の個人情報のみ）に対し実名/メール/ホーム絶対パス/APIキーpatternの検索でヒット0件を確認してから push。
