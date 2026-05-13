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

Latest game-shell/semantic QA evidence:

| State | Evidence |
| --- | --- |
| `gameplay_start` | `Docs/screenshots/rkg_shard_volley_v7_gameplay_start.jpg` |
| `mid_action` | `Docs/screenshots/rkg_shard_volley_v7_mid_action.jpg` |
| `fail_or_hit` | `Docs/screenshots/rkg_shard_volley_v7_fail_or_hit.jpg` |
| `results` | `Docs/screenshots/rkg_shard_volley_v7_results.jpg` |

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

The follow-up QA slice closed three of the gaps from this run:

- `qa-plan` now uses adapter-specific proof text for `custom_realitykit`; projectile plans call out charge, launch, hit, and result state values instead of generic archetype prose.
- `custom_realitykit` screenshot states now advertise launch-state automation with `--rkg-screenshot-state <state>`.
- `verify-screenshots` rejects valid-dimensional PNG evidence that is visually blank or near-solid via `blank_or_solid`, and generated custom overlays use smaller controls/padding for screenshot readability.
- `verify-screenshots` also samples JPEG evidence through `sips`, rejects malformed dimension-bearing JPEG files as `invalid_image`, rejects blank/solid JPEG captures, and rejects duplicate visual evidence across release states as `duplicate_visual_evidence`.
- `capture-screenshots` now writes screenshot sidecars, and `verify-screenshots` requires those sidecars to match the planned game id, state, automation hint, and visible roles.
- Generated apps now write runtime scene-role snapshots during screenshot launches; `capture-screenshots` copies them as `Docs/screenshots/<state>.scene.json`, and `verify-screenshots` requires the expected roles to appear as enabled, positioned `rkg|...` entities with measurable visual bounds in that running RealityKit scene metadata.
- `start-game` now closes the manual orchestration gap by scoring an idea, choosing camera/input/systems, writing the GameSpec, scaffolding the project, and returning the QA plan in one command.
- `start-game --json` now returns `asset_pipeline.tasks`, which maps every generated asset brief to ordered RKP command arrays: `make-asset`, `build-asset`, `inspect-usdz --json`, and `accept-asset --screenshot`.
- One emitted `asset_pipeline` task was dogfooded through RKP acceptance: `target_proxy` was built as `Assets/Imported/target_proxy.usdz`, inspected, loaded into the generated app screenshot flow, accepted with `Docs/screenshots/target_proxy_imported.jpg`, and verified by `rkp release-check --assets`.
- The dogfood run fixed RKG brief checklist drift: `accept-asset` now checks the RKG manifest/screenshot/acceptance lines, and checks the generated inspect line when the current USDZ also passes inspection.
- `accept-first-asset` now wraps the repeated bridge steps: it chooses the first gameplay-relevant asset, runs the RKP make/build/inspect commands, captures and verifies generated screenshots, copies the selected state screenshot to the asset acceptance path, runs `accept-asset`, and finishes with `release-check --assets`. It skips the prompt/make step when the Blender script already exists, so repeat runs can resume.
- Fresh generated projects now include `xcodegen generate` in the screenshot capture flow when `project.yml` exists, so `capture-screenshots` can build from a clean scaffold without a manually generated `.xcodeproj`.
- The local acceptance runner now dispatches `rkp` and `rkg` workflow steps through workspace Python modules with the workspace `src` path in `PYTHONPATH`, which prevents dogfood runs from accidentally exercising an older installed binary.
- The first polished demo slice regenerated `Build/rkg-polished-demo-v2/ShardVolleyStart`, built a 288-triangle `target_proxy` bullseye asset with a 512x512 base-color texture and `st` UVs, accepted it from the `fail_or_hit` screenshot, verified all four screenshot states, and passed `rkp release-check --assets`.
- `accept-assets` now runs the same bridge for multiple assets with one screenshot capture and one release-check. The full demo slice regenerated `Build/rkg-full-demo-v1/ShardVolleyStart` and accepted `player_proxy`, `arena_space`, `weapon_proxy`, `projectile_proxy`, and `target_proxy`; all five were imported, stayed under budget, had 512x512 base-color textures, had `st` UVs, and ended `ready` in RKP status.
- The game-skeleton presentation pass regenerated `Build/rkg-proper-skeleton-v6/ShardVolleyStart` from the Shard Volley idea and moved generated `custom_realitykit` apps away from the gray dev overlay: full-screen game shell, start overlay, compact HUD, icon projectile controls, `WorldRig.swift` lighting/backdrop/arena lanes/projectile feedback, neutral `procedural_capsule` fallback, projectile composition tuning, and result-only panel. `verify-game`, `capture-screenshots`, and `verify-screenshots --json` passed for all four states.
- The semantic visual QA pass regenerated `Build/rkg-proper-skeleton-v7/ShardVolleyStart`; `qa-plan` now emits `semantic_visual_contract`, `verify-screenshots` rejects `semantic_debug_overlay`, `semantic_flat_scene`, and `semantic_scene_too_dark`, and generated `custom_realitykit` controllers subscribe to `SceneEvents.Update` to drive `WorldRig.updateIdleMotion`. `verify-game`, `capture-screenshots`, and `verify-screenshots --json` passed for all four states.
- The first bottom-occlusion pixel gate extends `semantic_visual_contract` with a bottom-band light-coverage check. `verify-screenshots` now reports `semantic_control_occlusion` when a large bright control/tutorial panel consumes the bottom gameplay area while still allowing compact bottom controls.
- The first center-occlusion pixel gate extends the same contract with center-band light coverage. `verify-screenshots` now reports `semantic_center_occlusion` when a large bright modal/tutorial panel covers the middle of active gameplay, while result-like states such as `results`, `collision`, and `knockout` keep room for legitimate result panels.

## Remaining Gaps For A Comprehensive Tool

1. Screenshot verification has a first semantic visual contract. It now catches blank/solid PNG/JPEG evidence, duplicate state captures, missing/mismatched sidecars, declared-role metadata mismatches, missing/mismatched runtime scene-role snapshots, disabled expected scene roles, malformed role position metadata, missing/zero visual bounds metadata, debug-overlay-like top panels, bottom control-panel occlusion, center modal occlusion, flat scene bands, and too-dark scene bands. It still does not prove via pixels that each declared mesh is visible or perform OCR-level text-overlap analysis.
2. Generated UI now has a first game-shell pass for `custom_realitykit`, but broader iPhone/iPad layout review and targeted text-overlap checks are still needed before any shipping claim.
3. Generated fallback art is useful for proof, but not enough for production. The full demo now has imported first-pass player, arena, weapon, projectile, and target assets, and fallback composition is less noisy, but VFX, animation, silhouette readability, and broader product polish still need dedicated passes.
4. Adapter conflict rules need more coverage. `score` overlapping with collector was one example; future shared systems like `physics`, `timer`, `health`, or `enemy_ai` need explicit ownership rules.
5. There is no safe regeneration story for hand-edited generated projects. The tool can create a project, but it does not preserve user edits or apply structured patches yet.
6. Store metadata is draft-quality. It creates a checklist, but product-specific copy, privacy text, pricing notes, and App Review notes still require human pass.
7. Game tuning is shallow. We need spec-driven knobs for session length, target counts, win thresholds, score values, spawn timing, and difficulty ramps.
8. The generated project now has a proven multi-asset imported-art path. The remaining gap is not acceptance mechanics, but visual quality gates that prove the imported art is readable and well-composed in pixels.

## Next Slice

The next highest-value RKG slice is stricter visual QA plus richer feedback polish:

- Extend screenshot QA from runtime visual bounds metadata toward pixel-level target visibility and OCR-level text-overlap checks.
- Continue the demo polish pass: stronger hit VFX, launch/charge animation, sound/haptics hooks, and screenshot semantic checks for asset visibility.
