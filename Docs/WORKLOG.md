# RealityKit Pipeline Demo Worklog

Bu dosya projenin ortak çalışma defteri. Her yeni işe başlamadan önce buraya kısa hedef yazacağız; iş bitince ne yaptığımızı, hangi komutları çalıştırdığımızı ve ne öğrendiğimizi ekleyeceğiz.

## Nasıl Kullanacağız

1. Yeni iş başlamadan önce `Current Sprint` bölümünü güncelle.
2. İşi küçük görevlere böl: Claude, Codex, insan.
3. Asset veya kod sözleşmesi değişirse `Contracts` bölümüne yaz.
4. Build/test sonucu varsa `Verification Log` bölümüne ekle.
5. Kararları sadece sohbet içinde bırakma; `Decision Log` bölümüne kaydet.

## Current Sprint

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
