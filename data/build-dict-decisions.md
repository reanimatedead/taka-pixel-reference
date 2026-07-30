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

## Agent 2 (2nd iteration: Suffix Auditor)

（2026-07-30。scripts/parse_builds.py のサフィックス→地域/キャリア導出の監査・是正）

### 固定辞書だったか: NO
- 旧実装に「suffix→region のグローバル1次元固定辞書」は**存在しなかった**。region_scope はソースHTML（data/raw/2026-07-30/{ota,images}.html）の変異版キャリア注記 `<td>VERSION (BUILD_ID, Mon YYYY, REGION)</td>` を parse_device_tables が直接パースして導出していた（廃止対象なし）。
- ただし旧実装には2つの欠陥があった:
  1. **注記のトークン未分割**: 注記全体を1文字列として集合に入れていたため、images.html の tegu 行にあるソース側重複 `(BP4A.251205.006.C1, Dec 2025, Japan, Japan)` が `"Japan; Japan, Japan"` として出力されていた。
  2. **表記ゆれの未正規化**: VZW/Verizon、JP/Japan、Softbank/SoftBank が混在。

### 注記直接パースは可能か: YES（これを正とした）
- スコープ内66件のうち変異版の地域/キャリアは全て生HTML注記に存在（ota.html と images.html の両方に同一注記があることを32パターン全てで grep 確認）。
- 新実装: 注記直接パースが引き続き正。注記を "," でトークン分割→ REGION_NORMALIZE で正規化→集合で重複排除。
- 補完用に **SUFFIX_MONTH_MAP（base month × suffix の二次元テーブル、32エントリ）** を追加。key=(build_id 埋め込み日付由来の "YYYY-MM", suffix)、value={region, source}。source には生HTMLスナップショット内の該当注記原文と公式URLを記録。**注記が無い変異版のみ**のフォールバックで、現データでは1件も発動しない（発動時は region_scope_source フィールドに根拠を記録する設計）。
- 固定辞書が誤りである根拠（同一サフィックスの意味が月で変わる実例、全て生HTML注記由来）: .C1: 2025-12=Japan / 2026-02=Japan / 2026-06=Rogers。.A1: 2025-12=EMEA / 2026-05=Telia / 2026-06=AT&T / 2026-07=Rogers（2026-07はデバイスにより Australia 併記）。

### region_scope 正規化ルール
1. キャリア名は正式表記: VZW→Verizon、Softbank→SoftBank
2. 国は英語国名（ISO2レター略記禁止）: JP→Japan、AU→Australia
3. 略記の展開: NA GStore→North America (Google Store)
4. 複数対象は正規化トークンをソートし "; " 区切り
5. ソース側の同一トークン重複（"Japan, Japan"）は集合化で排除

### 訂正一覧（7件、全66件を生HTML注記と突き合わせ済み）
| build_id | before | after |
|---|---|---|
| BD3A.250721.001.A1 | NA GStore | North America (Google Store) |
| BD3A.251105.010.F1 | Japan carriers except Softbank | Japan carriers except SoftBank |
| BD3A.251105.010.J3 | Softbank | SoftBank |
| BP4A.251205.006.B1 | VZW | Verizon |
| BP4A.251205.006.C1 | Japan; Japan, Japan | Japan |
| BP4A.260205.001.B1 | VZW | Verizon |
| BP4A.260205.001.C1 | JP | Japan |

### 検証
- 再生成前後の機械 diff: **region_scope 以外の差分ゼロ**（66件・全フィールド比較をスクリプトで確認）。件数66維持・valid JSON。
- 冪等性: parse_builds.py を2回再実行し SHA-256 同一（byte-diff ゼロ）。
- tests/test_suffix_map.py 新規作成（23項目 PASS）: 二次元テーブルの既知確定値7組、「固定辞書なら FAIL する」月間不等式アサート（map側+データ側）、全エントリの出典存在、builds.json 実データ照合、正規化残渣ゼロ。
- tests/test_contract.py: 14/14 PASS 維持。
- 非改変の確認: entries.json / index.html は未変更（git status で機械確認）。

## Agent 1 (2nd iteration: ARB Historian)

日付: 2026-07-30。目的: anti-rollback（ARB）関連の欠落修正。既存値の改変なし（追記・新規フィールド・新規レコードのみ）。

### 1. Android 15 世代 ARB 例外レコード追加（BP1A.250505.005）
- builds.json への直接手書きは再生成で消えるため、scripts/parse_builds.py に **KNOWN_EXTRA_BUILDS**（スコープ外例外収載の注入機構）を新設し、main() 末尾（ソート前）で注入。既存の ANCHORS / ANTI_ROLLBACK_BUILDS 機構は不変。
- ソース根拠（両方確認済み → verify_state=VERIFIED）:
  - data/raw/2026-07-30/images.html 内に警告文が実在（offset 48280 付近）:
    "Special instructions for updating Pixel devices to the May 2025 monthly release / Warning: The May 2025 update for Pixel 6 (6, 6 Pro, 6a) and Pixel 8 (8, 8 Pro, 8a) devices contains a bootloader update that increments the anti-roll back version for the bootloader. ... you won't be able to flash and boot older Android 15 builds."
    → sources に https://developers.google.com/android/images を記録。
  - Android Police 記事の実URLを WebSearch/WebFetch で特定・実在確認:
    https://www.androidpolice.com/may-2025-google-pixel-security-update-anti-rollback-bootloader/
    （公開 2025-05-06 14:27 EDT、build_id BP1A.250505.005 と対象 Pixel 6系/6a/8系/8a を明記）
- security_patch "2025-05-05" は pixel-bulletin.html スナップショットの May 2025 行から parse_bulletin() の結果で再解決（_bulletin_month ヒントキー方式。スナップショットに行が無い場合のみレコード内フォールバック値を使用）。
- os は既存表記に合わせ "Android 15"（タスク指示の "15" は既存表記優先の指示に従い変換）。track=stable はタスク確定値のまま採用。
- devices は sorted 順（akita, bluejay, husky, oriole, raven, shiba）で既存レコードの整列規則に一致させた。

### 2. 既存 ARB 2件（CP1A.260505.005 / .A1）への scope / effect「追記」
- **ARB_EXTRA_FIELDS** を新設し、anti_rollback を {incremented, scope, effect, note} の順で再構成。incremented / note の値は byte 同一（機械照合済み）。
- scope の文言判断: タスク指示は「Pixel 10系機種」だが、images.html の May 2026 警告文は "Pixel 10, 10 Pro, 10 Pro XL and 10 Pro Fold" の4機種のみを列挙し **stallion (10a) を含まない**。既存 note は stallion を含むが note は不変で残し、scope はソース警告文の列挙に従い "Pixel 10, 10 Pro, 10 Pro XL, 10 Pro Fold（frankel/mustang/blazer/rango。ソース警告文の列挙。Pixel 9系以前は非対象）" とした。note との差異は本節を正とする（note は Agent 2 由来の既存値のため改変禁止）。

### 3. 旧世代 ARB 告知の全文検索（タスク2）
- data/raw/2026-07-30/{images,ota}.html を anti-rollback / anti rollback / antirollback / rollback / roll back / downgrad / revert / flash back / older build / previous version で全文検索。
- 結果: **ARB 告知は images.html 内の May 2025（Pixel 6/8系）と May 2026（Pixel 10系）の2件のみ**。ota.html には ARB 告知なし。Android 13 世代等さらに古い ARB 告知は該当なし → 追加レコードなし。
  （"flash back" の1件は "flash back to public" という Flash Tool の一般説明で ARB 無関係）

### 4. UI 強化（docs/dict/index.html、bx- 名前空間のみ）
- bxBuildInfo() の ARB 警告ブロックに追記: scope 表示（「対象機種: …」）+ 固定2文（ダウングレード不可 / A/B 両スロット sideload 注意）。既存の note 表示・bx-arb-warn / bx-arb-note クラスは維持（新規CSSなし）。
- 見出しの判断: 従来の固定文「⚠ これ以前のAndroid 16へ戻せません」は Android 15 世代の BP1A に対して事実誤りになるため、anti_rollback.effect が存在する場合は「⚠ 」+ effect を見出しとし、effect が無いレコードでは従来の固定文にフォールバック。現在 ARB 3件は全て effect を持つため正しい世代が表示される（赤字警告ブロック自体・note 表示は存置）。
- 変更行数: 5行 → 11行（+6行、置換1ブロックのみ）。node --check で inline script 2本とも構文 OK。

### 5. 整備手帳側リンク（docs/index.html — 今回のみ明示許可された追記）
- 追記位置: Lv3「復旧（リカバリー / sideload / Factory Image）」details 内、既存の最終 caveat（ブートローダーアンロック警告、旧 L545）の直後・`</div></details>` の直前に `<p class="caveat">` 1ブロックのみ追加（+1行）。既存内容は無変更。
- 内容: ARB 該当ビルドの1行要約（BP1A.250505.005=Pixel 6/8系・Android 15 / CP1A.260505.005=Pixel 10系・Android 16）+ dict/#bx-section へのリンク（アンカー id="bx-section" の実在を確認済み）。

### 6. テスト基準値の更新
- tests/test_suffix_map.py の「builds.json has 66 records」を **67** に更新（66→67 は BP1A 追加による増加。件数非減少の思想は維持）。tests/test_contract.py は builds 件数固定を持たないため変更不要（行数下限 1860 は 1894 で PASS）。

### 7. 検証結果
- 冪等性: parse_builds.py 2026-07-30 を2回実行し MD5 同一（c9ed3ba6f84f2cbfd1f4eb4c8437f5f4、byte-diff ゼロ）。
- 非破壊の機械照合: 再生成前後の全66件×全フィールド比較で、差分は CP1A.260505.005 / .A1 の anti_rollback への scope/effect 追加のみ（incremented/note は同値）。violations: NONE。
- tests/test_contract.py 14/14 PASS / tests/test_suffix_map.py 23/23 PASS。
- npx html-validate docs/dict/index.html docs/index.html → エラー 0（exit=0）。
- entries.json は未変更。git commit / push は実施していない。

## Agent 3 (2nd iteration: Schema Fixer)

日付: 2026-07-30。スコープ: docs/dict/data/builds.json のスキーマ拡張（base_month / release_date 分離）と human_review 日付矛盾の解決。builds.json は直接手書きせず scripts/parse_builds.py の変更→再生成で実施（冪等性契約を維持）。

### 1. base_month / release_date のスキーマ分離
- 新フィールド `base_month`（"YYYY-MM"）を**全67件**に追加。build_id の日付部6桁（XXXX.YYMMDD.NNN）からの機械導出（`base_month_of()` 既存関数を再利用、`with_base_month()` で release_date の直前に挿入）。機械導出のため全件付与。
- `release_date` の意味を「実際に配信された月（ソース掲載月ベース）」に確定。base_month との食い違いは矛盾ではなく「後月配信」として表現する。
- 分離後の「後月配信」レコード（base_month ≠ release_date 月）は10件: BD1A.250702.001 / BD1A.250702.001.A3 / BD3A.250721.001 / BD3A.250721.001.A1 / BD3A.250721.001.B7 / BD3A.250721.001.E1 / BD3A.250808.001 / BD6A.251031.001.A4 / BP2A.250605.031.A5 / BP2A.250705.008.A1。BP2A.250705.008.A1 以外の9件は元々ソース掲載月がそのまま release_date に入っており値の変更なし（ota.html / images.html の月注記で確認: 例 "(BD6A.251031.001.A4, Mar 2026)", "(BP2A.250605.031.A5, Aug 2025)"）。

### 2. BP2A.250705.008.A1 の human_review 解消
- 旧状態: anchor release_date=2025-07-08 とソース掲載月 2025-08 の食い違いで human_review=true / conflict_note 付き。
- 解決: パーサに `RESOLVED_CONFLICTS` 機構を新設。release_date 起因のアンカー矛盾のみ解決対象（os/track/region の矛盾は従来どおり human_review）。本件は release_date="2025-08"（ソース掲載月: ota/images 両方に "(BP2A.250705.008.A1, Aug 2025)" 注記あり）に確定し、human_review / conflict_note を除去、`resolution_note` に経緯を記録（「base_month/release_date 分離により矛盾でないと判明。…2026-07-30 解決」）。release_date_source_month=2025-08 は既存どおり残置。verify_state=VERIFIED（アンカー由来）は不変。security_patch=2025-08-05（ソース掲載月ベース）も不変。
- アンカー値 2025-07-08 は ANCHORS に不変で残る（照合機構は生きており、将来スナップショットで掲載月が変われば再び矛盾検知される）。
- これで builds.json の human_review は 1件→**0件**。

### 3. BP2A.250605.031.A5（例示された同種案件）の確認
- builds.json に**既存**（KNOWN_EXTRA_BUILDS 追加は不要）。ソース ota/images 両方に "(BP2A.250605.031.A5, Aug 2025)" 注記あり。
- 検証結果: base_month=2025-06 / release_date=2025-08 / security_patch=2025-08-05 / devices=[oriole, raven]（Pixel 6 / 6 Pro）— 指示された期待値と完全一致。値の変更なし。

### 4. タスク2: BD3A 系の収載確認
- **.C1**: 生HTML全ファイル（ota/images/pixel-bulletin/pixel-update-help）を `BD3A\.[0-9]{6}\.[0-9]{3}\.C[0-9]+` で走査 → **出現ゼロ。ソースに存在せず**、追加しない。（.C1 自体は BP4A/CP2A 系にのみ存在: 2025-12/2026-01/2026-02=Japan, 2026-06=Rogers）
- **BD3A.251105.010 親レコード**: `BD3A\.251105\.010[^.]` で走査 → 出現ゼロ。ソースには変異版 .E1/.F1/.J3 のみ掲載（親ビルドは未配信 = 変異版のみ配信）。親は追加しない。parent_build_id="BD3A.251105.010" は変異版の導出フィールドとして残る（実レコードの存在を意味しない）。
- **全走査照合**: `BD3A\.[0-9]{6}\.[0-9]{3}(\.[A-Z][0-9]+)?` で生HTML全走査 → distinct 16件。builds.json の BD3A 16件と**1:1 完全一致**（欠落ゼロ・過剰ゼロ）。.J5/.J6/.F1 は BD3A.251005.003 系に既収載を確認。

### 5. テスト更新（tests/test_contract.py）
- base_month の3チェックを追加: (a) 全件存在 (b) 形式 ^[0-9]{4}-[0-9]{2}$ (c) build_id 日付部（YYMMDD→20YY-MM）との整合。14→**17チェック**。
- **基準値更新**: MIN_LINES_BUILDS 1860→**1960**（base_month 全67件追加による増加 1894→1960行。human_review/conflict_note 2行減・resolution_note 1行増を含む。行数非減少の思想は維持し、新実測値まで引き上げ）。件数基準（suffix_map の 67件固定）は変更なし。

### 6. 検証結果
- 冪等性: parse_builds.py を2回実行し MD5 同一（d17931a2a95d956f26c2ec22bf5d333b、byte-diff ゼロ）。
- 非破壊の機械照合: 再生成前後の全67件×全フィールド比較。差分は (a) base_month 全件追加 (b) BP2A.250705.008.A1 の release_date 2025-07-08→2025-08 / human_review・conflict_note 除去 / resolution_note 追加、のみ。それ以外の差分ゼロ（unexpected diffs: []）。件数 67→67（新規レコードなし）。
- tests/test_contract.py 17/17 PASS / tests/test_suffix_map.py 23/23 PASS。valid JSON 確認済み。
- entries.json / index.html は未変更。git commit / push は実施していない。

## Agent 4 (2nd iteration: Cross-Validator)

日付: 2026-07-30。スコープ: builds.json 全67件をスクレイピング元 (developers.google.com/{ota,images} + source.android.com bulletin) とは独立の外部情報と突き合わせ、`confidence` / `confidence_sources` を付与。builds.json は直接手書きせず scripts/parse_builds.py の `CROSS_VALIDATION` テーブル + `apply_cross_validation()` で再生成（冪等性契約を維持）。

### 1. 判定規則（値域の解釈を明文化）
- **OFFICIAL**: Google 公式の第二経路 = **Pixel Community 公式月次投稿**（support.google.com/pixelphone/thread/*、Community Manager 投稿の「Google Pixel Update - <Month>」）で build_id の一致を確認したもの。
- **MULTI_SOURCE**: 公式第二経路では未確認だが、独立系ソース1つ以上で一致（スクレイピング元を1経路と数え、相互独立2経路以上で一致）。「独立2ソース」はこの相互独立経路数で解釈（devsite の ota/images 2ページは同一経路 = 1 と数える）。
- **SINGLE_SOURCE**: 外部照合できず（スクレイピング元の1経路のみ。要再確認）。
- デフォルトは SINGLE_SOURCE（テーブル未登録 = 未照合と同義）。既存 sources は不変、判定根拠 URL は新設 `confidence_sources` に記録。

### 2. 採用した独立ソース
1. **Pixel Community 公式月次投稿**（OFFICIAL の根拠）: 2025-06〜2026-07 の全14ヶ月分の公式投稿を発見・取得（WebFetch は JS レンダで不可 → curl 直接取得で本文の build 表を機械抽出）。スレッドID: 349745083 / 355981577 / 362911257 / 368006132 / 379076388 / 386109819 / 389367100 / 401468923 / 406938450 / 410784164 / 422905223 / 431077516 / 442096105 / 448470698。
2. **BetaWiki**（betawiki.net）: ビルド単位ページ（BP2A.250605.031.A2/.A3、BD1A.250702.001、BD3A.250721.001.B7、BP3A.250905.014、BP4A.251205.006）+ Android_16 一覧ページ。直接 fetch は Cloudflare でブロック → 検索スニペット経由で確認。
3. **XDA**（xdaforums.com）: 機種別 stable update スレッド（raven 4352027 / husky 4633839 / Pixel 10 系 4757843 / ARB 告知 4788187）。本文 fetch は 403 → スレッドタイトル（build_id・日付・地域を含む）と検索スニペットで確認。
4. **報道系**（代替独立ソース）: droid-life（月次 build 表が最も網羅的。8月/10月×2波/11月/12月/1月/2月/4月/7月/Pixel 10 factory images 記事を fetch）、9to5Google（7月/8月/9月/10月/12月19日/3月/5月/6月/7月/10a factory images）、Android Police（2025-05 ARB / 2025-07）、Android Authority ほか。
5. Verizon 公式サポートページ（Pixel 9a 更新履歴）も参照したが、掲載は基本ビルドのみで .B* 変異版の確認には使えず（キャリア公式であって Google 公式でないため OFFICIAL の根拠にもしない）。

### 3. 月別照合結果（カバレッジ）
| 月 | 公式投稿 | 独立系 | 判定 |
|---|---|---|---|
| 2025-05 (BP1A) | なし(スコープ外世代) | Android Police + XDA | MULTI 1 |
| 2025-06 | ✓(.A2/.A3) | BetaWiki + droid-life | OFFICIAL 2 |
| 2025-07 | ✓(.008) | 9to5G + droid-life + AP | OFFICIAL 1 |
| 2025-08 | ✓(.A5/.008.A1/.005) | droid-life + 9to5G + AA | OFFICIAL 3 / Pixel10ローンチ4件は公式投稿非掲載→droid-life factory記事+BetaWiki+9to5GでMULTI 4 |
| 2025-09 | ✓(.014/.014.A1/.B7) | BetaWiki + XDA + 9to5G | OFFICIAL 3 / .E1(9/16配信)は非掲載→XDA+9to5GでMULTI 1 |
| 2025-10 | ✓(10/8第1波: .B1/.A2/.W3/.J5) | droid-life(10/8,10/30) + XDA + 9to5G | OFFICIAL 4 / 10/30第2波7件はMULTI / rango系ローンチ(BD3A.250808.001=BetaWiki一覧でMULTI、BD3A.251005.003・.J2=外部確認できずSINGLE) |
| 2025-11 | ✓(全6件) | droid-life + XDA + AA | OFFICIAL 6 |
| 2025-12 | ✓(12/2第1波: base/.A1/.B1/.C1) | BetaWiki + droid-life + XDA + 9to5G | OFFICIAL 4 / 12/17-19第2波 .E1/.A4/.C2=9to5G+XDAでMULTI 3、.B3=外部確認できずSINGLE |
| 2026-01 | ✓(全4件) | droid-life + Forbes + AA | OFFICIAL 4 |
| 2026-02 | ✓(全6件) | droid-life + 9to5G + XDA | OFFICIAL 6 |
| 2026-03 | ✓(.018/.018.A1) | XDA + 9to5G + droid-life | OFFICIAL 2 / BD6A.251031.001.A4(10a出荷ビルド)=9to5G factory記事でMULTI 1 |
| 2026-04 | ✓(.005/.003.A1) | droid-life + XDA + 9to5G | OFFICIAL 2 / .005.B1(Telia)=外部確認できずSINGLE |
| 2026-05 | ✓(.005) | 9to5G + XDA + technobezz | OFFICIAL 1 / .A1(Telia)=XDAスレッドタイトルでMULTI 1 |
| 2026-06 | ✓(全4件) | 9to5G + XDA + AA | OFFICIAL 4 |
| 2026-07 | ✓(base/.A1) | droid-life + 9to5G + XDA | OFFICIAL 2 |

集計: **OFFICIAL 44 / MULTI_SOURCE 19 / SINGLE_SOURCE 4**（計67）。
SINGLE_SOURCE 4件 = BD3A.251005.003（rango 10/8波 global）/ BD3A.251005.003.J2（rango 10/8波 Japan）/ BP4A.251205.006.B3（Verizon 12月第2波）/ CP1A.260405.005.B1（Telia 4月）。いずれも exact-match 検索で外部出現なし（捏造せず SINGLE のまま。CROSS_VALIDATION に空エントリで「調査済み」を明示）。

### 4. 食い違い検出（タスク2）
- **記録した食い違い: 1件**。BP1A.250505.005 の release_date: builds.json=2025-05-05（パッチレベル由来のオーナー確定値）vs 独立2ソース（Android Police・XDA raven スレッド）=2025-05-06（ロールアウト開始日）。値は書き換えず conflict_note に外部値を追記（2025-05 は月内1件 ≤2 → human_review なし）。
- **同一月3件以上の食い違い: なし** → human_review を立てた月はゼロ。機構は `apply_cross_validation()` にリリース月単位のカウントとして実装済み（将来の再照合で自動発動）。
- **公式投稿で解消した外部同士の食い違い（レコードには記録せず）**:
  1. CP2A.260605.012.C1 (Rogers): 9to5Google 記事は Pixel 9a を含む10機種と読めるが、公式6月投稿の Rogers 列挙は 9a なしの9機種で builds.json と完全一致 → 食い違いなし（報道側の丸め）。
  2. CP2A.260705.006.A1 (AU+Rogers): droid-life は Rogers に 9a を含む13機種だが、公式7月投稿は AU 3機種 + Rogers 9機種（9a なし）= 12機種で builds.json と完全一致 → 食い違いなし。
  3. 2026-03: 9to5Google 記事本文は CP1A.260305.016 と誤記（同記事のコメント欄・XDA・公式投稿はいずれも .018）→ builds.json (.018) 側が正。
  4. BP2A.250705.008.A1 の release_date=2025-08（Agent 3 の解決）を droid-life/公式8月投稿が外部からも裏付け（Pixel 6a の8月配信ビルド）。

### 5. 実装
- `CROSS_VALIDATION`（build_id → confidence / confidence_sources / external_conflict）+ `COMMUNITY_POSTS`（公式投稿URL表）+ `apply_cross_validation()` を parse_builds.py に追加。KNOWN_EXTRA_BUILDS / ARB_EXTRA_FIELDS / RESOLVED_CONFLICTS と同型のテーブル駆動。適用は KNOWN_EXTRA 注入後・base_month 付与前（全67件に適用されるため）。
- 追加フィールドは各レコード末尾（verify_state の後）に confidence → confidence_sources の順で付与。既存フィールドは一切不変。
- tests/test_contract.py: confidence 3チェック追加（全件存在 / 3値域 / confidence_sources が https URL 配列）。17→**20チェック**。MIN_LINES_BUILDS 1960→**2286**（confidence_sources 全件追加による増加。行数非減少の思想は維持し新実測値へ引き上げ）。

### 6. 検証結果
- 冪等性: parse_builds.py 2026-07-30 を2回実行し MD5 同一（fa8229beee14b2527b8e1b469934398a、byte-diff ゼロ）。
- 非破壊の機械照合: 再生成前後の全67件×全フィールド比較。差分は confidence / confidence_sources の全件追加 + BP1A.250505.005 の conflict_note 追記のみ。violations: NONE。件数 67→67。
- tests/test_contract.py 20/20 PASS / tests/test_suffix_map.py 23/23 PASS。valid JSON 確認済み。
- entries.json / index.html は未変更。git commit / push は実施していない。

## Agent 5 (2nd iteration: Ops & Shipper)

作業日: 2026-07-30。Agent 1〜4 の未コミット成果の上に運用系を仕上げ、検証ゲートを通して出荷。

### 1. launchd plist の月2回化
- `launchd/com.taka.pixel-builds-monthly.plist` の StartCalendarInterval を dict → array 化し、毎月10日 03:00 と 20日 03:00 の2本に変更。`plutil -lint` OK。
- 理由: 月中リリースの取りこぼし防止。実績: A17正式版 6/16、Feature Drop 11/11、QPR2 2次更新 12/19 など、10日単発のスケジュールでは拾えない月中〜月末配信が繰り返し発生している。理由は plist 内 XML コメントと monthly_collect.sh 冒頭コメントの両方に記録。
- 設置は未実行（launchctl 操作は人間ゲート運用。コマンドは最終報告に記載）。

### 2. dead リンク4件の切り分け（真因判定）
初回 linkcheck（1st iteration）で dead=4 だった URL を再調査。結論: **3件はスクレイパー側の偽陰性、1件のみ dead 確定**。
- `support.google.com/pixelphone/answer/15701861` → **スクレイパー側**。HEAD が 404 を返すが GET では 200（HEAD 偽陰性）。旧実装は HEAD の 4xx を即 dead 判定していた。
- `support.google.com/pixelphone/answer/15738128` → **スクレイパー側**。同上（HEAD 404 / GET 200）。
- `support.google.com/pixelphone/thread/362205439/...` → **スクレイパー側**。同上（HEAD 404 / GET 200）。
- `wiki.rossmanngroup.com/wiki/Pixel_4a_Battery_Performance_Program` → **dead 確定**。DNS 解決不能（NXDOMAIN）。ルートドメイン rossmanngroup.com は生存（200）しており、wiki サブドメイン自体が廃止されたと判断。sources の差し替えは今回スコープ外（次回データ更新時に代替ソースを検討。候補: 同内容を扱う bmaupin/pixel4a-battery-research 等は既に別ソースとして収載済み）。
- 参考: `support.google.com/pixelphone/answer/4457705`（月次収集の取得元）も curl 直接確認で HEAD 404 / GET 200 の同パターン。**ページは有効**（リダイレクトなし・bot 検知なし。単に HEAD メソッドに 404 を返すサーバ仕様）。
- `scripts/verify_sources_alive.py` を改修: HEAD 失敗時は理由によらず GET で再確認 / support.google.com 系は GET 失敗時に hl=ja 付与で再試行（既存クエリがあれば &hl=ja）/ それでも失敗なら 1 回リトライ。User-Agent は既存設定を維持。改修後の全件再実行で dead=1（rossmann のみ）・support 系 3件は 200。

### 3. PXD-0004 の更新（人間承認済み）
今回の指示で「既存値変更が許可されている唯一の箇所」として明示承認されたもの。変更前→後:
- `fix_status`: "open" → **"patched"**（CP2A.260705.006 で修正済み。人間承認済み）
- `evidence_level`: "REPORTED_ONLY" → **"OFFICIAL"**（fixed_in が公式 confidence="official" で確定しているため。前後値を本行に記録）
- `recheck_at`: **"2026-08" を新規追加**（8月更新時に再発報告の有無を確認する運用マーカー）
- `build_link.fixed_in` = {"build_id": "CP2A.260705.006", "confidence": "official"} は既存で確認済み（変更なし）
- 機械照合: 変更前後の entries.json 全44件×全フィールドを比較し、差分が上記3点（PXD-0004 のみ）であることを assert で確認。他エントリ・他フィールドは不変。

### 4. スクリプト由来コメント
- `verify_sources_alive.py` / `decay_warning.py` の docstring に「Obsidian-Public-Vault 版とは別実装。将来共通化検討」を明記（従来の「他リポの同名スクリプト」という曖昧表現を具体化）。

### 5. テスト増強
- tests/test_contract.py 20→**23チェック**: (a) 既知 ARB 3件（BP1A.250505.005 / CP1A.260505.005 / CP1A.260505.005.A1）の anti_rollback.incremented=true、(b) incremented=true 全レコードの scope/effect 非空、(c) recheck_at 形式 ^[0-9]{4}-[0-9]{2}$（存在する場合のみ）。
- monthly_collect.sh の検証段に tests/test_suffix_map.py を追加（従来は test_contract.py のみで、サフィックス回帰が月次収集で走らなかった）。月次収集で両テストが必ず走ることを保証。

### 6. 検証ゲート結果（push 前）
- test_contract.py 23/23 PASS / test_suffix_map.py 23/23 PASS
- html-validate: docs/dict/index.html・docs/index.html とも PASS（エラー 0）
- decay_warning.py: stale=false（last_collected=2026-07-30）
- parse_builds.py 冪等性: 2026-07-30 で2回実行し MD5 同一（fa8229beee14b2527b8e1b469934398a）・作業ツリーの builds.json と byte 一致
- 行数: builds.json 2286 / entries.json 1765 / docs/dict/index.html 757（いずれも基準以上）
- forbidden terms スキャン・git status クリーンは commit 直前に実施（結果は最終報告）
