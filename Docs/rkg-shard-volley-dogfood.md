# RKG Shard Volley Dogfood

This is the first broad `custom_realitykit` dogfood run that starts from a game idea, scores it, generates a GameSpec, initializes a RealityKit project, verifies the generated build, captures simulator screenshots, and records the tool gaps found along the way.

## Test Game

`Shard Volley` is a projectile/shooting/score prototype:

- Camera: `third_person`
- Input: `drag`
- Systems: `projectile,shooting,score`
- Core action: aim, charge, and launch a shard at a target lane
- First playable assets: player launcher, shard projectile, target ring, arena

## Commands Run

```bash
rtk ./.venv/bin/python Tools/rkg.py score-idea Build/rkg-dogfood-shard-volley/idea.json --json
rtk ./.venv/bin/python Tools/rkg.py list-adapters
rtk ./.venv/bin/python Tools/rkg.py new-game --title "Shard Volley" --camera third_person --input drag --systems projectile,shooting,score --output Build/rkg-dogfood-shard-volley/GameSpec.json
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-dogfood-shard-volley/GameSpec.json --json
rtk ./.venv/bin/python Tools/rkg.py plan-game Build/rkg-dogfood-shard-volley/GameSpec.json --json
rtk ./.venv/bin/python Tools/rkg.py qa-plan Build/rkg-dogfood-shard-volley/GameSpec.json --json
rtk ./.venv/bin/python Tools/rkg.py init-game Build/rkg-dogfood-shard-volley/GameSpec.json --output Build/rkg-dogfood-shard-volley/ShardVolley --force
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-dogfood-shard-volley/ShardVolley
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-dogfood-shard-volley/ShardVolley --device booted
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-dogfood-shard-volley/ShardVolley --json
```

## Evidence

Generated screenshot evidence was copied from the generated project into the root docs screenshot area:

| State | Evidence |
| --- | --- |
| `gameplay_start` | `Docs/screenshots/rkg_shard_volley_gameplay_start.jpg` |
| `mid_action` | `Docs/screenshots/rkg_shard_volley_mid_action.jpg` |
| `fail_or_hit` | `Docs/screenshots/rkg_shard_volley_fail_or_hit.jpg` |
| `results` | `Docs/screenshots/rkg_shard_volley_results.jpg` |

`verify-screenshots` returned `ok: true` for all four generated screenshot files.

## What Worked

- `score-idea` accepted the idea with score `100` and verdict `pass`.
- `list-adapters` exposed the expected adapter matrix: racing, projectile, shooter, collector.
- `new-game` produced a valid `custom_realitykit` spec with player, arena, weapon, projectile, and target roles.
- `plan-game` listed the expected Swift modules, store docs, asset roles, runtime entities, and screenshot states.
- `init-game` generated a complete XcodeGen-based RealityKit project.
- `verify-game` passed for the generated `ShardVolley` project.
- `capture-screenshots` built, installed, launched all screenshot states on a booted simulator, and wrote four JPEG files.
- `verify-screenshots` validated all four files.

## Bugs Found And Fixed

The dogfood run found two product bugs:

- `score` was treated as enough to activate the collector adapter UI. Projectile games that included `score` also showed collector controls. Fix: collector adapter dispatch and UI now use `SystemFlags.hasCollect || SystemFlags.hasTimer`; score remains a shared scoring flag.
- The first screenshot could be captured before the launched app was visually settled. Fix: `capture-screenshots` now waits 2 seconds after each launch by default.

## Remaining Gaps For A Comprehensive Tool

1. `score-idea` and `new-game` are still separate manual commands. A comprehensive flow needs an orchestrator that can turn an accepted idea into a suggested camera/input/systems set and a generated project path.
2. `qa-plan` proof text is still archetype-level for `custom_realitykit`; projectile screenshots should say exactly what state values or controls prove `charge`, `launch`, `hit`, and `result`.
3. Screenshot verification checks file validity, not visual quality. It should catch blank screenshots, previous-app captures, major text overlap, and missing declared roles.
4. Generated UI is functional but not polished. On iPhone screenshots, the overlay is large and covers too much of the scene.
5. Generated fallback art is useful for proof, but not enough for production. The next bridge should turn each asset brief into `rkp make-asset` / `build-asset` / `accept-asset` tasks.
6. Adapter conflict rules need more coverage. `score` overlapping with collector was one example; future shared systems like `physics`, `timer`, `health`, or `enemy_ai` need explicit ownership rules.
7. There is no safe regeneration story for hand-edited generated projects. The tool can create a project, but it does not preserve user edits or apply structured patches yet.
8. Store metadata is draft-quality. It creates a checklist, but product-specific copy, privacy text, pricing notes, and App Review notes still require human pass.
9. Game tuning is shallow. We need spec-driven knobs for session length, target counts, win thresholds, score values, spawn timing, and difficulty ramps.
10. The generated project has no imported art path by default. A real 0-to-first-playable path should include at least one accepted USDZ asset with screenshot evidence.

## Next Slice

The next highest-value RKG slice is adapter-specific QA proof plus visual screenshot QA:

- Add `CustomRealityKitRuntimeAdapter` fields for screenshot proof text.
- Make `qa-plan` use adapter-specific proof when systems select an adapter.
- Add screenshot checks for blank image, wrong app capture, and basic content presence.
- Keep the Shard Volley dogfood flow as the regression example.
