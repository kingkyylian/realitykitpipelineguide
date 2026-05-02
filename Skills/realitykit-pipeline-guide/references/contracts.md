# Contracts and Gates

## Asset Contract

Every imported asset needs:

- `asset_id` in `snake_case`
- Runtime path: `Assets/Imported/<asset_id>.usdz`
- Manifest entry in `Tools/asset_manifest.json`
- Scale statement
- Origin/pivot statement
- UV/material statement
- Texture budget
- Collision expectation
- Fallback behavior
- Runtime screenshot evidence when visual

## Gameplay Contract

Every gameplay feature needs:

- Player action
- Runtime response
- HUD/UI response when relevant
- Hit/miss/reset behavior
- Duplicate event handling
- Temporary entity cleanup
- Verification command
- Simulator check for player-facing behavior

## Public Repo Gate

Before calling a public milestone ready:

- README quick start uses public commands.
- `rtk` or local wrappers are explained as non-dependencies.
- `make release-check` passes locally.
- GitHub Actions CI is green.
- Screenshots referenced by README/guide exist.
- `Docs/WORKLOG.md` records important lessons.
- `Docs/ai-handoff.md` is not stale.
- Release notes match the current milestone.

## Definition of Done

Code-only fix:

- Build passes.
- Behavior verified.
- Worklog updated if the bug teaches a reusable lesson.

Imported asset:

- Manifest updated.
- USDZ added.
- Loader path verified.
- Screenshot captured if visual.
- Worklog note written.

Gameplay feature:

- Build passes.
- Simulator behavior tested.
- UI language explains player progress.
- Feature brief exists if the change is substantial.

