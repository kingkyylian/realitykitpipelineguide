# Changelog

## Unreleased

- No unreleased changes yet.

## v0.2.0 - RKP product path and RKG labs preview (2026-05-10)

### RKP Product Surface

- Clarified the public product boundary: RKP is the active toolkit surface, RKG is experimental labs, and the included app is a verification fixture.
- Added Makefile `bootstrap-dev` and `verify-local` targets for local contributor setup and lint/test/doctor verification.
- Aligned Ruff configuration with test/tool bootstrap imports, cleaned current lint debt, and kept `pipeline doctor` from scanning local `.venv` metadata.
- Hardened RKP release and asset verification gates with USDZ inspection, direct USDZ fallback handling, Blender diagnostics, and safer cleanup support.
- Added `rkp build-asset --fallback-only` for explicit direct USDZ draft generation when Blender should be skipped.
- Added public-facing README badges, a Blender support/fallback matrix, and a first-good-issues list for learner-sized contributions.
- Shortened README into a concise public landing page and moved repeated command details back to `Docs/cli-tool.md`.
- Fixed GitHub Actions Python dependency installation on Homebrew-managed macOS runners by installing dev dependencies inside a workflow-local virtual environment.
- Updated `rkp doctor` CI validation so the release gate accepts the new virtualenv-backed test command.

### RKG Experimental Labs

- `rkg` RealityKit game-factory CLI surface for idea scoring, archetype discovery, spec validation, game planning, screenshot QA planning, project scaffolding, generated game verification, and store-pack checklist generation.
- Archetype registry for `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, and `wave_defense_lite`.
- Config-aware generated game projects with shared Swift modules: `GameState`, `SessionControl`, `FeedbackState`, `InputIntent`, `ScreenshotState`, `GameRules`, `GameSceneController`, `GameView`, `AssetLoader`, `FallbackFactory`, and result/UI surfaces.
- Required asset-role validation and runtime entity planning for generated games.
- Archetype screenshot proof cues exposed through `plan-game --json` and generated store screenshot checklists.
- Generated store screenshot QA runbooks that sequence capture states from `screenshot_proofs`.
- `rkg qa-plan` command for machine-readable and text screenshot capture plans.
- `rkg verify-screenshots` command for checking generated screenshot evidence files against a `qa-plan --json` payload or generated project `GameSpec.json`.
- Minimal playable generated loops for `target_shooter`, `lane_dodger`, `wave_defense_lite`, `toss_physics`, and `stack_puzzle`.
- RealityKit state-to-scene binding for the generated `target_shooter`, `lane_dodger`, `toss_physics`, `wave_defense_lite`, and `stack_puzzle` archetypes.
- Split growing RKG Swift string emitters out of `src/rkg/scaffold.py` into focused runtime/content-view generation modules.
- Renamed the shared state-bound generated `GameView` helper away from lane-dodger-specific terminology.
- Extracted shared generated scene entity load/reference wiring for state-bound RKG archetypes.
- Routed generated result/fail transitions through the shared `SessionControl.markResult` helper.
- Routed generated result overlay visibility through the shared `SessionControl.isResult` helper.
- Routed generated last-event display text through the shared `FeedbackState.message` helper.
- Routed generated primary/reset button labels through the shared `InputIntent` helper.
- Wired generated `ResultView` into playable archetype overlays when `state.phase == .result`.

### Fixture and Teaching

- Split the RealityKit fixture view into focused arena, target factory, hit-effect, and material helpers while preserving target fallback order.
- Clarified the multi-archetype RKG scope so target shooter remains one fixture, not the whole product.

### Verified

- `rtk make verify-local`
- `rtk .venv/bin/python Tools/rkp.py release-check`
- manifest validation
- XcodeGen project generation
- iOS simulator generic build

## v0.1.0 - Public pipeline toolkit preview

### Added

- `rkp` command-first pipeline CLI.
- Installable Codex skill and agent slash command surface.
- SwiftUI + RealityKit verification fixture.
- Procedural target and arena fallbacks.
- Imported `target_basic.usdz`.
- Imported textured `target_basic_textured.usdz`.
- Imported `arena_floor.usdz`.
- Ring-based scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- Asset manifest with budgets and learning notes.
- Blender starter script for arena floor generation.
- Public guide PDF, screenshots, release checklist, CI, contribution templates, and Makefile.
- CLI smoke tests through `python3 -m unittest discover -s Tests`.
- Showcase polish pass with a darker backdrop, readable HUD, reticle overlay, projectile-delayed scoring, and hit spark VFX.
- Modern RealityKit feel pass with physics bodies, physics motion, collision events, PBR helper materials, and availability-gated entity animation.

### Verified

- `make release-check`
- `make test`
- manifest validation
- XcodeGen project generation
- iOS simulator build
- simulator screenshot evidence under `Docs/screenshots`

### Known next steps

- Add a README demo GIF.
- Add target-generation Blender scripts.
- Add true `ParticleEmitterComponent` hit effects after confirming deployment-target support.
- Add audio feedback.
- Add roughness/metallic material comparison assets.
