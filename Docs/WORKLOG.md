# RealityKit Pipeline Demo Worklog

Bu dosya projenin ortak çalışma defteri. Her yeni işe başlamadan önce buraya kısa hedef yazacağız; iş bitince ne yaptığımızı, hangi komutları çalıştırdığımızı ve ne öğrendiğimizi ekleyeceğiz.

## Nasıl Kullanacağız

1. Yeni iş başlamadan önce `Current Sprint` bölümünü güncelle.
2. İşi küçük görevlere böl: Claude, Codex, insan.
3. Asset veya kod sözleşmesi değişirse `Contracts` bölümüne yaz.
4. Build/test sonucu varsa `Verification Log` bölümüne ekle.
5. Kararları sadece sohbet içinde bırakma; `Decision Log` bölümüne kaydet.

## Current Sprint

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
