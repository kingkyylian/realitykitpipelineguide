# Changelog

## Unreleased

### Added

- `rkg` RealityKit game-factory CLI surface for idea scoring, archetype discovery, spec validation, game planning, project scaffolding, generated game verification, and store-pack checklist generation.
- Archetype registry for `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, and `wave_defense_lite`.
- Config-aware generated game projects with shared Swift modules: `GameState`, `GameRules`, `GameSceneController`, `GameView`, `AssetLoader`, `FallbackFactory`, and result/UI surfaces.
- Required asset-role validation and runtime entity planning for generated games.
- Minimal playable generated loops for `lane_dodger`, `wave_defense_lite`, `toss_physics`, and `stack_puzzle`.
- RealityKit state-to-scene binding for the generated `lane_dodger` and `toss_physics` archetypes.

### Changed

- Split growing RKG Swift string emitters out of `src/rkg/scaffold.py` into focused runtime/content-view generation modules.
- Hardened RKP release and asset verification gates with USDZ inspection, direct USDZ fallback handling, Blender diagnostics, and safer cleanup support.
- Clarified the multi-archetype RKG scope so target shooter remains one fixture, not the whole product.

### Verified

- `/opt/homebrew/bin/python3.12 Tools/rkp.py release-check`
- `/opt/homebrew/bin/python3.12 -m unittest discover -s Tests`
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
