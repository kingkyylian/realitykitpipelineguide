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
| Game Factory CLI | Experimental first batch | `src/rkg/cli.py`, `src/rkg/archetypes.py`, `src/rkg/archetype_runtime.py`, `src/rkg/content_views.py`, `src/rkg/qa_plan.py`, `src/rkg/screenshot_status.py`, `Tools/rkg.py`, `Docs/game-factory.md`, `Docs/game-spec.md`, `Docs/rkg-architecture.md`, `Tests/test_rkg_spec.py`, `Tests/test_rkg_init_game.py`, `Tests/test_rkg_score_idea.py`, `Tests/test_rkg_archetypes.py`, `Tests/test_rkg_archetype_runtime.py`, `Tests/test_rkg_content_views.py`, `Tests/test_rkg_scaffold_generators.py`, `Tests/test_rkg_qa_plan.py`, `Tests/test_rkg_screenshot_status.py`; `score-idea`, `new-spec`, `new-game`, `list-archetypes`, `describe-archetype`, `plan-game`, `qa-plan`, `capture-screenshots`, `verify-screenshots`, `init-game`, and `verify-game` are active RKG surfaces. Native playable archetypes now include `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, `wave_defense_lite`, and `fighter_2_5d`; `custom_realitykit` covers generic racing/FPS/shooter-style skeletons. Fighter screenshot evidence exists at `Docs/screenshots/rkg_fighter_*.jpg`, but generated games still need human product review before any shipping claim |
| Fighter zero-to-skeleton walkthrough | Complete | `rkg new-spec`, `init-game`, `verify-game`, `capture-screenshots`, `verify-screenshots` |
| Generic RealityKit skeleton generator | First slice | `rkg new-game --title ... --camera ... --input ... --systems ...` writes `custom_realitykit` GameSpecs for racing and shooter/FPS-like starts, with role-aware fallback assets, asset briefs, generated store/QA docs, simulator capture, and screenshot verification |
| Fresh external project walkthrough | Verified | GitHub `pipx install`, `rkp init`, `doctor`, `make-asset`, fallback `build-asset`, and `release-check` recorded in `Docs/WORKLOG.md` Sprint 40 |
| Codebase audit route | Current | `Docs/codebase-audit.md` records dead-code scan, optimization findings, and prioritized cleanup plan |
| CLI smoke tests | Started | `Tests/test_rkp_cli.py`, `make test` |
| Material response first slice | Complete | `Assets/Imported/material_response_targets.usdz`, `Docs/screenshots/material_response_targets.png`, `rkp inspect-usdz` textureMaps output |
| Roughness readability polish | Complete | Neutral curved witness patch, stronger roughness values, grazing comparison lights |
| Metallic value comparison | Complete | Fourth `material_response_targets` panel; metallic remains a material value, not a texture map |

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
3. If deliberately continuing RKG, deepen the `custom_realitykit` runtime layer with generated `CameraRig.swift`, `InputController.swift`, and system adapters for vehicle movement, first-person aiming, weapon/projectile/hitscan, health, and collision; do not repeat the already-captured fighter screenshot task.
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
