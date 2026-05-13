# RealityKit Pipeline Demo Worklog

Bu dosya projenin ortak çalışma defteri. Her yeni işe başlamadan önce buraya kısa hedef yazacağız; iş bitince ne yaptığımızı, hangi komutları çalıştırdığımızı ve ne öğrendiğimizi ekleyeceğiz.

## Nasıl Kullanacağız

1. Yeni iş başlamadan önce `Current Sprint` bölümünü güncelle.
2. İşi küçük görevlere böl: Claude, Codex, insan.
3. Asset veya kod sözleşmesi değişirse `Contracts` bölümüne yaz.
4. Build/test sonucu varsa `Verification Log` bölümüne ekle.
5. Kararları sadece sohbet içinde bırakma; `Decision Log` bölümüne kaydet.

## Current Sprint

### Sprint 135: RKG Acceptance Runner Product Hardening

**Durum:** Tamamlandı
**Tarih:** 2026-05-13
**Amaç:** `rkg accept-first-asset` ve `rkg accept-assets` workflow'larını ürün davranışına yaklaştırmak: plan çıktısı kullanıcıya okunur `rkp`/`rkg` komutları göstermeye devam etmeli, ama executor lokal PATH veya eski kurulu binary'ye güvenmeden workspace source tree'yi çalıştırmalı.

**Yapılanlar:**

- Acceptance runner `_run_command` artık `rkp ...` komutlarını `python -m rkp.cli ...` olarak dispatch ediyor.
- Aynı resolver `rkg ...` komutlarını da `python -m rkg.cli ...` olarak dispatch ediyor.
- JSON/dry-run planları değişmedi; kullanıcıya ve dokümantasyona görünen workflow hâlâ `rkp make-asset`, `rkp build-asset`, `rkp accept-asset` gibi okunur komutlardan oluşuyor.
- Regression testleri hem workspace `PYTHONPATH` korumasını hem de module dispatch davranışını doğruluyor.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance: ok; 7 tests
rtk ./.venv/bin/python -m unittest discover -s Tests: ok; 238 tests
rtk ./.venv/bin/python -m ruff check src/rkg src/rkp Tests: ok
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
rtk ./.venv/bin/python -c "from pathlib import Path; from rkg.asset_acceptance import _run_command; p=Path('Build/rkg-proper-skeleton-v7/ShardVolleyStart'); print('rkp', _run_command(['rkp','status'], p)); print('rkg', _run_command(['rkg','qa-plan','GameSpec.json'], p))": ok; rkp 0, rkg 0
```

**Öğrenme notu:**

Ürünleşmiş agent workflow'unda plan okunabilir olabilir, ama executor deterministik olmalı. Bu değişiklik dogfood sırasında yanlışlıkla eski global `rkp`/`rkg` binary'sinin kullanılmasını engeller.

### Sprint 134: RKG Semantic Screenshot QA And Motion Feedback

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** Presentation parity sonrası kalan ilk kalite kapısını kapatmak: `qa-plan` her screenshot için piksel-level semantic contract üretmeli, `verify-screenshots` debug overlay/flat-scene gibi temel görsel hataları reddetmeli, generated `custom_realitykit` sahnesi de tamamen statik kalmayacak bir motion feedback hook'u taşımalı.

**Yapılanlar:**

- `qa-plan` screenshot adımlarına `semantic_visual_contract` eklendi.
- `verify-screenshots` artık image/sidecar/runtime scene snapshot sonrası piksel band analizi yapıyor:
  - üst bölgede fazla açık panel varsa `semantic_debug_overlay`
  - gameplay sahne bandı çok düzse `semantic_flat_scene`
  - sahne bandı yeterince okunur değilse `semantic_scene_too_dark`
- PNG sampler coordinate-aware hale geldi; JPEG semantic check aynı macOS `sips` rasterizer yolunu kullanıyor.
- Generated `WorldRig.swift` `updateIdleMotion(anchor:time:)` kazandı:
  - world root çok hafif sway
  - target frame bob
  - lane rail pulse
- Generated `custom_realitykit` `GameSceneController.swift` `SceneEvents.Update` subscription ile motion tick'i bağlıyor.
- V7 Shard Volley screenshot kanıtları `Docs/screenshots/rkg_shard_volley_v7_*.jpg` olarak kopyalandı.

**Dogfood Demo:**

```text
Build/rkg-proper-skeleton-v7/ShardVolleyStart
```

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_qa_plan Tests.test_rkg_screenshot_status Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_scaffold_generators: ok; 37 tests
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-start-game-dogfood/idea.json --output Build/rkg-proper-skeleton-v7/ShardVolleyStart --json: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-proper-skeleton-v7/ShardVolleyStart: ok; generated tests, doctor, release-check, xcodegen, xcodebuild
rtk xcrun simctl boot FF329D84-0179-49E2-AFC4-12D4935845FC: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-proper-skeleton-v7/ShardVolleyStart --device booted --json: ok; 4 screenshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-proper-skeleton-v7/ShardVolleyStart --json: ok; 4/4 screenshots, semantic contracts passed
rtk ./.venv/bin/python -m unittest discover -s Tests: ok; 237 tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
```

**Screenshot evidence:**

```text
Docs/screenshots/rkg_shard_volley_v7_gameplay_start.jpg
Docs/screenshots/rkg_shard_volley_v7_mid_action.jpg
Docs/screenshots/rkg_shard_volley_v7_fail_or_hit.jpg
Docs/screenshots/rkg_shard_volley_v7_results.jpg
```

**Öğrenme notu:**

Bu gate hâlâ insan gözü yerine geçmez; text overlap veya her mesh'in gerçekten okunabilir silüete sahip olduğunu kanıtlamıyor. Ama artık eski gri dev panel gibi temel görsel hatalar screenshot verification'da fail oluyor ve generated scene runtime'da ilk motion feedback omurgasına sahip.

### Sprint 133: RKG Game-Skeleton Presentation Parity

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** Shard Volley gibi `custom_realitykit` çıktılarının dev overlay/proof fixture hissini azaltıp en az oyun iskeleti seviyesine taşımak: full-screen game shell, okunur HUD, world/lighting rig, projectile feedback, temiz result state ve daha iyi fallback composition.

**Yapılanlar:**

- `custom_realitykit` `ContentView` artık tek gri debug panel üretmiyor:
  - full-screen `GameView`
  - `StartOverlay`
  - safe-area top `GameHUD`
  - bottom `PrimaryInputLayer`
  - ayrı `ResultView`
  - `statusBarHidden(true)` ve `persistentSystemOverlays(.hidden)`
- Projectile adapter kontrolleri metin ağırlıklı default button yerine icon button sözleşmesine geçti.
- Generated `WorldRig.swift` eklendi:
  - koyu arka plan
  - key/rim light
  - backdrop
  - arena floor + lane rails
  - target frame
  - projectile trail / hit pulse feedback
- Projectile scene composition yeniden ayarlandı:
  - player proxy küçültülüp aşağı alındı
  - weapon/projectile/target ölçekleri daha okunur hale getirildi
  - target hit state daha belirgin büyüme/renk feedback'i alıyor
- `procedural_capsule` fallback kırmızı default sphere yerine nötr launcher proxy oldu.
- Result state gameplay controls göstermiyor; sadece dark result panel + reset gösteriyor.

**Dogfood Demo:**

```text
Build/rkg-proper-skeleton-v6/ShardVolleyStart
```

**Verification:**

```text
rtk python3 -m unittest Tests.test_rkg_content_views Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_scaffold_generators Tests.test_rkg_start_game: ok; 21 tests
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-start-game-dogfood/idea.json --output Build/rkg-proper-skeleton-v6/ShardVolleyStart --json: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-proper-skeleton-v6/ShardVolleyStart: ok; generated tests, doctor, release-check, xcodegen, xcodebuild
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-proper-skeleton-v6/ShardVolleyStart --device booted: ok; 4 screenshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-proper-skeleton-v6/ShardVolleyStart --json: ok; 4/4 screenshots
```

**Screenshot evidence:**

```text
Build/rkg-proper-skeleton-v6/ShardVolleyStart/Docs/screenshots/gameplay_start.jpg
Build/rkg-proper-skeleton-v6/ShardVolleyStart/Docs/screenshots/mid_action.jpg
Build/rkg-proper-skeleton-v6/ShardVolleyStart/Docs/screenshots/fail_or_hit.jpg
Build/rkg-proper-skeleton-v6/ShardVolleyStart/Docs/screenshots/results.jpg
```

**Öğrenme notu:**

Bu sprint RKG'yi shipping oyun seviyesine getirmedi; ama generated `custom_realitykit` skeleton artık ilk screenshot'ta dev/debug panel değil, oyun shell'i, sahne dünyası, okunur controls ve result state üretiyor. Kalan kalite açığı pixel-level semantic QA: screenshot verifier hâlâ text overlap, mesh visibility ve kompozisyon kalitesini insan gözü kadar değerlendirmiyor.

### Sprint 132: RKG Full Demo Asset Acceptance

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** Tek `target_proxy` kabulünden çıkıp generated demo içindeki tüm temel gameplay role asset'lerini RKP acceptance zincirine sokmak; bunu tek simulator screenshot capture pass'i ile tekrarlanabilir komuta bağlamak.

**Yapılanlar:**

- Yeni `rkg accept-assets <generated-project>` komutu eklendi.
- Komut varsayılan olarak tüm generated asset görevlerini gameplay önceliğine göre sıralıyor:
  - `target`, `projectile`, `weapon`, `player`, `arena`
- `--asset-id` tekrar edilebilir; istenirse subset kabul edilebiliyor.
- Çoklu workflow sırası:
  - her asset için `rkp make-asset`, `rkp build-asset`, `rkp inspect-usdz --json`
  - bir kez `rkg capture-screenshots`
  - bir kez `rkg verify-screenshots`
  - her asset için uygun state screenshot'ını `<asset_id>_imported.jpg` path'ine kopyalama
  - her asset için `rkp accept-asset`
  - bir kez `rkp release-check --assets`
- `execute_asset_acceptance_plan` ortak executor olarak eklendi; `accept-first-asset` bunu kullanacak şekilde korundu.
- RKP generated-game role tipleri genişletildi:
  - `gameplay_actor`
  - `weapon_proxy`
  - `hit_vfx`
  - `ui_prop`
- `prompt-asset` artık generated-game role prompt'larını tanıyor:
  - `player`
  - `weapon`
  - `arena`
  - mevcut `projectile`
  - mevcut `target`
- Deterministic Blender template'lerine player capsule/proxy, weapon proxy, projectile orb+trail, arena floor+lanes/rails parçaları eklendi.

**Dogfood Demo:**

```text
Build/rkg-full-demo-v1/ShardVolleyStart
```

**Generated asset inspect sonuçları:**

```text
player_proxy: imported, 296 / 1500 triangles, 512x512 baseColor, st UV present
arena_space: imported, 50 / 1200 triangles, 512x512 baseColor, st UV present
weapon_proxy: imported, 68 / 700 triangles, 512x512 baseColor, st UV present
projectile_proxy: imported, 254 / 400 triangles, 512x512 baseColor, st UV present
target_proxy: imported, 288 / 700 triangles, 512x512 baseColor, st UV present
```

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance.RkgAssetAcceptanceTests.test_accept_assets_dry_run_plans_all_roles_with_one_capture Tests.test_rkg_asset_acceptance.RkgAssetAcceptanceTests.test_accept_assets_execution_captures_once_and_accepts_each_asset: expected red before command/executor existed; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkp_package.RkpPackageTests.test_template_generator_supports_generated_game_role_archetypes: expected red before budgets/archetypes existed; then ok
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-start-game-dogfood/idea.json --output Build/rkg-full-demo-v1/ShardVolleyStart --force --json: ok
rtk ./.venv/bin/python Tools/rkg.py accept-assets Build/rkg-full-demo-v1/ShardVolleyStart --device booted --dry-run --json: ok; one capture and one release-check planned
rtk ./.venv/bin/python Tools/rkg.py accept-assets Build/rkg-full-demo-v1/ShardVolleyStart --device booted --json: ok; all 5 assets built, inspected, captured, accepted, release-checked
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-full-demo-v1/ShardVolleyStart --json: ok; 4/4 screenshots
rtk /Users/kyylian/Developer/RealityKitPipelineDemo/.venv/bin/python -m rkp.cli status --json from generated project: all 5 assets imported and ready
```

**Öğrenme notu:**

`accept-assets` kaliteyi otomatik olarak "shipping art" seviyesine çıkarmıyor; ama full demo artık sadece procedural fallback proof değil. Beş role asset'i de RKP manifest, USDZ inspect, simulator screenshot evidence ve generated release-check zincirinden geçiyor. Kalan en önemli açık pixel-level semantic QA: screenshot içinde bu asset'lerin gerçekten okunur ölçekte göründüğünü ve overlay text'in çakışmadığını hâlâ insan gözü veya yeni görsel analiz doğrulamalı.

### Sprint 131: RKG Polished First Demo Slice

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** `accept-first-asset` workflow'unu fresh generated demo üzerinde tekrar dogfood etmek; ilk kabul edilen `target_proxy` asset'ini daha okunur bir gameplay hedefi yapmak ve sıfırdan demo üretiminde yakalanan toolchain açıklarını kapatmak.

**Yapılanlar:**

- `rkp prompt-asset` template'inde `target` archetype için düz quad yerine UV'li, hafif kalın, dairesel bullseye mesh üretimi eklendi.
- Target base-color texture daha okunur yüksek kontrast halka yapısına çekildi.
- Template regression testi `make_bullseye_target_mesh`, `st` UV ve target branch sözleşmesini kontrol edecek şekilde genişletildi.
- `rkg capture-screenshots` fresh generated project için `project.yml` varsa `xcodegen generate` adımını planlıyor ve build'den önce çalıştırıyor.
- `accept-first-asset` subprocess runner'ı CLI entrypoint'lerinde workspace `src` kodunu öne alan environment ile çalışıyor; bu dogfood sırasında kurulu eski `rkp` binary'sine düşme sorununu kapattı.
- `Build/rkg-polished-demo-v2/ShardVolleyStart` sıfırdan üretildi.
- `target_proxy` ilk asset olarak üretildi, inspect edildi, simulator screenshot akışından acceptance screenshot'ına kopyalandı ve `imported` yapıldı.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkp_package.RkpPackageTests.test_template_generator_does_not_call_claude_when_api_key_exists: ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_capture.RkgCaptureTests.test_capture_screenshots_dry_run_lists_fighter_launch_commands: ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_capture.RkgCaptureTests.test_capture_execution_runs_build_install_launch_and_screenshot_steps Tests.test_rkg_asset_acceptance.RkgAssetAcceptanceTests.test_acceptance_runner_prefers_workspace_pythonpath_for_cli_entrypoints: ok
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-start-game-dogfood/idea.json --output Build/rkg-polished-demo-v2/ShardVolleyStart --force --json: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-polished-demo-v2/ShardVolleyStart --device booted --dry-run --json: ok; generate step present
rtk ./.venv/bin/python Tools/rkg.py accept-first-asset Build/rkg-polished-demo-v2/ShardVolleyStart --asset-id target_proxy --source-state fail_or_hit --device booted --json: ok
rkp inspect-usdz target_proxy --json during acceptance: ok; 288 / 700 triangles, 512x512 baseColor, st UV present, USDZ 34844 bytes
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-polished-demo-v2/ShardVolleyStart --json: ok; 4/4 screenshots
rkp release-check --assets during acceptance: ok; generated project tests, manifest, imported asset inspect, XcodeGen, and xcodebuild all passed
```

**Öğrenme notu:**

Bu sprint iki farklı kalite bariyerini ayırdı: asset inspect artık yeni bullseye geometry'nin gerçekten build'e girdiğini sayısal olarak kanıtlıyor, screenshot verifier ise generated app'in dört release state'inin boş/duplicate olmayan, sidecar ve runtime scene-role kanıtı olan görüntüler ürettiğini kanıtlıyor. Hâlâ pixel-level semantic QA veya text-overlap kanıtı yok; bir sonraki RKG kalite işi bu olmalı.

### Sprint 130: RKG First Asset Acceptance Workflow

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** Sıfırdan demo üretiminde screenshot dosyalarını elle seçip kopyalama adımını azaltmak; generated project içindeki ilk gameplay-relevant asset'i tek RKG workflow'u ile RKP acceptance zincirine sokmak.

**Yapılanlar:**

- Yeni `src/rkg/asset_acceptance.py` modülü eklendi.
- Yeni `rkg accept-first-asset <generated-project>` komutu eklendi.
- Komut varsayılan olarak en yüksek öncelikli gameplay role'ünü seçiyor:
  - `target`, `enemy`, `opponent`, `projectile`, `weapon`, `player`, `vehicle`, `pickup`, `obstacle`, `cover`, `arena`
- `--asset-id` ile belirli asset seçilebiliyor.
- `--source-state` ile acceptance screenshot'ının hangi release state'inden alınacağı belirtilebiliyor.
- `--dry-run --json` planı makine-okunur şekilde döküyor.
- Normal çalışma sırası:
  - `rkp make-asset`
  - `rkp build-asset`
  - `rkp inspect-usdz --json`
  - `rkg capture-screenshots`
  - `rkg verify-screenshots`
  - seçilen release screenshot'ını `<asset_id>_imported.jpg` acceptance path'ine kopyalama
  - `rkp accept-asset`
  - `rkp release-check --assets`
- `Tests/test_rkg_asset_acceptance.py` plan ve executor davranışını kapsıyor.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance.RkgAssetAcceptanceTests.test_accept_first_asset_dry_run_selects_target_and_acceptance_screenshot: expected red before command existed; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance.RkgAssetAcceptanceTests.test_accept_first_asset_dry_run_skips_make_when_blender_script_exists: expected red before resume handling; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance: ok, 3 tests
rtk ./.venv/bin/python Tools/rkg.py accept-first-asset Build/rkg-start-game-dogfood/ShardVolleyStart --asset-id target_proxy --source-state fail_or_hit --device booted --json: ok; build, inspect, capture, verify-screenshots, copy, accept, release-check --assets all exited 0
rtk ./.venv/bin/python -m unittest Tests.test_rkg_asset_acceptance Tests.test_rkg_start_game Tests.test_rkp_project.RkpProjectTests.test_accept_asset_updates_rkg_generated_asset_brief_checklist: ok, 7 tests
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 229 tests
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok; CoreSimulator sandbox warnings appeared
```

**Öğrenme notu:**

Bu komut screenshot sayısını azaltmıyor; manuel screenshot dosyası yönetimini azaltıyor. Hedef artık "tek tek görsel dosya seçerek pipeline kapatmak" değil, generated demo project için ilk asset acceptance workflow'unu otomasyona bağlamak.

### Sprint 129: RKG Asset Bridge Dogfood

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** Sprint 128'de `start-game --json` içine eklenen `asset_pipeline.tasks` alanının sadece plan üretmediğini, gerçek bir generated project içinde RKP asset acceptance'a kadar çalıştığını kanıtlamak.

**Yapılanlar:**

- `Build/rkg-start-game-dogfood/ShardVolleyStart` current code ile yeniden üretildi.
- `asset_pipeline.tasks` içinden `target_proxy` görevi seçildi.
- Generated project root'unda şu RKP zinciri çalıştırıldı:
  - `rkp make-asset target_proxy --type gameplay_target --prompt "..."`
  - `rkp build-asset target_proxy`
  - `rkp inspect-usdz target_proxy --json`
  - `rkg capture-screenshots ... --device booted`
  - `rkg verify-screenshots ... --json`
  - `rkp accept-asset target_proxy --screenshot Docs/screenshots/target_proxy_imported.jpg`
  - `rkp release-check --assets`
- Blender bu ortamda segfault etti; RKP direct USDZ fallback devreye girip `Assets/Imported/target_proxy.usdz` üretti.
- Dogfood sırasında RKG-generated asset brief checklist'inin `accept-asset` sonrası eksik işaretlendiği görüldü.
- `src/rkp/accept_asset.py` RKG-generated brief formatındaki manifest/screenshot/acceptance checklist satırlarını işaretleyecek şekilde güncellendi.
- `accept-asset`, mevcut USDZ aynı anda inspect'ten geçiyorsa RKG brief'teki `rkp inspect-usdz ... --json` checklist satırını da işaretliyor; `inspect-usdz` non-mutating raporlama komutu olarak kaldı.
- `Tests/test_rkp_project.py` RKG-generated asset brief acceptance checklist regression testiyle genişletildi.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_accept_asset_updates_rkg_generated_asset_brief_checklist: expected red on unchecked RKG checklist; then ok
rkp make-asset target_proxy --type gameplay_target --prompt "...": ok, prompt script generated from target archetype
rkp build-asset target_proxy: ok via direct USDZ fallback after Blender exit 139; target_proxy.usdz 11536 bytes
rkp inspect-usdz target_proxy --json: ok; 192/700 triangles, baseColor 512x512, st UV present
rtk xcodegen generate: ok for generated ShardVolleyStart project
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-start-game-dogfood/ShardVolleyStart --device booted: ok, 4 screenshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-start-game-dogfood/ShardVolleyStart --json: ok, 4/4 screenshots
rkp accept-asset target_proxy --screenshot Docs/screenshots/target_proxy_imported.jpg: ok, manifest status imported
/Users/kyylian/Developer/RealityKitPipelineDemo/.venv/bin/python -m rkp.cli release-check --assets: ok; inspected imported target_proxy and built generated app
rtk ./.venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_accept_asset_updates_rkg_generated_asset_brief_checklist Tests.test_rkg_start_game: ok, 4 tests
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 226 tests
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok; CoreSimulator sandbox warnings appeared
```

**Öğrenme notu:**

RKG -> RKP bridge artık tek asset için pratikte kapandı: idea -> generated project -> asset task -> USDZ -> simulator screenshot -> `accept-asset` -> `release-check --assets`. Kalan iş bunu daha ergonomik ve otomatik hale getirmek; acceptance sınırı hâlâ screenshot kanıtıyla korunuyor.

### Sprint 128: RKG Asset Pipeline Bridge

**Durum:** Tamamlandı
**Tarih:** 2026-05-12
**Amaç:** `start-game` çıktısını generated asset brief dosyalarında bırakmayıp, her role asset için doğrudan izlenebilir RKP asset komut planına çevirmek.

**Yapılanlar:**

- Yeni `src/rkg/asset_pipeline.py` modülü eklendi.
- `rkg start-game --json` başarılı fikirler için artık `asset_pipeline` döndürüyor.
- Her asset task şunları içeriyor:
  - generated project `cwd`
  - `asset_id`, `role`, `type`
  - `Docs/assets/<asset_id>.md` brief path'i
  - `Assets/Imported/<asset_id>.usdz` runtime USDZ path'i
  - `Docs/screenshots/<asset_id>_imported.jpg` acceptance screenshot path'i
  - sıralı `rkp make-asset`, `build-asset`, `inspect-usdz --json`, `accept-asset` komut dizileri
- `start-game` testleri asset bridge sözleşmesini doğrulayacak şekilde genişletildi.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_start_game: expected red on missing asset_pipeline; then ok, 3 tests
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 225 tests
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok; CoreSimulator sandbox warnings appeared
```

**Öğrenme notu:**

Bu gerçek asset üretimini otomatik kabul etmiyor; doğru sınır bu. RKG artık "hangi asset brief'leri var?" sorusundan "generated project root'unda hangi RKP komutları sırayla çalışacak?" sorusuna makine-okunur cevap veriyor. Acceptance hâlâ screenshot kanıtı ve `rkp accept-asset` gerektiriyor.

### Sprint 127: RKG Idea-To-Project Start Command

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Sıfırdan oyun başlatma yolundaki en büyük ürün açığını kapatmak: kullanıcı `score-idea`, `new-game`, `init-game`, `qa-plan` sırasını bilmeden bir fikir dosyasından generated RealityKit skeleton alabilmeli.

**Yapılanlar:**

- `rkg start-game <idea> --output <dir>` komutu eklendi.
- Yeni `src/rkg/start_game.py` modülü fikir metninden deterministic öneri çıkarıyor:
  - fighter/duel kelimeleri -> native `fighter_2_5d`
  - racing/lap/vehicle kelimeleri -> `custom_realitykit` racing/lap/collision
  - projectile/charge/launch kelimeleri -> projectile/shooting/score
  - FPS/shooter/weapon/enemy/cover kelimeleri -> shooter/FPS systems
  - collect/pickup/timer kelimeleri -> collector/score/timer
- Komut önce `score-idea` sonucunu kullanıyor; verdict `pass` değilse proje yazmıyor.
- Pass olan fikir için GameSpec, generated project, store docs, asset briefs, runtime snapshot module, ve QA plan tek akışta üretiliyor.
- JSON çıktı score, recommendation, project/spec path ve QA planı içeriyor.
- Shard Volley Start dogfood: fikir dosyasından tek komutla projectile skeleton üretildi, Xcode project generate/build edildi, simulator screenshot capture ve runtime scene-backed verification geçti.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_start_game: expected red before implementation; then ok, 3 tests
rtk ./.venv/bin/python -m unittest Tests.test_rkg_start_game Tests.test_rkg_score_idea Tests.test_rkg_new_game Tests.test_rkg_init_game Tests.test_rkg_qa_plan Tests.test_rkg_plan_game: ok, 59 tests
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-start-game-dogfood/idea.json --output Build/rkg-start-game-dogfood/ShardVolleyStart --json: ok, score 100 pass, projectile/shooting/score recommendation
rtk xcodegen generate: ok for Build/rkg-start-game-dogfood/ShardVolleyStart
rtk xcodebuild -quiet -project ShardVolleyStart.xcodeproj -scheme ShardVolleyStart -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-start-game-dogfood/ShardVolleyStart --device booted: ok, 4 JPEG screenshots + 4 sidecars + 4 scene snapshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-start-game-dogfood/ShardVolleyStart --json: ok, 4 runtime-scene-backed screenshots
```

**Öğrenme notu:**

Bu artık "RKG bilen operatör" gereksinimini azaltıyor. Hâlâ production game değil; ama fikirden generated RealityKit skeleton + QA plan + simulator proof zinciri tek komuta indi.

**Karar:**

Bir sonraki kapsamlı-tool açığı asset bridge veya visual text-overlap QA. Orchestrator açığı kapandı; gerçek 0-to-first-playable için generated asset brief'lerini RKP asset command planına çevirmek daha değerli olacak.

### Sprint 126: RKG Runtime Scene Snapshot Evidence

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Screenshot sidecar'ın ötesine geçip generated app runtime'ından scene-role kanıtı almak; capture sadece plan metadata'sı yazmasın, çalışan RealityKit scene içinde hangi asset role'lerinin bound olduğunu da doğrulasın.

**Yapılanlar:**

- Generated projelere `RuntimeSceneSnapshot.swift` eklendi.
- `GameSceneController` artık role-bound entity'leri `rkg|asset=...|role=...|fallback=...` metadata ismiyle işaretliyor.
- Screenshot-state launch sırasında generated app simulator Documents klasörüne `rkg-scene-snapshot-<state>.json` yazıyor.
- `capture-screenshots` bu runtime dosyasını app data container'dan alıp proje içinde `Docs/screenshots/<state>.scene.json` olarak kopyalıyor.
- Screenshot sidecar artık `scene_snapshot` path'ini de taşıyor.
- `verify-screenshots` sidecar'dan sonra runtime scene snapshot'ı zorunlu doğruluyor; eksik dosya `missing_scene_snapshot`, bozuk dosya `invalid_scene_snapshot`, rol uyuşmazlığı `scene_role_mismatch` oluyor.
- Snapshot Volley adlı yeni projectile/shooting/score skeleton gerçek simulator üzerinde capture edildi; dört screenshot, dört sidecar ve dört scene snapshot birlikte doğrulandı.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_runtime_scene_snapshot_evidence_writer: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_capture.RkgCaptureTests.test_capture_screenshots_dry_run_lists_fighter_launch_commands Tests.test_rkg_capture.RkgCaptureTests.test_capture_execution_copies_runtime_scene_snapshot_after_successful_screenshot: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_requires_runtime_scene_snapshot_for_valid_sidecar Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_runtime_scene_snapshot_role_mismatch: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 222 tests
rtk xcodegen generate: ok for Build/rkg-runtime-snapshot/SnapshotVolley
rtk xcodebuild -quiet -project SnapshotVolley.xcodeproj -scheme SnapshotVolley -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-runtime-snapshot/SnapshotVolley --device booted: ok, 4 JPEG screenshots + 4 sidecars + 4 scene snapshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-runtime-snapshot/SnapshotVolley --json: ok, 4 runtime-scene-backed screenshots
```

**Öğrenme notu:**

Bu hâlâ pixel-level OCR veya text-overlap kontrolü değil. Ama artık verifier sadece "script planı böyleydi" demiyor; çalışan app'in RealityKit scene graph'ında player/arena/weapon/projectile/target gibi beklenen role binding'lerinin oluştuğunu da kanıtlıyor.

**Karar:**

Bir sonraki RKG QA seviyesi ya UI/text overlap için screenshot analizi, ya da idea-to-project orchestrator olmalı. Role-binding snapshot açığı kapandı; asset brief -> RKP asset-command köprüsü hâlâ ayrı eksik.

### Sprint 125: RKG Screenshot Evidence Sidecars

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Semantic QA için ilk sağlam kanıt kontratını eklemek: screenshot dosyası yanında hangi game/state/roles/proof cue ile yakalandığını gösteren JSON sidecar üretilmeli ve `verify-screenshots` bunu zorunlu olarak doğrulamalı.

**Yapılanlar:**

- `qa-plan --json` artık her screenshot state için `sidecar_path` veriyor.
- `capture-screenshots` her başarılı screenshot capture sonrasında `Docs/screenshots/<state>.json` sidecar yazıyor.
- Sidecar içinde `game_id`, `archetype`, `state`, `screenshot_state_case`, `visible_roles`, `drive`, `expected_evidence`, `automation`, ve screenshot path tutuluyor.
- `verify-screenshots` geçerli image dosyası için sidecar'ı zorunlu hale getirdi.
- Eksik sidecar `missing_sidecar`, bozuk sidecar `invalid_sidecar`, rol uyuşmazlığı `role_evidence_mismatch` olarak raporlanıyor.
- Shard Volley yeniden capture edildi; dört JPEG ve dört sidecar birlikte doğrulandı.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_capture.RkgCaptureTests.test_capture_screenshots_dry_run_lists_fighter_launch_commands Tests.test_rkg_capture.RkgCaptureTests.test_capture_execution_writes_sidecar_after_successful_screenshot Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_requires_sidecar_for_valid_image_capture Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_sidecar_role_mismatch: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_qa_plan.RkgQaPlanTests.test_build_qa_plan_sequences_screenshot_proofs_for_capture: expected red before sidecar_path; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_capture Tests.test_rkg_screenshot_status Tests.test_rkg_qa_plan: ok, 23 tests
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-qa-proof/ShardVolley --device booted: ok, 4 JPEG screenshots + 4 sidecars
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-qa-proof/ShardVolley --json: ok, 4 sidecar-backed screenshots
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 218 tests
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Sidecar gerçek OCR/vision yerine geçmez; screenshot içindeki target/weapon mesh'ini pikselden kanıtlamaz. Ama capture pipeline artık hangi state ve role contract'ı için kanıt üretildiğini makine-readable şekilde taşıyor. Bu, yanlış dosya/eksik sidecar/manual copy hatalarını yakalayan semantic QA tabanı.

**Karar:**

Bir sonraki semantik seviye generated app'in runtime state snapshot'ını veya scene-role visibility export'unu üretmesi olmalı. Sadece capture script'in QA planından yazdığı sidecar, görselin içeriğini değil capture contract'ını kanıtlar.

### Sprint 124: RKG JPEG Visual Evidence Guardrail

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Önceki sprintte kalan görsel QA açığını kapatmak: JPEG screenshot evidence yalnızca header/boyut ile kabul edilmemeli; boş/tek renk JPEG, decode edilemeyen JPEG stub, ve aynı görselin birden fazla release state için tekrar kullanılması yakalanmalı.

**Yapılanlar:**

- `verify-screenshots` JPEG captures için macOS `sips` decoder'ını kullanarak raster örnekleme yapıyor.
- Decode edilemeyen ama boyut bilgisi taşıyan JPEG stub artık `invalid_image` oluyor.
- Tek renk/boş JPEG evidence artık `blank_or_solid` oluyor.
- Release state'ler arasında aynı görsel fingerprint'i tekrar ederse ikinci ve sonraki state'ler `duplicate_visual_evidence` oluyor; bu previous-app / stuck capture sınıfı için pratik sinyal sağlıyor.
- Screenshot status docs ve dogfood gap listesi JPEG/duplicate guardrail ile güncellendi.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_dimension_only_jpeg_stub Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_solid_jpeg_capture Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_duplicate_visual_evidence_across_states: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_screenshot_status: ok, 11 tests
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-qa-proof/ShardVolley --json: ok, 4 JPEG screenshots sampled and unique
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 215 tests
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

JPEG visual QA için yeni Python dependency eklemeden macOS `sips` yeterli oldu. Bu OCR değil; rol varlığı/metin overlap gibi semantik kontroller hâlâ ayrı iş. Ancak boş ekran, malformed JPEG ve stuck/previous-state capture artık dosya boyutu doğru olsa bile geçmiyor.

**Karar:**

Bir sonraki görsel QA seviyesi OCR değilse bile role-presence için generated overlay/scene metadata ile screenshot sidecar üretmek olmalı; sadece pikselden "target rolü var mı" çıkarmak kırılgan olur.

### Sprint 123: RKG QA Proof and Screenshot Guardrails

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Shard Volley dogfood sırasında görülen QA güvenilirliği açıklarını kapatmak: `custom_realitykit` QA planı generic kalmamalı, capture verifier geçerli boyutlu ama boş/tek renk kanıtı yakalayabilmeli, ve generated custom overlay screenshot'ta sahneyi gereğinden fazla örtmemeli.

**Yapılanlar:**

- `CustomRealityKitRuntimeAdapter` registry entry'lerine adapter-specific screenshot proof map eklendi.
- `rkg qa-plan` artık `custom_realitykit` için seçili sistemlere göre racing/projectile/shooter/collector proof metni seçiyor.
- `custom_realitykit` QA automation hint'i `launch_arg --rkg-screenshot-state <state>` olarak güncellendi; generated custom apps zaten launch-state seeding kullanıyor.
- `verify-screenshots` PNG captures için geçerli header/boyutun yanında piksel örnekleme yapıyor ve tek renk/boş kanıtı `blank_or_solid` olarak reddediyor.
- Generated `custom_realitykit` overlay compact hale getirildi: küçük controls, daha düşük spacing/padding ve tek satır limitleri.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_qa_plan.RkgQaPlanTests.test_custom_projectile_qa_plan_uses_adapter_specific_proof_and_launch_automation Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_solid_png_capture Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_accepts_varied_png_capture: expected red before implementation; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_screenshot_status.RkgScreenshotStatusTests.test_verify_screenshots_rejects_solid_filtered_png_capture: expected red before PNG filter reconstruction; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_content_views.RkgContentViewTests.test_custom_realitykit_content_view_keeps_overlay_compact: expected red before compact overlay change; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_qa_plan Tests.test_rkg_screenshot_status Tests.test_rkg_content_views Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_init_game: ok, 56 tests
rtk ./.venv/bin/python Tools/rkg.py qa-plan Build/rkg-dogfood-shard-volley/GameSpec.json --json: ok, projectile-specific proof and launch_arg automation visible
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-dogfood-shard-volley/ShardVolley --json: ok, 4 existing screenshots
rtk git diff --check: ok
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 212 tests
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-dogfood-shard-volley/GameSpec.json --output Build/rkg-qa-proof/ShardVolley --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-qa-proof/ShardVolley: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-qa-proof/ShardVolley --device booted: ok, 4 simulator screenshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-qa-proof/ShardVolley --json: ok, 4 fresh screenshots
```

**Öğrenme notu:**

`custom_realitykit` artık sadece "generic skeleton" demiyor; screenshot QA planında hangi adapter'ın hangi state değerini kanıtladığını söylüyor. Görsel QA tarafı hâlâ tam OCR/wrong-app kontrolü değil; bu sprint boş/tek renk PNG kanıtını yakalayan ilk guardrail'i ekledi.

**Karar:**

RKG tarafında bir sonraki büyük değer yeni adapter değil; idea -> systems/spec orchestration, JPEG/real simulator visual-quality guardrail, ve asset brief -> RKP asset task köprüsü.

### Sprint 122: RKG Shard Volley Dogfood

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** RKG'nin kapsamlı tool olma yolunda eksiklerini varsayım yerine gerçek kullanım üzerinden görmek; sıfırdan bir projectile/shooting/score oyun fikrini idea score'dan simulator screenshot evidence'a kadar dogfood etmek.

**Yapılanlar:**

- `Shard Volley` fikri `score-idea` ile değerlendirildi; skor `100`, verdict `pass`.
- `rkg list-adapters`, `new-game`, `validate-spec`, `plan-game`, `qa-plan`, `init-game`, `verify-game`, `capture-screenshots`, ve `verify-screenshots` sırasıyla çalıştırıldı.
- Generated `ShardVolley` projesi `Build/rkg-dogfood-shard-volley/ShardVolley` altında üretildi ve build/release gate geçti.
- Dört screenshot state'i simulator'da capture edildi: `gameplay_start`, `mid_action`, `fail_or_hit`, `results`.
- Screenshot evidence root docs alanına kopyalandı: `Docs/screenshots/rkg_shard_volley_*.jpg`.
- Dogfood raporu `Docs/rkg-shard-volley-dogfood.md` olarak eklendi.
- Dogfood sırasında iki bug bulundu ve düzeltildi:
  - `score` sistemi collector adapter UI'ını tek başına aktive ediyordu; projectile+score oyununda collector controls görünüyordu. Collector condition artık `hasCollect || hasTimer`.
  - Capture ilk state'i çok erken yakalayabiliyordu. `capture-screenshots` default launch wait 2 saniyeye çıkarıldı.

**Verification:**

```text
rtk ./.venv/bin/python Tools/rkg.py score-idea Build/rkg-dogfood-shard-volley/idea.json --json: ok, score 100, verdict pass
rtk ./.venv/bin/python Tools/rkg.py list-adapters: ok
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Shard Volley" --camera third_person --input drag --systems projectile,shooting,score --output Build/rkg-dogfood-shard-volley/GameSpec.json: ok
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-dogfood-shard-volley/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py plan-game Build/rkg-dogfood-shard-volley/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py qa-plan Build/rkg-dogfood-shard-volley/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-dogfood-shard-volley/GameSpec.json --output Build/rkg-dogfood-shard-volley/ShardVolley --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-dogfood-shard-volley/ShardVolley: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-dogfood-shard-volley/ShardVolley --device booted: ok, 4 simulator screenshots
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-dogfood-shard-volley/ShardVolley --json: ok, 4 screenshots
rtk ./.venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime.RkgCustomRealityKitRuntimeTests.test_score_system_does_not_activate_collector_adapter_by_itself Tests.test_rkg_capture.RkgCaptureTests.test_capture_execution_waits_long_enough_after_launch_by_default: expected red before fixes; then ok
rtk git diff --check: ok
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 207 tests
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

RKG'nin command path'i artık gerçek bir sıfırdan oyun iskeleti çıkarabiliyor, build alabiliyor ve screenshot evidence üretebiliyor. Fakat kapsamlı tool olmak için sadece generator değil, dogfood edilen visual QA gerekiyor: generic `qa-plan` metni projectile için yeterince spesifik değil, screenshot verifier görsel kaliteyi anlamıyor, generated UI mobilde fazla büyük, ve idea->spec seçimi hâlâ manuel.

**Karar:**

Bir sonraki RKG işi yeni adapter eklemek değil; `CustomRealityKitRuntimeAdapter` içine screenshot proof/cue alanları eklemek, `qa-plan` çıktısını adapter-specific yapmak ve screenshot verification'a blank/wrong-app/basic-content kontrolleri eklemek.

### Sprint 121: RKG Projectile Adapter and Capability Matrix

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit` artık racing, shooter ve collector üretiyordu; broad projectile/shooting/score fikri veren kullanıcı da FPS adapter'a yanlış düşmeden charge/launch/travel/impact state'i olan, derlenebilir RealityKit iskeleti almalı. Adapter registry ayrıca CLI'dan görülebilir capability matrix üretmeli.

**Yapılanlar:**

- `projectile,shooting,score` için dördüncü `CustomRealityKitRuntimeAdapter` eklendi.
- `rkg new-game --systems projectile,shooting,score` artık projectile loop metni, `weapon_proxy`, `projectile_proxy`, ve `target_proxy` role/fallback asset'leri üretiyor.
- `SystemFlags.swift` projectile tarafında `hasProjectile` ve `hasShooting` üretiyor; `hasWeapon` artık yalnızca `weapon`/`hitscan` ile true oluyor.
- Generated `GameSessionState` projectile alanları üretiyor: `projectileShots`, `projectileHits`, `projectileCharge`, `projectileLane`, `targetLane`, `projectileTravel`, `projectileInFlight`, ve `lastProjectileHit`.
- Generated `GameRules.swift` projectile session start, lane aim, charge clamp, launch, charged-hit scoring, shot-limit result, target-clear result, ve screenshot-state seeding üretiyor.
- Generated `ContentView.swift` shots/hits/charge/aim HUD satırı ve Aim Left/Aim Right/Charge/Launch kontrolleri üretiyor.
- Generated `GameSceneController.swift` player, arena, weapon, projectile, target ve camera rig entity binding'i yapıyor; aim/target lane, charge, travel ve hit state'i RealityKit pozisyon/scale/enabled değişikliklerine yansıyor.
- `rkg list-adapters` ve `rkg list-adapters --json` eklendi; registry artık id, systems, state fields, rule members, scene properties ve scene roles olarak dışarı açılıyor.
- `procedural_rings` fallback id'si generated `FallbackFactory` içinde explicit ring/guard placeholder case'ine bağlandı; projectile `target_proxy` artık fallback idsini role-default sphere'e düşürmüyor.
- RKG docs/handoff/changelog generic skeleton kapsamını projectile ve adapter matrix ile güncelliyor.

**Verification:**

```text
rtk ./.venv/bin/python -m unittest Tests.test_rkg_new_game.RkgNewGameTests.test_new_game_writes_projectile_realitykit_skeleton_spec Tests.test_rkg_runtime_core.RkgRuntimeCoreTests.test_system_flags_swift_splits_projectile_from_weapon_systems Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_projectile_runtime_adapter_for_custom_realitykit: expected red before adapter/capability API; then ok, 7 tests
rtk ./.venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_projectile_runtime_adapter_for_custom_realitykit: expected red before procedural_rings fallback case; then ok
rtk ./.venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_runtime_core Tests.test_rkg_new_game Tests.test_rkg_init_game: ok, 48 tests
rtk ./.venv/bin/python -m ruff check src/rkg/custom_realitykit_runtime.py src/rkg/runtime_core.py src/rkg/spec_templates.py src/rkg/cli.py Tests/test_rkg_custom_realitykit_runtime.py Tests/test_rkg_init_game.py Tests/test_rkg_new_game.py Tests/test_rkg_runtime_core.py: ok
rtk ./.venv/bin/python Tools/rkg.py list-adapters --json: ok, racing/projectile/shooter/collector records
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Arc Volley" --camera third_person --input drag --systems projectile,shooting,score --output Build/rkg-mvp-projectile/GameSpec.json: ok
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-mvp-projectile/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-mvp-projectile/GameSpec.json --output Build/rkg-mvp-projectile/ArcVolley --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-mvp-projectile/ArcVolley: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-mvp-projectile/GameSpec.json --output Build/rkg-mvp-projectile/ArcVolley --force: ok after procedural_rings fallback change
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-mvp-projectile/ArcVolley: ok after procedural_rings fallback change
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-mvp-racing/GameSpec.json: ok
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-mvp-racing/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-mvp-racing/GameSpec.json --output Build/rkg-mvp-racing/DesertChase --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-mvp-racing/DesertChase: ok
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-mvp-shooter/GameSpec.json: ok
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-mvp-shooter/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-mvp-shooter/GameSpec.json --output Build/rkg-mvp-shooter/RoomBreach --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-mvp-shooter/RoomBreach: ok
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Orb Sprint" --camera top_down --input tap_swipe --systems collect,score,timer --output Build/rkg-mvp-collector/GameSpec.json: ok
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-mvp-collector/GameSpec.json --json: ok
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-mvp-collector/GameSpec.json --output Build/rkg-mvp-collector/OrbSprint --force: ok
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-mvp-collector/OrbSprint: ok
rtk git diff --check: ok
rtk ./.venv/bin/python -m ruff check src Tests Tools: ok
rtk ./.venv/bin/python -m unittest discover -s Tests: ok, 205 tests
rtk ./.venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Projectile, shooter adapter ile aynı "aim" kavramını paylaşsa da aynı sistem değil. `projectile` ve `shooting` sistemlerini `hasWeapon` altında tutmak generated ContentView ve rule dispatch'i FPS adapter'a yönlendiriyordu; ayrı `hasProjectile`/`hasShooting` flag'leri RKG'nin broad system composition modelini daha dürüst yaptı.

**Karar:**

`custom_realitykit` adapter registry artık doküman dışında da sorgulanabilir olmalı. `list-adapters --json`, gelecekte UI veya agent tarafının "hangi sistemleri seçmeliyim?" sorusunu prose parse etmeden yanıtlaması için canonical capability surface olarak kalacak.

### Sprint 120: RKG Collector Score Timer Runtime Adapter

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit` generic skeleton artık racing ve shooter üretiyordu; top-down collector, score chase veya timer tabanlı prototip isteyen kullanıcı da boş proje yerine pickup/timer/score state'i olan, derlenebilir ve screenshot state'leri farklı görünen RealityKit iskeleti almalı.

**Yapılanlar:**

- `collect,score,timer` için üçüncü `CustomRealityKitRuntimeAdapter` eklendi.
- `rkg new-game --systems collect,score,timer` artık collector loop metni, `pickup_proxy` ve `timer_gate` role/fallback asset'leri üretiyor.
- `SystemFlags.swift` artık `hasCollect`, `hasScore`, ve `hasTimer` booleans üretiyor.
- Generated `GameSessionState` collector alanları üretiyor: `collectedItems`, `collectiblesRemaining`, `collectionTimer`, `comboStreak`, `collectorLane`, `pickupLane`, ve `isCollectionTimedOut`.
- Generated `GameRules.swift` collector session start, lane clamp/move, pickup collection, score/combo update, timer-expired fail state, collection-complete result state, ve screenshot-state seeding üretiyor.
- Generated `ContentView.swift` item/timer/combo/lane HUD satırı ve Move Left/Move Right/Collect kontrolleri üretiyor.
- Generated `GameSceneController.swift` player, arena, pickup, timer ve camera rig entity binding'i yapıyor; lane/combo/timer state'i RealityKit pozisyon/scale/enabled değişikliklerine yansıyor.
- RKG docs/handoff/changelog collector adapter sınırını anlatacak şekilde güncellendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_new_game.RkgNewGameTests.test_new_game_writes_collector_score_timer_realitykit_skeleton_spec Tests.test_rkg_runtime_core.RkgRuntimeCoreTests.test_system_flags_swift_binds_collector_systems Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_collector_runtime_adapter_for_custom_realitykit: expected red before adapter; then ok, 5 tests
rtk .venv/bin/python -m ruff check src/rkg/custom_realitykit_runtime.py src/rkg/runtime_core.py src/rkg/spec_templates.py Tests/test_rkg_custom_realitykit_runtime.py Tests/test_rkg_init_game.py Tests/test_rkg_new_game.py Tests/test_rkg_runtime_core.py: ok
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_racing_runtime_adapter_for_custom_realitykit Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_shooter_runtime_adapter_for_custom_realitykit Tests.test_rkg_new_game.RkgNewGameTests.test_new_game_writes_racing_realitykit_skeleton_spec Tests.test_rkg_new_game.RkgNewGameTests.test_new_game_writes_fps_shooter_realitykit_skeleton_spec: ok, 4 tests
rtk .venv/bin/python Tools/rkg.py new-game --title "Orb Sprint" --camera top_down --input tap_swipe --systems collect,score,timer --output Build/rkg-collector-runtime/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-collector-runtime/GameSpec.json --output Build/rkg-collector-runtime/OrbSprint --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-collector-runtime/OrbSprint: ok
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-collector-runtime/OrbSprint --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-collector-runtime/OrbSprint: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-collector-regression-racing/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-collector-regression-racing/GameSpec.json --output Build/rkg-collector-regression-racing/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-collector-regression-racing/DesertChase: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-collector-regression-shooter/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-collector-regression-shooter/GameSpec.json --output Build/rkg-collector-regression-shooter/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-collector-regression-shooter/RoomBreach: ok
rtk git diff --check: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 200 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Registry formatı üçüncü adapter eklerken işe yaradı: template, state, rules, UI, scene binding ve screenshot seeding tek adapter kaydında toplandı; native archetype generator dosyaları büyümedi.

**Karar:**

Sıradaki RKG adapter işi `projectile` olabilir. Collector'dan sonra artık yarış, shooter ve pickup/timer eksenleri var; projectile adapter bu üçüne ek olarak travel/impact proof ve projectile role binding'i kapsamalı.

### Sprint 119: RKG Custom Runtime Adapter Registry

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit_runtime.py` modülü racing/shooter stringlerini tek büyük public fonksiyonlardan üretmeye başlamıştı. Üçüncü adapter eklemeden önce her system adapter state/rules/UI/scene binding parçalarını tek bir registry kaydında beyan etmeli.

**Yapılanlar:**

- Yeni `CustomRealityKitRuntimeAdapter` veri modeli eklendi.
- `custom_realitykit_runtime_adapters()` registry yüzeyi eklendi; şu an `racing` ve `shooter` kayıtlarını sıralı döndürüyor.
- `custom_realitykit_state_fields()`, `custom_realitykit_rule_members()`, `custom_realitykit_adapter_content_sections()`, ve `custom_realitykit_game_scene_controller_swift()` artık registry kayıtlarından compose ediyor.
- Racing ve shooter adapter'ları kendi `systems`, state field, rule member, ContentView section, scene property, scene binding, session dispatch, screenshot dispatch, ve scene update method parçalarını tek yerde taşıyor.
- `Tests/test_rkg_custom_realitykit_runtime.py` registry kontratını kapsayacak şekilde genişletildi; test önce eksik API import hatasıyla kırıldı.
- `CHANGELOG.md`, `Docs/ai-handoff.md`, `Docs/rkg-architecture.md`, ve `Docs/rkg-generic-skeleton.md` registry sınırını anlatacak şekilde güncellendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime: expected red before registry API; then ok, 2 tests
rtk .venv/bin/python -m ruff check src/rkg/custom_realitykit_runtime.py Tests/test_rkg_custom_realitykit_runtime.py: ok
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_racing_runtime_adapter_for_custom_realitykit Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_shooter_runtime_adapter_for_custom_realitykit: ok, 2 tests
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-registry-racing/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-registry-racing/GameSpec.json --output Build/rkg-registry-racing/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-registry-racing/DesertChase: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-registry-shooter/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-registry-shooter/GameSpec.json --output Build/rkg-registry-shooter/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-registry-shooter/RoomBreach: ok
rtk git diff --check: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 197 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Adapter ekleme işi artık tek bir büyük Swift string patch'i değil, bir registry kaydı ekleme işi haline geldi. Bu, `collect,score,timer` veya `projectile` gibi üçüncü adapter'ı küçük tutmak için gerekli ara katman.

**Karar:**

Sıradaki RKG davranış işi yeni registry şeklini kullanarak küçük bir üçüncü adapter eklemek olmalı. Öncelik `collect,score,timer`: yarış ve shooter'dan farklı olarak item/pickup role binding, skor artışı, timer proof ve sonuç state'i gösterebilir.

### Sprint 118: RKG Custom Runtime Adapter Module Split

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Racing ve FPS/shooter adapter'ları çalışır haldeyken üçüncü adapter eklemeden önce `custom_realitykit` generator ownership sınırını temizlemek; state/rules/UI/scene stringleri `archetype_runtime.py`, `content_views.py`, ve `scaffold.py` içinde büyümeye devam etmemeli.

**Yapılanlar:**

- Yeni `src/rkg/custom_realitykit_runtime.py` modülü eklendi.
- `custom_realitykit` state field listesi, racing/shooter rule member listesi, adapter UI content sections ve custom RealityKit scene controller üretimi bu modüle taşındı.
- `archetype_runtime.py` artık custom state/rules için sadece `custom_realitykit_state_fields()` ve `custom_realitykit_rule_members()` çağırıyor.
- `content_views.py` generic custom ContentView içinde adapter UI bloklarını `custom_realitykit_adapter_content_sections()` ile alıyor.
- `scaffold.py` custom scene controller üretimini `custom_realitykit_game_scene_controller_swift(spec)` fonksiyonuna devrediyor.
- Yeni modül sınırını korumak için `Tests/test_rkg_custom_realitykit_runtime.py` eklendi; test önce import hatasıyla kırıldı, modül taşınması sonrası geçti.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime: expected red before module; then ok
rtk .venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_racing_runtime_adapter_for_custom_realitykit Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_shooter_runtime_adapter_for_custom_realitykit: ok, 3 tests
rtk .venv/bin/python -m ruff check src/rkg/custom_realitykit_runtime.py src/rkg/archetype_runtime.py src/rkg/content_views.py src/rkg/scaffold.py Tests/test_rkg_custom_realitykit_runtime.py Tests/test_rkg_init_game.py: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-refactor-racing/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-refactor-racing/GameSpec.json --output Build/rkg-refactor-racing/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-refactor-racing/DesertChase: ok
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-refactor-racing/DesertChase --device booted: ok after sandbox escalation, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-refactor-racing/DesertChase: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-refactor-shooter/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-refactor-shooter/GameSpec.json --output Build/rkg-refactor-shooter/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-refactor-shooter/RoomBreach: ok
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-refactor-shooter/RoomBreach --device booted: ok after sandbox escalation, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-refactor-shooter/RoomBreach: ok, 4 screenshots
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 196 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Racing ve shooter adapter'ları çalışır haldeyken refactor yapmak, yeni davranış eklerken generator'ı büyütmekten daha güvenli oldu. Artık native archetype generator dosyaları custom systems adapter ayrıntılarıyla şişmiyor; RKG'nin sonraki system adapter'ı daha net bir ownership sınırından eklenebilir.

**Karar:**

Bir sonraki RKG davranış işi için iki yol var: aynı modül içinde üçüncü küçük adapter (`collect,score,timer` veya `projectile`) ya da `custom_realitykit_runtime.py` içindeki racing/shooter bölümlerini alt adapter listesine ayırmak. Yeni büyük adapterdan önce ikinci seçenek daha sağlıklı.

### Sprint 117: RKG FPS/Shooter Runtime Adapter

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit` generic runtime core üstüne ikinci system-specific adapter'ı eklemek: `weapon,hitscan,enemies,health,cover` seçen bir kullanıcı sıfırdan aim/fire/health/cover state'i olan, screenshot state'leri farklı görünen, derlenebilir RealityKit FPS/shooter iskeleti üretebilmeli.

**Yapılanlar:**

- `custom_realitykit` state'ine shooter alanları eklendi: `shooterHealth`, `enemiesRemaining`, `shotsFired`, `aimLane`, `enemyLane`, `isTakingCover`, `isShooterDefeated`, ve `lastShotHit`.
- `GameRules.swift` artık weapon/enemy/health/cover seçildiğinde `startShooterSession`, `aimLaneAfterMove`, `fireShooterWeapon`, `toggleShooterCover`, `applyShooterDamage`, `advanceShooterFrame`, ve `shooterScreenshotSession` üretiyor.
- `ContentView.swift` shooter seçildiğinde health/enemies/shots/aim HUD satırı, Aim Left/Aim Right ve Cover kontrolleri üretiyor.
- `GameSceneController.swift` custom path'i shooter adapter'a genişledi: player/weapon/enemy/cover entity referansları bağlanıyor; aim lane, enemy lane, hit, cover ve defeated state'i RealityKit pozisyon/scale/enabled değişikliklerine yansıyor.
- Racing adapter regresyonu korundu; `racing` seçildiğinde racing branch hâlâ öncelikli.
- Test önce `shooterHealth` eksikliğinden kırıldı, sonra shooter adapter generated Swift yüzeyi yeşile alındı.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_shooter_runtime_adapter_for_custom_realitykit: expected red before adapter; then ok
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game Tests.test_rkg_runtime_core Tests.test_rkg_new_game: ok, 38 tests
rtk .venv/bin/python -m ruff check src/rkg/archetype_runtime.py src/rkg/content_views.py src/rkg/scaffold.py Tests/test_rkg_init_game.py: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-shooter-runtime/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-shooter-runtime/GameSpec.json --output Build/rkg-shooter-runtime/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-shooter-runtime/RoomBreach: ok
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-shooter-runtime/RoomBreach --device booted: ok after sandbox escalation, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-shooter-runtime/RoomBreach: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-racing-regression/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-racing-regression/GameSpec.json --output Build/rkg-racing-regression/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-racing-regression/DesertChase: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 195 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Generic `custom_realitykit` artık iki system adapter ile çalışıyor: racing ve FPS/shooter. Bu, `new-game` yönünü doğruluyor; kullanıcı broad bir oyun fikri verdiğinde RKG boş Xcode projesi değil, seçilen systems set'ine göre state + UI + RealityKit binding + screenshot proof üreten bir başlangıç veriyor.

**Karar:**

Bir sonraki RKG işi yeni adapter eklemekten önce custom adapter üretimini modüllere bölmek olmalı. `archetype_runtime.py`, `content_views.py`, ve `scaffold.py` içinde racing/shooter stringleri büyümeye başladı; üçüncü adapterdan önce generator ownership sınırı temizlenmeli.

### Sprint 116: RKG Racing Runtime Adapter

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit` generic runtime core üstüne ilk system-specific adapter'ı eklemek: `racing,lap_timer,collision` seçen bir kullanıcı sıfırdan lane/lap/checkpoint/collision state'i olan, screenshot state'leri farklı görünen, derlenebilir RealityKit yarış iskeleti üretebilmeli.

**Yapılanlar:**

- `custom_realitykit` state'ine racing alanları eklendi: `raceDistance`, `currentLap`, `checkpointIndex`, `vehicleLane`, `obstacleLane`, ve `isRaceCollision`.
- `GameRules.swift` artık racing seçildiğinde `startRacingSession`, `laneAfterSteer`, `advanceRacingFrame`, `racingScreenshotSession`, checkpoint/lap scoring ve collision-result proof üretiyor.
- `ContentView.swift` generic custom overlay içinde racing seçildiğinde lap, distance, checkpoint, lane HUD satırı ve Left/Right lane steering kontrolleri üretiyor.
- `GameSceneController.swift` custom path'i racing adapter'a ayrıldı: vehicle/track/obstacle/checkpoint entity referansları bağlanıyor, `CameraRig.transform` scene içindeki camera rig entity'sine uygulanıyor, distance/lane/checkpoint/collision state'i RealityKit pozisyon/scale/enabled değişikliklerine yansıyor.
- Non-racing `custom_realitykit` yolu korunup generic state-bound overlay ile derlenmeye devam ediyor.
- Test önce `raceDistance` eksikliğinden kırıldı, sonra racing adapter generated Swift yüzeyi yeşile alındı.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_racing_runtime_adapter_for_custom_realitykit: expected red before adapter; then ok
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game Tests.test_rkg_runtime_core Tests.test_rkg_new_game: ok, 37 tests
rtk .venv/bin/python -m ruff check src/rkg/archetype_runtime.py src/rkg/content_views.py src/rkg/scaffold.py Tests/test_rkg_init_game.py: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-racing-runtime/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-racing-runtime/GameSpec.json --output Build/rkg-racing-runtime/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-racing-runtime/DesertChase: ok
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-racing-runtime/DesertChase --device booted: ok after sandbox escalation, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-racing-runtime/DesertChase: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health,cover --output Build/rkg-fps-runtime/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fps-runtime/GameSpec.json --output Build/rkg-fps-runtime/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fps-runtime/RoomBreach: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 194 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Generic RealityKit üretimi için doğru ara katman `systems` bazlı adapter. Racing artık `new-game` için sadece asset/fallback planı değil, generated state + UI + scene binding + screenshot proof üretiyor. FPS/weapon tarafı halen generic core üstünde derlenen skeleton; bir sonraki runtime adapter oraya eklenmeli.

**Karar:**

`custom_realitykit` içinde system-specific davranışlar tek bir placeholder branch'e yığılmayacak. Racing ilk adapter olarak kaldı; sıradaki anlamlı slice `weapon/hitscan/enemies/health/cover` için FPS/shooter adapter veya mevcut racing adapter'ı ayrı generator modülüne çıkarmak.

### Sprint 115: RKG Generic Runtime Core

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `custom_realitykit` çıktısını yalnızca metadata ve placeholder role üretmekten çıkarıp generated Swift tarafında camera/input/system core dosyaları, state-bound UI, ve screenshot-state seeding ile doğrulanabilir runtime iskeletine taşımak.

**Yapılanlar:**

- Generated projelere `CameraRig.swift`, `InputController.swift`, ve `SystemFlags.swift` eklendi.
- `CameraRig` seçilen camera id'si için compile-safe `Transform` sözleşmesi üretiyor; `ARView.cameraTransform` setter kullanılmadı çünkü API get-only.
- `InputController` seçilen input modelinden `supportsDrag`, `supportsTilt`, `primaryActionLabel`, ve `controlSummary` üretiyor.
- `SystemFlags` selected systems set'ini Swift'e taşıyor ve racing/lap/collision/weapon/enemy/health/cover boolean'ları üretiyor.
- `custom_realitykit` artık `GameView(state: state)` kullanıyor; generic `ContentView` state-bound overlay, score, input summary, system summary ve reset/result yüzeyi gösteriyor.
- `custom_realitykit` state/rules eklendi: `primaryActions`, `isFailureProofVisible`, `startCustomRealityKitSession`, `advanceCustomRealityKitSession`, ve `customRealityKitScreenshotSession`.
- `capture-screenshots` ile gelen `--rkg-screenshot-state` generic skeleton state'ini artık `gameplay_start`, `mid_action`, `fail_or_hit`, ve `results` için seed ediyor.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_runtime_core Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_generic_runtime_core_modules Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots: expected red before runtime core implementation; then ok
rtk .venv/bin/python -m unittest Tests.test_rkg_runtime_core Tests.test_rkg_new_game Tests.test_rkg_init_game Tests.test_rkg_plan_game Tests.test_rkg_scaffold_generators: ok, 48 tests
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-runtime-core-racing/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-runtime-core-racing/GameSpec.json --output Build/rkg-runtime-core-racing/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-runtime-core-racing/DesertChase: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-runtime-core-racing/DesertChase --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-runtime-core-racing/DesertChase: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health --output Build/rkg-runtime-core-fps/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-runtime-core-fps/GameSpec.json --output Build/rkg-runtime-core-fps/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-runtime-core-fps/RoomBreach: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-runtime-core-fps/RoomBreach --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-runtime-core-fps/RoomBreach: ok, 4 screenshots
```

**Öğrenme notu:**

RealityKit non-AR camera tarafında `ARView.cameraTransform` assignment get-only olduğu için generic `CameraRig` bu sprintte transform contract'ını üretip `GameView` içinde compile-safe configure hook'u sağlıyor. Sonraki doğru adım bu contract üstüne gerçek camera entity/anchor bağlamak; önce generated project compile ve screenshot gates'i kırmamak gerekiyor.

**Karar:**

Sprint 116 racing runtime'a geçebilir ama önce `CameraRig`/`InputController`/`SystemFlags` bu shared core olarak kalacak. Genre-specific behavior `scaffold.py` içine büyütülmeden system adapter katmanına taşınmalı.

### Sprint 114: Generic RealityKit Skeleton Generator

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** RKG'yi sadece fighter veya target shooter hattı olmaktan çıkarıp, yarış/FPS/shooter gibi broad RealityKit fikirleri için `camera + input + systems` üzerinden sıfırdan skeleton GameSpec ve generated project üretebilen ilk generic tool dilimine taşımak.

**Yapılanlar:**

- `rkg new-game --title ... --camera ... --input ... --systems ... --output ...` komutu eklendi.
- `custom_realitykit` registry kaydı eklendi: `fixed_non_ar`, `chase`, `first_person`, `third_person`, `top_down` camera; `tap`, `drag`, `tilt_tap`, `dual_stick`, `gamepad_touch`, `tap_swipe` input; racing/shooter/physics/health/cover gibi sistemler.
- Racing skeleton `player_vehicle`, `race_track`, `track_obstacle`, `checkpoint_gate` rolleriyle; FPS/shooter skeleton `player_proxy`, `arena_space`, `weapon_proxy`, `enemy_proxy`, `cover_block` rolleriyle üretilebiliyor.
- `new-game` unsupported system, camera ve input değerlerini spec yazmadan önce reddediyor.
- Generated runtime entity planı artık asset'in declared fallback id'sini taşıyor; `AssetLoader` ve `FallbackFactory` role yanında fallback id ile de placeholder mesh seçiyor.
- Vehicle, weapon, enemy, cover, track/gate gibi generic fallback primitive'leri eklendi.
- `Docs/rkg-generic-skeleton.md` generic racing/FPS walkthrough olarak eklendi; `Docs/game-factory.md`, `Docs/game-spec.md`, `Docs/rkg-architecture.md`, `Docs/ai-handoff.md`, ve `CHANGELOG.md` güncellendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_new_game Tests.test_rkg_archetypes: ok, 12 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_passes_declared_fallbacks_to_runtime_loader: expected red before fallback runtime fix; then ok
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_passes_declared_fallbacks_to_runtime_loader Tests.test_rkg_scaffold_generators Tests.test_rkg_plan_game: ok, 13 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_new_game Tests.test_rkg_init_game Tests.test_rkg_plan_game Tests.test_rkg_archetypes Tests.test_rkg_scaffold_generators: ok, 51 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 189 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
rtk .venv/bin/python Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output Build/rkg-generic-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-generic-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-generic-final/GameSpec.json --output Build/rkg-generic-final/DesertChase --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-generic-final/DesertChase: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-generic-final/DesertChase --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-generic-final/DesertChase: ok, 4 screenshots
rtk .venv/bin/python Tools/rkg.py new-game --title "Room Breach" --camera first_person --input dual_stick --systems weapon,hitscan,enemies,health --output Build/rkg-generic-fps-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-generic-fps-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-generic-fps-final/GameSpec.json --output Build/rkg-generic-fps-final/RoomBreach --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-generic-fps-final/RoomBreach: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-generic-fps-final/RoomBreach --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-generic-fps-final/RoomBreach: ok, 4 screenshots
```

**Öğrenme notu:**

Generic generator için doğru ilk hedef full racing/FPS gameplay değil, boş Xcode projesi yerine doğrulanabilir RealityKit skeleton üretmek. `new-game` ile kullanıcı camera/input/systems seçiyor; RKG valid spec, role-aware placeholder mesh, asset brief, store/QA docs, build gate ve screenshot gate'i hazırlıyor. Sonraki anlamlı slice `CameraRig.swift`, `InputController.swift`, vehicle movement, first-person aim, projectile/hitscan, health ve collision adapter'ları.

**Karar:**

RKG ürün yönü iki kola ayrıldı: `new-spec` native archetype template üretir, `new-game` generic `custom_realitykit` skeleton üretir. Generic skeleton shipping claim değildir; runtime sistemleri derinleşene kadar üretilebilir başlangıç projesi ve QA kontratı olarak konumlanacak.

### Sprint 113: RKG Fighter Zero-to-Skeleton Path

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Sıfırdan gelen kullanıcının JSON kopyalamadan `fighter_2_5d` GameSpec üretmesi, RealityKit projesi scaffold etmesi, generated app'i doğrulaması ve simulator screenshot kanıtlarını RKG ile capture etmesi.

**Yapılanlar:**

- `rkg new-spec fighter_2_5d --title ... --output ...` komutu eklendi.
- Generated `init-game` çıktısı her role asset için `Docs/assets/<asset_id>.md` brief dosyası yazıyor.
- `rkg capture-screenshots` dry-run planı ve gerçek simulator execution path'i eklendi.
- `verify-screenshots` header-only fake image dosyalarını reddedecek şekilde JPEG/PNG dimension kontrolü kazandı.
- `Docs/rkg-fighter-walkthrough.md` sıfırdan fighter skeleton akışını belgeliyor.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_new_spec Tests.test_rkg_validate_spec: ok, 8 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_writes_role_asset_briefs Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_fighter_state_and_rules: ok, 2 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_capture Tests.test_rkg_qa_plan: ok, 6 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_screenshot_status: ok, 5 tests
rtk .venv/bin/python Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter-capture/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-capture/GameSpec.json --output Build/rkg-fighter-capture/NeonRingDuel --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-capture/NeonRingDuel: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-fighter-capture/NeonRingDuel --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter-capture/NeonRingDuel: ok, 4 screenshots
rtk .venv/bin/python -m unittest discover -s Tests: ok, 182 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
rtk .venv/bin/python Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-fighter-final/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-final/GameSpec.json --output Build/rkg-fighter-final/NeonRingDuel --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-final/NeonRingDuel: ok
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-fighter-final/NeonRingDuel --device booted: ok, 4 simulator screenshots
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter-final/NeonRingDuel: ok, 4 screenshots
```

**Öğrenme notu:**

Fighter skeleton için kritik eksik yeni archetype değil, sıfırdan başlama yüzeyi ve gerçek screenshot automation kapısıydı. `new-spec` ve `capture-screenshots` birlikte JSON kopyalama ve manuel simulator adımlarını azaltıyor.

### Sprint 112: Module 4 Metallic Value Comparison

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** `material_response_targets` asset'ini roughness value/map karşılaştırmasından dört panelli material-response dersine genişletmek; metallic'i önce texture map değil material value olarak kanıtlamak.

**Yapılanlar:**

- Direct USDZ fallback builder dördüncü `metallic_value_panel` mesh'ini üretir hale getirildi.
- Material block sözleşmesine `metallic_value` parametresi eklendi; yeni panel `metallic=1.0`, `roughness=0.18` kullanıyor.
- Blender starter script'i ve RealityKit procedural fallback'i aynı dört panel düzenine hizalandı.
- Manifest, asset brief, guide, checklist, handoff, changelog ve guide PDF güncellendi.
- `material_response_targets.usdz` yeniden üretildi, simulator screenshot yenilendi ve asset tekrar accepted edildi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_material_response_fallback_uses_readable_roughness_values Tests.test_rkp_project.RkpProjectTests.test_material_response_fallback_meshes_include_curved_specular_witnesses Tests.test_fixture_refactor.FixtureRefactorTests.test_material_response_showcase_keeps_metallic_as_material_value: ok, 3 tests
rtk .venv/bin/python Tools/rkp.py build-asset material_response_targets --fallback-only: ok, 28730-byte USDZ
rtk .venv/bin/python Tools/rkp.py inspect-usdz material_response_targets --json: ok, 1664 triangles, baseColor 512x512, roughness 512x512, st UV present
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok, CoreSimulator sandbox warnings only
rtk xcrun simctl install FF329D84-0179-49E2-AFC4-12D4935845FC Build/DerivedData/Build/Products/Debug-iphonesimulator/RealityKitPipelineDemo.app: ok
rtk xcrun simctl launch --terminate-running-process FF329D84-0179-49E2-AFC4-12D4935845FC com.kyylian.RealityKitPipelineDemo --material-response-mode: ok
rtk xcrun simctl io FF329D84-0179-49E2-AFC4-12D4935845FC screenshot /Users/kyylian/Developer/RealityKitPipelineDemo/Docs/screenshots/material_response_targets.png: ok
rtk .venv/bin/python Tools/rkp.py accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.png: ok
rtk make guide: ok, PDF regenerated with Fontconfig/CSS warnings only
rtk .venv/bin/python -m unittest discover -s Tests: ok, 176 tests
rtk .venv/bin/python Tools/rkp.py release-check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
rtk pdfinfo Docs/pdf/realitykit-pipeline-guide.pdf: ok, 31 pages, 717737 bytes
```

**Öğrenme notu:**

Metallic öğrenimi map eklemekle başlamak zorunda değil. Yeni başlayan için daha iyi ilk adım aynı ışık/kamera/mesh altında tek material value değişikliğini görsel olarak kanıtlamak; per-pixel metallic map ancak asset brief gerçek metal/non-metal ayrımı istediğinde ayrı slice olmalı.

**Karar:**

Module 4'te sıradaki anlamlı konu ya gerçek metallic map ihtiyacı değerlendirmesi ya da normal-map export behavior olmalı. Aynı sprintte birden fazla yeni material map açılmayacak.

### Sprint 111: RKG Fighter Screenshot Gate Closure

**Durum:** Tamamlandı
**Tarih:** 2026-05-11
**Amaç:** Sprint 110'da eklenen `fighter_2_5d` archetype'ını gerçek simulator screenshot evidence ve `verify-screenshots` gate'iyle kapatmak.

**Yapılanlar:**

- Generated `ScreenshotState.swift` artık `RKG_SCREENSHOT_STATE` env'i ve `--rkg-screenshot-state <state>` launch arg'ını okuyabiliyor.
- Fighter runtime'a screenshot-state seed helper eklendi; `round_start`, `mid_combo`, `perfect_dodge`, ve `knockout` state'leri simulator launch sırasında kurulabiliyor.
- Fighter HUD mobil screenshot için toparlandı: uzun action metni kaldırıldı, kontrol butonları compact hale getirildi ve result state'te gereksiz kontrol satırı gizlendi.
- `qa-plan --json` fighter screenshot adımlarında launch automation hint'i veriyor.
- `Build/rkg-fighter-native/NeonRingDuel` yeniden üretildi, iPhone 17 Pro simulator'da dört screenshot state'i capture edildi ve `verify-screenshots` geçti.
- Public kanıt olarak `Docs/screenshots/rkg_fighter_round_start.jpg`, `Docs/screenshots/rkg_fighter_mid_combo.jpg`, `Docs/screenshots/rkg_fighter_perfect_dodge.jpg`, ve `Docs/screenshots/rkg_fighter_knockout.jpg` eklendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest discover -s Tests -p 'test_rkg*.py': ok, 95 tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
rtk .venv/bin/python Tools/rkg.py qa-plan Build/rkg-fighter-native/GameSpec.json --json: ok, launch_arg automation listed for all fighter screenshot states
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-native/GameSpec.json --output Build/rkg-fighter-native/NeonRingDuel --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-native/NeonRingDuel: ok
rtk xcrun simctl launch --terminate-running-process FF329D84-0179-49E2-AFC4-12D4935845FC com.kyylian.neonringduel --rkg-screenshot-state round_start: ok
rtk xcrun simctl launch --terminate-running-process FF329D84-0179-49E2-AFC4-12D4935845FC com.kyylian.neonringduel --rkg-screenshot-state mid_combo: ok
rtk xcrun simctl launch --terminate-running-process FF329D84-0179-49E2-AFC4-12D4935845FC com.kyylian.neonringduel --rkg-screenshot-state perfect_dodge: ok
rtk xcrun simctl launch --terminate-running-process FF329D84-0179-49E2-AFC4-12D4935845FC com.kyylian.neonringduel --rkg-screenshot-state knockout: ok
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter-native/NeonRingDuel --json: ok, 4/4 JPEG screenshots
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok, CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

RKG screenshot QA yalnızca dosya varlığını kontrol ederse loop yarım kalıyor. En küçük sağlam kapanış, generated app'in state'i launch argument ile kurması ve simulator screenshot'ın bu state üstünden alınması. Bu, manual tap kırılganlığını azaltırken `verify-screenshots` kapısını gerçek görüntü kanıtıyla besliyor.

**Karar:**

Fighter thread artık archetype + generated gameplay + screenshot evidence açısından kapandı. RKG tarafında devam edilecekse sonraki iş asset art/import veya ürün kalitesi incelemesi olmalı; varsayılan ana ürün yolu yine RKP Module 4 material response.

### Sprint 110: Native RKG 2.5D Fighter Archetype

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** RKG'nin target shooter fixture'ına sıkışmadığını göstermek için sıfırdan üretilecek 2.5D fighter fikrini native archetype olarak eklemek.

**Yapılanlar:**

- `fighter_2_5d` registry kaydı eklendi: fixed side-view duel, `tap_swipe` input, `player`/`opponent`/`arena` zorunlu rolleri ve `round_start`, `mid_combo`, `perfect_dodge`, `knockout` screenshot state'leri.
- Generated Swift runtime için fighter state/rules kontratı eklendi: health, combo, guard meter, dodge, hit scoring ve knockout/result transition.
- `init-game` çıktısına playable fighter loop eklendi: Attack, Dodge, Damage test input, Reset, result overlay ve swipe/tap dodge inputları.
- Generated RealityKit scene binding fighter rollerine genişletildi: player/opponent pozisyonları, hit VFX visibility, guard cue visibility ve procedural role fallback'leri.
- `plan-game` runtime entity pozisyonları fighter rolleri için rol-aware hale getirildi.
- `Build/rkg-fighter-native/NeonRingDuel` scratch projesiyle native spec doğrulandı; `validate-spec`, `plan-game`, `qa-plan`, `init-game`, ve `verify-game` geçti.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_archetypes.RkgArchetypeTests.test_registry_lists_seed_archetypes Tests.test_rkg_archetypes.RkgArchetypeTests.test_fighter_2_5d_exposes_duel_roles_input_and_screenshot_proofs Tests.test_rkg_validate_spec.RkgValidateSpecCliTests.test_validate_spec_cli_accepts_fighter_2_5d_spec Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_fighter_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_fighter_content_view_contract_is_outside_scaffold: ok, 5 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_fighter_runtime_entities_and_proofs Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_fighter_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_fighter_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_fighter_state_to_realitykit_scene: ok, 4 tests
rtk .venv/bin/python -m unittest Tests/test_rkg_archetypes.py Tests/test_rkg_archetype_runtime.py Tests/test_rkg_content_views.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py Tests/test_rkg_init_game.py: ok, 54 tests
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-fighter-native/GameSpec.json --json: ok
rtk .venv/bin/python Tools/rkg.py plan-game Build/rkg-fighter-native/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py qa-plan Build/rkg-fighter-native/GameSpec.json: ok
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-native/GameSpec.json --output Build/rkg-fighter-native/NeonRingDuel --force: ok
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-native/NeonRingDuel: ok
```

**Öğrenme notu:**

RKG'yi production oyun motoru gibi düşünmeden önce archetype sözleşmesini test etmek daha ucuz. Fighter için doğru ilk slice animasyon sistemi değil; input, state, role fallback, scene binding ve screenshot QA contract'ının uçtan uca çalışması.

**Karar:**

Gerçek simulator screenshot gate'i Sprint 111 ile kapandı. RKP ana ürün yoluna dönülürse Module 4 material slice önceliği korunacak.

### Sprint 109: Roughness Readability Polish

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** `material_response_targets` screenshot'ında roughness farkını teknik doğrulamadan görsel öğretime taşımak.

**Yapılanlar:**

- Direct USDZ fallback mesh'lerine küçük curved specular witness eklendi; triangle bütçesi 1248/1800 olarak kaldı.
- Matte/glossy roughness değerleri daha ayrık hale getirildi: `0.98` ve `0.04`.
- Roughness texture daha yüksek kontrastlı üretildi.
- BaseColor texture içinde dairesel nötr witness patch eklendi; ana hedef ring dili korunurken material response daha net okunuyor.
- `MaterialResponseShowcase` tek point light yerine grazing + rim point light düzeni kullanacak şekilde güncellendi.
- Simulator screenshot yenilendi ve asset yeniden accepted edildi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_material_response_fallback_uses_readable_roughness_values Tests.test_rkp_project.RkpProjectTests.test_material_response_fallback_meshes_include_curved_specular_witnesses Tests.test_rkp_project.RkpProjectTests.test_roughness_texture_uses_extreme_map_contrast Tests.test_rkp_project.RkpProjectTests.test_material_response_basecolor_includes_neutral_witness_patch: ok, 4 tests
rtk .venv/bin/python -m unittest Tests.test_fixture_refactor.FixtureRefactorTests.test_material_response_showcase_uses_grazing_lights_for_roughness_readability: ok
rtk .venv/bin/python Tools/rkp.py build-asset material_response_targets --fallback-only: ok, 25981-byte USDZ
rtk .venv/bin/python Tools/rkp.py inspect-usdz material_response_targets --json: ok, 1248 triangles, baseColor 512x512, roughness 512x512, st UV present
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok, CoreSimulator sandbox warnings only
rtk xcrun simctl launch 1209CEA7-6253-43D7-A6B3-9B755F09BDB1 com.kyylian.RealityKitPipelineDemo --material-response-mode: ok
rtk xcrun simctl io 1209CEA7-6253-43D7-A6B3-9B755F09BDB1 screenshot /Users/kyylian/Developer/RealityKitPipelineDemo/Docs/screenshots/material_response_targets.png: ok
rtk .venv/bin/python Tools/rkp.py accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.png: ok
```

**Öğrenme notu:**

Roughness map paketlemek tek başına iyi bir öğretim screenshot'ı üretmez. Düz target yüzeyi yerine küçük curved witness ve grazing light kullanmak, aynı asset kontratını bozmadan material response farkını görünür hale getirir.

**Karar:**

Module 4'ün bir sonraki slice'ında roughness'i tekrar genişletmek yerine metallic value comparison veya normal-map export behavior seçilecek; her seferinde tek material konusu ve screenshot evidence korunacak.

### Sprint 108: Module 4 Material Response First Slice

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Base color sonrası ilk material response dersini roughness value ve roughness map karşılaştırmasıyla doğrulamak.

**Yapılanlar:**

- `inspect-usdz` configured material maps raporlayacak şekilde genişletildi; `baseColorTexture` alias'ı geriye dönük uyumluluk için korundu.
- `material_response_targets` asset kontratı, Blender script'i, manifest kaydı ve brief'i eklendi.
- Blender 4.5.8 LTS background export yine startup sırasında segfault verdi; direct USDZ fallback builder configured `baseColor` + `roughness` map paketleyecek şekilde genişletildi.
- RealityKit fixture'a sadece `--material-response-mode` ile çalışan opt-in showcase eklendi; normal target fallback sırası değişmedi.
- Simulator screenshot ile asset kabul edildi.

**Acceptance:**

- USDZ: `Assets/Imported/material_response_targets.usdz`
- Screenshot: `Docs/screenshots/material_response_targets.png`
- Manifest status: `imported`

**Verification:**

```text
pipx install --force git+https://github.com/kingkyylian/realitykitpipelineguide.git@v0.2.1: installed package rkp 0.2.1
rkp --version: rkp 0.2.1
rkp init --project-name SmokeGame: ok in /private/tmp/rkp-v021-smoke-opf5Y5
rkp doctor --json: ok, 0 errors, 3 expected recommended-path warnings in minimal project
rkp build-asset smoke_drone --fallback-only: ok, 16068-byte USDZ
rkp inspect-usdz smoke_drone --json: ok, 804 triangles, 512x512 baseColor, st UV present
rtk .venv/bin/python -m unittest Tests/test_release_docs.py: ok, 6 tests
rtk .venv/bin/python -m unittest Tests/test_rkp_project.py: ok, 23 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 159 tests before fallback builder update; ok, 161 tests inside release-check after fallback builder update
rtk .venv/bin/python Tools/rkp.py build-asset material_response_targets: Blender segfaulted, direct USDZ fallback built 20281-byte USDZ
rtk .venv/bin/python Tools/rkp.py inspect-usdz material_response_targets --json: ok, baseColor 512x512, roughness 512x512, triangles=576, st UV present
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok, CoreSimulator sandbox warnings only
rtk xcrun simctl launch 1209CEA7-6253-43D7-A6B3-9B755F09BDB1 com.kyylian.RealityKitPipelineDemo --material-response-mode: ok
rtk xcrun simctl io 1209CEA7-6253-43D7-A6B3-9B755F09BDB1 screenshot /Users/kyylian/Developer/RealityKitPipelineDemo/Docs/screenshots/material_response_targets.png: ok
rtk .venv/bin/python Tools/rkp.py accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.png: ok
rtk .venv/bin/python Tools/rkp.py release-check --assets: ok, 161 tests, imported assets inspected, Xcode build ok
```

**Öğrenme notu:**

Asset kabulü dosyanın oluşmasıyla değil, runtime evidence ve manifest/worklog kaydıyla tamamlanır. Bu slice baseColor ve roughness map paket sözleşmesini kanıtladı; screenshot'ta üç material-response paneli front-facing ve target fallback'lerden ayrı görünüyor. Roughness ayrımı mevcut fixture ışığında sınırlı okunuyor, bu yüzden Module 4'ün sonraki adımı map sayısını artırmak değil ışık açısı, yüzey formu veya kamera düzenini iyileştirmek olmalı.

**Karar:**

Blender background export referans makinede güvenilir değilken direct fallback yalnızca baseColor varsaymamalı. Manifest `textureMaps` ne istiyorsa fallback draft o map dosyalarını pakete koymalı; yine de screenshot acceptance görsel son kapı olarak kalır.

### Sprint 107: RKP Tool Evaluation Before Module 4

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Module 4'e geçmeden önce RKP tool'unu yayınlanmış `v0.2.0` haliyle ve yerel patch adayıyla gerçekçi dış kullanıcı akışlarında test etmek.

**Bulgular:**

- `v0.2.0` GitHub tag install çalışıyor ama package metadata `0.1.0`; `rkp --version` yanlış release kimliği gösteriyor.
- `v0.2.0` `accept-asset` yalnızca dosya varlığını kontrol ettiği için JSON içerikli `.jpg` dosyasını screenshot evidence olarak kabul ediyor.
- Temiz dış proje bootstrap, prompt asset, `--fallback-only` USDZ build, inspect, verify, valid screenshot accept ve `release-check --assets` akışı çalışıyor.
- Minimal dış projede `release-check` test/Xcode yoksa skip edip OK veriyor; bu portability için iyi ama production readiness olarak okunmamalı.

**Yapılanlar:**

- `Docs/tool-evaluation-v0.2.0.md` raporu eklendi.
- `Docs/releases/v0.2.1.md` patch release taslağı eklendi.
- `accept-asset` PNG/JPEG header doğrulamasıyla sertleştirildi.
- Package/runtime metadata `0.2.1` patch adayına yükseltildi.
- Regression testleri eklendi/güncellendi.

**Verification:**

```text
/private/tmp/rkp-install-v020-a/bin/rkp --version: rkp 0.1.0, confirms published v0.2.0 mismatch
/private/tmp/rkp-install-local-021-a/bin/rkp --version: rkp 0.2.1
/private/tmp/rkp-install-local-021-a/bin/rkp accept-asset patch_drone --screenshot Docs/screenshots/not_an_image.jpg: rejected as not a valid PNG or JPEG image
/private/tmp/rkp-install-local-021-a/bin/rkp release-check --assets: ok in external project
rtk .venv/bin/python -m unittest Tests/test_release_docs.py Tests/test_rkp_cli.py Tests/test_rkp_package.py Tests/test_rkp_project.py: ok, 50 tests
rtk .venv/bin/python -m unittest Tests/test_tool_evaluation_docs.py Tests/test_release_docs.py Tests/test_public_polish_docs.py Tests/test_product_boundary_docs.py: ok, 14 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 155 tests
rtk make verify-local: ok, compileall + Ruff + 155 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check --assets: release-check ok; imported assets inspected; CoreSimulator sandbox warnings only
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

`v0.2.0` release geri yazılmayacak. Düzeltmeler `v0.2.1` patch release olarak yayınlandı; sonraki düzeltmeler yeni patch release ile yapılacak. Module 4'e geçmeden önce istenirse son bir temiz tag-install smoke test çalıştırılabilir.

### Sprint 104: v0.2.0 Release Candidate Notes

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Push/tag yapmadan, yereldeki `v0.2.0` release adayını changelog, GitHub showcase, release checklist, handoff ve ayrı release notes dosyasıyla netleştirmek.

**Plan:**

- Release dokümanlarının `v0.2.0` adayına baktığını testle koru.
- `CHANGELOG.md` içinde mevcut değişiklikleri `Unreleased` yerine `v0.2.0` draft bölümüne taşı.
- GitHub showcase ve repo release checklist dosyalarını eski `v0.1.0` publish akışından çıkar.
- `Docs/releases/v0.2.0.md` altında GitHub Release'e taşınabilir taslak metni hazırla.
- `Docs/ai-handoff.md` içinde sıradaki işi release candidate review olarak güncelle.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_release_docs.py: first run failed as expected; release draft and v0.2.0 checklist text were missing
rtk .venv/bin/python -m unittest Tests/test_release_docs.py: ok, 4 tests
rtk .venv/bin/python -m unittest Tests/test_public_polish_docs.py Tests/test_product_boundary_docs.py Tests/test_release_docs.py: ok, 13 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 151 tests
rtk make verify-local: ok, compileall + Ruff + 151 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

`v0.1.0` mevcut baseline olarak korunacak. Sıradaki yayın yerelde `v0.2.0` release candidate olarak hazır; push, tag ve GitHub Release sadece kullanıcı açıkça onaylarsa yapılacak.

### Sprint 105: v0.2.0 Publication Prep

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** `v0.2.0` release metnini draft durumundan final release note durumuna getirip push/tag/release sonrası bayat kalmayacak hale getirmek.

**Plan:**

- `CHANGELOG.md` içindeki `v0.2.0` başlığını draft etiketinden çıkar.
- `Docs/releases/v0.2.0.md` dosyasını GitHub Release body olarak kullanılabilecek final metne dönüştür.
- GitHub showcase ve release checklist dosyalarını “next draft” yerine yayın kopyası ve generic checklist olarak hizala.
- Release docs testlerini bu final metinle güncelle.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_release_docs.py: ok, 4 tests
rtk .venv/bin/python -m unittest Tests/test_public_polish_docs.py Tests/test_product_boundary_docs.py Tests/test_release_docs.py: ok, 13 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 151 tests
rtk make verify-local: ok, compileall + Ruff + 151 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

`Docs/releases/v0.2.0.md` artık GitHub Release body olarak kullanılabilecek final metin. Yayın sırası: `main` push, GitHub Actions sonucu bekleme, `v0.2.0` tag, GitHub Release.

### Sprint 106: GitHub Actions PEP 668 Fix

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** `v0.2.0` push sonrası GitHub Actions macOS runner'ında Homebrew-managed Python nedeniyle düşen dependency install adımını düzeltmek.

**Bulgu:**

```text
GitHub Actions run 25632680710 failed at "Install Python dev dependencies".
Root cause: python3 -m pip install -e ".[dev]" hit externally-managed-environment / PEP 668 on the macOS runner.
```

**Plan:**

- CI workflow içinde `.venv` oluştur.
- Dev install, Ruff ve unittest adımlarını `.venv/bin/python` üzerinden çalıştır.
- `pipeline doctor` CI kontrolünü virtualenv-backed test komutunu kabul edecek şekilde güncelle.
- Workflow metnini küçük bir testle koru.
- Release notes/changelog içine CI fix bilgisini dahil et.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_ci_workflow.py Tests/test_release_docs.py: ok, 5 tests
rtk .venv/bin/python -m unittest Tests/test_ci_workflow.py Tests/test_rkp_cli.py Tests/test_release_docs.py: ok, 14 tests
rtk .venv/bin/python Tools/rkp.py doctor --json: ok, errors 0
rtk .venv/bin/python -m unittest discover -s Tests: ok, 152 tests
rtk make verify-local: ok, compileall + Ruff + 152 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

CI sistem Python ortamına paket kurmayacak. GitHub Actions `.venv` kullanacak; `rkp doctor` hem eski `python3 -m unittest ...` hem yeni `.venv/bin/python -m unittest ...` test komutunu geçerli kabul edecek.

### Sprint 103: README Landing Refactor

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** README'yi full CLI manual olmaktan çıkarıp public landing sayfası gibi okunacak kısa bir vitrine dönüştürmek.

**Plan:**

- README landing davranışını testle koru: kısa dosya, az ana heading, `Docs/cli-tool.md` ve production/handoff linkleri.
- Tekrarlanan prompt, asset loop, common commands ve folder map bölümlerini README'den kaldır.
- Normal RKP path, product boundary, fixture evidence, docs map ve known limits bölümlerini koru.
- Detaylı CLI kullanımını `Docs/cli-tool.md` altında canonical bırak.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_public_polish_docs.PublicPolishDocsTests.test_readme_is_concise_landing_page_not_full_cli_manual: first run failed as expected; README was 578 lines
rtk .venv/bin/python -m unittest Tests/test_public_polish_docs.py Tests/test_product_boundary_docs.py: ok, 9 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 147 tests
rtk make verify-local: ok, compileall + Ruff + 147 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

README hızlı güven ve yönlendirme yüzeyi olacak; command reference `Docs/cli-tool.md`, öğrenme anlatısı `Docs/guide.md`, üretim gate'leri `Docs/production-playbook.md` içinde kalacak.

### Sprint 102: Explicit Fallback Build Path

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Blender background export sorunlu olduğunda fallback davranışını sadece otomatik recovery olmaktan çıkarıp bilinçli CLI seçeneği yapmak: `rkp build-asset --fallback-only`.

**Plan:**

- `build-asset --fallback-only` için önce failing test ekle.
- CLI flag'i `src/rkp/cli.py` ve `src/rkp/build_asset.py` içinde bağla.
- Blender script ve Blender executable kontrolünü fallback-only modda atla.
- Makefile `fallback=1` kullanımını ekle.
- README, CLI docs ve Blender support dokümanını yeni explicit fallback yolu ile güncelle.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_fallback_only_skips_blender_and_script_requirements: first run failed as expected; CLI did not recognize --fallback-only
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_fallback_only_skips_blender_and_script_requirements: ok, 1 test
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_uses_external_config_and_fails_gracefully_without_blender Tests.test_rkp_project.RkpProjectTests.test_build_asset_fallback_only_skips_blender_and_script_requirements Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_missing_texture_as_info_after_successful_build Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_when_texture_exists_but_is_not_packaged_in_usdz Tests.test_rkp_project.RkpProjectTests.test_build_asset_does_not_report_texture_info_when_usdz_contains_texture Tests.test_rkp_project.RkpProjectTests.test_fallback_builder_uses_external_config_and_reports_missing_usdzip Tests.test_public_polish_docs.PublicPolishDocsTests.test_blender_support_documents_fallback_without_acceptance_shortcut: ok, 7 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 146 tests
rtk make verify-local: ok, compileall + Ruff + 146 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

Fallback-built USDZ hâlâ draft kabul edilecek. `--fallback-only` sadece build yolunu seçer; manifest status değiştirmez ve screenshot acceptance gerekliliğini kaldırmaz.

### Sprint 101: Public Polish Follow-up

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Product-focus cleanup sonrası public repo vitrini için küçük ama kalıcı onboarding yüzeylerini tamamlamak.

**Plan:**

- README üstüne CI/Python/license/RealityKit badge'leri ekle.
- Blender sürüm ve direct USDZ fallback davranışını tek dokümanda topla.
- Learner-friendly first-good-issue listesi ekle.
- GitHub showcase ve AI handoff dosyalarını yeni public polish yüzeyiyle güncelle.
- Bu dokümanları küçük Python testleriyle koru.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_public_polish_docs.py: ok, 4 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 145 tests
rtk make verify-local: ok, compileall + Ruff + 145 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

Push/tag yapılmadan önce yereldeki public polish tamamlanabilir. GitHub web UI işleri, tag ve release işlemleri kullanıcı açıkça istemeden yapılmayacak.

### Sprint 100: Product Focus Cleanup

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Projeyi tek ana ürün omurgasına geri oturtmak: `rkp` aktif RealityKit asset pipeline tool'u, `rkg` ise açıkça experimental labs katmanı.

**Plan:**

- Mevcut RKG screenshot evidence işini ayrı checkpoint olarak kapat.
- README ilk ekranını `rkp` happy path'e indir.
- `Docs/ai-handoff.md` içine default-to-RKP karar kuralı ekle.
- `Docs/cli-tool.md` içinde normal kullanıcı yolunu beş komutluk RKP akışına sadeleştir.
- `Docs/game-factory.md` ve `Docs/rkg-architecture.md` dosyalarını experimental labs olarak işaretle.
- `CHANGELOG.md` içinde RKP product surface ve RKG experimental labs ayrımını görünür yap.
- Product boundary doc testleri ekle.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_product_boundary_docs.py: ok, 4 tests
rtk .venv/bin/python -m unittest discover -s Tests: ok, 141 tests
rtk make verify-local: ok, compileall + Ruff + 141 tests + pipeline doctor
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Karar:**

Ürün vitrini `rkp` olacak. `rkg` korunacak, test edilecek ve dokümante edilecek; ancak README/CLI/handoff ana akışında experimental labs olarak kalacak.

### Sprint 99: RKG Screenshot Evidence Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-09 18:46 +03
**Amaç:** `rkg qa-plan --json` çıktısını tüketen ve generated projedeki screenshot evidence dosyalarını doğrulayan ilk komut kapısını eklemek.

**Yapılanlar:**

- `src/rkg/screenshot_status.py` eklendi.
- `rkg verify-screenshots <generated-project> [--plan qa-plan.json] [--json]` komutu eklendi.
- Komut `--plan` verilirse doğrudan `rkg qa-plan --json` payload'unu tüketiyor.
- `--plan` verilmezse generated projenin `GameSpec.json` dosyasından QA planını tekrar üretiyor.
- Her screenshot state için `capture_path`, dosya varlığı, dosya boyutu ve JPEG/PNG header kontrolü yapılıyor.
- JSON çıktı `ok`, `game_id`, `display_name`, `archetype` ve state bazlı `checks` listesi veriyor.
- Generated `Docs/store/screenshot-qa.md` artık capture öncesi `rkg verify-game`, capture sonrası `rkg verify-screenshots .` komutunu söylüyor.
- `Docs/game-factory.md`, `Docs/rkg-architecture.md`, `Docs/ai-handoff.md` ve `CHANGELOG.md` yeni evidence gate ile güncellendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests/test_rkg_screenshot_status.py: first run failed as expected; rkg.screenshot_status module was missing
rtk .venv/bin/python -m unittest Tests/test_rkg_screenshot_status.py: ok, 4 tests
rtk .venv/bin/python -m unittest Tests.test_rkg_store_pack.StorePackTests.test_screenshot_qa_runbook_sequences_generated_proof_cues: first run failed as expected; generated runbook did not mention verify-screenshots
rtk .venv/bin/python -m unittest Tests.test_rkg_store_pack.StorePackTests.test_screenshot_qa_runbook_sequences_generated_proof_cues Tests/test_rkg_screenshot_status.py: ok, 5 tests
rtk .venv/bin/python -m unittest Tests/test_rkg_screenshot_status.py Tests/test_rkg_qa_plan.py Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py: ok, 34 tests
rtk .venv/bin/python -c "<generate target_shooter temp project, write JPEG screenshot stubs, rkg verify-screenshots --json>": screenshot evidence ok for gameplay_start, mid_session, results
rtk .venv/bin/python -m compileall -q src Tools Tests: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk make verify-local: ok, compileall + Ruff + 137 tests + pipeline doctor
rtk make validate: manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Öğrenme notu:**

Screenshot automation için önce dosya contract'ı doğrulanmalı. Bu sprint simülatörü sürmüyor; onun yerine gelecekteki capture aracının yazacağı `Docs/screenshots/<state>.jpg` dosyalarını aynı QA planına göre denetleyen küçük ama net bir kapı ekliyor.

### Sprint 98: RKG Target Shooter Shared State Loop

**Durum:** Tamamlandı
**Tarih:** 2026-05-09 18:45 +03
**Amaç:** `target_shooter` generated app'ini eski local `score/isPlaying` overlay'inden çıkarıp diğer RKG archetype'larıyla aynı shared state, result ve RealityKit scene binding contract'ına taşımak.

**Yapılanlar:**

- `target_shooter` generated `GameState.swift` artık `targetsHit` ve `perfectHits` alanlarını üretiyor.
- `GameRules.swift` target shooter için `startTargetShooterSession`, `recordTargetHit` ve `finishTargetShooterSession` pure rule helper'larını üretiyor.
- Target shooter `ContentView.swift` artık `GameSessionState`, `SessionControl.isPlaying`, `FeedbackState.message`, `InputIntent.primaryButtonTitle`, `ResultView` ve `SessionControl.reset` kullanıyor.
- Primary action label'ı target shooter için `Hit` oldu; `Finish` button'u result state'e geçişi `SessionControl.markResult` üzerinden yapıyor.
- Generated `GameView.swift` target shooter için de state-bound hale geldi.
- Generated `GameSceneController.swift` target entity referansını state'e bağlayıp hit sayısına göre target pozisyonunu, perfect hit sonrası scale feedback'ini güncelliyor.
- Runtime/content/scaffold testleri target shooter'ın shared contract'a geçtiğini ve bilinmeyen archetype generic fallback'inin hâlâ durduğunu kanıtlayacak şekilde güncellendi.
- `Docs/rkg-architecture.md`, `Docs/game-factory.md`, `Docs/ai-handoff.md` ve `CHANGELOG.md` yeni coverage ile güncellendi.

**Verification:**

```text
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_target_shooter_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_target_shooter_state_to_realitykit_scene: first run failed as expected; target_shooter still used local score/isPlaying and GameView()
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_target_shooter_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_target_shooter_state_to_realitykit_scene: ok, 2 tests
rtk .venv/bin/python -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py: ok, 36 tests
rtk .venv/bin/python -c "<generate target_shooter temp project, rkg verify-game>": target-shooter generated verify ok; release-check ok; CoreSimulator sandbox warnings only
rtk .venv/bin/python -m compileall -q src Tools Tests: ok
rtk .venv/bin/python -m ruff check src Tests Tools: ok
rtk .venv/bin/python -m unittest discover -s Tests: ok, 133 tests
rtk make verify-local: ok, compileall + Ruff + 133 tests + pipeline doctor
rtk make validate: manifest ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Öğrenme notu:**

Target shooter RKG'nin ürünü değil ama seed archetype olduğu için eski local state yolunda kalmamalıydı. Artık beş seed archetype da aynı generated state/result/scene-binding yüzeyinden ilerliyor; sonraki RKG işi screenshot automation veya daha zengin store-pack checklist tarafına kayabilir.

### Sprint 97: GameARView Fixture Refactor

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 18:55 +03
**Amaç:** Fixture app'in tek büyük `GameARView.swift` dosyasını davranışı bozmadan daha okunur öğretici parçalara ayırmak.

**Yapılanlar:**

- `GameARView.swift` 622 satırdan 430 satıra indirildi.
- Arena/backdrop kurulumu `ArenaBuilder.swift` içine taşındı.
- Target asset sırası, imported orientation/scale, spawn slotları ve procedural fallback `TargetFactory.swift` içine taşındı.
- Hit spark/flash lifecycle `HitEffectSystem.swift` içine taşındı.
- PBR material helper'ı `RealityMaterials.swift` ile ortaklaştırıldı.
- Refactor sınırını koruyan `Tests/test_fixture_refactor.py` eklendi.
- XcodeGen project dosyası yeni Swift kaynaklarını içerecek şekilde yenilendi.

**Verification:**

```text
.venv/bin/python -m unittest Tests/test_fixture_refactor.py: first run failed as expected; ArenaBuilder.swift missing
.venv/bin/python -m unittest Tests/test_fixture_refactor.py: ok, 1 test
.venv/bin/python -m ruff check Tests/test_fixture_refactor.py: ok
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: first run failed because stale .xcodeproj did not include new Swift files
rtk xcodegen generate: ok
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild: ok; CoreSimulator sandbox warnings only
rtk make verify-local: ok, compileall + Ruff + 130 tests + pipeline doctor
rtk make validate: manifest ok
rtk .venv/bin/python Tools/rkp.py doctor: pipeline doctor: ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Öğrenme notu:**

Bu refactor davranış eklemedi; amaç fixture app'i üretim oyunu gibi büyütmek değil, asset pipeline kanıt harness'ını okunabilir tutmak. Yeni Swift dosyası ekleyince doğrudan `xcodebuild` öncesi XcodeGen yenilemek gerekiyor; aksi halde `.xcodeproj` yeni dosyaları görmüyor.

### Sprint 96: Product Boundary and Dev Setup

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 18:45 +03
**Amaç:** İlk kez gelen birinin RKP/RKG/fixture ayrımını doğru anlamasını sağlamak ve lokal dev/lint setup boşluğunu kapatmak.

**Yapılanlar:**

- README'ye product boundary matrisi eklendi.
- `rkg` README ve game-factory dokümanlarında experimental olarak konumlandı.
- Fixture app'in üretim oyunu değil verification harness olduğu ilk giriş yüzeyinde netleştirildi.
- Makefile'a `.venv` tabanlı `bootstrap-dev` ve `verify-local` hedefleri eklendi.
- `.venv/` `.gitignore` kapsamına alındı.
- Ruff dev dependency olarak bağlandı; mevcut import/typing lint borcu temizlendi.
- `pipeline doctor` `.venv` metadata'sını public text taramasından hariç tutuyor.
- `Docs/cli-tool.md`, `Docs/ai-handoff.md`, `CHANGELOG.md`, ve worklog güncellendi.

**Verification:**

```text
rtk make bootstrap-dev: ok, .venv içinde editable rkp + PyYAML + Ruff kuruldu
.venv/bin/python -m unittest Tests.test_rkp_package.RkpPackageTests.test_doctor_ignores_local_virtualenv_metadata: ok, 1 test
rtk make verify-local: ok, compileall + Ruff + 129 tests + pipeline doctor
rtk make lint: ok, All checks passed!
rtk make validate: manifest ok
rtk .venv/bin/python Tools/rkp.py doctor: pipeline doctor: ok
rtk .venv/bin/python Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild: ok; CoreSimulator sandbox warnings only
rtk git diff --check: ok
```

**Öğrenme notu:**

İlk bakış analizindeki ana risk yanlış beklenti oluşmasıydı. Bu sprint kod üretmekten çok ürün sınırını görünür hale getiriyor: RKP aktif toolkit yüzeyi, RKG deneysel factory katmanı, fixture app ise kanıt harness'ı. Yerel setup boşluğu da gerçek koşuda yakalandı: Homebrew-managed Python global pip kurulumunu reddettiği için bootstrap `.venv` tabanına taşındı.

### Sprint 95: RKG Session Result Helper

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 18:31 +03
**Amaç:** Generated result overlay görünürlük kararını inline `state.phase == .result` yerine `SessionControl.isResult` sözleşmesine taşımak.

**Yapılanlar:**

- `SessionControl.swift` generator'ı `isResult(_:)` helper'ını üretiyor.
- `lane_dodger`, `wave_defense_lite`, `toss_physics`, ve `stack_puzzle` generated ContentView'leri result overlay branch'inde `SessionControl.isResult(state)` kullanıyor.
- Changelog, game factory, RKG architecture ve AI handoff dokümanları result visibility sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_session_control_generator_emits_shared_session_helpers Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: first run failed as expected; `isResult` helper was missing and ContentViews still checked `state.phase` inline
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_session_control_generator_emits_shared_session_helpers Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: ok, 7 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_plan_game.py: ok, 34 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert SessionControl.isResult usage, rkg verify-game>": session-result-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 128 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

`SessionControl` artık oynuyor mu ve result mı sorularını birlikte sahipleniyor. Result UI branch'leri aynı lifecycle sözleşmesine bağlı kaldığı için sonraki fail/miss davranışı eklemeleri ContentView phase detayına yayılmadan ilerleyebilir.

### Sprint 94: RKG Result Overlay Wiring

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 18:25 +03
**Amaç:** Generated `ResultView.swift` modülünü playable archetype overlay'lerine gerçek result-state UI olarak bağlamak.

**Yapılanlar:**

- `lane_dodger`, `wave_defense_lite`, `toss_physics`, ve `stack_puzzle` generated ContentView'leri `state.phase == .result` olduğunda `ResultView(state:onReset:)` gösteriyor.
- `ResultView` reset button label'ını hard-coded `"Reset"` yerine `InputIntent.resetTitle` üzerinden alıyor.
- Toss ve stack reset closure'ları local kontrol state'lerini de eski başlangıç değerine döndürüyor (`throwPower`, `stablePlacement`).
- Changelog, game factory, RKG architecture ve AI handoff dokümanları result overlay sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_result_view_generator_uses_shared_reset_title Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: first run failed as expected; `ResultView` was generated but not wired into ContentViews
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_result_view_generator_uses_shared_reset_title Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: ok, 7 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_plan_game.py: ok, 34 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, assert ResultView wiring, rkg verify-game>": result-view-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 128 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Bu adım yeni abstraction eklemekten çok boşa duran generated modülü gerçek vertical slice'a bağladı. Result phase artık sadece state enum değeri değil, oyuncunun görebildiği resetlenebilir bir UI durumu.

### Sprint 93: RKG Input Intent Module

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 18:19 +03
**Amaç:** Generated Swift overlay'lerdeki primary/reset button label kararını ortak `InputIntent.swift` modülüne almak.

**Yapılanlar:**

- `plan-game` source file listesine `Sources/<GameName>/InputIntent.swift` eklendi.
- `rkg init-game` artık her generated proje için `InputIntent.swift` yazıyor.
- `InputIntent` `startTitle`, `resetTitle`, `primaryActionTitle`, ve `primaryButtonTitle(isPlaying:)` helper'larını üretiyor.
- `lane_dodger`, `wave_defense_lite`, `toss_physics`, ve `stack_puzzle` generated ContentView'leri primary action button label'ını `InputIntent.primaryButtonTitle` üzerinden alıyor.
- Generated generic target-shooter fallback ContentView de start/reset label'larını `InputIntent` üzerinden alıyor.
- RKG architecture, game factory, changelog ve AI handoff dokümanları yeni generated Swift modül sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_input_intent_generator_emits_primary_button_titles Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_generic_content_view_contract_remains_available: first run failed as expected; `InputIntent.swift` was not planned/generated and ContentView button labels were inline
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_input_intent_generator_emits_primary_button_titles Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_generic_content_view_contract_remains_available: ok, 6 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_plan_game.py: ok, 33 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate toss_physics temp project, assert InputIntent usage, rkg verify-game>": input-intent-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 127 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

`InputIntent` button copy kararını generated overlay'lerden çıkarıyor. Bu şimdilik sadece start/reset ve primary action title sınırında tutuldu; secondary archetype action'ları (`Damage`, `Collapse`) ayrı karar gerektirdiği için inline kaldı.

### Sprint 92: RKG Feedback State Module

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:58 +03
**Amaç:** Generated Swift overlay'lerdeki last-event feedback metnini ortak `FeedbackState.swift` modülüne almak.

**Yapılanlar:**

- `plan-game` source file listesine `Sources/<GameName>/FeedbackState.swift` eklendi.
- `rkg init-game` artık her generated proje için `FeedbackState.swift` yazıyor.
- `FeedbackState.message(for:)` generated overlay'lerin gösterdiği `lastEvent` metnini merkezi hale getiriyor.
- `lane_dodger`, `wave_defense_lite`, `toss_physics`, ve `stack_puzzle` generated ContentView'leri inline `state.lastEvent.capitalized` yerine `FeedbackState.message(for: state)` kullanıyor.
- RKG architecture, game factory, changelog ve AI handoff dokümanları yeni generated Swift modül sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_feedback_state_generator_emits_display_message_helper Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold: first run failed as expected; `FeedbackState.swift` was not planned/generated and ContentView feedback text was inline
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_feedback_state_generator_emits_display_message_helper Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold: ok, 5 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_plan_game.py: ok, 32 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert FeedbackState usage, rkg verify-game>": feedback-state-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 126 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

`FeedbackState` küçük ama yararlı bir sınır: UI copy formatı ContentView'lerden çıkıyor, ancak event kararları ve gameplay-specific flags hâlâ ilgili `GameRules`/archetype akışlarında kalıyor.

### Sprint 91: RKG Screenshot QA Plan Command

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:51 +03
**Amaç:** `screenshot_proofs` ve store screenshot QA runbook bilgisini makine-okunur `rkg qa-plan` CLI yüzeyine bağlamak.

**Yapılanlar:**

- `src/rkg/qa_plan.py` eklendi.
- `build_qa_plan` GameSpec'ten ordered screenshot capture step listesi üretiyor.
- Her QA step `order`, `state`, `screenshot_state_case`, `drive`, `visible_roles`, `expected_evidence`, `capture_path`, ve `automation` alanlarını içeriyor.
- `rkg qa-plan <GameSpec> [--json]` CLI komutu eklendi; dosya yazmadan text veya JSON capture plan döndürüyor.
- `Docs/store/screenshot-qa.md` üretimi aynı `qa_steps_for` helper'ını kullanacak şekilde toparlandı.
- Changelog, game factory, production playbook, RKG architecture ve AI handoff dokümanları `qa-plan` sözleşmesiyle güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_qa_plan.py: first run failed as expected; `rkg.qa_plan` module was missing
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_qa_plan.py Tests/test_rkg_store_pack.py: ok, 7 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_qa_plan.py Tests/test_rkg_store_pack.py Tests/test_rkg_plan_game.py Tests/test_rkg_init_game.py: ok, 31 tests
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 125 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Store runbook insan-readable çıktı olmaya devam ediyor; `qa-plan --json` aynı capture sırasını simulator automation veya başka ajanların okuyabileceği kararlı veri yüzeyine çeviriyor.

### Sprint 90: RKG Result Transition Routing

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:43 +03
**Amaç:** Generated GameRules içindeki result/fail transition'larını `SessionControl.markResult` üzerinden geçirmek.

**Yapılanlar:**

- `lane_dodger` collision sonucunu `SessionControl.markResult(next, event: "hit obstacle")` ile kapatıyor.
- `toss_physics` landing ve attempts-spent result transition'larını `SessionControl.markResult` ile kapatıyor.
- `stack_puzzle` collapsed ve tower-complete result transition'larını `SessionControl.markResult` ile kapatıyor.
- `wave_defense_lite` defeated/base-breached transition'ını `SessionControl.markResult` ile kapatıyor.
- Archetype-specific flag ve score alanları kendi rules içinde kalıyor; shared helper yalnızca phase/event result yazımını topluyor.
- Changelog, game factory, RKG architecture ve AI handoff dokümanları güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_lane_dodger_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_wave_defense_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_stack_puzzle_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_toss_physics_result_transitions_use_session_control Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: first run failed as expected; generated GameRules still wrote result phase/event inline
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_lane_dodger_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_wave_defense_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_stack_puzzle_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_toss_physics_result_transitions_use_session_control Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: ok, 8 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetype_runtime.py Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_scaffold_generators.py: ok, 33 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, assert markResult usage, rkg verify-game>": result-control-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 121 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

`SessionControl.markResult` artık gerçek generated rules tarafından kullanılıyor. Ortak helper'ın sınırı net: result phase/event standardizasyonu burada, skor ve archetype-specific outcome flag'leri hâlâ ilgili archetype rule'larında.

### Sprint 89: RKG Shared Session Control Module

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:37 +03
**Amaç:** Generated playable ContentView'lerde tekrar eden playing/reset davranışını ortak Swift modülüne almak.

**Yapılanlar:**

- `plan-game` source file listesine `Sources/<GameName>/SessionControl.swift` eklendi.
- `rkg init-game` artık her generated proje için `SessionControl.swift` yazıyor.
- `SessionControl` `isPlaying`, `reset`, ve `markResult` helper'larını üretiyor.
- `lane_dodger`, `wave_defense_lite`, `toss_physics`, ve `stack_puzzle` generated ContentView'leri `state.phase == .playing` ve direkt `GameSessionState()` reset yerine `SessionControl` kullanıyor.
- RKG architecture, game factory, changelog ve AI handoff dokümanları yeni generated Swift modül sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_session_control_generator_emits_shared_session_helpers Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold: first run failed as expected; `SessionControl.swift` was not planned/generated and ContentView reset/playing logic was inline
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_session_control_generator_emits_shared_session_helpers Tests.test_rkg_content_views.RkgContentViewTests.test_toss_physics_content_view_contract_is_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold: ok, 5 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py Tests/test_rkg_plan_game.py: ok, 31 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert SessionControl usage, rkg verify-game>": session-control-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 120 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

`SessionControl` şu an küçük ama doğru sınırda: UI state'in oynuyor mu/sıfırlanıyor mu bilgisini merkezi hale getiriyor, archetype-specific start/core action kurallarını ise `GameRules` içinde bırakıyor. Bu çizgi yeni reusable modules işinde gereksiz abstraction riskini düşük tutuyor.

### Sprint 88: RKG Typed Screenshot State Module

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:27 +03
**Amaç:** Generated Swift projelerde `release.screenshots` listesini typed `ScreenshotState` modülüne dönüştürmek.

**Yapılanlar:**

- `plan-game` source file listesine `Sources/<GameName>/ScreenshotState.swift` eklendi.
- `rkg init-game` artık her generated proje için `ScreenshotState.swift` yazıyor.
- `ScreenshotState` enum'u `String`, `CaseIterable`, ve `Identifiable`; case raw value'ları GameSpec screenshot state id'lerini koruyor.
- Her case için `evidencePath` `Docs/screenshots/<state>.jpg` yolunu üretüyor.
- RKG architecture, game factory, changelog ve AI handoff dokümanları yeni generated Swift modül sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_screenshot_state_generator_emits_typed_release_states: first run failed as expected; `ScreenshotState.swift` was not planned/generated and helper was missing
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_screenshot_state_generator_emits_typed_release_states: ok, 3 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py Tests/test_rkg_init_game.py Tests/test_rkg_scaffold_generators.py: ok, 27 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert ScreenshotState near_miss case, rkg verify-game>": screenshot-state-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 119 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Store QA runbook insanın izleyeceği capture sırasını veriyor; `ScreenshotState.swift` aynı state id'lerini Swift tarafında typed sözleşmeye bağlıyor. Bu, ileride screenshot capture automation veya in-app QA overlay için aynı release state kaynaklarını kullanmayı kolaylaştıracak.

### Sprint 87: RKG Screenshot QA Runbook

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:22 +03
**Amaç:** `screenshot_proofs` bilgisini generated store pack içinde sıralı QA capture talimatına dönüştürmek.

**Yapılanlar:**

- `plan-game` dry-run dosya listesine `Docs/store/screenshot-qa.md` eklendi.
- `rkg init-game` store pack üretimi artık screenshot QA runbook dosyasını yazıyor.
- QA runbook release screenshot state'lerini sırayla listeliyor; her satır generated proof cue, beklenen görünür asset rolleri ve evidence path içeriyor.
- Store pack, game factory, RKG architecture, changelog ve AI handoff dokümanları yeni dosya sözleşmesine göre güncellendi.

**Verification:**

```text
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_store_pack.StorePackTests.test_screenshot_qa_runbook_sequences_generated_proof_cues: first run failed as expected; `Docs/store/screenshot-qa.md` was not planned/generated
rtk /opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_store_pack.StorePackTests.test_screenshot_qa_runbook_sequences_generated_proof_cues Tests.test_rkg_store_pack.StorePackTests.test_store_pack_includes_screenshots_and_monetization_files: ok, 4 tests
rtk /opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py: ok, 27 tests
rtk /opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert screenshot QA runbook, rkg verify-game>": qa-runbook-generated verify ok; release-check ok; generated project doctor warnings only for optional README/LICENSE/Makefile
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 118 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Checklist tekil screenshot gereksinimini anlatıyor; QA runbook ise capture sırasını ve beklenen kanıtı yürütülebilir hale getiriyor. Bir sonraki otomasyon adımı, bu dosyayı okuyup simulator screenshot komutlarını sıraya bağlamak olabilir.

### Sprint 86: RKG Screenshot Proof Metadata

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:17 +03
**Amaç:** RKG archetype'larının store screenshot checklist ve `plan-game --json` çıktısında gerçek oynanış kanıtını tarif etmesini sağlamak.

**Yapılanlar:**

- Her seed archetype için `screenshot_proofs` registry alanı eklendi.
- `rkg plan-game --json` çıktısı artık seçilen `release.screenshots` durumlarına filtrelenmiş `screenshot_proofs` döndürüyor.
- `rkg init-game` store pack üretimi `Docs/store/screenshots.md` içine `Generated proof cue` kolonu yazıyor.
- Proof cue metinleri buton/gesture akışını ve ilgili `GameSessionState` değerini birlikte tarif ediyor.
- `CHANGELOG.md`, `Docs/rkg-architecture.md`, `Docs/game-factory.md`, ve `Docs/ai-handoff.md` yeni sözleşmeye göre güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py: first run failed as expected; screenshot_proofs missing from registry/plan payload and generated checklist
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_archetypes.RkgArchetypeTests.test_describe_archetype_exposes_roles_modules_and_screenshots Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_files_roles_and_screenshots Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_runtime_entities_for_declared_roles Tests.test_rkg_store_pack.StorePackTests.test_screenshot_checklist_includes_generated_proof_cues: ok, 4 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py Tests/test_rkg_validate_spec.py: ok, 36 tests
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, assert screenshot proof cues, rkg verify-game>": lane-dodger-screenshot-proof-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 117 tests
rtk /opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
rtk /opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Store screenshot checklist artık yalnızca hangi state'in yakalanacağını değil, o state'in generated oyunda nasıl kanıtlanacağını da söylüyor. Bu, sonraki QA automation adımı için doğrudan bir sıra verisi sağlayacak.

### Sprint 85: RKG Scene Entity Wiring Helper

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:15 +03
**Amaç:** State-bound RKG scene-controller generator'larında tekrarlanan entity load/reference wiring kodunu ortak helper'a çekmek.

**Yapılanlar:**

- `Tests/test_rkg_scaffold_generators.py` içine `_scene_entity_setup_lines` sözleşmesi eklendi.
- Yeni helper `AssetLoader.loadPrimaryEntity`, initial position assignment, `anchor.addChild`, ve ilk matching role reference assignment işini tek yerde topluyor.
- `lane_dodger`, `toss_physics`, `wave_defense_lite`, ve `stack_puzzle` scene-controller generator'ları helper'ı kullanacak şekilde refactor edildi.
- Role binding helper aynı role'den birden fazla asset olduğunda ilk match'i reference olarak bağlıyor, diğer entity'leri scene'e eklemeye devam ediyor.
- Dört state-bound generated archetype gerçek `rkg verify-game` kapısından tekrar geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_scene_entity_setup_lines_load_and_bind_first_matching_roles: first run failed as expected; `_scene_entity_setup_lines` helper missing
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_scene_entity_setup_lines_load_and_bind_first_matching_roles Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_lane_dodger_state_to_realitykit_scene Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_toss_physics_state_to_realitykit_scene Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_wave_defense_state_to_realitykit_scene Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_stack_puzzle_state_to_realitykit_scene: ok, 5 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_archetype_runtime.py Tests/test_rkg_scaffold_generators.py: ok, 30 tests
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, rkg verify-game>": lane-dodger-refactor-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -c "<generate toss_physics temp project, rkg verify-game>": toss-physics-refactor-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -c "<generate wave_defense_lite temp project, rkg verify-game>": wave-defense-refactor-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, rkg verify-game>": stack-puzzle-refactor-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 116 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Generated Swift çıktısı davranış olarak aynı kaldı, ama scene-controller generator'ları artık ortak role-binding primitive'ini kullanıyor. Bundan sonra yeni state-bound archetype eklerken yalnızca reference role mapping'i ve update(state:) formülü yazmak yeterli olmalı.

### Sprint 84: RKG Stack Puzzle Scene Binding

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 17:05 +03
**Amaç:** `stack_puzzle` generated app'i overlay-only loop'tan RealityKit state-bound scene loop'a taşımak.

**Yapılanlar:**

- `stack_puzzle` generated `ContentView.swift` artık `GameView(state: state)` çağırıyor.
- `stack_puzzle` generated `GameView.swift` state-bound coordinator yolunu kullanıyor.
- `stack_puzzle` generated `GameSceneController.swift` piece ve obstacle entity referanslarını saklıyor.
- Piece entity pozisyonu `piecesPlaced` ve `stablePieces` üzerinden height/offset feedback'i alıyor.
- Collapse halinde piece scale'i küçülüyor, obstacle entity yukarı çıkıp büyüyerek fail/result state'i görselleştiriyor.
- Gerçek generated `stack_puzzle` proje `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_stack_puzzle_state_to_realitykit_scene: first run failed as expected; stack ContentView still called GameView() and scene had no update(state:)
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_stack_puzzle_state_to_realitykit_scene Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_state_bound_game_view_generator_is_archetype_neutral: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_archetype_runtime.py Tests/test_rkg_scaffold_generators.py: first run caught stale stack content-view contract expecting GameView()
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_archetype_runtime.py Tests/test_rkg_scaffold_generators.py: ok, 29 tests
/opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, rkg verify-game>": stack-puzzle-scene-bound-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 115 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Bu sprintle ilk dört non-generic RKG archetype (`lane_dodger`, `toss_physics`, `wave_defense_lite`, `stack_puzzle`) hem playable SwiftUI state loop'una hem de RealityKit scene state binding'ine sahip oldu. Bundan sonra en değerli bakım işi, archetype-specific scene-controller generator'larındaki ortak entity load/reference wiring'i azaltmak.

### Sprint 83: RKG State-Bound GameView and Wave Scene Binding

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 16:55 +03
**Amaç:** Sprint 82 değişikliklerini commit'leyip state-bound `GameView` generator borcunu temizlemek ve `wave_defense_lite` overlay state'ini RealityKit scene'e bağlamak.

**Yapılanlar:**

- Sprint 82 değişiklikleri `71d7fff Add stack puzzle loop and toss scene binding` commit'iyle kaydedildi.
- `scaffold.py` içindeki state-bound generated `GameView` helper'ı lane-dodger özel adından `_state_bound_game_view_swift` adına taşındı.
- `Tests/test_rkg_scaffold_generators.py` eklendi; state-bound `GameView` generator sözleşmesi archetype-neutral helper üzerinden kapsanıyor.
- `wave_defense_lite` generated `ContentView.swift` artık `GameView(state: state)` çağırıyor.
- `wave_defense_lite` generated `GameSceneController.swift` defender ve threat entity referanslarını saklıyor.
- Threat entity pozisyonu `wave` ve `threatsRemaining` üzerinden güncelleniyor.
- Defender entity low-health ve defeated state için basit position/scale feedback'i alıyor.
- Gerçek generated `wave_defense_lite` proje `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_state_bound_game_view_generator_is_archetype_neutral: first run failed as expected; `_state_bound_game_view_swift` helper missing
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_state_bound_game_view_generator_is_archetype_neutral Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_lane_dodger_state_to_realitykit_scene Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_toss_physics_state_to_realitykit_scene: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_wave_defense_state_to_realitykit_scene: first run failed as expected; wave ContentView still called GameView() and scene had no update(state:)
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_wave_defense_state_to_realitykit_scene Tests.test_rkg_scaffold_generators.RkgScaffoldGeneratorTests.test_state_bound_game_view_generator_is_archetype_neutral: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_archetype_runtime.py Tests/test_rkg_scaffold_generators.py: ok, 28 tests
/opt/homebrew/bin/python3.12 -c "<generate wave_defense_lite temp project, rkg verify-game>": wave-defense-scene-bound-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 114 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

State-bound `GameView` artık lane-dodger'a özel isim taşımıyor. Scene-controller tarafında hâlâ benzer entity load/reference wiring blokları var; sıradaki düşük riskli refactor bu tekrarı yardımcı fonksiyonlara çekmek olabilir.

### Sprint 82: RKG Stack Loop and Toss Scene Binding

**Durum:** Tamamlandı
**Tarih:** 2026-05-08 16:45 +03
**Amaç:** Lokal release hazırlığını netleştirip RKG tarafında sıradaki oynanabilir archetype ve scene binding işlerini TDD ile ilerletmek.

**Yapılanlar:**

- `CHANGELOG.md` içine mevcut lokal RKG commitlerini kapsayan `Unreleased` bölümü eklendi.
- `Docs/ai-handoff.md` release notu güncellendi: mevcut `v0.1.0` tag'i yeniden yazılmayacak, sonraki yayın yeni tag/release olarak hazırlanacak.
- `stack_puzzle` generated `ContentView.swift` artık `@State private var state = GameSessionState()` ve `stablePlacement` toggle'ı kullanıyor.
- `stack_puzzle` overlay'i score, placed pieces, stable pieces, last event, `Place/Start`, `Collapse`, ve `Reset` kontrollerini üretiyor.
- `GameRules` stack puzzle için `startStackPuzzleSession`, `placeStackPiece` ve `collapseStack` üretiyor.
- `toss_physics` generated `ContentView.swift` artık `GameView(state: state)` çağırıyor.
- `toss_physics` generated `GameView.swift` state-bound coordinator yolunu kullanıyor.
- `toss_physics` generated `GameSceneController.swift` projectile ve target entity referanslarını saklıyor; projectile pozisyonu/scale'i `lastThrowPower`, `landedInZone`, ve `attemptsRemaining` üzerinden güncelleniyor.
- Gerçek generated `stack_puzzle` ve `toss_physics` projeleri `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_stack_puzzle_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: first run failed as expected; stack start/place/collapse rules and ContentView controls missing
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_archetype_runtime.RkgArchetypeRuntimeTests.test_stack_puzzle_runtime_contract_is_exposed_outside_scaffold Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_stack_puzzle_loop: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_toss_physics_state_to_realitykit_scene: first run failed as expected; toss ContentView still called GameView() and scene had no projectile update(state:)
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_toss_physics_state_to_realitykit_scene: ok, 1 test
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py Tests/test_rkg_archetype_runtime.py: ok, 26 tests
/opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, rkg verify-game>": first run caught Swift compile failure; stack ContentView incorrectly passed state into GameView
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold: first regression run failed as expected; stack ContentView emitted GameView(state:)
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_content_views.RkgContentViewTests.test_stack_puzzle_content_view_contract_is_outside_scaffold Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_toss_physics_state_to_realitykit_scene: ok, 2 tests
/opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, rkg verify-game>": stack-puzzle-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -c "<generate toss_physics temp project, rkg verify-game>": toss-physics-scene-bound-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 112 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

String-contract testleri hızlı yön veriyor ama Swift compile kapısı hâlâ zorunlu. `stack_puzzle` için gerçek generated project build'i, testlerin yakalamadığı `GameView(state:)` imza uyumsuzluğunu buldu. Bundan sonra yeni generated Swift UI sözleşmeleri en az bir gerçek `rkg verify-game` kapısıyla kapatılmalı.

### Sprint 81: RKG Scaffold Cleanup

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 21:55 +03
**Amaç:** Güncel projeyi kod temizliği açısından tarayıp düşük riskli bakım düzeltmelerini yapmak.

**Yapılanlar:**

- `scaffold.py` içindeki büyük `ContentView.swift` generator blokları `src/rkg/content_views.py` modülüne taşındı.
- `scaffold.py` ContentView üretimini artık `content_view_swift(display_name, spec)` üzerinden çağırıyor.
- `Tests/test_rkg_content_views.py` yeni modül sözleşmesini generic target shooter ve `toss_physics` overlay üzerinden kapsıyor.
- `scaffold.py` 775 satırdan 473 satıra indi; RKG scaffold tekrar dosya yazma ve proje orkestrasyonuna daha yakın kaldı.
- `rkp clean --apply` ile yerel scratch dosyaları temizlendi: `Build`, `__pycache__`, `src/rkp.egg-info`, `.DS_Store` ve boş usdzip geçici klasörleri.
- `ruff` taraması denendi ama dev dependency bu ortamda kurulu olmadığı için çalıştırılamadı.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py: first run failed as expected; rkg.content_views module missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_content_views.py: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_content_views.py: ok, 18 tests
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --dry-run: 10 candidates
/opt/homebrew/bin/python3.12 Tools/rkp.py clean --apply: removed 10 candidates
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 108 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -B Tools/rkp.py clean --apply: removed regenerated local scratch candidates
```

**Öğrenme notu:**

Son playable archetype sprintlerinden sonra en hızlı büyüyen yüzey Swift string emitter'lardı. ContentView üretimini ayırmak, sıradaki `stack_puzzle` playable loop veya scene binding işlerinde scaffold merge riskini düşürür.

### Sprint 80: RKG Toss Physics Playable Overlay

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 21:25 +03
**Amaç:** `toss_physics` generated app'i static HUD'dan çıkarıp power/attempt/landing temelli minimal oynanabilir SwiftUI overlay loop'una taşımak.

**Yapılanlar:**

- `toss_physics` generated `ContentView.swift` artık `@State private var state = GameSessionState()` kullanıyor.
- HUD score, remaining attempts, throw power ve last event gösteriyor.
- `Slider(value: $throwPower, in: 0...1)` ile throw power seçimi eklendi.
- `Button(isPlaying ? "Throw" : "Start")` ile session başlatma veya toss resolve akışı eklendi.
- `Reset` button'u state'i ve throw power'ı sıfırlıyor.
- `GameRules` toss physics için `landedInScoringZone`, `startTossSession` ve `resolveToss` üretiyor.
- Gerçek generated `toss_physics` proje `rkg verify-game` ile build kapısından geçirildi.
- `Docs/rkg-architecture.md` playable archetype durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop: first run failed as expected; generated ContentView still used local score/isPlaying
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_toss_physics_loop: ok, 1 test
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_archetype_runtime.py: ok, 20 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py src/rkg/archetype_runtime.py: ok
/opt/homebrew/bin/python3.12 -c "<generate toss_physics temp project, rkg verify-game>": toss-physics-playable-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 106 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Bu sprint RKG'nin sadece tap/defense/dodge değil, attempt ve analog power seçimi isteyen oyun türleri için de ilk oynanabilir scaffold üretebildiğini gösteriyor. Fizik simülasyonu henüz gerçek projectile arc'a bağlı değil; sıradaki toss işi `GameSceneController` içinde projectile entity pozisyonunu `lastThrowPower` ve `landedInZone` ile görsel hale getirmek olmalı.

### Sprint 79: RKG Archetype Runtime Extraction

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 21:06 +03
**Amaç:** RKG generated runtime state/rules contract'larını büyüyen scaffold dosyasından çıkarıp archetype odaklı ayrı bir Python modülüne taşımak.

**Yapılanlar:**

- `src/rkg/archetype_runtime.py` eklendi.
- `archetype_state_fields`, `archetype_rule_members` ve `indent_swift_block` public helper olarak dışarı alındı.
- `src/rkg/scaffold.py` artık `GameState.swift` alanlarını ve `GameRules.swift` üyelerini bu modülden alıyor.
- `Tests/test_rkg_archetype_runtime.py` yeni modül sözleşmesini lane dodger, wave defense, unknown archetype ve indentation üzerinden kapsıyor.
- Swift generation davranışı değiştirilmedi; bu sprint bakım yüzeyini küçültmeye odaklandı.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetype_runtime.py: first run failed as expected; rkg.archetype_runtime module missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetype_runtime.py: ok, 4 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_archetype_runtime.py: ok, 19 tests
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 105 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Playable archetype sayısı arttıkça en kritik risk scaffold'un tek dosyada oyun mantığı, Swift emitter ve asset wiring sorumluluklarını biriktirmesi. Runtime contract'ı ayrı modüle almak, sıradaki toss/stack playable loop işlerini daha kontrollü hale getiriyor.

### Sprint 78: RKG Wave Defense Playable Overlay

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 20:42 +03
**Amaç:** `wave_defense_lite` generated app'i statik HUD'dan çıkarıp minimal oynanabilir SwiftUI overlay loop'una taşımak.

**Yapılanlar:**

- `wave_defense_lite` generated `ContentView.swift` artık `@State private var state = GameSessionState()` kullanıyor.
- HUD score, health, wave, threats, cleared count ve event gösteriyor.
- `Button(isPlaying ? "Fire" : "Start")` ile session başlatma veya threat clear frame'i ekleniyor.
- `Damage` button'u health azaltma ve result state'e düşme sözleşmesini tetikliyor.
- `Reset` button'u session state'i sıfırlıyor.
- `GameSessionState` wave defense için `clearedThreats` ve `isDefeated` alanlarını da üretiyor.
- `GameRules` wave defense için `threatsForWave`, `startWaveDefenseSession`, `clearThreat` ve `applyThreatDamage` üretiyor.
- Gerçek generated `wave_defense_lite` proje `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop: first run failed as expected; generated ContentView still used local score/isPlaying
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_wave_defense_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_escapes_swift_string_literals_from_spec_text: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py Tests/test_rkg_validate_spec.py: ok, 24 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate wave_defense_lite temp project, rkg verify-game>": wave-defense-playable-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 101 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

İkinci playable archetype, RKG'nin sadece lane-dodger'a özel bir demo olmadığını gösteriyor. Wave defense hâlâ RealityKit target movement'a bağlı değil, ama health/wave/threat loop'u generated Swift içinde oynanabilir hale geldi.

### Sprint 77: RKG Lane Dodger Scene Binding

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 20:28 +03
**Amaç:** `lane_dodger` generated SwiftUI overlay state'ini RealityKit scene entity pozisyonlarına bağlamak.

**Yapılanlar:**

- `lane_dodger` generated `ContentView.swift` artık `GameView(state: state)` çağırıyor.
- `lane_dodger` generated `GameView.swift` `let state: GameSessionState` alıyor.
- `GameView` artık `UIViewRepresentable` coordinator ile tek `GameSceneController` instance'ını koruyor.
- `makeUIView` ve `updateUIView` controller `update(state:)` çağırıyor.
- `GameSceneController.swift` player ve obstacle entity referanslarını saklıyor.
- Player entity `state.currentLane`, obstacle entity `state.obstacleLane` ve `state.distance` ile pozisyon güncelliyor.
- Generic archetype'lar eski static scene yolunda bırakıldı.
- Gerçek generated `lane_dodger` proje `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_lane_dodger_state_to_realitykit_scene: first run failed as expected; ContentView still called GameView() and scene had no update(state:)
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_binds_lane_dodger_state_to_realitykit_scene Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generated_modules_reference_planned_asset_ids: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py Tests/test_rkg_validate_spec.py: ok, 23 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, rkg verify-game>": lane-dodger-scene-bound-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 100 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Bu sprint lane dodger'ı overlay-only prototipten generated 3D gameplay loop'a yaklaştırdı. RKG artık en az bir archetype için SwiftUI state'i RealityKit entity transformlarına taşıyan proje üretiyor.

### Sprint 76: RKG Lane Dodger Playable Overlay

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 18:44 +03
**Amaç:** `lane_dodger` generated app'i statik HUD'dan çıkarıp minimal oynanabilir SwiftUI overlay loop'una taşımak.

**Yapılanlar:**

- `lane_dodger` generated `ContentView.swift` artık `@State private var state = GameSessionState()` kullanıyor.
- HUD score, lane count, obstacle lane, distance, near-miss ve `lastEvent.capitalized` gösteriyor.
- `Button(isPlaying ? "Dodge" : "Start")` ile session başlatma veya frame ilerletme eklendi.
- `Reset` button'u session state'i sıfırlıyor.
- `DragGesture(minimumDistance: 20).onEnded` ile lane değiştirme eklendi.
- `GameSessionState` lane dodger için `obstacleLane` ve `isDefeated` alanlarını da üretiyor.
- `GameRules` lane dodger için `laneAfterMove`, `nextObstacleLane(after:)`, `startLaneDodgerSession` ve `advanceLaneDodgerFrame` üretiyor.
- Collision durumunda result phase, defeat flag, event ve score update sözleşmesi eklendi.
- Gerçek generated `lane_dodger` proje `rkg verify-game` ile build kapısından geçirildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop: first run failed as expected; generated ContentView still used local score/isPlaying
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop: second run failed as expected; stronger playable contract required Dodge/Start, drag gesture, isDefeated, and named lane session rules
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_playable_lane_dodger_loop Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_lane_dodger_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_escapes_swift_string_literals_from_spec_text: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py Tests/test_rkg_validate_spec.py: ok, 22 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, rkg verify-game>": lane-dodger-playable-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 99 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

RKG'nin oyun geliştirme tool'u olduğunu kanıtlayan ilk nokta, generated app'in sadece scene göstermesi değil state değiştiren bir loop üretmesi. Bu sprint RealityKit entity movement'a girmeden, lane dodger için start/drag/dodge/result/reset akışını SwiftUI overlay ve pure rules üstünden başlattı.

### Sprint 75: RKG Stack Puzzle State Rules

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 18:21 +03
**Amaç:** `stack_puzzle` generated Swift modules için piece/stability/collapse pure rules sözleşmesini eklemek.

**Yapılanlar:**

- `stack_puzzle` scaffold'u `GameState.swift` içine `piecesPlaced`, `stablePieces` ve `collapsed` alanlarını ekliyor.
- `GameRules.swift` stack puzzle için `maxPieces`, `nextPieceIndex`, `isStable` ve `scoreForStack` üyelerini üretiyor.
- Physics/collision veya UI interaction eklenmedi; bu sprint sadece compile-safe state/rules contract'ı ekliyor.
- Gerçek generated `stack_puzzle` proje `rkg verify-game` ile build kapısından geçirildi.
- `Docs/rkg-architecture.md` tüm non-target seed archetype'ların first-pass state-rules durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_stack_puzzle_state_and_rules: first run failed as expected; stack_puzzle state/rules were generic
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_stack_puzzle_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_toss_physics_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_lane_dodger_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules: ok, 4 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py: ok, 21 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate stack_puzzle temp project, rkg verify-game>": stack-puzzle-rules-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 98 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Seed registry'deki target dışı archetype'lar artık en az bir compile-safe state/rules contract üretiyor. Bu, sonraki fazda gerçek input, physics ve loop davranışlarını eklerken her oyun türünün kavramlarını karıştırmadan büyütmeyi sağlar.

### Sprint 74: RKG Toss Physics State Rules

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 18:19 +03
**Amaç:** `toss_physics` generated Swift modules için attempts, throw power ve landing pure rules sözleşmesini eklemek.

**Yapılanlar:**

- `toss_physics` scaffold'u `GameState.swift` içine `attemptsRemaining`, `lastThrowPower` ve `landedInZone` alanlarını ekliyor.
- `GameRules.swift` toss physics için `maxAttempts`, `clampedThrowPower`, `consumeAttempt` ve `scoreForLanding` üyelerini üretiyor.
- Physics simulation veya gesture handling eklenmedi; bu sprint sadece compile-safe rule contract'ı ekliyor.
- Gerçek generated `toss_physics` proje `rkg verify-game` ile build kapısından geçirildi.
- `Docs/rkg-architecture.md` toss physics state-rules durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_toss_physics_state_and_rules: first run failed as expected; toss_physics state/rules were generic
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_toss_physics_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_lane_dodger_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py: ok, 20 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate toss_physics temp project, rkg verify-game>": toss-physics-rules-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 97 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Toss physics için ilk değer gesture değil, attempts/throw/landing contract'ı. Bu contract generated rules içinde durunca ileride RealityKit physics veya gesture input eklemek daha kontrollü olur.

### Sprint 73: RKG Lane Dodger State Rules

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 18:17 +03
**Amaç:** `lane_dodger` generated Swift modules için ilk pure state/rules sözleşmesini eklemek.

**Yapılanlar:**

- `lane_dodger` scaffold'u `GameState.swift` içine `currentLane`, `nearMisses` ve `distance` alanlarını ekliyor.
- `GameRules.swift` lane dodger için `laneCount`, `nearMissBonus`, `clampedLane`, `isCollision` ve `scoreForDistance` üyelerini üretiyor.
- UI ve scene loop hâlâ basit tutuldu; bu sprint sadece compile-safe state/rules contract'ı ekliyor.
- Gerçek generated `lane_dodger` proje `rkg verify-game` ile build kapısından geçirildi.
- `Docs/rkg-architecture.md` lane/wave archetype state-rules durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_lane_dodger_state_and_rules: first run failed as expected; lane_dodger state/rules were generic
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_lane_dodger_state_and_rules Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py: ok, 19 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, rkg verify-game>": lane-dodger-rules-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 96 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Lane dodger için gerçek oyun davranışına geçmeden önce lane index, collision ve near-miss scoring gibi kavramlar generated pure rules içinde isimlenmeli. Bu, ileride input/gesture veya RealityKit collision eklenirken ortak contract sağlar.

### Sprint 72: RKG Wave Defense State Rules

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 18:14 +03
**Amaç:** Generated Swift modules içinde ilk archetype-specific pure state/rules sözleşmesini `wave_defense_lite` için eklemek.

**Yapılanlar:**

- `wave_defense_lite` scaffold'u `GameState.swift` içine `health`, `wave` ve `threatsRemaining` alanlarını ekliyor.
- `GameRules.swift` wave defense için `startingHealth`, `healthAfterDamage`, `isDefeated` ve `nextWave` pure rule üyelerini üretiyor.
- Default archetype'lar mevcut score/timer contract'ında bırakıldı; UI ve scene loop karmaşıklığı eklenmedi.
- Gerçek generated `wave_defense_lite` proje `rkg verify-game` ile build kapısından geçirildi.
- `Docs/rkg-architecture.md` generated module sözleşmesiyle güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules: first run failed as expected; wave defense state/rules were generic
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_wave_defense_state_and_rules: ok, 1 test
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py: ok, 18 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -c "<generate wave_defense_lite temp project, rkg verify-game>": wave-defense-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 95 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Archetype-specific büyüme önce pure state/rules seviyesinde başlamalı. Böylece farklı oyun türleri için gerçek davranış sözleşmesi oluşur ama `GameView` ve RealityKit scene glue erken karmaşıklaşmaz.

### Sprint 71: RKG Archetype Input and Camera Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 17:52 +03
**Amaç:** `GameSpec` içindeki `game.input` ve `game.camera` değerlerini seçilen archetype registry sözleşmesine bağlamak.

**Yapılanlar:**

- `validate-spec` artık `game.input` değerinin archetype `input` listesinde bulunmasını zorunlu tutuyor.
- `validate-spec` artık `game.camera` değerinin archetype `camera` listesinde bulunmasını zorunlu tutuyor.
- Hatalar registry id'siyle açıklanıyor: ör. `game.input drag is not supported by target_shooter`.
- `Docs/game-spec.md` ve `Docs/rkg-architecture.md` runtime contract validasyonuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_validate_spec.RkgValidateSpecCliTests.test_validate_spec_cli_rejects_input_not_supported_by_archetype Tests.test_rkg_validate_spec.RkgValidateSpecCliTests.test_validate_spec_cli_rejects_camera_not_supported_by_archetype: first run failed as expected; unsupported input/camera were accepted
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_validate_spec.py Tests/test_rkg_spec.py: ok, 17 tests
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 94 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Archetype registry sadece asset role seti değil, kontrol ve kamera sözleşmesini de yönetmeli. Böylece `init-game` başlamadan önce yanlış input/camera kombinasyonları durdurulur.

### Sprint 70: RKG Runtime Entity Plan Payload

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 17:47 +03
**Amaç:** `plan-game` dry-run çıktısının generated scene'deki runtime entity coverage'ı açıkça göstermesini sağlamak.

**Yapılanlar:**

- `build_game_plan(spec)` payload'una `runtime_entities` eklendi.
- Runtime entity kayıtları `asset_id`, `role`, Swift variable adı ve deterministic position içeriyor.
- Entity plan helper'ı `src/rkg/plan.py` içinde tek source of truth oldu.
- `init-game` scaffold'u `GameSceneController.swift` üretirken aynı `runtime_entities_for(spec)` helper'ını kullanıyor.
- `Docs/rkg-architecture.md` plan payload örneği yeni alanla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_runtime_entities_for_declared_roles: first run failed as expected; runtime_entities payload was missing
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_plan_game.RkgPlanGameTests.test_build_game_plan_exposes_runtime_entities_for_declared_roles Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generated_scene_loads_all_declared_required_roles: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py Tests/test_rkg_init_game.py Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py Tests/test_rkg_store_pack.py Tests/test_rkg_verify_game.py: ok, 33 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/plan.py src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 92 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Dry-run sadece dosya listesi değil, runtime coverage contract'ı da göstermeli. Aksi halde kullanıcı `init-game` çalışmadan hangi asset rollerinin sahneye bağlanacağını göremez.

### Sprint 69: RKG Role-Aware Generated Scene

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 17:42 +03
**Amaç:** Generated scene kurulumunu single primary asset varsayımından çıkarıp tüm declared asset role'ları runtime load attempt kapsamına almak.

**Yapılanlar:**

- `GameSceneController.swift` üretimi artık spec'teki tüm asset kayıtlarını deterministic entity planına çeviriyor.
- Her asset için `AssetLoader.loadPrimaryEntity(assetId:role:)` çağrısı üretiliyor; imported USDZ yoksa role-based fallback çalışmaya devam ediyor.
- `lane_dodger` regression testi eklendi: `player`, `obstacle` ve `arena` rollerinin hepsi generated scene'de yüklenmek zorunda.
- Hard-coded `FallbackFactory.makeFallback(role: "arena") + primary` sahne kurulumu kaldırıldı.
- `Docs/rkg-architecture.md` generated scene role coverage davranışıyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generated_scene_loads_all_declared_required_roles: first run failed as expected; crate and lane_floor load attempts were missing
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generated_scene_loads_all_declared_required_roles Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generated_modules_reference_planned_asset_ids: ok, 2 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py Tests/test_rkg_verify_game.py: ok, 32 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py src/rkg/spec.py: ok
/opt/homebrew/bin/python3.12 -c "<generate lane_dodger temp project, rkg verify-game>": lane-dodger-generated verify ok; release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 91 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Multi-archetype factory için ilk runtime eşiği mekanik çeşitliliği değil, role coverage. Bir oyun türü `player`, `obstacle`, `arena` diyorsa generated project bu rolleri scene'e bağlamalı; yoksa RKP asset acceptance yolu runtime'da görünmez kalır.

### Sprint 68: RKG Required Archetype Roles

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 17:30 +03
**Amaç:** RKG GameSpec validasyonunu target-shooter varsayımından çıkarıp seçilen archetype'ın required asset role sözleşmesini zorunlu hale getirmek.

**Yapılanlar:**

- `validate-spec` artık seçilen archetype'ın tüm `required_asset_roles` değerlerinin `assets.<id>.role` içinde bulunmasını şart koşuyor.
- Generated manifest asset kayıtları artık `role` alanını da yazıyor.
- Target shooter test fixture'ları role-aware hale getirildi: `target_basic` -> `target`, `arena_floor` -> `arena`.
- `Docs/game-spec.md`, `Docs/game-factory.md` ve `Docs/rkg-architecture.md` required role sözleşmesiyle güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_validate_spec.py: first run failed as expected; lane_dodger missing obstacle was accepted
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_validate_spec.py: ok, 3 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py Tests/test_rkg_init_game.py Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py: ok, 26 tests
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 90 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Archetype registry sadece listeleme verisi olmamalı. RKG'nin her oyun türü için kullanışlı olabilmesi için scaffold öncesi spec, runtime'ın ihtiyaç duyacağı asset role setini eksiksiz kanıtlamalı.

### Sprint 67: RKG Generated Game Verification

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 17:12 +03
**Amaç:** Generated RKG projeleri için command-based verification gate eklemek.

**Yapılanlar:**

- `src/rkg/verify.py` eklendi.
- `rkg verify-game <project>` CLI komutu eklendi.
- Verify gate required generated files'ı kontrol ediyor: `GameSpec.json`, `rkp.json`, `project.yml`, `Tools/asset_manifest.json`.
- Generated proje içinde `Tests/test*.py` varsa unittest discovery çalışıyor; boş `Tests/` klasörü test komutu eklemiyor.
- Verify gate `rkp doctor` ve `rkp release-check` çalıştırıyor.
- `init-game` generated projeye `Tests/test_smoke.py` ekliyor; böylece RKP `release-check` test adımı boş suite nedeniyle düşmüyor.
- Generated manifest artık RKP doctor uyumlu `maxTriangles` ve `maxTextureSize` alanlarını budget string'inden yazıyor.
- `Docs/rkg-architecture.md` verify-game behavior ile güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_verify_game.py: first run failed as expected; rkg.verify module was missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_verify_game.py: first implementation exposed empty Tests/ directory and missing Tools/rkp.py wrapper issues
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, rkg verify-game>": first run failed; generated manifest missed maxTriangles/maxTextureSize
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, rkg verify-game>": second run failed; generated Tests directory had no test files
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_creates_realitykit_project_skeleton Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_writes_planned_manifest_assets Tests/test_rkg_verify_game.py: ok, 7 tests
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, rkg verify-game>": verify-generated ok
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 89 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

`verify-game` gerçek generated proje üzerinde çalıştırılmadan güvenilir sayılmıyor. RKG scaffold, RKP doctor/release-check kapılarının beklediği manifest budget alanlarını ve en az bir smoke test'i üretmeli.

### Sprint 66: RKG Store Pack Contract

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 16:55 +03
**Amaç:** Generated games için metadata/review/privacy yanında screenshot ve monetization checklist üreten store pack contract'ını uygulamak.

**Yapılanlar:**

- `src/rkg/store_pack.py` eklendi.
- `build_store_pack(spec)` store dosyalarını tek yerden üretiyor.
- `init-game` store docs üretimini `build_store_pack` üzerinden yapıyor.
- Yeni generated dosyalar: `Docs/store/screenshots.md` ve `Docs/store/monetization.md`.
- Screenshot checklist state, purpose, required asset roles ve evidence path içeriyor.
- Monetization checklist external unlock ve gerçek gameplay/paid content notlarını içeriyor.
- `plan-game` generated store files listesine `screenshots.md` ve `monetization.md` ekliyor.
- `Docs/rkg-architecture.md` store pack contract uygulama durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py: first run failed as expected; rkg.store_pack and generated screenshots/monetization files were missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py: first run failed as expected; plan-game did not include new store files
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py: ok, 11 tests
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/store_pack.py src/rkg/scaffold.py src/rkg/plan.py: ok
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 84 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, xcodegen, xcodebuild>": generated-build ok
```

**Öğrenme notu:**

Store pack scaffold'un yan ürünü değil, factory contract'ın parçası. `plan-game` ve `init-game` aynı dosya kapsamını göstermeli; yoksa dry-run güvenilirliğini kaybeder.

### Sprint 65: RKG Module-Based Swift Scaffold

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 16:45 +03
**Amaç:** Generated game scaffold'u tek `GameView.swift` ağırlığından çıkarıp reusable Swift module layout'a taşımak.

**Yapılanlar:**

- `init-game` artık şu Swift dosyalarını üretiyor: `GameState.swift`, `GameRules.swift`, `GameSceneController.swift`, `GameView.swift`, `AssetLoader.swift`, `FallbackFactory.swift`, `ResultView.swift`.
- `GameView.swift` artık asset loading yapmıyor; sadece `ARView` oluşturup `GameSceneController` çağırıyor.
- `AssetLoader.swift` `Entity.load(named:)` ve fallback kararını sahipleniyor.
- `FallbackFactory.swift` role-based procedural primitive üretiyor.
- `GameSceneController.swift` primary asset id/role ile scene kuruyor.
- `Docs/rkg-architecture.md` module ownership durumuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py: first run failed as expected; generated shared Swift module files were missing
/opt/homebrew/bin/python3.12 -m py_compile src/rkg/scaffold.py: ok
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py: ok, 6 tests
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, xcodegen, xcodebuild>": first run failed; generated code tried to assign get-only ARView.cameraTransform
/opt/homebrew/bin/python3.12 -c "<generate temp RKG project, xcodegen, xcodebuild>": generated-build ok
```

**Öğrenme notu:**

RKG'nin multi-archetype hale gelmesi için ilk zorunlu sınır Swift dosya ownership'i. `GameView` asset/policy bilmemeli; archetype farkları ileride `GameSceneController`, `GameRules`, `AssetLoader` ve `FallbackFactory` üzerinden büyümeli.

### Sprint 64: RKG Dry-Run Game Planning

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 15:47 +03
**Amaç:** `init-game` öncesinde yazma yapmadan generated project planını görebileceğimiz dry-run komutunu eklemek.

**Yapılanlar:**

- `src/rkg/plan.py` eklendi.
- `build_game_plan(spec)` generated dosyaları, Swift app adı, archetype kaydı, asset role map'i ve screenshot state listesini üretiyor.
- `rkg plan-game <GameSpec> [--json]` CLI komutu eklendi.
- `plan-game` invalid spec durumunda nonzero dönüyor ve output klasörü oluşturmuyor.
- `Docs/rkg-architecture.md` ve `Docs/game-factory.md` dry-run plan yüzeyiyle güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py: first run failed as expected; rkg.plan module was missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py: ok, 3 tests
```

**Öğrenme notu:**

`plan-game`, `init-game` için güvenli bir önizleme kapısı. Bundan sonra scaffold değişiklikleri önce planner payload'ında görünmeli; CLI doğrudan dosya yazmadan kullanıcıya ve ajanlara üretim kapsamını anlatabilmeli.

### Sprint 63: Registry-Aware GameSpec Validation

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 15:44 +03
**Amaç:** `GameSpec` validasyonunu RKG archetype registry ile bağlamak ve scaffold öncesi spec gate'i eklemek.

**Yapılanlar:**

- `validate_game_spec` artık bilinmeyen `game.archetype` değerlerini reddediyor.
- Asset `role` alanı present olduğunda seçili archetype'ın required/optional role setine göre doğrulanıyor.
- `release.screenshots` değerleri seçili archetype'ın screenshot state listesine göre doğrulanıyor.
- `rkg validate-spec <GameSpec>` komutu eklendi; `--json` machine-readable `ok/issues` çıktısı veriyor.
- `Docs/game-spec.md` role-aware spec örneği, validation rules ve validate-spec komutuyla güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py: first run failed as expected; registry-aware validation and validate-spec CLI were missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py: ok, 14 tests
```

**Öğrenme notu:**

Archetype registry sadece listeleme yüzeyi olmamalı; `GameSpec` gate'i onu policy kaynağı olarak kullanmalı. Role alanı şu an backward-compatible optional, ama present olduğunda template contract'a bağlanıyor.

### Sprint 62: RKG Architecture Plan and Archetype Registry

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 15:37 +03
**Amaç:** Multi-archetype RKG planını yürütülebilir mimari dokümana çevirmek ve ilk ortak registry yüzeyini CLI'a eklemek.

**Yapılanlar:**

- `Docs/rkg-architecture.md` eklendi: boundaries, data flow, archetype registry, asset role taxonomy, runtime state machine, generated Swift module layout, CLI roadmap, verification matrix, store-pack contract ve decision rules.
- `Docs/superpowers/plans/2026-05-07-rkg-multi-archetype-factory.md` eklendi: Task 1-6 için TDD adımları, dosyalar, komutlar ve commit sırası.
- `src/rkg/archetypes.py` eklendi.
- Seed archetype registry eklendi: `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, `wave_defense_lite`.
- `rkg list-archetypes` ve `rkg describe-archetype <id>` CLI komutları eklendi; ikisi de `--json` destekliyor.
- `Docs/game-factory.md` architecture doc'a bağlandı.
- `Docs/ai-handoff.md` yeni RKG yüzeyleriyle güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py: first run failed as expected; rkg.archetypes module was missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py: ok, 5 tests
```

**Öğrenme notu:**

Registry ilk gerçek multi-archetype yüzey. Bundan sonra `GameSpec` validation ve `plan-game` registry'ye bakarak ilerlemeli; `init-game` tek başına policy kaynağı olmamalı.

### Sprint 61: RKG Multi-Archetype Scope Correction

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 15:16 +03
**Amaç:** RKG yönünü tek bir target-shooter template'ine daraltmadan, her çeşit küçük RealityKit oyunu için kullanılacak genel game factory olarak netleştirmek.

**Yapılanlar:**

- `Docs/game-factory.md` içine RKG product scope bölümü eklendi.
- Target shooter fixture'ı ana ürün değil, sadece ilk reference archetype olarak tanımlandı.
- RKG shared factory layer netleştirildi: idea scoring, GameSpec validation, project scaffolding, asset role mapping, fallback contracts, reusable Swift modules, generated-project verification, screenshot/store-pack orchestration.
- "First Archetypes" bölümü "Seed Archetypes" olarak değiştirildi; order'ın product priority olmadığı yazıldı.
- `Docs/ai-handoff.md` next task listesi target-shooter derinleştirme yerine archetype registry ve shared template contract yönüne çekildi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
git diff --check: ok
```

**Öğrenme notu:**

Target shooter hızlı doğrulama için iyi fixture, ama RKG'nin ana değeri archetype-agnostic factory layer'da. Tek archetype'a yatırım yapmadan önce template registry ve ortak runtime contract kurulmalı.

### Sprint 60: Local Checkpoint Hygiene

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 14:39 +03
**Amaç:** Local agent checkpoint dosyalarının public docs/doctor gate'ini kirletmesini engellemek.

**Yapılanlar:**

- `Docs/checkpoints/` `.gitignore` kapsamına alındı.
- Pipeline doctor `Docs/checkpoints/` altındaki local resume notlarını public text taramasından hariç tutuyor.
- Regression test eklendi: checkpoint markdown içindeki local absolute path public warning üretmiyor.
- GitHub Actions checkout adımı resmi güncel major olan `actions/checkout@v6` sürümüne taşındı.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkp_package.RkpPackageTests.test_doctor_ignores_local_checkpoint_markdown: first run failed as expected; doctor still scanned Docs/checkpoints
/opt/homebrew/bin/python3.12 -m unittest Tests.test_rkp_package.RkpPackageTests.test_doctor_ignores_local_checkpoint_markdown: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: pipeline doctor: ok
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 69 tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
git diff --check: ok
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Resume/checkpoint dosyaları agent-local scratch kabul edilmeli. Public docs altında yaşasalar bile release doctor'ın öğretim dokümanı kalitesiyle karıştırılmamalı.

### Sprint 59: RKG Idea Score Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-07 14:31 +03
**Amaç:** RKG/Game Factory katmanında proje scaffold öncesi fikir eleme kapısını CLI ve testlerle netleştirmek.

**Yapılanlar:**

- `src/rkg/idea_score.py` eklendi.
- `rkg score-idea <idea.json> [--json]` alt komutu eklendi.
- Fikir skoru `pass`, `revise`, `reject` verdict'i üretiyor.
- İlk dalga için büyük scope bayrakları reject ediliyor: multiplayer, open world, backend, heavy character animation, moderation, user-generated content.
- `rkg init-game` generated Swift output'u spec text'i için string literal escape yapacak şekilde düzeltildi.
- Generated `GameView` ilk gameplay asset id'sini `Entity.load(named:)` ile deniyor, yoksa procedural target fallback'e dönüyor.
- `PyYAML>=6.0` package dependency olarak eklendi; CLI'nın `.yaml` desteği fresh install'da karşılıksız kalmıyor.
- `Docs/game-factory.md`, `Docs/production-playbook.md` ve `Docs/ai-handoff.md` RKG score gate ile güncellendi.

**Verification:**

```text
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_score_idea.py: first run failed as expected; rkg.idea_score module was missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_score_idea.py: ok, 5 tests
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py: first run failed as expected; Swift escaping and generated asset load were missing
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py: ok, 6 tests
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests: ok, 68 tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": manifest ok
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor: 0 errors, 4 warnings
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check: release-check ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

RKG asset kabulünü kendisi sahiplenmemeli; generated runtime sadece RKP'nin kabul edeceği asset id'sini denemeli ve fallback'i korumalı. Game idea gate'i de scaffold'dan önce çalışmalı, yoksa factory zayıf oyunları otomatik proje haline getirir.

### Sprint 58: Ruff Lint Configuration

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 21:10 +03
**Amaç:** Audit rotasındaki first-class Python lint altyapısını yapılandırmak.

**Yapılanlar:**

- `pyproject.toml` içine `dev` optional dependency olarak `ruff` eklendi.
- Ruff config eklendi: Python 3.10 target, `src/Tests/Tools` kapsamı, temel `E/F/I/UP/B` lint seçimi.
- Makefile `lint` hedefi eklendi.
- GitHub Actions içine editable dev install ve `python3 -m ruff check src Tests Tools` adımı eklendi.
- README, `Docs/cli-tool.md` ve audit dosyası lint komutuyla güncellendi.

**Verification:**

```text
command -v ruff: not installed in current local environment
python3 Tools/rkp.py doctor --json: ok, 0 errors, 1 checkout warning
python3 -m unittest discover -s Tests: ok
git diff --check: ok
```

**Öğrenme notu:**

Lint gate'i CI'da kurulabilir hale geldi; local makinede çalıştırmak için önce `python3 -m pip install -e ".[dev]"` gerekiyor.

### Sprint 57: Safe Cleanup Command

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 21:05 +03
**Amaç:** Audit rotasındaki local scratch cleanup işini destructive olmayan keşif modu ve explicit apply modu ile CLI'a taşımak.

**Yapılanlar:**

- `src/rkp/cleanup.py` eklendi.
- `rkp clean --dry-run` ignored local output adaylarını listeliyor.
- `rkp clean --apply` sadece explicit istendiğinde adayları kaldırıyor.
- Cleanup adayları: `Build`, `__pycache__`, `*.egg-info`, `.DS_Store`, boş `Assets/Imported/(A Document Being Saved By usdzip*)` klasörleri.
- Makefile `clean` hedefi `python3 Tools/rkp.py clean --apply` kullanıyor.
- README ve `Docs/cli-tool.md` clean komutlarıyla güncellendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_cleanup_dry_run_reports_candidates_without_removing: first run failed as expected; rkp.cleanup module was missing
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_cleanup_dry_run_reports_candidates_without_removing: ok
python3 Tools/rkp.py clean --dry-run: ok, listed 9 candidates and removed nothing
python3 -m unittest Tests.test_rkp_package Tests.test_rkp_cli: ok, 22 tests
python3 -m compileall -q src Tools Tests: ok
```

**Öğrenme notu:**

Cleanup komutu güvenli keşif moduyla başlamalı. `--apply` bilinçli bir kullanıcı aksiyonu; release verification sırasında otomatik temizlik yapılmıyor.

### Sprint 56: Game Rules Extraction

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 21:00 +03
**Amaç:** `GameARView.swift` sorumluluklarını azaltma rotasının ilk güvenli dilimini uygulamak.

**Yapılanlar:**

- `Sources/RealityKitPipelineDemo/GameRules.swift` eklendi.
- Wave target count hesapları `WaveRules` içine taşındı.
- Screen-space ve spatial target scoring eşikleri `TargetScoring` içine taşındı.
- `GameARView.swift` bu pure helper'ları kullanacak şekilde sadeleştirildi.
- XcodeGen yeniden çalıştırıldı; yeni Swift dosyası projeye eklendi.

**Verification:**

```text
xcodegen generate: ok
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild: ok; CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Bu refactor behavior değiştirmeden sadece pure math/rules katmanını ayırdı. Sonraki güvenli dilimler target factory, arena builder ve hit effect system olabilir.

### Sprint 55: Binary USDZ Inspection via usdcat

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:55 +03
**Amaç:** `inspect-usdz` kalite kapısındaki binary `.usdc` geometry/UV blind spot'unu gidermek.

**Yapılanlar:**

- `inspect-usdz`, text `.usda`/`.usd` üye bulamazsa ve `usdcat` mevcutsa USDZ paketini text'e decode edip aynı triangle/UV parser'larını kullanıyor.
- `usdcat` yoksa veya hata dönerse mevcut güvenli davranış korunuyor: geometry/UV `unknown`, sahte count yok.
- Binary `.usdc` decode yolu unit testle mock'landı.
- `Docs/cli-tool.md` binary inspection davranışıyla güncellendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_inspect_usdz_uses_usdcat_for_binary_geometry_when_available: first run failed as expected; inspect_usdz had no usdcat path
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_inspect_usdz_uses_usdcat_for_binary_geometry_when_available: ok
python3 Tools/rkp.py inspect-usdz target_basic_textured --json: ok, triangles=284, triangleStatus=ok, uv st=present, baseColor 512x512 / 1024
python3 -m unittest Tests.test_rkp_package Tests.test_rkp_project: ok, 31 tests
python3 -m compileall -q src Tools Tests: ok
```

**Öğrenme notu:**

Binary USDZ için doğru yaklaşım "bilinmiyor" demekten "araç varsa ölç, yoksa bilinmiyor de" seviyesine çıktı. Bu, release gate'i daha anlamlı yapıyor ama tool-less makinelerde deterministik fallback'i koruyor.

### Sprint 54: Shared Blender Discovery

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:48 +03
**Amaç:** `doctor --blender` ve `build-asset` arasındaki Blender executable discovery duplication'ını kaldırmak.

**Yapılanlar:**

- `src/rkp/tool_discovery.py` eklendi.
- `resolve_blender()` env override, PATH lookup ve macOS app fallback sonucunu structured `ToolResolution` olarak döndürüyor.
- `pipeline_doctor.py` ve `build_asset.py` aynı resolver'a geçirildi.
- Invalid `BLENDER` override hata mesajı korunarak testle sabitlendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_tool_discovery_reports_invalid_blender_override: first run failed as expected; rkp.tool_discovery module was missing
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_tool_discovery_reports_invalid_blender_override Tests.test_rkp_cli.RkpCliTests.test_doctor_blender_reports_invalid_override: ok
python3 -m compileall -q src Tools Tests: ok
rg "MACOS_BLENDER_APP|shutil\\.which\\(\"blender\"\\)|BLENDER" src/rkp: ok; executable discovery lives in src/rkp/tool_discovery.py
python3 -m unittest discover -s Tests: ok, 46 tests
python3 Tools/rkp.py doctor --blender --json: ok, 0 errors, 1 checkout warning
BLENDER=/nonexistent/blender python3 Tools/rkp.py doctor --blender --json: expected failure, BLENDER error reported
```

**Öğrenme notu:**

Tool discovery bir CLI alt komutu değil, paylaşılan platform bilgisi. Aynı resolver build, doctor ve gelecekte version matrix için tek doğruluk kaynağı olmalı.

### Sprint 53: Manifest Helper Consolidation

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:42 +03
**Amaç:** Audit rotasındaki manifest/asset lookup duplication riskini azaltmak ve baseColor contract semantiğini tek helper modülünde toplamak.

**Yapılanlar:**

- `src/rkp/asset_manifest.py` eklendi.
- `load_manifest`, `write_manifest`, `find_asset`, `load_asset`, `imported_asset_ids`, `asset_usdz_path`, `expected_basecolor_name` ve `expected_basecolor_texture` helper'ları merkezileştirildi.
- `build_asset.py`, `inspect_usdz.py`, `usdz_fallback_builder.py`, `accept_asset.py`, `new_asset.py` ve `cli.py` shared helper'lara geçirildi.
- `textureMaps` eksikse baseColor required; açık `textureMaps: []` varsa baseColor not-required davranışı testle sabitlendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_asset_manifest_helpers_expose_shared_contract: first run failed as expected; rkp.asset_manifest module was missing
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_asset_manifest_helpers_expose_shared_contract: ok
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_asset_manifest_helpers_expose_shared_contract Tests.test_rkp_package.RkpPackageTests.test_release_check_assets_inspects_imported_assets_before_xcode: ok
python3 -m compileall -q src Tools Tests: ok
rg "def load_asset|def load_manifest|def write_manifest|def find_asset|def expected_basecolor_name|def expected_basecolor_texture" src/rkp: ok; definitions only in src/rkp/asset_manifest.py
python3 -m unittest discover -s Tests: ok, 45 tests
python3 Tools/rkp.py verify-asset target_basic_textured: ok
python3 Tools/rkp.py doctor --json: ok, 0 errors, 1 checkout warning
```

**Öğrenme notu:**

Manifest contract semantiği tek yerde durmalı; aksi halde `build-asset`, `inspect-usdz` ve `release-check --assets` aynı asset için farklı gerçeklikler üretebilir.

### Sprint 52: Runtime Helper Extraction

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:35 +03
**Amaç:** Audit rotasındaki P2 coupling riskini azaltmak; subprocess helper'larını `cli.py` entrypoint'inden çıkarıp shared runtime modülüne taşımak.

**Yapılanlar:**

- `src/rkp/runtime.py` eklendi.
- `package_env`, `module_command` ve subprocess `run` helper'ı runtime modülüne taşındı.
- `cli.py`, `accept_asset.py`, `build_asset.py` ve `prompt_asset.py` runtime helper import'larına geçirildi.
- `cli.py` artık shared helper modülü gibi kullanılmıyor; entrypoint/orchestration rolüne yaklaştırıldı.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_runtime_helpers_expose_package_subprocess_contract: first run failed as expected; rkp.runtime module was missing
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_runtime_helpers_expose_package_subprocess_contract: ok
python3 -m unittest Tests.test_rkp_package Tests.test_rkp_cli: ok, 18 tests
python3 -m compileall -q src Tools Tests: ok
rg "from rkp\\.cli import module_command|from rkp\\.cli import package_env|def package_env|def module_command|def run\\(" src/rkp Tests: ok; runtime helper definitions only in src/rkp/runtime.py
```

**Öğrenme notu:**

Küçük shared runtime modülü, sonraki manifest/tool-discovery refactor'ları için daha temiz bağımlılık yönü sağlıyor. CLI artık alt komutlar için helper sağlayan merkez değil, komut yüzeyi.

### Sprint 51: Release Asset Gate and Starter Stub Contract

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:30 +03
**Amaç:** Audit rotasının ilk P1 maddelerini uygulamak: release gate'e imported asset inspection eklemek ve plain `new-asset` stub'unu baseColor texture contract ile hizalamak.

**Yapılanlar:**

- `rkp release-check --assets` eklendi.
- `release-check --assets`, manifestte `status: imported` olan asset'ler için Xcode build öncesinde `inspect-usdz <id>` çalıştırıyor ve ilk hatada duruyor.
- Makefile `make release-check assets=1` destekliyor.
- `target_basic` manifest kaydı texture'sız imported asset niyetini açıkça `textureMaps: []` ile belirtiyor.
- `new-asset` Blender starter script'i artık 512x512 baseColor texture üretir, `st` UV layer yazar, node material zinciri kurar ve `export_textures_mode="NEW"` ile export eder.
- README, `Docs/cli-tool.md`, `Docs/ai-handoff.md` ve `Docs/codebase-audit.md` yeni P1 durumuyla güncellendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_release_check_assets_inspects_imported_assets_before_xcode: first run failed as expected; run_release_check did not accept include_assets
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_release_check_assets_inspects_imported_assets_before_xcode: ok
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_new_asset_blender_stub_matches_basecolor_export_contract: first worker run failed as expected on old stub contract
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_new_asset_blender_stub_matches_basecolor_export_contract: ok
python3 Tools/rkp.py release-check --assets: first full run failed at target_basic because textureMaps intent was implicit
python3 Tools/rkp.py release-check --assets: ok; 43 tests, all imported assets inspected, xcodebuild ok with CoreSimulator sandbox warnings only
```

**Öğrenme notu:**

Yeni gate hemen gerçek drift yakaladı: texture'sız legacy asset bile manifestte açık contract istemeli. Release kapısını sıkılaştırmak refactor'dan önce geldiği için doğru sıraydı.

### Sprint 50: Whole Repo Audit and Cleanup Route

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 20:20 +03
**Amaç:** Tüm projeyi dead code, optimizasyon, kalite kapısı ve refactor riski açısından tarayıp uygulanabilir rota çıkarmak.

**Yapılanlar:**

- Git history hotspot/bug-magnet taraması yapıldı; en riskli kod dosyası `Sources/RealityKitPipelineDemo/GameARView.swift` olarak işaretlendi.
- Python AST dead-code taraması yapıldı; public top-level fonksiyon/class için doğrulanmış silinebilir tracked dead code bulunmadı.
- Swift referans taraması yapıldı; tek false-positive sonuçlar `UIViewRepresentable` protocol method'larıydı.
- Local hygiene taraması yapıldı; ignored `Build/`, `__pycache__/`, `src/rkp.egg-info/`, `.DS_Store` ve boş usdzip scratch klasörleri cleanup adayı olarak kaydedildi.
- `Docs/codebase-audit.md` eklendi; P1/P2/P3 rota, acceptance komutları ve bulgu gerekçeleri yazıldı.
- `Docs/ai-handoff.md` yeni audit rotasına bağlandı.

**Verification:**

```text
python3 -m compileall -q src Tools Tests: ok
python3 -m unittest discover -s Tests: ok, 41 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors, 1 warning (.github/workflows/ci.yml Node 20 deprecation)
python3 Tools/rkp.py doctor --blender --json: ok, Blender discovery passes
python3 Tools/rkp.py inspect-usdz target_basic_textured --json: ok, baseColor 512x512 / 1024
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild: ok; CoreSimulator sandbox warnings only
python3 Tools/rkp.py release-check: ok; doctor warning only, tests ok, xcodegen ok, xcodebuild ok
```

**Öğrenme notu:**

Bu repo şu an kırık değil; ana risk sessiz asset regresyonu. Bu yüzden ilk rota maddesi refactor değil, imported asset inspection'ı release gate içine almak.

### Sprint 49: Blender Diagnostic and Dead Code Cleanup

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 14:25 +03
**Amaç:** Release öncesi Blender kurulum kırılma noktasını açık diagnostic'e taşımak ve son eklenen CLI kodundaki bariz dead code'u temizlemek.

**Yapılanlar:**

- `rkp doctor --blender` flag'i eklendi.
- JSON ve text doctor akışları Blender executable discovery kontrolünü opsiyonel olarak çalıştırabiliyor.
- `BLENDER=/path/to/blender rkp doctor --blender` override path'ini doğruluyor; invalid override explicit error veriyor.
- Makefile `make doctor blender=1 [json=1]` destekliyor.
- README, `Docs/cli-tool.md` ve `Docs/ai-handoff.md` Blender diagnostic durumuyla güncellendi.
- Dead code temizliği: `src/rkp/meshy_asset.py` içindeki kullanılmayan `urllib.error` import'u kaldırıldı; `src/rkp/cli.py` içindeki redundant lokal `import os` kaldırıldı.
- `Tools/*.py` wrapper'ları temizlenmedi; package sonrası bile geriye dönük CLI uyumluluğu sağladıkları için intentional compatibility layer olarak bırakıldı.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_cli.RkpCliTests.test_doctor_blender_reports_invalid_override: first run failed as expected because doctor --blender was not implemented
python3 -m unittest Tests.test_rkp_cli.RkpCliTests.test_doctor_blender_reports_invalid_override Tests.test_rkp_cli.RkpCliTests.test_doctor_json_reports_no_errors: ok
python3 -m unittest Tests.test_rkp_cli Tests.test_rkp_init: ok, 16 tests
python3 -m unittest discover -s Tests: ok, 41 tests
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
BLENDER=/nonexistent/blender python3 Tools/rkp.py doctor --blender --json: expected failure, BLENDER error reported
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py verify-asset target_basic_textured: ok, baseColor size 512x512 / 1024
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild: ok; CoreSimulator sandbox warnings only
git diff --check: ok
```

**Öğrenme notu:**

Blender sorunu `build-asset` sırasında sürpriz olmamalı. Normal `doctor` minimal projeleri gürültüsüz tutar; explicit `--blender` ise setup debugging için bilinçli, fail-fast bir kapı sağlar.

### Sprint 48: Guide and PDF Refresh

**Durum:** Tamamlandı
**Tarih:** 2026-05-06 14:10 +03
**Amaç:** Public learning guide ve PDF çıktısını yeni CLI kalite kapılarıyla hizalamak.

**Yapılanlar:**

- `Docs/guide.md` tarihi 2026-05-06 olarak güncellendi.
- Completion standard `rkp verify-asset` ve `rkp inspect-usdz` kalite kapılarıyla hizalandı.
- Yeni `CLI Quality Gate` bölümü eklendi: `make-asset`, `build-asset`, `verify-asset`, `inspect-usdz`, screenshot acceptance ve release-check ilişkisi anlatıldı.
- Asset draft üretim yolları guide'a eklendi: deterministic template, Blender build, Meshy backend ve explicit Claude generator.
- Coverage matrix `inspect-usdz`, `verify-asset` ve CLI draft generation satırlarıyla güncellendi.
- `Docs/pdf/realitykit-pipeline-guide.pdf` yeniden üretildi.

**Verification:**

```text
make guide: ok; PDF regenerated, WeasyPrint/fontconfig warnings only
pdfinfo Docs/pdf/realitykit-pipeline-guide.pdf: ok, 31 pages, A4, 714898 bytes
pdftotext Docs/pdf/realitykit-pipeline-guide.pdf - | rg "CLI Quality Gate|verify-asset|inspect-usdz": ok
pdftoppm -f 1 -l 6 -png Docs/pdf/realitykit-pipeline-guide.pdf Build/pdf-preview/guide: ok
Visual check: rendered pages 1, 4, 5 and 6 are legible; CLI Quality Gate section and split asset-draft table render without clipped text.
python3 -m unittest discover -s Tests: ok, 40 tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
git diff --check: ok
python3 Tools/rkp.py verify-asset target_basic_textured: ok, baseColor size 512x512 / 1024
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
```

**Öğrenme notu:**

CLI kalite kapıları README'de kalmamalı; öğretici PDF'te de aynı acceptance standardı anlatılmalı. Aksi halde public guide eski manuel akışı öğretmeye devam eder.

### Sprint 47: Texture Dimension Budget Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-05 19:30 +03
**Amaç:** `inspect-usdz` içindeki texture kontrolünü sadece "dosya var mı" seviyesinden manifest texture budget denetimine yükseltmek.

**Yapılanlar:**

- `inspect-usdz` PNG ve JPEG header'larından baseColor texture width/height okuyabiliyor.
- JSON payload `baseColorTexture.width`, `height`, `maxSize` ve `sizeStatus` alanlarını raporluyor.
- Texture boyutu manifest `maxTextureSize` değerini aşarsa `inspect-usdz` non-zero dönüyor.
- Okunamayan/unsupported texture dimension durumunda değer uydurulmuyor; `sizeStatus=unknown` kalıyor.
- README, `Docs/cli-tool.md` ve `Docs/ai-handoff.md` inspect kapsamını texture dimension budget ile güncelledi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_basecolor_texture_exceeds_budget: first run failed as expected because texture dimensions were not reported and over-budget textures passed
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_basecolor_texture_exceeds_budget: ok
python3 Tools/rkp.py inspect-usdz target_basic_textured --json: ok, baseColor 512x512 / 1024
python3 Tools/rkp.py inspect-usdz enemy_drone --json: ok, baseColor 512x512 / 1024
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_budget_or_texture_gate_fails Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_text_usd_lacks_st_uv Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_basecolor_texture_exceeds_budget: ok
python3 -m unittest discover -s Tests: ok, 40 tests
python3 Tools/rkp.py verify-asset target_basic_textured: ok, baseColor size 512x512 / 1024
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
git diff --check: ok
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
```

**Öğrenme notu:**

Texture budget manifestte sayı olarak durmamalı; üretilen USDZ paketinin içindeki gerçek image header'ı ile ölçülmeli. Böylece 512/1024 kararları screenshot öncesi otomatik kalite kapısına dönüşür.

### Sprint 46: Asset Verification Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-05 19:20 +03
**Amaç:** Build, USDZ inspection, screenshot acceptance ve release-check parçalarını tek kalite kapısı komutunda birleştirmek.

**Yapılanlar:**

- `rkp verify-asset <asset_id>` komutu eklendi.
- Varsayılan davranış built USDZ için `inspect-usdz` kapısını çalıştırıyor.
- `--build` verilirse inspect öncesi `build-asset`, `--screenshot` verilirse inspect sonrası `accept-asset`, `--release-check` verilirse en sonda release-check çalışıyor.
- Komut ilk başarısız gate'te duruyor ve hangi adımda durduğunu stderr'e yazıyor.
- Makefile'a `make verify-asset id=<asset_id> [build=1] [screenshot=...] [release=1]` wrapper'ı eklendi.
- README ve `Docs/cli-tool.md` ilk asset akışını `verify-asset` üstünden anlatacak şekilde güncellendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_verify_asset_runs_build_inspect_accept_and_release_check Tests.test_rkp_package.RkpPackageTests.test_verify_asset_stops_when_inspection_fails: first run failed as expected because run_verify_asset did not exist
python3 -m unittest Tests.test_rkp_package.RkpPackageTests.test_verify_asset_runs_build_inspect_accept_and_release_check Tests.test_rkp_package.RkpPackageTests.test_verify_asset_stops_when_inspection_fails: ok
python3 -m unittest Tests.test_rkp_cli.RkpCliTests.test_verify_asset_runs_inspection_gate_for_ready_asset Tests.test_rkp_cli.RkpCliTests.test_verify_asset_rejects_unknown_asset: ok
python3 -m unittest discover -s Tests: ok, 39 tests
python3 Tools/rkp.py verify-asset target_basic_textured: ok, inspect-usdz passed with baseColor present and binary .usdc geometry/uv unknown
git diff --check: ok
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
```

**Öğrenme notu:**

Tek komut, tek doğruluk kaynağı değildir; arkasındaki kapıların sıralı ve durdurucu olması gerekir. `verify-asset` acceptance'ı otomatikleştirmiyor, screenshot kanıtı verilirse acceptance kapısını kontrollü şekilde çalıştırıyor.

### Sprint 45: USDZ Inspection Gate

**Durum:** Tamamlandı
**Tarih:** 2026-05-05 19:10 +03
**Amaç:** Built USDZ dosyasını acceptance öncesi hızlıca denetleyen gerçek kalite kapısı eklemek.

**Yapılanlar:**

- `rkp inspect-usdz <asset_id>` komutu eklendi.
- Komut manifest asset kaydını ve config-aware asset path'ini kullanıyor; external `rkp.json` projelerinde de çalışıyor.
- USDZ zip paketi okunup entry listesi, dosya boyutu, beklenen `<asset_id>_basecolor.png` texture varlığı, text USDA içinde `primvars:st` sinyali ve `faceVertexCounts` üzerinden bilinen triangle count raporlanıyor.
- Triangle count manifest `maxTriangles` değerini aşarsa, beklenen baseColor texture paket içinde yoksa veya text USD'de `st` UV primvar eksikse komut non-zero dönüyor.
- Binary-only USD içerikte geometry count uydurulmuyor; bilinmiyorsa `unknown` raporlanıyor.
- `build-asset` ve `make-asset --build` çıktıları acceptance öncesi `rkp inspect-usdz <id>` öneriyor.
- Makefile'a `make inspect-usdz id=<asset_id> [json=1]` wrapper'ı eklendi.
- README ve `Docs/cli-tool.md` ilk asset akışına inspect adımını ekledi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_budget_or_texture_gate_fails: first run failed as expected because inspect-usdz command did not exist
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_budget_or_texture_gate_fails: ok
python3 -m unittest Tests.test_rkp_cli.RkpCliTests.test_inspect_usdz_rejects_unknown_asset Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_missing_texture_as_info_after_successful_build: ok
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_text_usd_lacks_st_uv: first run failed as expected because missing text USD st was reported ok
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_json_reports_texture_and_budget_status Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_budget_or_texture_gate_fails Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_fails_when_text_usd_lacks_st_uv: ok
python3 Tools/rkp.py inspect-usdz target_basic_textured --json: ok, texture present, geometry/uv unknown because package contains binary .usdc
python3 -m unittest discover -s Tests: ok, 35 tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
git diff --check: ok
python3 Tools/rkp.py inspect-usdz target_basic_textured: ok, baseColor texture present, geometry/uv unknown for binary .usdc package
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
```

**Öğrenme notu:**

Acceptance screenshot hâlâ son kapı, ama screenshot'tan önce otomatik paket denetimi yapılmalı. Tool'un değeri “dosya var” demekten çok, USDZ'nin içindeki öğretici kontrat sinyallerini ölçmesinde.

### Sprint 44: Explicit AI Asset Backends

**Durum:** Tamamlandı
**Tarih:** 2026-05-05 18:40 +03
**Amaç:** Yarım kalan Claude/Meshy asset üretim denemesini deterministik default davranışı bozmadan kapatmak.

**Yapılanlar:**

- `prompt-asset` için `--generator template|claude` eklendi; `template` default kaldı ve ortamda `ANTHROPIC_API_KEY` olsa bile otomatik ağ çağrısı yapmıyor.
- Claude generator, repo config-aware Blender boilerplate + `export_usdz(obj)` snippet'i etrafına model çıktısını sarıyor; format string bug'ı regression testiyle kapatıldı.
- `make-asset --backend meshy --quality preview|refine` eklendi; Meshy text-to-3D USDZ çıktısı `Assets/Imported/<id>.usdz` path'ine indiriliyor, preview task mobil başlangıç bütçesi olarak 1500 poly hedefliyor, ardından opsiyonel `--screenshot`/`--release-check` kapılarını çalıştırabiliyor.
- `--generator claude` için API key/paket yoksa manifest mutasyonu yapmadan erken hata dönmesi sağlandı.
- `anthropic` paket bağımlılığı optional `rkp[ai]` kapsamına alındı.
- README ve `Docs/cli-tool.md` deterministic template, explicit Claude generator ve Meshy backend kullanımını ayıracak şekilde güncellendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_package: first run failed as expected on Claude export snippet format bug
python3 -m unittest Tests.test_rkp_package: ok, 5 tests
python3 -m unittest discover -s Tests: ok, 29 tests
python3 -m unittest discover -s Tests: ok, 30 tests after Meshy acceptance orchestration test
python3 -m unittest discover -s Tests: ok, 31 tests after Claude missing-key no-mutation test
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')": ok
python3 Tools/rkp.py doctor --json: ok, errors=0, warnings=1 (.github/workflows/ci.yml Node 20 deprecation)
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
```

**Öğrenme notu:**

Asset CLI'da API key varlığı davranışı değiştirmemeli. Öğretici ve test edilebilir default template kalır; ağ kullanan üreticiler açık flag ile seçilir ve kabul kapısı yine RealityKit screenshot evidence ister.

### Sprint 43: Prompt Geometry Boundary

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 19:25 +03
**Amaç:** `prompt-asset` çıktısının full text-to-3D gibi algılanmasını engellemek ve default geometry fallback'i görünür yapmak.

**Yapılanlar:**

- Unrecognized prompt test'i genişletildi; stdout artık default geometry template sınırını açıkça söylemek zorunda.
- `prompt-asset` unrecognized archetype durumunda `geometry: default <type> procedural template; edit the Blender script for prompt-specific shape` mesajı basıyor.
- Manifest note'u `type-default` gibi internal string yerine default geometry template ve Blender script edit sınırını anlatıyor.
- README ve `Docs/cli-tool.md` `prompt-asset` / `make-asset` davranışını scaffold-first olarak tanımlıyor; desteklenen archetype set'i ve katana/spaceship gibi prompt'larda elle Blender script düzenleme gereği belgelendi.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_prompt_asset_reports_unrecognized_archetype_without_internal_label: first run failed as expected; geometry fallback message was missing
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_prompt_asset_reports_unrecognized_archetype_without_internal_label: ok
```

**Öğrenme notu:**

Prompt pipeline'ın güvenilirliği sadece ne ürettiğinde değil, ne üretmediğini açık söylemesinde. v0.1 prompt'u brief/archetype/template seçimi için kullanır; yeni 3D form icat etmez.

### Sprint 42: Texture Packaging Info Condition

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 19:10 +03
**Amaç:** `build-asset` başarılı olduğunda texture info mesajının gerçek Blender/USDZ durumunu ölçmesini sağlamak.

**Yapılanlar:**

- Root cause bulundu: önceki condition kaynak `Assets/Textures/<id>_basecolor.png` dosyasını kontrol ediyordu. Blender bu dosyayı oluşturup USDZ içine paketleyemeyince info mesajı susuyordu.
- `build-asset` artık USDZ paketinin içindeki dosya listesini kontrol ediyor ve `<asset_id>_basecolor.png` paketlenmemişse info mesajı basıyor.
- USDZ içinde texture varsa info mesajı basılmadığını doğrulayan ters yön regression testi eklendi.
- `chown: Operation not permitted` repo kodunda bulunmadı; `strings /usr/bin/usdzip` ve Blender binary output'unda external tool kaynaklı izin mesajı izi var.

**Verification:**

```text
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_when_texture_exists_but_is_not_packaged_in_usdz: first run failed as expected; source texture existed so old condition did not print info
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_when_texture_exists_but_is_not_packaged_in_usdz Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_missing_texture_as_info_after_successful_build: ok, 2 tests
python3 -m unittest Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_when_texture_exists_but_is_not_packaged_in_usdz Tests.test_rkp_project.RkpProjectTests.test_build_asset_reports_missing_texture_as_info_after_successful_build Tests.test_rkp_project.RkpProjectTests.test_build_asset_does_not_report_texture_info_when_usdz_contains_texture: ok, 3 tests
```

**Öğrenme notu:**

Build UX için doğru soru kaynak texture dosyası var mı değil, kullanıcıya verilen USDZ içinde texture var mı. Testin de aynı artifact boundary'yi ölçmesi gerekiyor.

### Sprint 41: First Asset UX Copy

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 18:45 +03
**Amaç:** Fresh asset loop'ta başarılı build çıktısını yanlış alarm gibi gösteren iki küçük CLI mesajını düzeltmek.

**Yapılanlar:**

- Prompt archetype tanınmadığında kullanıcı çıktısı `type-default` yerine `unrecognized - using default (<asset_type>)` gösteriyor.
- Manifest note'ları artık internal `type-default` string'ini yazmıyor.
- Başarılı `build-asset` sonrası beklenen basecolor texture yoksa `warning` yerine açıklayıcı `info: no texture file found - USDZ built without texture` mesajı basılıyor.
- README First Asset bölümüne `accept-asset` için Xcode/simulator screenshot gerektiği, bu yoksa asset'in `planned` draft olarak kalabileceği notu eklendi.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected on archetype fallback and missing-texture info tests
python3 -m unittest Tests/test_rkp_project.py: ok, 11 tests
python3 -m unittest discover -s Tests: ok, 24 tests
rtk python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 24 passed, manifest ok, iOS build ok; CoreSimulator sandbox warnings present)
```

**Öğrenme notu:**

CLI copy'si pipeline doğruluğunun parçası. USDZ başarıyla üretildiyse eksik texture veya tanınmayan prompt sınıflandırması kullanıcıda build failure hissi yaratmamalı.

### Sprint 40: Fresh Project Walkthrough

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 18:10 +03
**Amaç:** Clone bilmeyen yeni kullanıcının GitHub install ile boş bir projede ilk asset contract ve USDZ draft'ına ulaşabildiğini kanıtlamak, Blender/fallback sınırını dürüstçe belgelemek.

**Yapılanlar:**

- `/private/tmp/rkp_walkthrough_project` içinde fresh external project denemesi yapıldı.
- GitHub URL üzerinden izole `pipx install` çalıştırıldı; `rkp --version` `0.1.0` döndü.
- `rkp init --force --project-name WalkthroughGame` minimal workspace oluşturdu.
- `rkp doctor --json` external projede `0 error(s)` ve sadece `README.md`, `LICENSE`, `Makefile` warning'leri verdi.
- `rkp make-asset walkthrough_drone --type gameplay_target --prompt "red bullseye drone target"` manifest, asset brief ve Blender script üretti.
- Blender 4.5.8 background build bu makinede segmentation fault 11 ile düştü; RKP crash log path'ini raporladı ve `usdzip` fallback ile `Assets/Imported/walkthrough_drone.usdz` üretti.
- README ve `Docs/cli-tool.md` fresh-project walkthrough, expected doctor output, Blender fallback davranışı ve v0.1 limitleriyle güncellendi.

**Verification:**

```text
PIPX_HOME=/private/tmp/rkp_walkthrough_pipx_home PIPX_BIN_DIR=/private/tmp/rkp_walkthrough_pipx_bin pipx install --force git+https://github.com/kingkyylian/realitykitpipelineguide.git: ok
/private/tmp/rkp_walkthrough_pipx_bin/rkp --version: ok, rkp 0.1.0
/private/tmp/rkp_walkthrough_pipx_bin/rkp init --force --project-name WalkthroughGame: ok
/private/tmp/rkp_walkthrough_pipx_bin/rkp doctor --json: ok, 0 errors / 3 warnings
/private/tmp/rkp_walkthrough_pipx_bin/rkp make-asset walkthrough_drone --type gameplay_target --prompt "red bullseye drone target": ok
BLENDER=/opt/homebrew/bin/blender /private/tmp/rkp_walkthrough_pipx_bin/rkp build-asset walkthrough_drone: Blender exit 139, fallback USDZ built via /usr/bin/usdzip, 16192 bytes
/private/tmp/rkp_walkthrough_pipx_bin/rkp status --json: ok, asset next command points to screenshot acceptance
/private/tmp/rkp_walkthrough_pipx_bin/rkp release-check: ok (doctor 0 errors/3 warnings, tests skipped, manifest ok, xcode skipped)
```

**Öğrenme notu:**

İlk kullanıcı deneyimi artık "repo'yu clone'la" demeden çalışıyor. Kalan güven açığı CLI bootstrap değil; Blender background export'un makineye göre değişebilmesi ve arbitrary Xcode project resource wiring'in hâlâ manuel olması.

### Sprint 39: External Doctor Warning UX

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 17:26 +03  
**Amaç:** Yeni kullanıcı `rkp init -> rkp doctor` akışında toolkit development repo dosyaları eksik diye 20+ warning görmesin.

**Yapılanlar:**

- `Tests/test_rkp_init.py` external init projesinde doctor warning set'ini regression test ile kilitledi.
- `Doctor.is_toolkit_repo()` eklendi; `pyproject.toml` + `src/rkp/cli.py` varsa toolkit repo-specific recommended path'leri kontrol ediliyor.
- External projelerde recommended warning set'i sadece `README.md`, `LICENSE`, `Makefile` olarak kaldı.
- Toolkit repo içinde mevcut doctor coverage korunuyor; package/dev dosyaları hâlâ bu repo için recommended.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_init.py: first new warning-set test failed as expected; external init project emitted toolkit repo warnings
python3 -m unittest Tests/test_rkp_init.py: ok, 7 tests
python3 -m unittest discover -s Tests: ok, 22 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 22 passed, manifest ok, iOS build ok; CoreSimulator sandbox warnings present)
```

**Öğrenme notu:**

Doctor aynı anda iki persona'ya hizmet ediyor: toolkit maintainer ve external project user. Bu iki warning budget'ı ayrılmadan onboarding UX yanlış sinyal veriyor.

### Sprint 38: Install-First README and CI Smoke

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 17:18 +03  
**Amaç:** Yeni kullanıcı için README'yi clone-first değil `pipx install git+...` + `rkp` flow'una çevirmek ve GitHub install güvenini CI'a taşımak.

**Yapılanlar:**

- README Quick Start artık normal kullanımda clone gerektirmeyen `pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git` akışıyla başlıyor.
- README `Prompt To Asset`, `First Asset Loop` ve `Common Commands` örnekleri `python3 Tools/rkp.py` yerine `rkp ...` komutlarını ana yol yaptı.
- Repo-local wrapper anlatımı maintainer/toolkit development akışına indirildi.
- `Docs/cli-tool.md` ve skill command reference install örnekleri GitHub pipx install URL'ine güncellendi.
- GitHub Actions CI'a `push` + `main` için `pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git` ve `rkp --version` smoke adımı eklendi.
- CI smoke adımı PEP 668 riskinden kaçınmak için `python3 -m pip install --user pipx` yerine Homebrew `pipx` kullanıyor.

**Verification:**

```text
brew list pipx: ok
PYTHONUSERBASE=/private/tmp/rkp_ci_userbase python3 -m pip install --user pipx: failed as expected on this Homebrew Python due to externally-managed-environment; CI changed to brew-managed pipx
PIPX_HOME=/private/tmp/rkp_ci_smoke_home PIPX_BIN_DIR=/private/tmp/rkp_ci_smoke_bin pipx install --force git+https://github.com/kingkyylian/realitykitpipelineguide.git: ok
/private/tmp/rkp_ci_smoke_bin/rkp --version: ok, rkp 0.1.0
```

**Öğrenme notu:**

CI package smoke test'i PR'da default branch'i test etmemeli. Bu yüzden GitHub URL install gate'i `push` + `main` ile sınırlı; PR'lar checkout üstündeki unit/release gates ile korunuyor.

### Sprint 36: Python Package Entry Point

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 16:20 +03  
**Amaç:** Faz 3 packaging başlangıcı için CLI implementation'ını `src/rkp` paketine taşımak, local import kırılganlığını kapatmak ve subprocess çağrılarını package module formuna geçirmek.

**Yapılanlar:**

- `src/rkp` paketi eklendi; implementation modülleri `cli.py`, `new_asset.py`, `prompt_asset.py`, `build_asset.py`, `accept_asset.py`, `pipeline_doctor.py`, `rkp_project.py` ve `usdz_fallback_builder.py` altına taşındı.
- `Tools/*.py` dosyaları repo-local geriye uyum wrapper'larına çevrildi.
- Local import'lar `from rkp...` absolute package import'larına çevrildi.
- `rkp.cli` subprocess çağrıları `python -m rkp.prompt_asset`, `python -m rkp.build_asset`, `python -m rkp.accept_asset` ve `python -m rkp.cli release-check` formuna geçti.
- `pyproject.toml` eklendi; console entry point `rkp = "rkp.cli:main"`.
- `Tests/test_rkp_package.py` eklendi; `make-asset` orchestration'ın package module subprocess vektörlerini kullandığını doğruluyor.
- `rkp init` sonrası boş manifestin doctor/release-check için geçerli external başlangıç state'i olduğu testlendi; doctor boş `assets: []` listesini artık error saymıyor.
- `Tools/*.py` wrapper'ları `src` path'ini her zaman `sys.path[0]` yapacak şekilde düzeltildi; release-check child process'lerinde `Tools/rkp.py` dosyasının `rkp` paketini gölgelemesi engellendi.
- README, CLI docs, handoff ve skill command reference `rkp` entry point ve package/wrapper ayrımına göre güncellendi.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_package.py: first run failed as expected; no rkp package existed
python3 -m unittest Tests/test_rkp_package.py: ok
python3 -m unittest Tests/test_rkp_init.py: first new doctor test failed as expected; empty assets list was an error
python3 -m unittest Tests/test_rkp_init.py: ok, 6 tests
python3 -m unittest discover -s Tests: ok, 20 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: first package run failed as expected; wrapper path order let Tools/rkp.py shadow the rkp package in child test processes
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 20 passed, manifest ok, iOS build ok; CoreSimulator sandbox warnings present)
UV_CACHE_DIR=/private/tmp/uv-cache uv pip install --target /private/tmp/rkp_uv_pkg_install_test .: ok after network approval for setuptools
PIPX_HOME=/private/tmp/rkp_pipx_home PIPX_BIN_DIR=/private/tmp/rkp_pipx_bin pipx install --force .: ok after network approval for build dependencies
/private/tmp/rkp_pipx_bin/rkp status --json: ok
/private/tmp/rkp_pipx_bin/rkp init --project-name PipxGame: ok in external temp project
/private/tmp/rkp_pipx_bin/rkp release-check: ok in empty external temp project (0 errors, docs/showcase warnings, tests/xcode skipped)
```

**Öğrenme notu:**

Package geçişinde en kırılgan kısım import'tan çok process boundary. Parent CLI package import etse bile child process ancak `python -m rkp.<module>` ve doğru install/PYTHONPATH ile aynı kodu görür.

### Sprint 37: GitHub Install Probe

**Durum:** Bloklu  
**Tarih:** 2026-05-03 16:28 +03  
**Amaç:** Faz 3 kapanışı için GitHub URL üzerinden `pipx install git+...` ve `rkp --version` smoke testini doğrulamak.

**Yapılanlar:**

- `rkp --version` eklendi; package version `src/rkp/__init__.py` içinde `0.1.0`.
- `Tests/test_rkp_cli.py` `--version` regression testiyle genişletildi.
- Local package install sonrası `/private/tmp/rkp_version_pipx_bin/rkp --version` `rkp 0.1.0` döndü.
- Kullanıcının verdiği exact URL test edildi: `git+https://github.com/kyylian/RealityKitPipelineDemo`.
- Repo'nun gerçek remote'u ayrıca test edildi: `git+https://github.com/kingkyylian/realitykitpipelineguide.git`.

**Blok:**

GitHub install henüz kapanmadı çünkü exact URL GitHub'da bulunamıyor, gerçek `origin` ise remote üzerinde henüz local package değişikliklerini içermiyor. Bu workspace'teki `pyproject.toml` ve `src/rkp` değişiklikleri push edilmeden GitHub URL install geçemez.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_cli.py: first version test failed as expected; parser required subcommand before --version
python3 -m unittest Tests/test_rkp_cli.py: ok, 5 tests
PIPX_HOME=/private/tmp/rkp_version_pipx_home PIPX_BIN_DIR=/private/tmp/rkp_version_pipx_bin pipx install --force .: ok
/private/tmp/rkp_version_pipx_bin/rkp --version: ok, rkp 0.1.0
pipx install git+https://github.com/kyylian/RealityKitPipelineDemo: failed, remote repository not found
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git: failed, remote has neither setup.py nor pyproject.toml
```

**Sonraki adım:**

Package değişiklikleri commit/push edildikten sonra aynı GitHub install testi remote URL üzerinden tekrar koşulmalı.

### Sprint 35: Minimal Project Init

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 16:08 +03  
**Amaç:** Faz 2 portability için mevcut RealityKit projelerinde minimal RKP workspace bootstrap eden `rkp init` komutunu eklemek.

**Yapılanlar:**

- `Tests/test_rkp_init.py` eklendi; boş dizinde init, overwrite guard, `--force`, `--project-name` ve mevcut `Assets/Imported` içeriğini koruma senaryoları kapsandı.
- `Tools/rkp.py` global `load_project()` çağrısından lazy project yüklemeye geçirildi; böylece `init` `rkp.json` yokken de çalışabiliyor.
- `rkp init` `rkp.json`, boş `Tools/asset_manifest.json` ve minimal pipeline klasörlerini oluşturuyor.
- `rkp init` mevcut config/manifest varsa `--force` olmadan hata veriyor.
- README, CLI docs, handoff ve skill command reference `init` scope'unu ve Faz 3 paketleme sınırını anlatacak şekilde güncellendi.

**Sınır:**

`rkp init` CLI'ı pip/pipx ile kurmaz. Faz 3 hâlâ `Tools/*.py` dosyalarını `src/rkp` paket modüllerine taşımak, console entry point eklemek ve local import'ları düzeltmek.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_init.py: first run failed as expected; rkp.py imported load_project before parsing init
python3 -m unittest Tests/test_rkp_init.py: ok, 5 tests
python3 -m unittest Tests/test_rkp_project.py Tests/test_rkp_cli.py: ok, 13 tests
python3 -m unittest discover -s Tests: ok, 18 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 18 passed, manifest ok, iOS build ok; CoreSimulator sandbox warnings present)
```

**Öğrenme notu:**

Bootstrap komutu en tehlikeli yerde yazıyor: proje kökü. Bu yüzden default davranış "create only" olmalı; reinitialize ancak `--force` ile açıkça istenmeli.

### Sprint 28: Toolkit Framing and CLI Smoke Tests

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 15:08 +03  
**Amaç:** Repo framing'ini game-first yerine command-first RealityKit pipeline toolkit olarak netleştirmek ve CLI yüzeyine ilk otomatik smoke test kapısını eklemek.

**Yapılanlar:**

- README, AGENTS, handoff, GitHub showcase, changelog ve skill metinleri toolkit/skill/commands ana ürün; SwiftUI + RealityKit app verification fixture olacak şekilde güncellendi.
- `status --json` artık `project` ve `scale` metadata'sı döndürüyor.
- `Tests/test_rkp_cli.py` eklendi; `status --json`, `doctor --json`, `make-asset` acceptance guard'ı ve unknown asset rejection test ediliyor.
- `make test`, CI test adımı ve `release-check` içindeki `tests` gate'i eklendi.
- `enemy_drone` manifest/brief drift'i temizlendi; stale imported scale notu `0.90` ile güncellendi.
- MCP beklentisi açıklandı: standalone MCP server henüz yok, JSON yüzeyleri future MCP-style wrapper için stabil interface.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_cli.py: first run failed as expected because status JSON had no project metadata
python3 -m unittest Tests/test_rkp_cli.py: ok
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 4 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Repo'nun profesyonel sinyali demo oyun mimarisinden çok tekrar kullanılabilir CLI/skill/command kontratından geliyor. Fixture app asset acceptance kanıtı sağlar; ürün kimliği toolkit yüzeyinde kalmalı.

### Sprint 29: External Project Integration Stance

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 15:18 +03  
**Amaç:** README'nin sadece "bu repo içinde kullan" akışını değil, kendi RealityKit projesine taşımak isteyen kullanıcı için mevcut v0.1 sınırını net anlatması.

**Yapılanlar:**

- README'ye `Use In Your Own Project` bölümü eklendi.
- `Docs/cli-tool.md` içine portability notu eklendi.
- `Docs/ai-handoff.md` v0.1 portability durumunu repo-template/fork modeli olarak kaydetti.

**Karar:**

v0.1 standalone package değil. `Tools/rkp.py` repo kökünü ve RKP layout'unu varsayıyor; `--project-root` yok. En dürüst entegrasyon yolu fork/copy toolkit folders + kendi Xcode resource setup'ına `Assets/Imported` bağlamak.

**Verification:**

```text
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 4 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Developer tool framing sadece "öğrenme" senaryosunu değil "mevcut projeme nasıl taşırım?" sorusunu da cevaplamalı. Paketlenmemiş bir aracı paketlenmiş gibi göstermemek daha profesyonel.

### Sprint 30: Project Config Discovery Start

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 15:32 +03  
**Amaç:** Faz 1 portability için `ROOT = __file__` bağımlılığını kırmaya başlamak.

**Yapılanlar:**

- `rkp.json` eklendi; manifest/assets/docs/blender/textures/source path'leri config'e taşındı.
- `Tools/rkp_project.py` eklendi; CWD'den yukarı `rkp.json` arayan `find_project_root()` ve `ProjectPaths` context'i sağlıyor.
- `Tools/rkp.py status --json` artık script konumunu değil, çalışılan dizinden bulunan `rkp.json` projesini okuyor.
- `Tools/pipeline_doctor.py` `ProjectPaths` kabul edecek şekilde güncellendi; manifest/assets/textures path'leri config'ten okunuyor.
- `Tests/test_rkp_project.py` eklendi; external temp project içinde `status --json` config manifestini okuyabildiğini doğruluyor.
- README, CLI docs, handoff ve skill command reference portability durumunu güncelledi.

**Sınır:**

Bu ilk slice sadece `status` ve `doctor` için config-aware. `new_asset`, `prompt_asset`, `build_asset`, `accept_asset`, `usdz_fallback_builder` ve generated Blender script path'leri hâlâ sonraki slice'ta `ProjectPaths` üstüne taşınacak.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected; no rkp_project module and status read script repo manifest
python3 -m unittest discover -s Tests: ok, 6 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 6 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Portable CLI için ilk kırılacak yer entrypoint değil project context. `rkp.json` bulunmadan package veya MCP wrapper yapmak sadece path problemini başka yere taşır.

### Sprint 31: Portable Asset Scaffolding

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 15:47 +03  
**Amaç:** Faz 1 portability içinde `new-asset` ve `prompt-asset` komutlarını external `rkp.json` projesinde çalışır hale getirmek.

**Yapılanlar:**

- `Tests/test_rkp_project.py` external temp project için `new-asset` ve `prompt-asset` regression testleriyle genişletildi.
- `Tools/rkp.py` subprocess script path'leri artık temp proje kökündeki `Tools/` klasörünü değil, gerçek RKP tool script dizinini kullanıyor.
- `Tools/new_asset.py` `ProjectPaths` kullanacak şekilde güncellendi; manifest, brief, blender script, assets ve textures klasörleri `rkp.json` config'inden türetiliyor.
- `Tools/prompt_asset.py` `ProjectPaths` kullanacak şekilde güncellendi; prompt metadata, brief ve generated Blender script config path'lerine yazılıyor.
- Generated Blender stub/template artık `rkp.json` arayarak `assets_dir`, `source_dir` ve `textures_dir` değerlerini okuyacak bootstrapping kodu içeriyor.

**Sınır:**

Bu slice `new-asset` ve `prompt-asset` için portable scaffolding sağlar. `build-asset`, `accept-asset`, `usdz_fallback_builder` ve full `release-check` hâlâ sonraki slice'ta `ProjectPaths` üstüne taşınacak.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected; rkp.py temp project root under Tools/new_asset.py and Tools/prompt_asset.py searched
python3 -m unittest Tests/test_rkp_project.py: ok, 4 tests
python3 -m unittest discover -s Tests: ok, 8 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 8 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Subprocess path'i config path'i değildir. External project testinde gerçek subprocess kullanmak, script path'in proje root'una göre yanlış çözülmesini otomatik yakaladı.

### Sprint 32: Portable Asset Acceptance

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 16:03 +03  
**Amaç:** `accept-asset` komutunu external `rkp.json` projelerinde relative ve absolute screenshot path'leriyle çalışır hale getirmek.

**Yapılanlar:**

- `Tests/test_rkp_project.py` external temp project için iki `accept-asset` testiyle genişletildi:
  - `--screenshot Docs/screenshots/<file>` project root'a göre çözülüyor.
  - Absolute screenshot path project `Docs/screenshots/<asset_id>_accepted.<ext>` altına kopyalanıyor.
- `Tools/accept_asset.py` `ProjectPaths` kullanacak şekilde güncellendi.
- Manifest, USDZ path, asset brief, worklog, screenshot dir ve doctor subprocess path'i config-aware oldu.
- `Tools/pipeline_doctor.py` minimal external project kullanımını destekleyecek şekilde core pipeline path'lerini error, public showcase path'lerini warning olarak ayırdı.
- README, CLI docs, handoff ve skill command reference portability durumunu `accept-asset` dahil olacak şekilde güncelledi.

**Sınır:**

`build-asset`, `usdz_fallback_builder` ve full `release-check` hâlâ sonraki slice'ta `ProjectPaths` üstüne taşınacak.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected; accept_asset.py repo-local manifest read and unknown asset id returned
python3 -m unittest Tests/test_rkp_project.py: ok, 6 tests
python3 -m unittest discover -s Tests: ok, 10 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 10 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Portable acceptance için screenshot path çözümü asset path çözümü kadar kritik. Relative screenshot project root'a göre, absolute screenshot ise kopyalanarak public evidence dizinine göre kaydedilmeli.

### Sprint 33: Portable Asset Build and Fallback Paths

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 16:20 +03  
**Amaç:** `build-asset` ve direct USDZ fallback komutlarını external `rkp.json` projelerinde config manifest/assets/blender path'leriyle çalışır hale getirmek.

**Yapılanlar:**

- `Tests/test_rkp_project.py` external temp project için iki build testiyle genişletildi:
  - `BLENDER=/nonexistent/blender` graceful failure veriyor, traceback üretmiyor ve expected USDZ path'i config `assets_dir` üzerinden raporluyor.
  - `usdz_fallback_builder.py` external manifest'i okuyup `usdzip` yokken 127 ile açık hata veriyor.
- `Tools/build_asset.py` `ProjectPaths` kullanacak şekilde güncellendi.
- Blender script path, output USDZ path, fallback subprocess cwd ve fallback script path'i config-aware oldu.
- Geçersiz `BLENDER` override artık Python traceback yerine açık executable hatası döndürüyor.
- `Tools/usdz_fallback_builder.py` manifest ve output USDZ path için `ProjectPaths` kullanıyor.
- README, CLI docs, handoff ve skill command reference portability durumunu `build-asset` dahil olacak şekilde güncelledi.

**Sınır:**

Full `release-check` hâlâ repo'nun XcodeGen/build layout'una bağlı. Sonraki slice release-check'i portable doctor/test/manifest gates ve optional Xcode build gates olarak ayırmalı.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected; build/fallback scripts repo-local manifest read
python3 -m unittest Tests/test_rkp_project.py: ok, 8 tests
python3 -m unittest discover -s Tests: ok, 12 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors / 1 checkout warning
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 12 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

External process failures must be product behavior, not Python traceback. `BLENDER=/nonexistent` regression test'i build command'in path portability ve failure semantics'ini aynı anda kilitledi.

### Sprint 34: Portable Release Check Gates

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 16:34 +03  
**Amaç:** `release-check` komutunu external `rkp.json` projelerinde repo-local `Tools/rkp.py`, hardcoded manifest path ve zorunlu Xcode layout varsayımlarından çıkarmak.

**Yapılanlar:**

- `Tests/test_rkp_project.py` external temp project için `release-check` testiyle genişletildi.
- `rkp.json` `tests_dir`, `xcode_project`, `xcode_scheme`, `xcode_destination` ve `derived_data_path` alanlarıyla genişletildi.
- `Tools/rkp_project.py` bu alanlar için typed path/property yüzeyleri aldı.
- `Tools/rkp.py release-check` artık:
  - `Doctor(PROJECT).run()` doğrudan çalıştırıyor.
  - `tests_dir` yoksa test gate'ini skip ediyor.
  - Manifest validation'ı config manifest üzerinden yapıyor.
  - `xcode_project` yoksa Xcode gate'ini skip ediyor.
  - `xcode_project` varsa `project.yml` üzerinden generate ve config project/scheme/destination/DerivedData ile build çalıştırıyor.
- README, CLI docs, handoff ve skill command reference release-check portability durumunu güncelledi.

**Sınır:**

Faz 1 config decoupling ana CLI yüzeyi için tamamlandı. Sonraki büyük adım Faz 3'e hazırlık: `Tools/*.py` scriptlerini `src/rkp` paket modüllerine taşımak ve local imports (`from pipeline_doctor import Doctor`, `from prompt_asset import infer_palette`) kırılganlığını kaldırmak.

**Verification:**

```text
python3 -m unittest Tests/test_rkp_project.py: first run failed as expected; release-check external project root under Tools/rkp.py searched
python3 -m unittest Tests/test_rkp_project.py: ok, 9 tests
python3 Tools/rkp.py release-check: ok (doctor 0 errors/1 checkout warning, tests 13 passed, manifest ok, iOS build ok)
```

**Öğrenme notu:**

Portable release gate tek komut kalabilir ama gate'ler optional olmalı. External project minimumunda doctor/test/manifest yeterli; Xcode build ancak `xcode_project` contract'ı verilirse çalışmalı.

### Accepted Asset: enemy_drone

**Durum:** Tamamlandı  
**Tarih:** 2026-05-03 01:22  
**Amaç:** `enemy_drone` asset'ini production pipeline'a screenshot evidence ile kabul etmek.

**Acceptance:**

- USDZ: `Assets/Imported/enemy_drone.usdz`
- Screenshot: `Docs/screenshots/enemy_drone_imported.jpg`
- Manifest status: `imported`

**Verification:**

```text
make doctor: ok
```

**Öğrenme notu:**

Asset kabulü dosyanın oluşmasıyla değil, runtime evidence ve manifest/worklog kaydıyla tamamlanır.

### Sprint 27: Real Asset Build Guardrails

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 03:18 +03
**Amaç:** `/rkp-asset` ve `build-asset` akışının gerçek USDZ üretmesi, yanlış klasörde fake pipeline üretmemesi ve Blender crash durumunu açık raporlaması.

**Yapılanlar:**

- Gerçek repo içinde `enemy_drone` prompt asset'i üretildi; archetype `drone`.
- `Tools/build_asset.py` macOS'ta `/Applications/Blender.app/Contents/MacOS/Blender` yolunu otomatik bulacak şekilde güncellendi.
- Blender build failure mesajı expected USDZ path, Blender executable ve crash log path gösterecek şekilde netleştirildi.
- `Tools/usdz_fallback_builder.py` eklendi; Blender background startup crash yaşarsa `usdzip` ile doğrudan USDZ üretimi deneniyor.
- `Assets/Imported/enemy_drone.usdz` üretildi; manifest acceptance öncesi bilinçli olarak `planned` kaldı.
- `/rkp-asset` command sözleşmesi default build deneyecek ve RKP repo guard'ı uygulayacak şekilde güncellendi.
- Global Claude slash command ve global Codex skill kopyası repo ile senkronlandı.

**Verification:**

```text
python3 -m py_compile Tools/build_asset.py Tools/rkp.py Tools/prompt_asset.py: ok
python3 -m py_compile Tools/blender/create_enemy_drone.py: ok
python3 Tools/rkp.py doctor: ok, 1 known warning
python3 Tools/rkp.py build-asset enemy_drone: ok through direct USDZ fallback after Blender startup crash
usdcat Assets/Imported/enemy_drone.usdz: ok, contains Mesh, primvars:st, UsdUVTexture
xcodegen generate: ok
global slash command diff: ok
global Codex skill diff: ok
```

**Known blocker:**

Blender 5.1.0, 5.1.1 ve 4.5.8 LTS bu makinede background startup sırasında Metal/USD init aşamasında çöküyor. Crash log: `/var/folders/jg/ppc_rfwj63v8qprgfw63k3pr0000gn/T/blender.crash.txt`. Python backtrace boş, yani `create_enemy_drone.py` script'i çalışmadan önce çöküyor.

**Öğrenme notu:**

Prompt-to-asset akışında scaffold, build ve accept farklı kabul edilmeli. Skill başarılı sayılmadan önce gerçek USDZ dosyası oluşmalı; screenshot acceptance olmadan durum `planned` kalmalı.

### Sprint 26: Short `/rkp` Slash Command

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 00:52 +03
**Amaç:** Kullanıcının beklediği `/rkp ...` slash command girişini eklemek.

**Yapılanlar:**

- `.claude/commands/rkp.md` dispatcher komutu eklendi.
- `/rkp status`, `/rkp status json`, `/rkp asset ...`, `/rkp doctor`, `/rkp release` akışları tanımlandı.
- README, CLI docs, slash command docs ve skill command reference `/rkp` kullanımını gösterecek şekilde güncellendi.
- Pipeline doctor `/rkp` komut dosyasını required path olarak kontrol edecek şekilde güncellendi.

**Verification:**

```text
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
global install: ok, copied to /Users/kyylian/.claude/commands/rkp.md
```

**Öğrenme notu:**

Kullanıcı slash command yüzeyinde kısa komutu bekler. `/rkp-asset` doğru ama discoverability için `/rkp` dispatcher gerekir.

### Sprint 25: Slash Command Surface

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 00:46 +03
**Amaç:** Python CLI komutlarını agent CLI içinde `/rkp-asset` ve `/rkp-status` gibi slash command yüzeyine taşımak.

**Yapılanlar:**

- `.claude/commands/rkp-asset.md` eklendi.
- `.claude/commands/rkp-status.md` eklendi.
- `Docs/slash-commands.md` eklendi.
- README, CLI docs ve skill command reference slash command kullanımını gösterecek şekilde güncellendi.
- Pipeline doctor slash command dosyalarını required path olarak kontrol edecek şekilde güncellendi.

**Verification:**

```text
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Slash command sadece kullanıcı yüzeyi olmalı; gerçek implementation `Tools/rkp.py` içinde kalmalı. Böylece `/rkp-asset` agent ergonomisi verir ama pipeline kurallarını bypass etmez.

### Sprint 24: One-Command Asset Loop

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 00:34 +03
**Amaç:** Hiç bilmeyen kullanıcı için prompt-to-asset akışını tek üst komuta bağlamak.

**Yapılanlar:**

- `python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<brief>"` komutu eklendi.
- `make-asset` prompt scaffolding, opsiyonel build, opsiyonel screenshot acceptance ve opsiyonel release-check adımlarını orkestre ediyor.
- `--screenshot` için `--build` zorunlu hale getirildi; acceptance yine built USDZ gerektiriyor.
- `make make-asset id=<id> type=<type> prompt="<brief>"` wrapper'ı eklendi.
- README, CLI docs ve skill command reference tek komut akışına göre güncellendi.

**Verification:**

```text
python3 -m py_compile Tools/rkp.py: ok
python3 Tools/rkp.py make-asset smoke_make --type gameplay_target --prompt "red bullseye drone target" --force: ok, archetype=drone
python3 -m py_compile Tools/blender/create_smoke_make.py: ok
python3 Tools/rkp.py status --json: ok, smoke_make archetype=drone
python3 Tools/rkp.py make-asset smoke_make_accept --type gameplay_target --prompt "red bullseye drone target" --screenshot Docs/screenshots/missing.jpg: blocked as expected because --screenshot requires --build
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Tek komut rahatlık sağlamalı ama pipeline sınırlarını gizlememeli. Bu yüzden build, screenshot acceptance ve release-check bayraklarla açıkça istenir.

### Sprint 23: Prompt Archetype Status Surface

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 00:12 +03
**Amaç:** Prompt archetype bilgisini machine-readable pipeline state'e taşımak ve README'de prompt-to-asset akışını görünür yapmak.

**Yapılanlar:**

- `prompt-asset` artık manifest entry içine `prompt` ve `archetype` metadata'sı yazıyor.
- `python3 Tools/rkp.py status --json` çıktısına `archetype` alanı eklendi.
- `python3 Tools/rkp.py status` text tablosu archetype sütunu gösterecek şekilde güncellendi.
- Generated Blender script'te archetype bulunmadığında `ARCHETYPE = null` yerine Python uyumlu `ARCHETYPE = None` üretilecek şekilde düzeltildi.
- README'ye `Prompt To Asset` bölümü eklendi.
- CLI docs ve skill command reference `status --json` archetype davranışını anlatacak şekilde güncellendi.

**Verification:**

```text
python3 -m py_compile Tools/prompt_asset.py Tools/rkp.py: ok
python3 Tools/rkp.py prompt-asset test_status_drone --type gameplay_target --prompt "red bullseye drone target" --force: ok, archetype=drone
python3 Tools/rkp.py status --json: ok, includes archetype=drone for prompt-backed asset
python3 -m py_compile Tools/blender/create_test_status_drone.py: ok
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Prompt pipeline agent'lar için ancak state yüzeyinde okunabiliyorsa işe yarar. `archetype` alanı Blender script içinde kalmamalı; CLI status üzerinden planlanabilir olmalı.

### Sprint 22: Prompt Archetype Geometry

**Durum:** Tamamlandı
**Tarih:** 2026-05-03 00:05 +03
**Amaç:** `prompt-asset` komutuna archetype inference ekleyerek type-based primitive'den gerçek geometry dispatch sistemine geçmek.

**Yapılanlar:**

- `infer_archetype(prompt)` eklendi. Keyword tabanlı, öncelik sırası: `drone > tower > crate > projectile > target > None (type fallback)`.
- 5 archetype her biri için ayrı Blender geometry builder: `make_drone_parts`, `make_tower_parts`, `make_crate_parts`, sphere (projectile), quad (target).
- Multi-part meshler `join_and_uv()` ile birleştiriliyor: `bpy.ops.object.join` + Smart UV Project + UV layer "st" rename.
- Texture de archetype-aware: drone → radial sektör, tower → horizontal band, crate → panel seam, target → bullseye rings, projectile → solid.
- USD export bug düzeltildi: `export_textures=True` → `export_textures_mode="NEW"`.
- Asset brief'e archetype annotation eklendi (`Inferred archetype: drone`).

**Verification:**

```text
python3 -m py_compile Tools/prompt_asset.py: ok
python3 Tools/rkp.py prompt-asset test_drone --type gameplay_target --prompt "red bullseye drone target" --force: ok (archetype: drone)
python3 -m py_compile Tools/blender/create_test_drone.py: ok
python3 Tools/rkp.py doctor: ok (1 known warning)
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Archetype inference öncelik sırası kritik. "red bullseye drone target" gibi multi-keyword promptlarda `drone > target` olmazsa yanlış dispatch olur. Keyword eşleşmesi `lower in prompt` ile yapılıyor; LLM semantiği yok, bu bilinçli sınır.

### Sprint 21: Prompt-Backed Asset Command

**Durum:** Tamamlandı
**Tarih:** 2026-05-02 23:50 +03
**Amaç:** Kullanıcının tek komutla prompt girip asset contract + Blender generator + opsiyonel USDZ build başlatabilmesini sağlamak.

**Yapılanlar:**

- `Tools/prompt_asset.py` eklendi.
- `python3 Tools/rkp.py prompt-asset <id> --type <type> --prompt "<brief>"` komutu eklendi.
- `--build` opsiyonu eklendi; Blender varsa generator sonrası USDZ build tetiklenebiliyor.
- Prompt asset brief içine `Prompt Source` olarak kaydediliyor.
- Generated Blender script prompt'a göre basit procedural texture ve mesh draft oluşturuyor.
- `make prompt-asset id=<id> type=<type> prompt="<brief>"` wrapper'ı eklendi.
- README, CLI docs ve skill command reference güncellendi.

**Verification:**

```text
python3 -m py_compile Tools/prompt_asset.py Tools/rkp.py Tools/new_asset.py: ok
python3 Tools/rkp.py prompt-asset test_prompt_target --type gameplay_target --prompt "blue bullseye target" --force: ok
python3 -m py_compile Tools/blender/create_test_prompt_target.py: ok
python3 Tools/rkp.py build-asset test_prompt_target: blocked as expected because Blender is not on PATH
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Prompt komutu production acceptance'ın yerine geçmemeli. Prompt hızlı draft başlatır; oyuna girme sınırı hala USDZ build + simulator screenshot + `accept-asset`.

### Sprint 20: README Tool Positioning

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 23:34 +03  
**Amaç:** README'nin ilk ekranında repo kimliğini netleştirmek: pipeline tool ana ürün, mini oyun canlı örnek.

**Yapılanlar:**

- README başlığı `RealityKit Pipeline Guide` olarak güncellendi.
- İlk paragraf command-first pipeline tool konumlandırmasına çevrildi.
- `What This Is` bölümü eklendi: CLI, live app, docs/skill katmanları ayrıldı.
- `Showcase` bölümü `Live Example App` olarak yeniden adlandırıldı.
- `First Asset Loop` manuel manifest/export anlatımından CLI akışına çevrildi.
- GitHub description önerisi pipeline tool kimliğine göre güncellendi.

**Verification:**

```text
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Tool + demo ikiliği sorun değil; sorun bu hiyerarşinin ilk ekranda belirsiz kalması. README'nin ilk işi repo'nun "araç, oyun bunun kanıtı" mesajını vermek.

### Sprint 19: Machine-Readable CLI Output

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 23:24 +03  
**Amaç:** CLI'ı gelecekte CI, agent ve MCP-style wrapper'ların okuyabileceği structured output yüzeyiyle güçlendirmek.

**Yapılanlar:**

- `python3 Tools/rkp.py status --json` eklendi.
- `python3 Tools/rkp.py doctor --json` eklendi.
- `Tools/pipeline_doctor.py` text output'u bozmadan import edilebilir `collect()` / `summary()` yapısına ayrıldı.
- README, `Docs/cli-tool.md` ve skill command reference JSON kullanımını gösterecek şekilde güncellendi.
- JSON kapsamı bilinçli olarak `status` ve `doctor` ile sınırlı tutuldu; side-effect komutlar text-first kaldı.

**Verification:**

```text
python3 -m py_compile Tools/rkp.py Tools/pipeline_doctor.py: ok
python3 Tools/rkp.py status --json: ok
python3 Tools/rkp.py doctor --json: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Agent/MCP entegrasyonunda ilk ihtiyaç yan etkili komutlardan önce structured project state'tir. `status --json` ve `doctor --json` bu yüzden en iyi ilk JSON yüzeyi.

### Sprint 18: Command-First Pipeline Tool

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 23:12 +03  
**Amaç:** Repo'yu sadece rehber değil, geliştiricinin günlük kullanacağı CLI pipeline tool haline getirmek.

**Yapılanlar:**

- `Tools/rkp.py` eklendi.
- `status`, `doctor`, `new-asset`, `build-asset`, `accept-asset`, `release-check` subcommand'leri eklendi.
- `Makefile` geriye uyumlu wrapper olacak şekilde CLI'a bağlandı.
- `Docs/cli-tool.md` eklendi; guide artık destek materyali, CLI primary interface olarak konumlandı.
- README, production playbook, skill references ve AI handoff command-first akışa güncellendi.
- Pipeline doctor artık CLI ve CLI dokümanını required path olarak kontrol ediyor.

**Verification:**

```text
python3 -m py_compile Tools/rkp.py Tools/pipeline_doctor.py Tools/accept_asset.py Tools/build_asset.py Tools/new_asset.py: ok
python3 Tools/rkp.py status: ok
python3 Tools/rkp.py doctor: ok
python3 Tools/rkp.py release-check: ok
```

**Öğrenme notu:**

Bir repo "guide" olarak faydalı olabilir, ama tekrar tekrar kullanılacak developer value CLI kontratından gelir. Guide açıklamalı katman, CLI ise günlük operasyon yüzeyi olmalı.

### Sprint 17: Asset Acceptance Gate

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:50 +03  
**Amaç:** USDZ üretilmiş asset'i production pipeline'a alırken screenshot evidence zorunlu olsun; manifest, brief ve worklog kaydı otomatik oluşsun.

**Yapılanlar:**

- `Tools/accept_asset.py` eklendi.
- `make accept-asset id=<asset_id> screenshot=<path>` hedefi eklendi.
- Screenshot parametresi zorunlu; screenshot yoksa komut çalışmıyor.
- Komut USDZ var/boş değil kontrolü yapıyor.
- Manifest status `imported` yapılıyor ve notes içine screenshot evidence ekleniyor.
- `Docs/assets/<id>.md` varsa acceptance checklist ve evidence bölümü güncelleniyor.
- `Docs/WORKLOG.md` başına accepted asset kaydı ekleniyor.
- Acceptance sonrası `Tools/pipeline_doctor.py` çalışıyor.

**Verification:**

```text
make accept-asset id=arena_floor: blocked as expected without screenshot
python3 Tools/accept_asset.py --id nope --screenshot Docs/screenshots/arena_floor_imported.jpg: ok, unknown asset id rejected
make accept-asset id=arena_floor screenshot=Docs/screenshots/arena_floor_imported.jpg: ok
make release-check: ok
```

**Öğrenme notu:**

Screenshot evidence accept gate'in parçası olmalı. Aksi halde manifest `imported` dese bile runtime scale/origin/material davranışı geriye dönük kanıtlanamaz.

### Accepted Asset: arena_floor

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:42  
**Amaç:** `arena_floor` asset'ini production pipeline'a screenshot evidence ile kabul etmek.

**Acceptance:**

- USDZ: `Assets/Imported/arena_floor.usdz`
- Screenshot: `Docs/screenshots/arena_floor_imported.jpg`
- Manifest status: `imported`

**Verification:**

```text
make doctor: ok
```

**Öğrenme notu:**

Asset kabulü dosyanın oluşmasıyla değil, runtime evidence ve manifest/worklog kaydıyla tamamlanır.

### Sprint 16: Asset Build Command

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:45 +03  
**Amaç:** `new-asset` ile açılan contract'tan sonra Blender script'ini çalıştırıp USDZ çıktısını doğrulayan ikinci pipeline adımını eklemek.

**Yapılanlar:**

- `Tools/build_asset.py` eklendi.
- `make build-asset id=<asset_id>` hedefi eklendi.
- Komut `Tools/blender/create_<id>.py` dosyasını Blender background mode ile çalıştırıyor.
- `BLENDER=/path/to/blender` override destekleniyor.
- Komut beklenen `Assets/Imported/<id>.usdz` dosyasının oluştuğunu ve boş olmadığını doğruluyor.
- Manifest status bilinçli olarak değiştirilmedi; `imported` kabulü ayrı `accept-asset` gate'i olarak kalacak.

**Verification:**

```text
make build-asset id=arena_floor: blocked as expected, Blender executable not found in this environment
python3 Tools/build_asset.py --id nope: ok, unknown asset id rejected
make release-check: ok
```

**Öğrenme notu:**

Build ve accept farklı kapılar olmalı. USDZ dosyasının üretilmesi teknik çıktıdır; RealityKit içinde scale/origin/material/screenshot doğrulanmadan asset imported sayılmamalı.

### Sprint 15: New Asset Scaffolder

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:35 +03  
**Amaç:** Yeni asset'e başlama adımını standartlaştırmak: manifest entry, asset brief ve Blender starter script tek komutla oluşsun.

**Yapılanlar:**

- `Tools/new_asset.py` eklendi.
- `make new-asset id=<asset_id> type=<asset_type>` hedefi eklendi.
- Desteklenen tipler: `gameplay_target`, `environment`, `prop`, `projectile`.
- Scaffolder `status: planned` manifest kaydı, `Docs/assets/<id>.md` brief'i ve `Tools/blender/create_<id>.py` placeholder export script'i oluşturuyor.
- README, production playbook ve skill command/workflow reference güncellendi.

**Verification:**

```text
make new-asset id=test_dummy type=prop: ok
generated manifest entry, Docs/assets/test_dummy.md, Tools/blender/create_test_dummy.py: ok
cleanup of test_dummy scaffold: ok
make doctor: ok, 1 known warning for actions/checkout@v4 Node 20 deprecation
make release-check: ok
```

**Öğrenme notu:**

Scaffolder asset üretmemeli; asset işinin başlangıç contract'ını üretmeli. Final USDZ, screenshot ve imported status hâlâ bilinçli production adımları olarak kalmalı.

### Sprint 14: Reproducible Demo GIF

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:25 +03  
**Amaç:** Public README için manuel tıklamaya bağlı olmayan, tekrar üretilebilir kısa gameplay GIF'i üretmek.

**Yapılanlar:**

- `--demo-mode` launch argument eklendi.
- Demo mode normal app davranışını değiştirmiyor; sadece launch arg varsa deterministic hedeflere otomatik projectile atıyor.
- `Docs/screenshots/demo.gif` eklendi ve README hero görseli olarak bağlandı.

**Verification:**

```text
make release-check: ok
simulator demo frames: ok
README GIF: ok
```

**Öğrenme notu:**

README GIF'i tek seferlik manuel kayıt olmamalı. İyi public repo'da demo medyası da tekrar üretilebilir olmalı; böylece gameplay değiştikçe aynı akış yeniden kaydedilebilir.

### Sprint 13: Pipeline Doctor

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:10 +03  
**Amaç:** Repo'yu geliştiriciler için günlük kullanılabilir tool haline getirmek: asset manifest, imported USDZ, docs evidence, XcodeGen path, CI ve skill packaging sorunlarını tek komutla yakalamak.

**Yapılanlar:**

- `Tools/pipeline_doctor.py` eklendi.
- `make doctor` hedefi eklendi.
- `make release-check` artık doctor -> generate -> validate -> build sırasını kullanıyor.
- README, production playbook ve skill command reference `make doctor` kullanımını anlatıyor.

**Verification:**

```text
make doctor: ok, 1 known warning for actions/checkout@v4 Node 20 deprecation
make release-check: ok
```

**Öğrenme notu:**

Guide'ın vazgeçilmez tool'a dönüşmesi için sadece anlatması yetmez; pipeline kırıldığında hızlı ve deterministik şekilde söylemesi gerekir. Doctor build'in yerini tutmaz, ama CI'a gitmeden önce en sık public repo/pipeline hatalarını yakalar.

### Sprint 12: Installable Skill Pack

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 22:00 +03  
**Amaç:** Repo'yu sadece okunacak guide olmaktan çıkarıp, clone eden kişinin Codex içinde tekrar kullanabileceği skill/pipeline kit haline getirmek.

**Yapılanlar:**

- `Skills/realitykit-pipeline-guide` altında installable Codex skill paketi eklendi.
- Skill referansları eklendi: workflow routing, contracts/gates, commands.
- `check_repo.py` hızlı yapı/manifest kontrol script'i eklendi.
- `make install-skill` hedefi eklendi; skill `${CODEX_HOME:-$HOME/.codex}/skills` altına kopyalanabiliyor.
- README, guide ve production playbook skill kullanımını anlatacak şekilde güncellendi.

**Verification:**

```text
official skill validator: blocked locally, quick_validate.py requires missing PyYAML module
Ruby YAML frontmatter check: ok
manual TODO check: ok
skill repo check: ok
temporary install test: ok with CODEX_HOME=/private/tmp/realitykitpipelineguide-skill-test
local Codex install: ok at ~/.codex/skills/realitykit-pipeline-guide
make release-check: ok
```

**Öğrenme notu:**

Guide tek başına insan için iyi, ama ekip/AI workflow'u için aynı standartların yüklenebilir bir skill haline gelmesi gerekiyor. Skill kısa kalmalı; detaylar progressive disclosure ile references dosyalarına ayrılmalı.

### Sprint 11: Wave Game Loop

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 21:45 +03  
**Amaç:** Prototype'ı sonsuz target sandbox hissinden çıkarıp, açık wave/progress bilgisi olan mini oyun loop'una yaklaştırmak.

**Yapılanlar:**

- `GameSession` içine `wave`, `targetsThisWave`, `clearedTargets` ve `waveProgressText` eklendi.
- Wave 1 artık 2 hedefle başlıyor; wave temizlenince hedef sayısı deterministic spawn slot limiti içinde artıyor.
- HUD'da `Targets` metriği yerine `Wave` ve `Cleared` metriği gösteriliyor.
- Manual `Spawn` butonu practice/debug hedefi olarak mevcut wave'in hedef sayısını artırıyor.
- Feature brief kaydı: `Docs/features/wave-game-loop.md`.

**Verification:**

```text
make release-check: ok
simulator interaction: ok, HUD shows Wave and Cleared progress
```

**Öğrenme notu:**

Oyun loop'u sadece "hedef bitince yenisini spawn et" değildir. Session state, HUD dili, reset davranışı ve edge case'ler aynı contract içinde tanımlanmadığında oyuncu ilerlemeyi anlayamaz.

### Sprint 10: Production Guide System

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 21:30 +03  
**Amaç:** Repo'yu sadece demo/öğrenme dokümanı olmaktan çıkarıp, ileride yeni RealityKit oyunları başlatırken tekrar kullanılacak production guide sistemine çevirmek.

**Yapılanlar:**

- `Docs/production-playbook.md` eklendi: feature brief, gameplay contract, asset contract, verification, worklog, quality gates ve definition of done.
- `Docs/new-game-startup.md` eklendi: yeni RealityKit oyunu başlatma fazları, ilk hafta planı, asset class tablosu ve stop conditions.
- `Prompts/game-feature-brief.md` eklendi: gameplay/UI/VFX/pipeline işleri için AI veya ekip arkadaşına verilecek kapsamlı brief şablonu.
- `README.md`, `Docs/guide.md` ve `Docs/ai-handoff.md` yeni rehber sistemini gösterecek şekilde güncellendi.

**Verification:**

```text
make release-check: ok
```

**Öğrenme notu:**

Guide ile playbook ayrı tutulmalı. `Docs/guide.md` öğrenme anlatısıdır; `Docs/production-playbook.md` gerçek iş yaparken kapı/gate sistemidir; `Docs/new-game-startup.md` aynı disiplini gelecekteki oyunlara taşır.

### Teaching Goal: Asset + Texture Pipeline

**Durum:** Tamamlandı  
**Amaç:** Bu proje sadece oynanabilir demo üretmek için değil; Blender -> USDZ -> RealityKit asset ve texture sistemini Kyylian ve Mehmet'e adım adım öğretmek için de kullanılacak.

**Not alma kuralı:**

- Her asset/texture kararını `Decision Log` içine yaz.
- Her yeni asset denemesini `Verification Log` içinde build/görsel doğrulama sonucu ile kapat.
- Blender tarafında öğrenilen export/origin/scale/material derslerini `Docs/blender-usdz-checklist.md` dosyasına ekle.
- RealityKit tarafında öğrenilen loader, scale, orientation ve material davranışlarını bu worklog'a kısa not olarak geçir.
- Kyylian ve Mehmet aynı pipeline bilgisini öğrenecek; iş bölümü aracı sahiplenmek için değil, pratik ilerlemek için yapılacak.

### Sprint 5: Arena Floor Environment Asset

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 19:30 +03  
**Amaç:** Procedural floor yerine `arena_floor.usdz` environment asset pipeline'ını öğretmek.

**Codex hazırlığı:**

- `GameARView.addArena()` artık önce `arena_floor.usdz` yüklemeyi dener.
- `arena_floor.usdz` yoksa mevcut procedural floor + lane fallback korunur.
- `Tools/asset_manifest.json` içindeki `arena_floor` kaydı environment/texture öğretim notlarıyla genişletildi.
- Fallback görsel doğrulama çıktısı: `Docs/screenshots/arena_floor_fallback_ready.jpg`.
- Imported arena görsel doğrulama çıktısı: `Docs/screenshots/arena_floor_imported.jpg`.

**Sonuç:**

- `Assets/Imported/arena_floor.usdz` eklendi.
- Asset bilgisi: 3.2m x 3.2m flat plane, origin center, 128 triangle, `st` UV primvar, 512x512 embedded base color texture.
- Manifest status `imported` yapıldı.
- Simulator'da imported floor grid/texture göründü ve target readability bozulmadı.

**Asset handoff beklentisi:**

- Dosya: `Assets/Imported/arena_floor.usdz`
- Ölçü: mevcut procedural floor ile uyumlu, yaklaşık 3.2m x 3.2m gameplay alanı.
- Origin: floor merkezinde; gameplay placement için uygun.
- Doku: tek base color texture ile başlanmalı; 512px tercih, 1024px üst limit.
- Görsel hedef: target readability'yi bozmayan düşük kontrastlı floor.

**Öğrenme hedefi:**

- Environment asset scale/origin davranışı target asset'ten nasıl farklı?
- Floor texture tiling veya atlas target readability'yi nasıl etkiler?
- Procedural fallback environment pipeline'da nasıl korunur?

### Sprint 6: Public Onboarding Polish

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02  
**Amaç:** Repo'yu public clone eden birinin `rtk` veya önceki internal akışlara takılmadan projeyi üretebilmesi, build edebilmesi ve Blender asset loop'una başlayabilmesi.

**Yapılanlar:**

- README public quick start olarak yeniden düzenlendi.
- `rtk` public dependency değil, local agent wrapper olarak açıklandı.
- `LICENSE`, `CONTRIBUTING.md`, `Makefile`, GitHub Actions CI, PR template ve issue template'leri eklendi.
- `Tools/blender/create_arena_floor.py` ve `Tools/blender/README.md` eklendi.
- `Assets/Source/README.md` ile source-art handoff alanı belirlendi.
- `Docs/blender-usdz-checklist.md` içindeki Sprint 3'e özel stale handoff satırı genel asset id kontratına çevrildi.

**Öğrenme notu:**

Public repo onboarding'i local agent workflow'dan ayrılmalı. `rtk` gibi ekip içi wrapper'lar AGENTS/worklog içinde kalabilir, ama README normal kullanıcının çalıştıracağı çıplak komutları göstermeli.

### Sprint 7: GitHub Showcase Prep

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02  
**Amaç:** Repo'nun ilk 10 saniye izlenimini güçlendirmek ve weekly/trending/curated listelere gönderim için gerekli metinleri hazırlamak.

**Yapılanlar:**

- README en üstüne "neden farklı?" anlatısı eklendi.
- README'e `What You Learn` ve iki görselli showcase bölümü eklendi.
- GitHub description ve topics önerileri README'e işlendi.
- `CHANGELOG.md` ile `v0.1.0` release içeriği hazırlandı.
- `Docs/github-showcase.md` ile release, topics ve outreach metni tek yerde toplandı.

**Öğrenme notu:**

İyi teknik repo ile paylaşılabilir repo aynı şey değil. Public listeler için ilk ekranın 10 saniyede "ne öğretiyor, ne çalışıyor, neden farklı" sorularını cevaplaması gerekiyor.

### Sprint 8: Showcase Vertical Slice

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02  
**Amaç:** Demo GIF almadan önce mevcut sahneyi daha okunabilir ve daha az amatör gösterecek küçük bir gameplay/showcase polish katmanı eklemek.

**Yapılanlar:**

- RealityKit sahnesine koyu showcase backdrop eklendi.
- Directional light intensity artırıldı.
- Hit anında target pozisyonunda kısa ömürlü renkli spark/flash VFX eklendi.
- HUD yeniden düzenlendi: başlık, büyük skor, status renkleri, targets metriği.
- Ortaya non-interactive reticle overlay eklendi.
- İlk showcase pass'teki "target'a tıkla ve anında patlat" davranışı kaldırıldı.
- Tap artık projectile yönünü belirliyor; target removal, skor ve VFX projectile temasında çalışıyor.
- Hit VFX tek büyüyen flash yerine dışarı dağılan spark parçacıklarına çevrildi.

**Verification:**

```text
make build: ok
make release-check: ok
specific iPhone 17 simulator build/screenshot: sandbox CoreSimulator destination discovery nedeniyle alınamadı
```

**Öğrenme notu:**

Showcase GIF için önce "çalışıyor" kanıtı değil, ilk ekranda anlaşılır bir görsel hiyerarşi gerekiyor. Küçük HUD/framing/VFX işleri repo'nun öğretici değerini bozmadan ilk izlenimi yükseltir. Ancak showcase polish gameplay sözleşmesini bozmamalı: hedefler tıklanınca değil, projectile gerçekten temas edince düşmeli.

### Sprint 9: Modern RealityKit Feel

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02  
**Amaç:** Apple'ın güncel RealityKit yönüyle projeyi karşılaştırıp oyunun basit görünmesine sebep olan eksikleri azaltmak: physics, collision events, PBR material ve availability-gated entity animation.

**Yapılanlar:**

- Target entity'lerine `PhysicsBodyComponent(mode: .static)` eklendi.
- Projectile entity'lerine `PhysicsBodyComponent(mode: .dynamic)` ve `PhysicsMotionComponent` eklendi.
- `CollisionEvents.Began` subscription eklendi; projectile-target teması event üzerinden resolve ediliyor.
- Manual distance check fallback olarak kaldı; ana davranış artık RealityKit collision event'i ile uyumlu.
- Procedural target/fallback floor/showcase backdrop materyalleri `PhysicallyBasedMaterial` helper'ına taşındı.
- Target spawn animasyonu SDK-stable `move(to:relativeTo:duration:)` ile eklendi; public CI'nin Xcode 16/iOS 18 baseline'ında derlenebilir kaldı.
- Projectile body mode `.dynamic` yerine `.kinematic` yapıldı; böylece projectile gravity ile düşmeden düz aim çizgisini koruyor.
- `resolveHit` içine projectile/target hâlâ aktif mi guard'ı eklendi; aynı collision için duplicate event gelirse double-score engelleniyor.
- Simulator run sırasında alt controls alanının da ARView tap gesture tarafından projectile ateşleyebildiği görüldü; HUD/controls dışındaki gameplay alanı için tap guard eklendi.
- Target'a dokununca anında patlatmayan delayed aim assist geri eklendi: tap projectile yönünü hedefe çevirir, skor/target removal yine collision event sonrası çalışır.
- Showcase framing için imported target scale `0.90` yapıldı; ilk iki spawn slotu daha yakın, simetrik ve reticle çevresine alındı.
- Collision radius `0.32`, bullseye/inner scoring eşikleri `0.104/0.215` olarak scale ile uyumlu güncellendi.
- Kinematic projectile hareketi frame başına manuel pozisyon update'ine taşındı; böylece gravity kapalı kalırken mermi havada donmuyor.
- Hit VFX update'i aktif projectile sayısından bağımsız hale getirildi; patlama efektleri mermi listesi boşken de tamamlanıyor.

**Verification:**

```text
make build: ok
make release-check: ok
build_run_sim: ok, iPhone 17 Pro Max simulator
screenshot check: opening targets are larger, symmetric, and readable enough for first GIF test
```

**Öğrenme notu:**

RealityKit'in güncel API'leri her zaman deployment target ile uyumlu değil. `Entity.animate` Apple docs'ta modern öneri olarak var ama iOS 26+ gerektiriyor ve eski SDK'da symbol hiç bulunmadığı için sadece availability guard yeterli değil. iOS 18 hedefleyen public repo'da SDK-stable API kullanmak daha doğru. Projectile gibi oyuncu aim çizgisini koruması gereken body'lerde `.dynamic` gravity hissi bozabilir; `.kinematic` daha doğru. Bu projede kinematic projectile'ın hareketi bilinçli olarak game loop içinde manuel sürülüyor; collision event modern RealityKit tarafını, distance fallback ise öğretici ve stabil gameplay tarafını koruyor.

### Sprint 4: Ring Bazlı Skor ve Texture-Gameplay Bağlantısı

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 19:20 +03  
**Amaç:** Target üzerindeki bullseye/ring texture'ını sadece görsel olmaktan çıkarıp gameplay skoruna bağlamak.

**Yapılanlar:**

- Hit scoring artık tek sabit `+10` değil.
- Projectile impact anında target merkezine göre mesafe ölçülüyor.
- Impact bölgesi hedef yüzeyindeki halka merkezine göre hesaplanıyor.
- Bullseye: `+5`, inner ring: `+3`, outer ring: `+1`.
- HUD status hit bölgesini gösteriyor: `Bullseye +5`, `Inner ring +3`, `Outer ring +1`.
- Görsel doğrulama çıktısı: `Docs/screenshots/ring_scoring_inner_hit.jpg`.

**Öğrenme notu:**

- Texture sadece görsel kalite için değil, gameplay bilgisini oyuncuya anlatmak için de kullanılabilir.
- Görsel mesh ve collision hâlâ ayrı: collision basit sphere kalıyor, skor ise bu non-AR prototype'ta target'ın ekrandaki halka merkezinden hesaplanıyor.
- Screen-space hit çözümü, discrete projectile step veya non-AR RealityKit hit-test belirsizliği yüzünden görsel olarak doğru tıklanan hedefin kaçırılmasını engeller.

### Sprint 3: İlk Texture'lı Target Asset

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 18:15 +03  
**Amaç:** `target_basic_textured.usdz` ile ilk base color texture import akışını öğretmek ve doğrulamak.

**Yapılanlar:**

- `target_basic.usdz` Blender Python ile import edildi; Cylinder mesh (229 verts, 284 poly) korundu.
- `'st'` UV primvar yerinde override edildi: Z ekseninden planar projeksiyon (u=x/0.65+0.5, v=y/0.65+0.5).
- 512×512 PNG base color texture Blender Python ile üretildi: kırmızı merkez, beyaz/kırmızı halkalar, koyu dış.
- Tek `mat_textured` materyali: PrincipledBSDF + ImageTexture → Base Color, roughness=0.65, metallic=0.
- USDZ export (Blender `wm.usd_export`, `export_textures_mode='NEW'`): texture ~11 KB PNG olarak embed edildi.
- `rtk xcodegen generate` → build → simulator: `target_basic_textured ready` HUD'da görüldü.
- Screenshot: `Build/target_textured_sprint3_fresh.png`.

**Öğrenme notları:**

- Blender USD export, shader'daki UV Map node'unun `uv_map` alanına göre primvar seçer — hangi layer'ı aktif yaptığın değil, node'un referans ettiği isim önemli.
- Orijinal asset `'st'` primvar kullandığı için yeni UV'yi `'st'` layer'ına yazmak gerekti; yoksa UVMap layer aktif olsa bile texture yanlış primvar'a bind edilirdi.
- `export_textures_mode='NEW'` `/tmp` path'inden kopyalama uyarısı veriyor ama PNG yine de USDZ içine embed oluyor — RealityKit tarafında sorunsuz yükleniyor.
- Texture boyutu 512×512 simulator'da yeterli çözünürlük veriyor; 1024 şimdilik gerekmiyor.

### Sprint 2: Imported Target Scale ve Spawn Tuning

**Durum:** Tamamlandı  
**Tarih:** 2026-05-02 14:36 +03  
**Amaç:** `target_basic.usdz` assetinin ekranda çok büyük veya kadraj dışı görünmesini düzeltmek.

**Sonuç:**

- Imported target için RealityKit tarafında `0.48` uniform scale uygulandı.
- Rastgele spawn yerine sabit, kadraj içi spawn slotları eklendi.
- Reset sonrası slot sırası başa alınıyor; bu eğitim/debug sırasında aynı sahneyi tekrar üretilebilir yapıyor.
- Görsel doğrulama çıktısı: `Build/target_basic_scale_slots.jpg`.

### Sprint 1: İlk Gerçek Target Asset Import

**Durum:** Tamamlandı  
**Tarih:** 2026-04-30 16:47 +03  
**Amaç:** Claude/Blender tarafından üretilen `target_basic.usdz` assetini app resource pipeline'a almak ve build içinde doğrulamak.

**Sonuç:**

- `Assets/Imported/target_basic.usdz` eklendi.
- Asset bilgisi: 284 triangle, 3 materyal, merkez origin, yaklaşık 19KB USDZ.
- `Tools/asset_manifest.json` içinde `target_basic` durumu `imported` olarak güncellendi.
- XcodeGen sonrası asset `.app/Imported/target_basic.usdz` altında bundle'a kopyalandı.
- Generic iOS Simulator build başarılı.

### Sprint 0: Demo Pipeline Hazırlığı

**Durum:** Tamamlandı  
**Tarih:** 2026-04-29 16:53 +03  
**Amaç:** RealityKit öğrenmek için küçük ama gerçek pipeline taşıyan demo proje kurmak.

**Kapsam:**

- iOS RealityKit sandbox app.
- Procedural hedef vurma döngüsü.
- Blender/Claude asset export sözleşmesi.
- XcodeGen tabanlı resource pipeline.
- Öğrenme ve QA dokümanları.

**Kapsam dışı:**

- Final art.
- Substance pipeline.
- visionOS target.
- Reality Composer Pro package.
- Gerçek cihaz profiling.

## Role Split

### Kyylian + Mehmet

- Asset ve texture pipeline'ını uçtan uca birlikte öğrenir.
- İş bölümünü kendi aralarında yapar; amaç bir kişinin sadece Blender, diğerinin sadece kod bilmesi değildir.
- Oyun hissi, tema, art direction ve kalite beklentilerini birlikte netleştirir.
- Asset export sonrası simulator screenshot'ını birlikte yorumlar: scale, origin, orientation, material, texture, collision.
- Öğrenilen dersleri checklist ve worklog'a yazdırır.

### Asset Üretim İstasyonu

- Blender, Blender MCP veya Claude otomasyonu kullanılabilir.
- Çıktı `.usdz` olarak `Assets/Imported` altına konur.
- Asset scale, origin, naming, UV ve texture sözleşmesine uyar.
- Üretim aracı değişebilir; öğrenilecek konu pipeline davranışıdır.

### Codex İstasyonu

- RealityKit/Swift/Xcode tarafını kurar.
- Gameplay sistemlerini yazar.
- Asset import, bundle, loader, scale/orientation/material davranışı ve build pipeline sorunlarını çözer.
- Build/test/verification sonuçlarını kaydeder.
- Gerektiğinde eğitim notlarını, checklistleri ve handoff sözleşmelerini günceller.

## Contracts

### Asset Contract

İlk hedef asset:

```text
Path: /Users/kyylian/Developer/RealityKitPipelineDemo/Assets/Imported/target_basic.usdz
Format: USDZ
Scale: 1 Blender unit = 1 meter
Origin: gameplay pivot
Naming: snake_case
First asset id: target_basic
```

Yeni `.usdz` dosyası eklendikten sonra:

```bash
rtk xcodegen generate
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator build
```

### Loader Contract

`ImportedAssetLoader` tek asset adı için bundle içinde şu sırayla dosya arar:

1. Bundle root: `<asset_id>.usdz`
2. Bundle subdirectory: `Imported/<asset_id>.usdz`
3. Bundle subdirectory: `Assets/Imported/<asset_id>.usdz`

`GameARView` target spawn ederken asset id sırası olarak önce `target_basic_textured`, sonra `target_basic` dener. İkisi de yoksa procedural sphere fallback kullanır. Bu sayede texture asset veya base asset yokken de app çalışır.

## Project Map

| Path | Amaç |
| --- | --- |
| `Sources/RealityKitPipelineDemo` | SwiftUI + RealityKit app kodu |
| `Assets/Imported` | Blender/Claude `.usdz` çıktıları |
| `Assets/Textures` | Texture kaynakları veya exportları |
| `Tools/asset_manifest.json` | Asset listesi, bütçe ve durum |
| `Docs/pipeline.md` | Genel üretim pipeline |
| `Docs/blender-usdz-checklist.md` | Blender export kontrol listesi |
| `Docs/asset-budget.md` | Mobil performans bütçesi |
| `Prompts` | Claude/Codex tekrar kullanılabilir promptları |

## Change Log

### 2026-04-30

- Claude/Blender çıktısı `Assets/Imported/target_basic.usdz` projeye eklendi.
- `target_basic` manifest kaydı `imported` durumuna alındı.
- XcodeGen proje dosyası asset resource klasörüyle yeniden üretildi.
- Build çıktısında `target_basic.usdz` dosyasının `Imported/` altında bundle'a girdiği doğrulandı.
- Simulator üzerinde app launch edildi ve imported target görsel olarak doğrulandı.
- USDZ içindeki nested mesh için child-level orientation düzeltmesi eklendi; ring materyalleri görünür hale geldi.
- Imported target spawn sırasında kameraya baktırıldı ve 180 derece front-face düzeltmesi yapıldı; hedef tahtası artık kırmızı/beyaz ön yüzüyle oyuncuya bakıyor.

### 2026-05-02

- Repo açmadan önce öğretici paket için `Docs/guide.md` eklendi; asset'in gameplay ihtiyacından simulator screenshot'ına kadar yolculuğu rehber formatında anlatıldı.
- `Docs/guide.md` profesyonel eğitim yapısına refactor edildi: öğrenme hedefleri, mental model, core concepts, sprint walkthrough, debugging playbook, yeni asset checklist'i ve repo release checklist eklendi.
- Pipeline şeması kaynak Mermaid (`Docs/diagrams/pipeline.mmd`) ve görüntülenebilir SVG (`Docs/diagrams/pipeline.svg`) olarak eklendi.
- Rehberden `Build/realitykit-pipeline-guide.html` ve `Build/realitykit-pipeline-guide.pdf` üretildi.
- Public repo hazırlığı için seçilmiş görsel kanıtlar `Docs/screenshots` altına, paylaşılabilir PDF `Docs/pdf/realitykit-pipeline-guide.pdf` altına kopyalandı.
- `.gitignore` public repo için genişletildi; `Build/` scratch output olarak bırakıldı.
- `Docs/repo-release-checklist.md` eklendi.
- Sprint 3 için `target_basic_textured` manifest kaydı ve loader fallback sırası hazırlandı.
- Texture eğitim asset'i için Blender checklist'e base color odaklı export kuralları eklendi.
- Imported target scale `0.48` olarak RealityKit tarafında normalize edildi.
- Spawn noktaları sabit slot listesine çevrildi; hedefler HUD ve alt kontrol butonlarıyla çakışmadan kadraj içinde görünür hale geldi.
- Reset sonrası spawn slot sırası resetlenerek debug ve eğitim tekrar üretilebilirliği artırıldı.

### 2026-04-29

- `RealityKitPipelineDemo` klasörü oluşturuldu.
- XcodeGen `project.yml` eklendi.
- SwiftUI app entry, HUD ve kontrol butonları eklendi.
- `GameARView` ile non-AR RealityKit sandbox kuruldu.
- Procedural arena, target, projectile, hit detection, score ve reset eklendi.
- `ImportedAssetLoader` eklendi.
- `target_basic.usdz` bulunamazsa procedural fallback davranışı eklendi.
- `Assets/Imported` ve `Assets/Textures` resource folder olarak XcodeGen’e bağlandı.
- `README.md`, pipeline, Blender checklist, asset budget ve learning roadmap eklendi.
- Claude/Codex/QA prompt şablonları eklendi.

## Verification Log

### 2026-05-02

Komut:

```bash
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('json: ok')"
```

Sonuç:

```text
json: ok
```

Komut:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

Sonuç:

```text
xcodebuild: ok
```

MCP görsel doğrulama (Sprint 2 sonu):

```text
build_run_sim: ok, iPhone 17 simulator
screenshot: Build/target_basic_scale_slots.jpg
screenshot: Build/target_textured_fallback_ready.jpg
```

Not:

- CoreSimulator servis uyarıları shell build sırasında devam ediyor; build sonucunu engellemedi.
- Screenshot'ta iki imported target kadraj içinde ve okunur ölçekte görünüyor.
- `target_basic_textured.usdz` henüz yokken fallback olarak `target_basic.usdz` yüklenmeye devam ediyor.

Sprint 4 — ring skor doğrulaması:

```text
build_run_sim: ok, iPhone 17 simulator
tap: right target center
screenshot: Docs/screenshots/ring_scoring_inner_hit.jpg
HUD: Inner ring +3
Score: 3
Hits: 1
Accuracy: 100%
```

Sprint 5 — arena fallback hazırlık doğrulaması:

```text
manifest: ok
xcodebuild: ok
build_run_sim: ok, iPhone 17 simulator
screenshot: Docs/screenshots/arena_floor_fallback_ready.jpg
```

Sprint 5 — imported arena doğrulaması:

```text
asset: Assets/Imported/arena_floor.usdz (15.5 KB)
manifest: ok
xcodegen generate: ok
xcodebuild: ok
build_run_sim: ok, iPhone 17 simulator
screenshot: Docs/screenshots/arena_floor_imported.jpg
```

Sprint 3 — texture asset doğrulaması:

```bash
# Blender Python ile asset üretimi
blender --background --python /tmp/make_textured_target.py
# → Assets/Imported/target_basic_textured.usdz (29.4 KB)
# → textures/target_basic_textured_basecolor.png 512x512 embedded

rtk xcodegen generate
rtk xcodebuild -quiet ... build
xcrun simctl launch ... com.kyylian.RealityKitPipelineDemo
xcrun simctl io ... screenshot target_textured_sprint3_fresh.png
```

Sonuç:

```text
xcodebuild: ok
HUD: target_basic_textured ready
screenshot: Build/target_textured_sprint3_fresh.png
```

Not:

- Texture UV planar projection Z'den; `'st'` primvar override edildi.
- HUD ilk açılışta `target_basic_textured ready` yazıyor — textured asset yüklendi.
- Concentric ring pattern UV flip/bozukluk yok.
- Scale ve origin `target_basic` ile aynı kalıyor.

### 2026-04-30

Komut:

```bash
rtk xcodegen generate
```

Sonuç:

```text
Created project at /Users/kyylian/Developer/RealityKitPipelineDemo/RealityKitPipelineDemo.xcodeproj
```

Komut:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

Sonuç:

```text
xcodebuild: ok
```

Bundle kontrolü:

```text
Build/Products/Debug-iphonesimulator/RealityKitPipelineDemo.app/Imported/target_basic.usdz
```

Not:

- İlk build denemesi varsayılan `~/Library/Developer/Xcode/DerivedData` yazma izni nedeniyle düştü.
- Workspace içindeki `Build/DerivedData` ile build başarılı.
- CoreSimulator servis uyarıları devam ediyor; generic build sonucunu engellemedi.
- Asset simulator üzerinde yüklendi ve screenshot ile doğrulandı.
- İlk görsel testte asset edge-on görünüyordu; nested mesh child rotation sonrası kırmızı/beyaz ringler görünür hale geldi.
- Screenshot çıktısı: `Build/target_basic_simulator_childrot.png`.
- Son düzeltme sonrası front-facing screenshot: `Build/target_basic_frontface.png`.
- Kalan tuning: target scale ve spawn bounds ayarlanmalı; bazı hedefler ekrana büyük veya kenardan taşmış gelebiliyor.

### 2026-04-29

Komut:

```bash
rtk xcodegen generate
```

Sonuç:

```text
Created project at /Users/kyylian/Developer/RealityKitPipelineDemo/RealityKitPipelineDemo.xcodeproj
```

Komut:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator build
```

Sonuç:

```text
xcodebuild: ok
```

Not:

- CoreSimulator servisinden sandbox kaynaklı uyarılar geliyor.
- Generic iOS Simulator build başarılı.
- App görsel olarak henüz simülatörde/cihazda çalıştırılarak doğrulanmadı.

## Decision Log

### D001: Substance ilk aşamada zorunlu değil

Mobil RealityKit MVP için Substance kullanılmayacak. İlk aşamada Blender + Claude asset otomasyonu + RealityKit entegrasyonu yeterli. Substance ancak PBR texture üretimi darboğaz olursa değerlendirilecek.

### D002: Asset pipeline bilgisi ortak öğrenilecek

Kyylian ve Mehmet asset/texture pipeline'ını birlikte öğrenecek. Blender, Blender MCP, Claude otomasyonu ve Codex ayrı istasyonlar olarak kullanılabilir; ancak kalıcı rol ayrımı "asset'i bir kişi bilir, kodu diğer kişi bilir" şeklinde yapılmayacak. Her handoff simulator screenshot, build sonucu ve kısa öğrenme notuyla kapatılacak.

### D003: Elle Xcode resource eklemek yerine XcodeGen kullanılacak

Yeni assetler `Assets/Imported` altına eklenecek, sonra `rtk xcodegen generate` çalıştırılacak. Böylece Xcode project dosyası elle düzenlenmeyecek.

### D004: Asset yokken app çalışmaya devam edecek

`target_basic.usdz` bulunamazsa procedural sphere kullanılacak. Bu karar öğrenme hızını korur ve asset pipeline bozukken gameplay development’ı durdurmaz.

## Next Sprint Candidates

- Imported target scale/orientation ayarı yap.
- Target health ve wave timer ekle.
- Hit VFX ve spatial sound ekle.
- Basit device/simulator run checklist oluştur.
