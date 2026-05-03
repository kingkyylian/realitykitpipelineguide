# Changelog

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
