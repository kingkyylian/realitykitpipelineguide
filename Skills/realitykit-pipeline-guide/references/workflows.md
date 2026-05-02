# Workflows

## Asset Import or Texture Work

Use this when the task mentions Blender, USDZ, UVs, texture maps, materials, scale, origin, or asset budgets.

Before any asset work, verify:

```bash
test -f Tools/rkp.py && test -f Tools/asset_manifest.json
```

If this fails, stop. Do not create a minimal replacement pipeline. Ask the user to move into the RKP repo, clone the template, or explicitly request a bootstrap.

Steps:

1. Define the gameplay need in one sentence.
2. Prefer `python3 Tools/rkp.py make-asset <asset_id> --type <asset_type> --prompt "<brief>"` for prompt-backed assets. Use `new-asset` only when the asset should start from a blank contract.
3. Edit the asset brief and Blender starter script.
4. Build the USDZ with `python3 Tools/rkp.py build-asset <asset_id>`.
5. Update `Tools/asset_manifest.json` notes, but keep `status: planned` until visual acceptance.
6. Put final runtime USDZ files in `Assets/Imported`.
7. Keep source art or scripts in `Assets/Source` or `Tools/blender`.
8. Run project generation and build.
9. Verify in RealityKit, not only in Blender.
10. Capture screenshot evidence when visual behavior changed.
11. Accept the asset with `python3 Tools/rkp.py accept-asset <asset_id> --screenshot <path>`.
12. Add any extra lesson to `Docs/WORKLOG.md`.

## Gameplay Feature

Use this when the task changes input, scoring, waves, state, HUD, hit detection, VFX, audio, haptics, or reset behavior.

Steps:

1. Start from `Prompts/game-feature-brief.md`.
2. Identify affected state in `GameSession`.
3. Identify affected runtime code in `GameARView`.
4. Keep UI state visible in `ContentView` when it matters to the player.
5. Handle edge cases: duplicate input, duplicate collision, missing asset, reset, and expired temporary entities.
6. Run `python3 Tools/rkp.py release-check`.
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
