# 付録E: 調査データダイジェスト（2026-07-24実施・data/research-2026-07.md として保存すること）

以下、項目ごとに「層 / 機序 / confidence / 出典URL / 修正状況」。エージェントはこれを一次参照とし、ここに無い機序を創作しない。

## Android 17
- **タッチ操作異常**: 層=未特定(framework/HAL疑い) / 機序=**unknown**（Google認知あり・PixelCommunity公式が対処提示、根本原因非公開）/ 出典: https://9to5google.com/2026/06/22/android-17-causes-google-pixel-scrolling-bug/ , https://9to5google.com/2026/06/23/another-touchscreen-bug-appears-in-android-17-on-pixel/ , https://www.androidcentral.com/apps-software/android-os/android-17-is-off-to-a-rough-start-with-new-pixel-touchscreen-complaints / 修正: 未。回避=Launcherキャッシュ・Smooth Display無効化
- **5G→LTE落ち・モバイル通信不能・eSIM消滅**: 層=modem_fw(eUICC/無線プロファイル) / 機序=**inferred**（"scrambled cellular radio profiles"とAndroid Authorityが推定表現）/ 出典: https://www.androidauthority.com/android-17-knocks-off-5g-3679536/ , https://www.androidcentral.com/apps-software/android-os/android-17-woes-continue-with-pixel-users-losing-5g-connectivity , https://www.phonearena.com/news/after-installing-android-17-some-pixels-lose-5g_id181265 / 対処=モバイルネットワーク設定リセット、eSIM消滅はキャリア再発行
- **仕事用プロファイルWi-Fi通信不可**: 層=framework / 機序=**confirmed**（Google表明: "We are aware of this bug affecting Work Profile users, and a fix will be rolled out in a software update soon"。Work ProfileとA17の連携不良。IPv6有効化で解決例あり=IPv6単独原因ではない）/ 出典: https://cybernews.com/tech/android-17-bug-google-pixel/ , https://www.phonearena.com/news/android-17-delivers-odd-pixel-wi-fi-bug_id181232 , https://www.androidpolice.com/android-17-wi-fi-issues/ / 修正: 表明あり時期未定
- **再起動ループ・文鎮化（2026年3〜5月更新起因）**: 層=未特定(A/B・ブートローダー疑い) / 機序=**unknown**（Google認知・Issue Tracker約800件、原因非公開）/ 出典: https://9to5google.com/2026/04/10/google-pixel-bootloop-issue-march-update/ , https://android.gadgethacks.com/news/google-pixel-bootloop-issue-explained-fixes-risks-and-what-google-says/ / 修正: 統一パッチなし。個別対応+ベータ復旧ツール+初期化

## Android 16
- **Wi-Fi突発切断**: 層=framework疑い / **inferred** / 出典: https://www.phonearena.com/news/android-16-qpr3-beta-2-is-here-to-solve-your-pixel-charging-problems-and-more_id177342 / QPR3 Beta 2で修正対象
- **バッテリー異常消費（6/6a世代）**: 層=modem_fw+hardware / 機序=**inferred**（Exynos 5123モデムの"Mobile network standby"ドレイン。Tensorサーマルエンジンの高頻度ポーリングも寄与）/ 出典: https://www.androidpolice.com/pixel-tensor-driver-update-deep-dive/ , https://discuss.grapheneos.org/d/29280-pixel-6-exynos-5123-modem-causing-problems-since-update , https://xdaforums.com/t/tensor-running-too-hot-fix-overheating-improve-battery-life-on-stock-android-no-custom-rom-no-custom-kernel-pixel-phones.4785321/ / 対処=5G無効化・Adaptive Connectivity無効化
- **通知遅延（バッテリー最適化自動変更）**: 層=framework / **inferred**（仕様と副作用の境界）/ 出典: https://support.google.com/pixelphone/thread/362205439/battery-optimisation-options-missing-in-android-16 / 対処=対象アプリを「制限なし」
- **戻る無反応・ホワイトアウト**: 層=未特定 / **unknown** / 出典: https://android.gadgethacks.com/news/android-16-qpr3-beta-2-fixes-battery-drain-on-pixel/（QPR3 Beta 2でUIレンダリング修正対象）
- **GNSS非スリープドレイン（2026年3月〜）【新規候補】**: 層=kernel/HAL〜modem_fw境界 / 機序=GNSSモジュールがスリープに入らずDoze移行を阻害、画面オフ・機内モードでも消費。Google P1認知だが「なぜ眠らないか」非公開=**inferred** / 出典: https://www.technobezz.com/pixel-battery-drain-android-16-fix , https://piunikaweb.com/2026/05/06/pixel-may-update-battery-drain-bootloop/ / 修正: May 2026でも未修正

## Android 14
- **複数ユーザー時ストレージロック**: 層=kernel(ファイルシステム/FUSE) / 機序=**confirmed**（/data/media/0 が "Structure needs cleaning"、Issue Tracker **305766503**、P2→P0格上げ、Google声明 2023-10-28）/ 出典: https://borncity.com/win/2023/10/28/android-14-bug-locks-out-users-with-multiple-profiles-threat-of-data-loss/ , https://www.phonearena.com/news/android-14-storage-bug-fix-now-available-as-a-separate-tool-for-pixel-devices-stuck-in-reboot-loop_id152580 / 修正: **patched 2023-11**（+スタンドアロン修復ツール。2024-01に再発報告あり）

## Android 12-13
- **Material You期ドレイン**: 層=modem_fw+hardware疑い / **inferred**（Exynos 5123 "Mobile network standby"説。※「AOSP #29481/NearbyDevicesService」説はコンテンツファーム由来で不採用）/ 出典: https://xdaforums.com/t/network-standby-battery-drain-exceeding-29-always-p6p-why.4365549/page-6 , https://9to5google.com/2021/12/06/pixel-6-december-update/
- **Pixel 6世代 指紋低速【新規候補】**: 層=hardware+framework / 機序=**confirmed（公式見解として）**: Google声明 "The Pixel 6 fingerprint sensor utilizes enhanced security algorithms. In some instances, these added protections can take longer to verify or require more direct contact with the sensor." コミュニティは技術的妥当性を疑問視 / 出典: https://www.engadget.com/google-pixel-6-slow-fingerprint-sensor-195023475.html , https://www.androidpolice.com/google-details-why-pixel-6-fingerprint-sensor-is-slow-but-were-not-satisfied-with-the-explanation/
- **A13ワイヤレス充電断続【新規候補】**: 層=framework(充電制御) / **inferred**（ソフトの充電制御起因と両ソース推定、Issue Tracker **242836221**）/ 出典: https://9to5google.com/2022/08/19/pixel-wireless-charging-android-13/ , https://www.androidpolice.com/android-13-wireless-charging-bug/ / 関連: May 2026更新(CP1A.260505.005)で「75〜80%時のワイヤレス低速化」を公式修正 https://www.androidauthority.com/may-2026-pixel-software-update-3663791/

## Android 11
- **壁紙ブートループ**: 層=framework(SystemUI) / 機序=**confirmed**（ImageProcessHelper で RGB合計値を配列indexに使用、丸めで256到達→`ArrayIndexOutOfBoundsException: length=256; index=256`→SystemUIクラッシュ連鎖。開発者Davide BiancoがAOSP修正提出。A11以降はsRGB強制変換で影響なし=A10以前の事象）/ 出典: https://www.xda-developers.com/wallpaper-triggers-rare-bug-causing-android-devices-bootloop/ , https://www.androidauthority.com/android-wallpaper-crash-1124577/ , https://medium.com/@srivastavahardik/diving-into-androids-wallpaper-crash-bug-7bda055b9641 / 修正: patched（AOSP）

## 機種固有
- **4aバッテリー制限（2025-01）**: 層=cloud→kernel(dtbo) / 機序=**confirmed**（Hector Martinのdtbo差分解析: LSNセル個体のみ `max-voltage-uv` 0x43e6d0(4.45V)→0x3c45b0(3.95V)、容量 0xc08(3080mAh)→0x604(1540mAh)。セル判別=電池QRコード横番号 **8230015901=ATL(非対象) / 8230020501=LSN(対象)**。豪ACCCリコール文書: 過熱が "could potentially lead to fire or burns" と明記。EMRとして配信、Adaptive Charging無効化も）/ 出典: https://github.com/bmaupin/pixel4a-battery-research , https://www.androidauthority.com/pixel-4a-battery-update-explained-3522417/ , https://support.google.com/pixelphone/answer/15701861 , https://wiki.rossmanngroup.com/wiki/Pixel_4a_Battery_Performance_Program / 補償プログラムは2026-01-08受付終了
- **5a膨張・電源ボタン**: 層=hardware / **inferred** / 出典: https://xdaforums.com/t/bulging-pixel-5a-screen-battery.4474615/
- **6aモデム不安定・発熱**: 層=modem_fw+hardware / **inferred**（Exynos 5123構造的非効率。Project ZeroがExynosモデム脆弱性を2023年に複数開示）/ 出典: https://www.androidpolice.com/pixel-tensor-driver-update-deep-dive/ , https://discuss.grapheneos.org/d/29280-pixel-6-exynos-5123-modem-causing-problems-since-update
- **7a発熱・ちらつき**: 層=hardware(Tensor G2)+framework / **unknown/inferred**（ちらつきはPWM/リフレッシュ切替のソフト説とパネル損傷のハード説が併存）/ 出典: https://www.androidauthority.com/google-pixel-7a-problems-fixes-3333284/
- **8a緑（2種を分離すること）**: (A)緑ティント/フラッシュ=層=framework(ディスプレイドライバ)・**confirmed**（2024-03更新で修正）(B)恒久縦ライン=層=hardware(OLED/フレックス接続)・故障として確定/供給元因果は**inferred** / 出典: https://www.androidpolice.com/pixel-8-pro-tinted-colors-always-on-screen-issue/ , https://www.digitbin.com/pixel-green-line-display-issue-fix/
- **9a発売延期ロット**: 層=hardware / 延期事実=**confirmed**（Google: "component quality issue"）、過熱原因=リーク**inferred**。Battery Health Assistanceがデフォルト有効・無効化不可（200〜1000サイクルで電圧段階低下）/ 出典: https://www.tomsguide.com/phones/google-pixel-phones/google-pixel-9a-pre-orders-delayed-due-to-component-quality-issue-heres-when-you-can-get-one , https://support.google.com/pixelphone/answer/15738128
- **Fold内側画面破損**: 層=hardware(構造設計) / **inferred**（①フィルム端とヒンジ間の密封不足→水分浸入 ②防塵なし→塵埃 ③保護層剥離 ④5Gアンテナ線に沿う割れ=JerryRigEverything曲げ試験。ベゼルリップ薄）/ 出典: https://www.ifixit.com/Guide/Google+Pixel+Fold+Inner+Screen+Assembly+Replacement/162894 , https://www.tomsguide.com/news/google-pixel-fold-has-a-potentially-fatal-design-flaw-heres-why
- **Play Integrity連鎖**: 層=cloud+hardware鍵 / 機序=**confirmed**（basicIntegrity/deviceIntegrity/strongIntegrityの3段階、strongはハードウェア鍵アテステーション。droidguardが信号収集。2025-05ポリシー変更でアンロックブートローダーはbasicも不通過に）/ 出典: https://xdaforums.com/t/info-play-integrity-api-replacement-for-safetynet.4479337/page-6 , https://xdaforums.com/t/google-play-integrity-api-policy-as-of-may-2025-and-rooted-devices.4732970/

## コードネーム確定
- **10a = stallion（STA5）確定**: https://9to5google.com/2026/03/05/pixel-10a-factory-images/
- 既存9件（sunfish/bramble/barbet/bluejay/lynx/akita/tegu/felix/comet）照合一致: https://www.androidpolice.com/google-pixel-codename-list/ , https://wiki.lineageos.org/devices/ , https://source.android.com/docs/setup/build/building-pixel-kernels
- 10 Pro Fold = rango はリーク段階（公式Factory Image未掲載）→ UNVERIFIED維持: https://www.xda-developers.com/google-pixel-10-leaks-codenames/

## 先行事例（README追記用）
- bmaupin/pixel4a-battery-research（ソース差分+判別手順の粒度モデル）/ GrapheneOS os-issue-tracker（logcat根拠のIssue化）/ Rossmann wiki / Google Issue Tracker。「機序+確度付き統合台帳」の公開事例は確認できず＝本辞書に独自性。
