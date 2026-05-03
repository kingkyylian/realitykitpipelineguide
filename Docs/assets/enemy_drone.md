# Asset Brief: enemy_drone

## Purpose

Gameplay purpose: prompt-backed drone target used to prove the asset pipeline can create, build, accept, and document a non-default gameplay target.

## Runtime Contract

- Asset id: `enemy_drone`
- Type: `gameplay_target`
- Runtime USDZ path: `Assets/Imported/enemy_drone.usdz`
- Fallback behavior: the demo fixture keeps its existing target fallback order and does not switch to this asset by default.
- Collision expectation: accepted as a visual/pipeline asset; gameplay collision tuning is a future fixture task if the drone becomes an active target.

## Blender Contract

- Approximate size in meters: compact target-scale drone draft.
- Origin/pivot: centered for fixture placement.
- Forward/up orientation: authored for RealityKit import and screenshot verification.
- Triangle budget: max 1500.
- Texture budget: max 1024, first pass base color.
- UV primvar: `st`.
- Material count: one base-color material target.

## Acceptance Criteria

- [x] USDZ exported to `Assets/Imported/enemy_drone.usdz`.
- [x] `Tools/asset_manifest.json` status changed from `planned` to `imported`.
- [x] `make doctor` passes without new errors.
- [x] `make release-check` passes.
- [x] Simulator screenshot captured if visual.
- [x] `Docs/WORKLOG.md` lesson added.

## Prompt Source

```text
red bullseye drone target
```

## Prompt Pipeline Notes

- Inferred archetype: `drone`
- Generated through `python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt ...`.
- Treat the Blender script as a first procedural draft, not final art direction.
- Build creates USDZ; acceptance still requires simulator screenshot evidence.

## Evidence

![Accepted enemy_drone](../screenshots/enemy_drone_imported.jpg)
