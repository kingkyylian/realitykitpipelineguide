# RealityKit Pipeline Demo Worklog

Bu dosya projenin ortak çalışma defteri. Her yeni işe başlamadan önce buraya kısa hedef yazacağız; iş bitince ne yaptığımızı, hangi komutları çalıştırdığımızı ve ne öğrendiğimizi ekleyeceğiz.

## Nasıl Kullanacağız

1. Yeni iş başlamadan önce `Current Sprint` bölümünü güncelle.
2. İşi küçük görevlere böl: Claude, Codex, insan.
3. Asset veya kod sözleşmesi değişirse `Contracts` bölümüne yaz.
4. Build/test sonucu varsa `Verification Log` bölümüne ekle.
5. Kararları sadece sohbet içinde bırakma; `Decision Log` bölümüne kaydet.

## Current Sprint

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
