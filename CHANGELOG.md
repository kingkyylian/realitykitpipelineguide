# Changelog

## v0.1.0 - Public learning pipeline preview

### Added

- SwiftUI + RealityKit playable prototype.
- Procedural target and arena fallbacks.
- Imported `target_basic.usdz`.
- Imported textured `target_basic_textured.usdz`.
- Imported `arena_floor.usdz`.
- Ring-based scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- Asset manifest with budgets and learning notes.
- Blender starter script for arena floor generation.
- Public guide PDF, screenshots, release checklist, CI, contribution templates, and Makefile.

### Verified

- `make release-check`
- manifest validation
- XcodeGen project generation
- iOS simulator build
- simulator screenshot evidence under `Docs/screenshots`

### Known next steps

- Add a README demo GIF.
- Add target-generation Blender scripts.
- Add hit VFX and audio feedback.
- Add roughness/metallic material comparison assets.
