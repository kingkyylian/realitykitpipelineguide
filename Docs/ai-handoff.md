# AI Handoff

This file is the fast orientation page for any AI agent opening the repository.

## Project Status

Current state: public Git repo on `main`: `https://github.com/kingkyylian/realitykitpipelineguide`. Use `git log --oneline --decorate -6` for the latest commit list instead of relying on a fixed count in this document.

The project is a command-first RealityKit pipeline toolkit. `Tools/rkp.py`, the installable Codex skill, and the slash commands are the main product; the SwiftUI + RealityKit target-shooting app is a verification fixture for proving imported assets in Xcode/RealityKit.

## What This Project Is

RealityKitPipelineDemo is a small RealityKit asset-pipeline toolkit. It teaches and automates a complete asset and texture pipeline:

```text
Blender / asset generation -> USDZ -> XcodeGen resource bundle -> RealityKit import -> simulator screenshot -> documented learning note
```

It is not a game-first repository. Treat the fixture app as a test harness for the CLI/skill workflow, not as the product architecture.

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
| Game Factory CLI | First batch active | `src/rkg/cli.py`, `src/rkg/archetypes.py`, `src/rkg/archetype_runtime.py`, `src/rkg/content_views.py`, `Tools/rkg.py`, `Docs/game-factory.md`, `Docs/game-spec.md`, `Docs/rkg-architecture.md`, `Tests/test_rkg_spec.py`, `Tests/test_rkg_init_game.py`, `Tests/test_rkg_score_idea.py`, `Tests/test_rkg_archetypes.py`, `Tests/test_rkg_archetype_runtime.py`, `Tests/test_rkg_content_views.py`, `Tests/test_rkg_scaffold_generators.py`; `score-idea`, `list-archetypes`, `describe-archetype`, `plan-game`, `init-game`, and `verify-game` are active RKG surfaces |
| Fresh external project walkthrough | Verified | GitHub `pipx install`, `rkp init`, `doctor`, `make-asset`, fallback `build-asset`, and `release-check` recorded in `Docs/WORKLOG.md` Sprint 40 |
| Codebase audit route | Current | `Docs/codebase-audit.md` records dead-code scan, optimization findings, and prioritized cleanup plan |
| CLI smoke tests | Started | `Tests/test_rkp_cli.py`, `make test` |

## Planned Learning Modules

Recommended order:

1. Expand `Tools/rkp.py` and the skill package as the reusable developer tool surface.
2. Module 4: Texture Maps and Material Response.
3. Module 5: Performance and Mobile Asset Budget.
4. Module 6: Collision, VFX, and Gameplay Feel. Ring scoring is started; VFX/audio remain.
5. Module 7: Environment Asset and Texture Atlas. Arena floor import is complete; future work can expand atlas/tiling variants.
6. Module 8: Repo and Authoring Workflow.

MCP status: no standalone MCP server ships yet. `status --json` and `doctor --json` are the stable machine-readable surfaces for current automation and future MCP-style wrapping.

Portability status: config decoupling and packaging are in place. `pyproject.toml` exposes `rkp = "rkp.cli:main"` and `rkg = "rkg.cli:main"`, implementation modules live under `src/rkp` and `src/rkg`, and repo-local `Tools/*.py` files are wrappers. `rkp.json` marks the project root and configures manifest/assets/docs/blender/textures/source/tests/Xcode paths. `init`, `status`, `doctor`, `doctor --blender`, `new-asset`, `prompt-asset`, `build-asset`, `inspect-usdz`, `verify-asset`, `accept-asset`, direct USDZ fallback, Meshy USDZ draft generation, and `release-check` are config-aware. `inspect-usdz` checks package existence, expected base color texture, PNG/JPEG dimensions against `maxTextureSize`, text USDA `primvars:st`, and known triangle budget status before screenshot acceptance. `verify-asset` orchestrates optional build, USDZ inspection, optional screenshot acceptance, and optional release-check, stopping at the first failed gate. `release-check --assets` inspects all imported manifest assets before the optional Xcode build. `prompt-asset` remains deterministic by default; Claude script generation requires explicit `--generator claude` and the optional AI dependency. `rkp init` bootstraps a minimal external project and refuses to overwrite existing config unless `--force` is passed. If `xcode_project` is omitted, `release-check` skips the Xcode gate after doctor/tests/manifest validation. `rkg score-idea` evaluates first-wave scope before scaffolding; `rkg list-archetypes` and `rkg describe-archetype` expose the seed archetype registry; `rkg plan-game --json` exposes selected `screenshot_proofs`; `rkg init-game` generates a minimal fixed-camera SwiftUI + RealityKit project with planned RKP manifest assets, procedural runtime fallback, and store screenshot proof cues. Current generated playable coverage: `lane_dodger`, `wave_defense_lite`, `toss_physics`, and `stack_puzzle` have playable SwiftUI loops and bind SwiftUI state into RealityKit scene entity movement. Fresh external project walkthrough is verified from GitHub install through fallback USDZ build; see `Docs/WORKLOG.md` Sprint 40.

## Current Recommended Next Task

If the user asks to make the repository look professional on GitHub, do this next:

1. Review and publish the local commits that are ahead of `origin/main`; do not rewrite the existing `v0.1.0` tag.
2. Create the next release/tag from the `CHANGELOG.md` `Unreleased` section after the release notes are reviewed.
3. Document the supported Blender version matrix or add a first-class `rkp build-asset --fallback-only` path. `rkp doctor --blender` diagnostic already exists.
4. Add README badges if they are not already present.
5. Set or verify GitHub repo description/topics from `Docs/github-showcase.md`.
6. Add a first-good-issue list for learners.
7. Decide whether to keep all `Tools/*.py` wrappers long-term now that `rkp` is installable.

If the user asks to continue education content, do this next:

1. Start Module 4: Texture Maps and Material Response.
2. Define a roughness/material value comparison asset.
3. Keep base color pipeline intact.
4. Add screenshot-based comparison.

If the user asks to continue the game factory route, do this next:

1. Keep RKG framed as a multi-archetype RealityKit game factory, not a target-shooter generator.
2. Define reusable generated Swift modules for start, core action, feedback, fail/miss, reset, result, and screenshot states.
3. Add optional generated QA instructions that sequence screenshots from `screenshot_proofs`.
4. Consider extracting common state-update formula helpers only if another archetype repeats the same movement pattern.
5. Add richer store-pack checklist expansion from `release.screenshots`.

## Key Files to Read First

1. `AGENTS.md`
2. `README.md`
3. `Docs/cli-tool.md`
4. `Docs/guide.md`
5. `Docs/WORKLOG.md`
6. `Tools/asset_manifest.json`
7. `Sources/RealityKitPipelineDemo/GameARView.swift`

## Known Implementation Details

- `GameARView` uses non-AR RealityKit mode as a verification fixture.
- `GameARView` loads `target_basic_textured` first, then `target_basic`, then procedural fallback.
- Imported target scale is normalized with `0.90`.
- Spawn positions are deterministic slots for teaching/debugging.
- Ring scoring is deterministic screen-space scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- `GameARView.addArena()` tries `arena_floor` first, then falls back to procedural floor + lane markers.
- `arena_floor.usdz` is imported and manifest status is `imported`.
- Fixture polish exists: darker backdrop, readable HUD, reticle overlay, projectile-delayed scoring, and hit spark VFX.
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
