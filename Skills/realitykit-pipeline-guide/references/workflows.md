# Workflows

## Asset Import or Texture Work

Use this when the task mentions Blender, USDZ, UVs, texture maps, materials, scale, origin, or asset budgets.

Steps:

1. Define the gameplay need in one sentence.
2. Create or update an asset brief.
3. Update `Tools/asset_manifest.json` with id, file, type, status, budgets, texture maps, and notes.
4. Put final runtime USDZ files in `Assets/Imported`.
5. Keep source art or scripts in `Assets/Source` or `Tools/blender`.
6. Run project generation and build.
7. Verify in RealityKit, not only in Blender.
8. Capture screenshot evidence when visual behavior changed.
9. Add the lesson to `Docs/WORKLOG.md`.

## Gameplay Feature

Use this when the task changes input, scoring, waves, state, HUD, hit detection, VFX, audio, haptics, or reset behavior.

Steps:

1. Start from `Prompts/game-feature-brief.md`.
2. Identify affected state in `GameSession`.
3. Identify affected runtime code in `GameARView`.
4. Keep UI state visible in `ContentView` when it matters to the player.
5. Handle edge cases: duplicate input, duplicate collision, missing asset, reset, and expired temporary entities.
6. Run `make release-check`.
7. Run simulator when player-facing behavior changed.
8. Add a feature brief under `Docs/features` for substantial gameplay changes.

## Documentation or Release Polish

Use this when the task changes README, public onboarding, CI, release notes, guide PDF, or GitHub presentation.

Steps:

1. Keep README focused on the first 10 seconds: what this is, how to run it, where to learn.
2. Keep `Docs/guide.md` as the learning guide.
3. Keep `Docs/production-playbook.md` as the reusable production standard.
4. Regenerate `Docs/pdf/realitykit-pipeline-guide.pdf` when `Docs/guide.md` materially changes.
5. Run CI or equivalent local checks.

## New Game Startup

Use `Docs/new-game-startup.md` when the user wants to start a new RealityKit game based on this repo.

First decisions:

- Player fantasy
- Core action
- Camera style
- Session length
- Main asset classes
- First playable goal

Do not start with hero art. Start with runtime skeleton, procedural placeholders, and one imported asset vertical slice.

