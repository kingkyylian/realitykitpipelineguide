# Game Feature Brief Template

Use this before asking an AI agent or teammate to implement gameplay, asset, VFX, UI, or pipeline work.

## Feature

Name:

One-sentence player value:

## Current State

What exists now:

Relevant files:

Known constraints:

## Desired Behavior

Player action:

Runtime response:

UI/HUD response:

Audio/haptic/VFX response:

Failure or miss behavior:

Reset behavior:

## Asset Contract

New or changed asset ids:

USDZ paths:

Texture paths:

Scale/origin notes:

Collision notes:

Fallback behavior:

## Acceptance Criteria

- [ ] `make release-check` passes.
- [ ] Simulator behavior tested.
- [ ] Screenshot or video captured if visual.
- [ ] `Tools/asset_manifest.json` updated if assets changed.
- [ ] `Docs/WORKLOG.md` lesson added.
- [ ] README/guide updated if public behavior changed.

## Edge Cases

- Duplicate input:
- Duplicate collision:
- Missing asset:
- Old simulator cache:
- Small-screen UI:
- Performance risk:

## Notes for AI Agents

Keep changes scoped. Do not remove fallbacks unless the task explicitly says so. Prefer deterministic test behavior while the feature is being taught.

