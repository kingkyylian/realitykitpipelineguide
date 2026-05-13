# AI Handoff

This file is the fast orientation page for any AI agent opening the repository.

## Project Status

Current state: public Git repo on `main`: `https://github.com/kingkyylian/realitykitpipelineguide`. Use `git log --oneline --decorate -6` for the latest commit list instead of relying on a fixed count in this document.

The project is a command-first RealityKit pipeline toolkit. `Tools/rkp.py`, the installable Codex skill, and the slash commands are the main product; the SwiftUI + RealityKit target-shooting app is a verification fixture for proving imported assets in Xcode/RealityKit.

Default decision rule: default to `rkp` asset-pipeline work unless the user explicitly asks for `rkg`, game factory, generated games, archetypes, store packs, or screenshot QA for generated projects; only work on `rkg` when that experimental labs route is explicitly requested or when maintaining existing RKG tests/docs.

## What This Project Is

RealityKitPipelineDemo is a small RealityKit asset-pipeline toolkit. It teaches and automates a complete asset and texture pipeline:

```text
Blender / asset generation -> USDZ -> XcodeGen resource bundle -> RealityKit import -> simulator screenshot -> documented learning note
```

It is not a game-first repository. Treat the fixture app as a test harness for the CLI/skill workflow, not as the product architecture.

## Product Surface

The stable product surface is the RKP pipeline:

- `Tools/rkp.py`
- `src/rkp`
- `Tools/asset_manifest.json`
- `Assets/Imported`
- `Docs/cli-tool.md`
- `Docs/guide.md`
- `Skills/realitykit-pipeline-guide`

## Experimental Labs Surface

RKG is useful but secondary:

- `Tools/rkg.py`
- `src/rkg`
- `Docs/game-factory.md`
- `Docs/rkg-architecture.md`
- `Tests/test_rkg_*.py`

Do not expand RKG while doing product-focus cleanup unless a test or doc boundary requires it.

## Completed Learning Modules

| Module | Status | Evidence |
| --- | --- | --- |
| First USDZ import | Complete | `Assets/Imported/target_basic.usdz`, `Docs/screenshots/target_basic_frontface.png` |
| Scale/orientation tuning | Complete | `Docs/screenshots/target_basic_scale_slots.jpg` |
| Base color textured asset | Complete | `Assets/Imported/target_basic_textured.usdz`, `Docs/screenshots/target_textured_sprint3_fresh.png` |
| UV primvar lesson | Complete | `Docs/blender-usdz-checklist.md`, `Docs/WORKLOG.md` |
| Ring-based scoring | Complete | `Docs/screenshots/ring_scoring_inner_hit.jpg` |
| Arena floor fallback | Complete | `Docs/screenshots/arena_floor_fallback_ready.jpg` |
| Arena floor import | Complete | `Assets/Imported/arena_floor.usdz`, `Docs/screenshots/arena_floor_imported.jpg` |
| Teaching guide | Strong first version | `Docs/guide.md`, `Docs/pdf/realitykit-pipeline-guide.pdf` |
| Pipeline CLI | Active product surface | `src/rkp/cli.py`, `Tools/rkp.py`, `Docs/cli-tool.md`, `Tests/test_rkp_cli.py`, `Tests/test_rkp_init.py`, `Tests/test_rkp_package.py`; `verify-asset`, `inspect-usdz`, `release-check --assets`, explicit `--generator claude`, and `--backend meshy` draft paths are documented |
| Game Factory CLI | Experimental first batch | `src/rkg/cli.py`, `src/rkg/archetypes.py`, `src/rkg/archetype_runtime.py`, `src/rkg/content_views.py`, `src/rkg/custom_realitykit_runtime.py`, `src/rkg/qa_plan.py`, `src/rkg/runtime_core.py`, `src/rkg/screenshot_status.py`, `Tools/rkg.py`, `Docs/game-factory.md`, `Docs/game-spec.md`, `Docs/rkg-architecture.md`, `Tests/test_rkg_spec.py`, `Tests/test_rkg_init_game.py`, `Tests/test_rkg_custom_realitykit_runtime.py`, `Tests/test_rkg_score_idea.py`, `Tests/test_rkg_archetypes.py`, `Tests/test_rkg_archetype_runtime.py`, `Tests/test_rkg_content_views.py`, `Tests/test_rkg_runtime_core.py`, `Tests/test_rkg_scaffold_generators.py`, `Tests/test_rkg_qa_plan.py`, `Tests/test_rkg_screenshot_status.py`; `score-idea`, `new-spec`, `new-game`, `list-archetypes`, `list-adapters`, `describe-archetype`, `plan-game`, `qa-plan`, `capture-screenshots`, `verify-screenshots`, `init-game`, and `verify-game` are active RKG surfaces. Native playable archetypes now include `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, `wave_defense_lite`, `fighter_2_5d`, and `flappy_side_scroller`; `custom_realitykit` covers generic racing/projectile/FPS/shooter/collector-style skeletons with generated `CameraRig`, `InputController`, `SystemFlags`, `RuntimeSceneSnapshot`, compact state-bound overlay, screenshot-state seeding, adapter-specific `qa-plan` proof text, a racing adapter for lane/lap/checkpoint/collision proof, a projectile adapter for charge/launch/travel/impact proof, a shooter adapter for aim/fire/health/cover/enemy proof, and a collector adapter for pickup/score/timer proof. Custom adapters are declared through `CustomRealityKitRuntimeAdapter` registry entries and exposed through `rkg list-adapters --json`. `capture-screenshots` writes screenshot JSON sidecars and runtime `.scene.json` role snapshots; `verify-screenshots` checks sidecar state/role metadata, runtime scene-role metadata, file validity/dimensions, samples PNG plus JPEG evidence on macOS, rejects blank/solid captures, rejects duplicate visual evidence across release states, and enforces first-pass semantic visual contracts for debug-overlay, flat-scene, and too-dark-scene failures. Fighter screenshot evidence exists at `Docs/screenshots/rkg_fighter_*.jpg`; Flappy evidence exists at `Docs/screenshots/rkg_flappy_*.jpg`. Generated games still need human product review before any shipping claim |
| Fighter zero-to-skeleton walkthrough | Complete | `rkg new-spec`, `init-game`, `verify-game`, `capture-screenshots`, `verify-screenshots` |
| Generic RealityKit skeleton generator | System adapter slice | `rkg new-game --title ... --camera ... --input ... --systems ...` writes `custom_realitykit` GameSpecs for racing, projectile/shooting, shooter/FPS-like, and collector-style starts, with role-aware fallback assets, asset briefs, generated store/QA docs, `CameraRig`, `InputController`, `SystemFlags`, simulator capture, and screenshot verification. Racing specs generate lane steering, lap/checkpoint progress, collision/result proof, and state-to-scene binding. Projectile specs generate charge/launch/hit state, weapon/projectile/target role binding, controls, scene binding, and screenshot proof. FPS/shooter specs generate aim/fire/health/cover/enemy state, controls, scene binding, and screenshot proof. Collector specs generate pickup/timer/combo state, controls, scene binding, and screenshot proof |
| Shard Volley RKG dogfood | Verified | `Docs/rkg-shard-volley-dogfood.md`, `Docs/screenshots/rkg_shard_volley_*.jpg`, `Docs/screenshots/rkg_shard_volley_v7_*.jpg`; idea score, `new-game`, `validate-spec`, `plan-game`, `qa-plan`, `init-game`, `verify-game`, `capture-screenshots`, and `verify-screenshots` were run end-to-end for a projectile/shooting/score game. Dogfood found and fixed collector-score adapter overlap, too-short screenshot launch wait, game-shell presentation gaps, and first semantic visual QA gaps |
| Fresh external project walkthrough | Verified | GitHub `pipx install`, `rkp init`, `doctor`, `make-asset`, fallback `build-asset`, and `release-check` recorded in `Docs/WORKLOG.md` Sprint 40 |
| Codebase audit route | Current | `Docs/codebase-audit.md` records dead-code scan, optimization findings, and prioritized cleanup plan |
| CLI smoke tests | Started | `Tests/test_rkp_cli.py`, `make test` |
| Material response first slice | Complete | `Assets/Imported/material_response_targets.usdz`, `Docs/screenshots/material_response_targets.png`, `rkp inspect-usdz` textureMaps output |
| Roughness readability polish | Complete | Neutral curved witness patch, stronger roughness values, grazing comparison lights |
| Metallic value comparison | Complete | Fourth `material_response_targets` panel; metallic remains a material value, not a texture map |

RKG latest note: `rkg start-game` now scores an idea, chooses native fighter/flappy or custom RealityKit camera/input/systems from idea keywords, scaffolds the project, and returns the QA plan plus `asset_pipeline.tasks` in one command. Each asset pipeline task maps a generated asset brief to ordered RKP command arrays for `make-asset`, `build-asset`, `inspect-usdz --json`, and screenshot-gated `accept-asset`. `flappy_side_scroller` is now the native Flappy-like proof: `Build/rkg-flappy/FlappyReef` passes `verify-game`, `capture-screenshots`, and `verify-screenshots --json` for `gameplay_start`, `mid_flight`, `near_gap`, `collision`, and `results`; public evidence is `Docs/screenshots/rkg_flappy_*.jpg`. `rkg accept-first-asset` wraps the first gameplay-relevant task into one workflow: make/build/inspect, capture and verify screenshots, copy the selected state screenshot to `<asset_id>_imported.jpg`, accept, and run `release-check --assets`. It skips the make step when `Tools/blender/create_<asset_id>.py` already exists, so it can resume. The acceptance executor keeps plan output readable as `rkp`/`rkg` commands, but dispatches those entrypoints through workspace modules so local dogfood cannot accidentally use an older installed binary. The dogfood proof is `Build/rkg-start-game-dogfood/ShardVolleyStart`: generated build/capture/sidecars/scene snapshots pass, and one emitted task (`target_proxy`) has been built, inspected, accepted with `Docs/screenshots/target_proxy_imported.jpg`, and verified by `rkp release-check --assets`. The current custom game-skeleton proof is `Build/rkg-proper-skeleton-v7/ShardVolleyStart`: generated `custom_realitykit` apps include a full-screen game shell, start overlay, compact HUD, icon controls, `WorldRig.swift` with lighting/backdrop/arena lanes/projectile feedback only when the projectile adapter needs it, `SceneEvents.Update` idle motion, neutral fallback player proxy, result-only panel, and semantic visual screenshot contracts; `verify-game`, `capture-screenshots`, and `verify-screenshots --json` all pass for four screenshot states.

## Planned Learning Modules

Recommended order:

1. Expand `Tools/rkp.py` and the skill package as the reusable developer tool surface.
2. Module 4: Texture Maps and Material Response.
3. Module 5: Performance and Mobile Asset Budget.
4. Module 6: Collision, VFX, and Gameplay Feel. Ring scoring is started; VFX/audio remain.
5. Module 7: Environment Asset and Texture Atlas. Arena floor import is complete; future work can expand atlas/tiling variants.
6. Module 8: Repo and Authoring Workflow.

MCP status: no standalone MCP server ships yet. `status --json` and `doctor --json` are the stable machine-readable surfaces for current automation and future MCP-style wrapping.

Portability status: `rkp` is installable, config-aware, and usable from external RealityKit projects. `rkp.json` marks the project root and configures manifest/assets/docs/blender/textures/source/tests/Xcode paths. The stable machine-readable surfaces are `rkp status --json` and `rkp doctor --json`. `rkg` also ships as an entry point, but it remains experimental labs work.

## Current Recommended Next Task

Post-release state: `v0.2.1` is published and GitHub Actions passed on the release commit. Do not rewrite `v0.2.0` or `v0.2.1`; use a future patch release for corrections.

Recommended next path:

1. Default back to the RKP product path and continue Module 4: Texture Maps and Material Response.
2. Pick exactly one next material slice: metallic map need assessment or normal-map export behavior.
3. If deliberately continuing RKG, use `Docs/rkg-shard-volley-dogfood.md` plus the Flappy evidence from Sprint 136 as the current gap list. Adapter-specific `qa-plan` proof text, blank/solid PNG/JPEG guardrails, malformed JPEG rejection, duplicate visual evidence detection, capture-contract sidecars, runtime scene-role snapshots, idea-to-project orchestration, generated asset-brief to RKP command planning, one emitted asset task dogfood, `accept-first-asset`, `accept-assets`, fresh capture XcodeGen generation, local CLI subprocess module dispatch, the readable `target_proxy` bullseye asset, full five-asset Shard Volley demo acceptance, first game-shell/world-rig presentation parity, first semantic visual QA, SceneEvents-based idle motion, and native Flappy-like scaffold proof are done. The next useful slice is text-overlap/mesh-visibility QA or richer Flappy/charge/launch VFX, sound, haptics, and level variety hooks.
4. Keep screenshot evidence required before marking any visual asset imported.
5. Use `Docs/blender-support.md` when answering Blender/fallback setup questions.
6. Use `Docs/first-good-issues.md` when creating learner-friendly issue candidates.

## Key Files to Read First

1. `AGENTS.md`
2. `README.md`
3. `Docs/cli-tool.md`
4. `Docs/guide.md`
5. `Docs/WORKLOG.md`
6. `Tools/asset_manifest.json`
7. `Sources/RealityKitPipelineDemo/GameARView.swift`
8. `Sources/RealityKitPipelineDemo/TargetFactory.swift`
9. `Sources/RealityKitPipelineDemo/ArenaBuilder.swift`

## Known Implementation Details

- `GameARView` uses non-AR RealityKit mode as a verification fixture.
- `TargetFactory` loads `target_basic_textured` first, then `target_basic`, then procedural fallback.
- `TargetFactory` normalizes imported target scale with `0.90`.
- `TargetFactory` owns deterministic spawn slots for teaching/debugging.
- Ring scoring is deterministic screen-space scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- `ArenaBuilder.addArena()` tries `arena_floor` first, then falls back to procedural floor + lane markers.
- `arena_floor.usdz` is imported and manifest status is `imported`.
- Fixture polish exists: darker backdrop, readable HUD, reticle overlay, projectile-delayed scoring, and hit spark VFX through `HitEffectSystem`.
- Modern RealityKit pass exists: physics bodies, collision events, PBR helper materials, and SDK-stable target spawn animation with `move(to:relativeTo:duration:)`.
- Public onboarding includes `README.md`, `LICENSE`, `CONTRIBUTING.md`, `Makefile`, GitHub Actions, issue templates, and `Tools/blender`.
- `Build/` is ignored scratch output.
- Public screenshots are copied to `Docs/screenshots`.
- Reusable production docs exist: `Docs/production-playbook.md`, `Docs/new-game-startup.md`, and `Prompts/game-feature-brief.md`.

## Verification Commands

Manifest:

```bash
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Build:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

CLI tests:

```bash
rtk python3 -m unittest discover -s Tests
```

Guide PDF:

```bash
rtk pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
rtk weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
rtk cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

## Documentation Contract

If you change code, assets, or teaching flow:

- update `Docs/WORKLOG.md`
- update `Tools/asset_manifest.json` if assets changed
- update `Docs/guide.md` if the learning path changed
- regenerate `Docs/pdf/realitykit-pipeline-guide.pdf` if guide changed
- update this file if the next task changes

## Git Notes

- Current branch: `main`
- Keep commits focused.
- Do not push unless the user explicitly asks.
- Do not commit ignored scratch output.
