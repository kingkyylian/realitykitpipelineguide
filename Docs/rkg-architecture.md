# RKG Architecture

> **Experimental labs architecture:** This document is for maintaining RKG internals. It should not be used as the main product overview. The main product overview is the RKP path in `README.md` and `Docs/cli-tool.md`.

RKG is the game-factory layer above RKP. RKP owns asset truth; RKG owns game planning, template selection, project generation, and store/QA orchestration.

The architecture goal is to support many small RealityKit game shapes without letting one reference game become the product. Target shooter is a fixture, not the center.

RKG can call RKP commands. It cannot mark assets accepted without RKP screenshot evidence.

## Boundaries

| Layer | Owns | Must not own |
| --- | --- | --- |
| RKP | Asset manifest, USDZ build/inspect, budgets, screenshot acceptance, release gate. | Game rules, store positioning, archetype choice. |
| RKG | Game idea scoring, GameSpec, archetype registry, project scaffold, reusable gameplay modules, store/QA pack. | Marking assets imported, bypassing RKP acceptance, hiding fallback gaps. |
| Generated game | Runtime loop, generated Swift modules, procedural fallback use, actual gameplay proof. | Tool policy, repo-wide acceptance state. |

## Core Data Flow

```text
idea.json
-> rkg start-game
   or: rkg score-idea -> rkg new-spec/rkg new-game
-> GameSpec.yaml
-> rkg validate-spec
-> rkg plan-game
-> rkg init-game
-> generated SwiftUI + RealityKit project
-> rkp build/inspect/accept assets
-> rkg verify-game
-> rkg verify-screenshots
-> store pack
```

## Archetype Registry

An archetype is a small template plugin. It describes what the factory should generate, not how assets are accepted.

Registry record:

```json
{
  "id": "lane_dodger",
  "display_name": "Lane Dodger",
  "mechanic": "move between lanes to avoid hazards and collect pickups",
  "input": ["drag", "tap"],
  "camera": ["fixed_non_ar"],
  "required_asset_roles": ["player", "obstacle", "arena"],
  "optional_asset_roles": ["pickup", "ui_prop", "environment"],
  "runtime_modules": ["GameState", "GameRules", "GameSceneController", "AssetLoader", "FallbackFactory"],
  "screenshot_states": ["gameplay_start", "mid_session", "near_miss", "results"],
  "scope_risk": "low"
}
```

Initial registry ids:

| ID | Purpose | First vertical slice |
| --- | --- | --- |
| `target_shooter` | Tap/aim at targets. | Spawn target, tap/hit score, timer, result. |
| `lane_dodger` | Move between lanes. | Player piece, obstacles, collision/miss, distance score. |
| `toss_physics` | Throw or toss objects. | Drag/release, physics arc, landing score. |
| `stack_puzzle` | Place pieces. | Spawn piece, stack/collapse rule, height/result score. |
| `wave_defense_lite` | Survive waves. | Spawn wave, target priority, health/result state. |
| `fighter_2_5d` | Fixed side-view duel. | Attack, dodge, health, combo, guard cue, knockout/result state. |
| `custom_realitykit` | Compose from camera, input, and systems. | Generic player/arena roles plus racing, weapon, enemy, cover, pickup, projectile, or obstacle proof roles. |

## Asset Role Taxonomy

RKG should reason in roles. RKP can still store asset `type`, but generated games need role semantics.

| Role | Runtime meaning | Required fallback |
| --- | --- | --- |
| `player` | Player-controlled entity or avatar proxy. | Capsule, cube, or sphere with readable material. |
| `vehicle` | Vehicle or mount proxy when the player role is not enough to describe the mesh. | Low box chassis with readable direction. |
| `weapon` | Held, mounted, or screen-forward weapon proxy. | Thin metallic box or barrel-like primitive. |
| `enemy` | Non-player threat or target actor. | Contrasting capsule or box. |
| `cover` | Protective geometry or line-of-sight blocker. | Low wall or block. |
| `target` | Entity that can be hit, tapped, collected, or cleared. | Sphere, ring, or billboard target. |
| `opponent` | Opposing character, enemy proxy, or duel target. | Readable box or capsule with contrasting material. |
| `obstacle` | Entity that causes miss, damage, or blocked movement. | Box, wall, cone, or lane marker. |
| `pickup` | Positive collectible or bonus. | Small sphere or gem-like primitive. |
| `projectile` | Launched or moving object. | Small sphere with trail-ready material. |
| `arena` | Floor, lane grid, board, or playfield. | Plane with grid/lane markings. |
| `hazard` | Timed or environmental danger. | Red translucent primitive. |
| `hit_vfx` | Short-lived contact, hit, or score feedback entity. | Small bright sphere or spark proxy. |
| `guard_cue` | Defensive timing, block, or parry readability cue. | Thin panel, ring, or translucent guard marker. |
| `telegraph` | Pre-attack warning or timing lane. | Thin colored strip or warning block. |
| `ui_prop` | 3D score marker, sign, timer prop, or button-like object. | Flat panel or text-safe block. |
| `environment` | Decorative but screenshot-visible set dressing. | Simple backdrop/floor primitive. |

Every role must map to:

- A manifest asset id.
- A generated load attempt.
- A procedural fallback.
- A screenshot state that proves the role is visible or intentionally absent.

## Shared Runtime State Machine

Every generated game should start with this state machine unless an archetype explicitly proves it needs less.

```text
idle
-> countdown
-> playing
-> paused
-> result
-> reset -> idle
```

Required events:

| Event | From | To | Notes |
| --- | --- | --- | --- |
| `start` | `idle`, `result` | `countdown` | Clears session-local state. |
| `countdownFinished` | `countdown` | `playing` | Spawns first playable state. |
| `pause` | `playing` | `paused` | Optional UI, no simulation progression. |
| `resume` | `paused` | `playing` | Restores loop. |
| `sessionEnded` | `playing` | `result` | Time, health, fail, win, or puzzle completion. |
| `reset` | `paused`, `result`, `playing` | `idle` | Deterministic cleanup. |

Required state data:

```json
{
  "phase": "idle",
  "score": 0,
  "elapsed_seconds": 0,
  "session_seconds": 60,
  "attempt": 1,
  "last_event": "none"
}
```

## Generated Swift Module Layout

Generated projects should move away from one large `GameView.swift`. The target layout:

```text
Sources/<GameName>/
  <GameName>App.swift
  ContentView.swift
  GameState.swift
  SessionControl.swift
  FeedbackState.swift
  InputIntent.swift
  ScreenshotState.swift
  CameraRig.swift
  InputController.swift
  SystemFlags.swift
  GameRules.swift
  GameSceneController.swift
  GameView.swift
  AssetLoader.swift
  FallbackFactory.swift
  RuntimeSceneSnapshot.swift
  ResultView.swift
```

Responsibilities:

| File | Responsibility |
| --- | --- |
| `GameState.swift` | Value types for phase, score, timer, attempt, last event. |
| `SessionControl.swift` | Shared playing, reset, and result helpers for generated session lifecycle. |
| `FeedbackState.swift` | Shared last-event display text helper for generated overlays. |
| `InputIntent.swift` | Shared start/reset and primary action button labels for generated overlays. |
| `ScreenshotState.swift` | Typed release screenshot states, launch-state request parsing, and evidence paths derived from `release.screenshots`. |
| `CameraRig.swift` | Spec-selected camera id and compile-safe RealityKit transform contract. |
| `InputController.swift` | Spec-selected input model, input capability booleans, and generated control labels. |
| `SystemFlags.swift` | Spec-selected gameplay systems exposed as Swift booleans and summary text. |
| `GameRules.swift` | Pure scoring, session, spawn, and fail/win rules. |
| `GameSceneController.swift` | RealityKit scene lifecycle and per-archetype loop glue. |
| `GameView.swift` | SwiftUI/RealityKit bridge only. |
| `AssetLoader.swift` | Try accepted/imported USDZ by asset id; report fallback use. |
| `FallbackFactory.swift` | Role- and fallback-id-based procedural primitives. |
| `RuntimeSceneSnapshot.swift` | Writes runtime scene-role metadata during screenshot-state launches. |
| `ResultView.swift` | Result summary UI with reset action. |

Current `init-game` writes this module layout. The first implementation keeps gameplay simple, but the ownership boundaries are in place: `GameView` no longer loads assets directly, `GameSceneController` wires all declared asset roles into the scene, `SessionControl` owns shared playing/reset/result primitives plus generated result visibility, and generated result/fail transitions route through `markResult`. `FeedbackState` owns generated last-event display text, `InputIntent` owns generated primary/reset button labels, `ScreenshotState` owns the typed release screenshot state ids, launch argument/env parsing, and evidence paths, `RuntimeSceneSnapshot` owns runtime scene-role evidence export during screenshot launches, `CameraRig` owns the selected camera id plus a compile-safe transform contract, `InputController` owns selected input capabilities, `SystemFlags` owns selected gameplay-system booleans, `ResultView` owns the generated result summary/reset overlay, `AssetLoader` owns USDZ loading, and `FallbackFactory` owns role- and fallback-id-based procedural primitives. `target_shooter` has a playable SwiftUI overlay loop and RealityKit state binding for start, hit scoring, perfect-hit feedback, finish/result, reset, target movement, result overlay, and scoring. `stack_puzzle` has a playable SwiftUI overlay loop and RealityKit state binding for start, stable/unstable placement, collapse/result, reset, piece count, stable count, piece height/offset feedback, obstacle collapse feedback, result overlay, and scoring. `lane_dodger` has a minimal playable generated loop in SwiftUI and RealityKit state binding: start, drag lane change, dodge frame advance, player/obstacle lane movement, collision/result, reset, score, result overlay, and near-miss state. `wave_defense_lite` has a playable SwiftUI overlay loop and RealityKit state binding for start, fire, damage, wave progression, health/result, threat movement, low-health defender feedback, reset, result overlay, and scoring. `toss_physics` has a playable SwiftUI overlay loop and RealityKit state binding for start, power selection, throw resolution, projectile position, landing/result feedback, attempts, reset, result overlay, and scoring. `fighter_2_5d` has a playable generated side-view duel loop with attack, swipe/tap dodge, damage test input, health, combo, guard meter, knockout/result state, hit VFX role binding, guard cue role binding, compact mobile HUD controls, and launch-state screenshot seeding for `round_start`, `mid_combo`, `perfect_dodge`, and `knockout`. `custom_realitykit` currently generates a composable skeleton with camera/input/system runtime core, fallback-id-driven placeholder meshes, asset briefs, store/QA docs, screenshot-state seeding, runtime scene-role snapshots, and screenshot gates; its system adapters cover racing lane steering, lap/checkpoint state, collision/result proof, vehicle/track/obstacle/checkpoint scene binding, projectile charge/launch/travel/impact proof, FPS/shooter aim/fire/health/cover/enemy proof, collector pickup/timer/combo proof, and camera rig entity binding. Custom adapter state/rules/UI/scene strings live behind `CustomRealityKitRuntimeAdapter` registry entries in `src/rkg/custom_realitykit_runtime.py`, and `rkg list-adapters --json` exposes that registry as a machine-readable capability matrix so docs/tools do not need to infer support from prose.

Generated projects also write `Docs/assets/<asset_id>.md` for every declared role. These are not acceptance records; they are RKP handoff briefs for the later asset import loop.

The state-bound scene generators share one entity setup helper for the repeated `AssetLoader.loadPrimaryEntity`, initial position, anchor attachment, and first matching role-to-entity-reference binding. Archetype-specific scene controllers now own only their state update formulas and entity reference names.

## CLI Roadmap

| Command | Purpose | First behavior |
| --- | --- | --- |
| `rkg start-game <idea>` | Score an idea, infer a starting archetype/camera/input/systems set, scaffold the project, and return the QA plan. | Implemented for fighter, racing, projectile, shooter/FPS-like, and collector keyword routing; refuses non-pass ideas without writing a project. |
| `rkg new-spec <archetype>` | Write a starter GameSpec from a native archetype template. | Implemented for `fighter_2_5d`. |
| `rkg new-game` | Write a composable `custom_realitykit` GameSpec from title, camera, input, and gameplay systems. | Implemented for racing, projectile, shooter/FPS-like, and collector skeletons with early validation. |
| `rkg list-adapters` | Show `custom_realitykit` adapter capability records. | Text and `--json`; exposes systems, generated state/rules, scene properties, and roles. |
| `rkg list-archetypes` | Show registry ids and short descriptions. | Text and `--json`. |
| `rkg describe-archetype <id>` | Explain required roles, modules, screenshots, risk. | Text and `--json`. |
| `rkg validate-spec GameSpec.yaml` | Validate GameSpec and archetype support. | Nonzero on invalid. |
| `rkg plan-game GameSpec.yaml` | Print files/modules/assets/screenshots that `init-game` will generate. | Implemented; does not write files. |
| `rkg qa-plan GameSpec.yaml` | Print ordered screenshot capture steps from `screenshot_proofs`. | Text and `--json`; includes screenshot, sidecar, and scene snapshot paths, and custom RealityKit proof text is adapter-specific when systems select racing, projectile, shooter, or collector. |
| `rkg capture-screenshots <dir>` | Build, install, launch screenshot states, and save simulator captures. | Drives `xcrun simctl`, writes JPEG captures, JSON sidecars, and runtime `.scene.json` role snapshots copied from the app container. |
| `rkg verify-screenshots <dir>` | Verify captured screenshot evidence against a generated project or `qa-plan --json` payload. | Checks file presence, nonzero size, JPEG/PNG header, readable dimensions, sidecar metadata, runtime scene-role snapshot metadata, blank/solid PNG/JPEG evidence, and duplicate visual evidence across states. |
| `rkg init-game GameSpec.yaml --output <dir>` | Generate project skeleton from registry. | Refuses non-empty output unless `--force`. |
| `rkg verify-game <dir>` | Run generated project tests and RKP doctor/release gate. | Implemented with command-only project verification. |

Current `verify-game` behavior:

- Confirms `GameSpec.json`, `rkp.json`, `project.yml`, and `Tools/asset_manifest.json` exist.
- Runs generated Python tests only when `Tests/test*.py` exists.
- Runs `rkp doctor`.
- Runs `rkp release-check`.
- Stops at the first failing command.

Current `verify-screenshots` behavior:

- Accepts `rkg verify-screenshots <generated-project>`.
- If `--plan qa-plan.json` is passed, consumes the machine-readable `rkg qa-plan --json` payload directly.
- If no plan is passed, reads `<generated-project>/GameSpec.json` and rebuilds the QA plan.
- Checks each `capture_path` under the generated project.
- Reports `missing`, `not_file`, `empty`, `invalid_image`, `invalid_dimensions`, `missing_sidecar`, `invalid_sidecar`, `role_evidence_mismatch`, `missing_scene_snapshot`, `invalid_scene_snapshot`, `scene_role_mismatch`, `blank_or_solid`, `duplicate_visual_evidence`, or `ok`.
- Accepts JPEG and PNG image headers only when the file carries readable dimensions of at least 300x300 pixels.
- Requires a JSON sidecar next to every valid planned screenshot. The sidecar must match the QA plan game id, state, automation hint, visible roles, and point at a runtime scene snapshot.
- Requires `Docs/screenshots/<state>.scene.json` runtime evidence copied from the generated app container. The snapshot must match the state and include the expected asset roles bound in the running RealityKit scene.
- For 8-bit RGB/RGBA PNG captures, reconstructs filtered scanlines, samples pixels, and rejects near-solid images as `blank_or_solid`.
- On macOS, uses `sips` to rasterize JPEG captures into the same sampler. A malformed dimension-bearing JPEG is `invalid_image`; a near-solid JPEG is `blank_or_solid`.
- If two planned states produce the same sampled visual fingerprint, the later state is `duplicate_visual_evidence`.
- Exits nonzero when any planned screenshot evidence is missing or invalid.

Current `plan-game --json` shape:

```json
{
  "game_id": "ring_dash",
  "display_name": "Ring Dash",
  "swift_name": "RingDash",
  "archetype": {
    "id": "target_shooter"
  },
  "files": [
    "GameSpec.json",
    "rkp.json",
    "Tools/asset_manifest.json",
    "project.yml",
    "Sources/RingDash/GameState.swift"
  ],
  "asset_roles": {
    "target_basic": "target",
    "arena_floor": "arena"
  },
  "runtime_entities": [
    {
      "asset_id": "target_basic",
      "role": "target",
      "fallback": "procedural_rings",
      "variable": "targetBasic",
      "position": "[-0.45, 0.00, -1.25]"
    },
    {
      "asset_id": "arena_floor",
      "role": "arena",
      "fallback": "procedural_grid",
      "variable": "arenaFloor",
      "position": "[0, -0.45, 0]"
    }
  ],
  "screenshot_states": ["gameplay_start", "mid_session", "results"],
  "screenshot_proofs": {
    "gameplay_start": "Tap Start; state.phase == .playing; target and arena are visible.",
    "mid_session": "Tap Start, then score at least one hit; state.score > 0.",
    "results": "End the session or reset after play; state.phase == .result or result UI is visible."
  }
}
```

Current `qa-plan --json` shape:

```json
{
  "game_id": "lane_dash",
  "display_name": "Lane Dash",
  "archetype": "lane_dodger",
  "preflight": ["rkg verify-game <generated-project>"],
  "capture_root": "Docs/screenshots",
  "steps": [
    {
      "order": 1,
      "state": "gameplay_start",
      "screenshot_state_case": "gameplayStart",
      "drive": "Tap Start; state.phase == .playing; runner, obstacle, and arena are visible.",
      "visible_roles": ["player", "obstacle", "arena"],
      "expected_evidence": "Declared roles available: player, obstacle, arena",
      "capture_path": "Docs/screenshots/gameplay_start.jpg",
      "sidecar_path": "Docs/screenshots/gameplay_start.json",
      "scene_snapshot_path": "Docs/screenshots/gameplay_start.scene.json",
      "automation": "manual_capture"
    }
  ]
}
```

For `fighter_2_5d` and `custom_realitykit`, the automation field is `launch_arg --rkg-screenshot-state <state>` because those generated apps can seed release screenshot states during launch. `custom_realitykit` proof text comes from the selected system adapter when possible.

Current `verify-screenshots --json` shape:

```json
{
  "game_id": "lane_dash",
  "display_name": "Lane Dash",
  "archetype": "lane_dodger",
  "ok": false,
  "checks": [
    {
      "order": 1,
      "state": "gameplay_start",
      "capture_path": "Docs/screenshots/gameplay_start.jpg",
      "status": "missing",
      "bytes": 0
    }
  ]
}
```

## Verification Matrix

Every new RKG feature should prove the smallest useful behavior.

| Area | Required tests |
| --- | --- |
| Registry | Known archetypes list, unknown archetype error, JSON output shape. |
| GameSpec | Required fields, supported archetype, supported input/camera, valid roles, screenshot states. |
| Required roles | Every selected archetype `required_asset_roles` entry must appear in `assets.<id>.role`. |
| Planning | `plan-game` prints files, modules, assets, screenshots without writing output. |
| Scaffolding | Generated files exist, Swift literals escape correctly, screenshot states become typed Swift cases, every declared asset role gets a generated load attempt with fallback. |
| Generated modules | Pure rule tests for state transitions, scoring, archetype-specific state/rules, playable overlay loops for `target_shooter`, `lane_dodger`, `wave_defense_lite`, `toss_physics`, `stack_puzzle`, and `fighter_2_5d`, plus scene binding tests for archetypes that move RealityKit entities from SwiftUI state. |
| Verification | Missing generated project fails clearly; valid project runs configured checks. |
| Screenshot evidence | `verify-screenshots` reports missing/empty/invalid image evidence, requires matching JSON sidecars and runtime scene-role snapshots, rejects blank/solid PNG/JPEG captures, rejects duplicate visual evidence across states, and accepts captured JPEG/PNG files at planned paths. |

## Store Pack Contract

Generated store docs should be honest drafts, never marketing filler.

Required files:

```text
Docs/store/metadata.md
Docs/store/review-notes.md
Docs/store/privacy.md
Docs/store/screenshots.md
Docs/store/screenshot-qa.md
Docs/store/monetization.md
```

Required screenshot rows:

| Field | Meaning |
| --- | --- |
| `state` | Screenshot state from archetype registry or GameSpec. |
| `purpose` | What App Store reviewer/player should see. |
| `generated_proof_cue` | The generated interaction or state value that proves the screenshot is real gameplay. |
| `required_asset_roles` | Roles that must be visible or explained. |
| `evidence_path` | `Docs/screenshots/<state>.jpg` once captured. |

`Docs/store/screenshot-qa.md` sequences the same states in capture order, with the generated interaction cue, expected visible roles, and final screenshot path for each row. It tells QA to run `rkg verify-game` before capture and `rkg verify-screenshots .` after capture.

Current `init-game` writes all required store files through `src/rkg/store_pack.py`. `plan-game` includes those files and filtered `screenshot_proofs` in its dry-run output, so store scope and QA proof cues are visible before the project is generated. `verify-screenshots` is the current post-capture evidence gate; simulator-driving automation should write files that satisfy this command.

## Decision Rules

Add a new archetype only when:

- It can reach a first playable with 3 to 5 asset roles.
- It uses the shared state machine or documents the smaller machine it needs.
- It adds no more than two new role types.
- It has at least three screenshot states.
- It has a clear App Review risk note.
- It can be verified without network services or multiplayer in v1.

Deepen a single archetype only when the work improves either:

- Shared runtime modules.
- Shared asset role/fallback behavior.
- Shared verification/store-pack behavior.
- A registry template that does not leak policy into RKP.
