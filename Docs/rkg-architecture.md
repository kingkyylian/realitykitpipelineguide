# RKG Architecture

RKG is the game-factory layer above RKP. RKP owns asset truth; RKG owns game planning, template selection, project generation, and store/QA orchestration.

The architecture goal is to support many small RealityKit game shapes without letting one reference game become the product. Target shooter is a fixture, not the center.

## Boundaries

| Layer | Owns | Must not own |
| --- | --- | --- |
| RKP | Asset manifest, USDZ build/inspect, budgets, screenshot acceptance, release gate. | Game rules, store positioning, archetype choice. |
| RKG | Game idea scoring, GameSpec, archetype registry, project scaffold, reusable gameplay modules, store/QA pack. | Marking assets imported, bypassing RKP acceptance, hiding fallback gaps. |
| Generated game | Runtime loop, generated Swift modules, procedural fallback use, actual gameplay proof. | Tool policy, repo-wide acceptance state. |

## Core Data Flow

```text
idea.json
-> rkg score-idea
-> GameSpec.yaml
-> rkg validate-spec
-> rkg plan-game
-> rkg init-game
-> generated SwiftUI + RealityKit project
-> rkp build/inspect/accept assets
-> rkg verify-game
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

## Asset Role Taxonomy

RKG should reason in roles. RKP can still store asset `type`, but generated games need role semantics.

| Role | Runtime meaning | Required fallback |
| --- | --- | --- |
| `player` | Player-controlled entity or avatar proxy. | Capsule, cube, or sphere with readable material. |
| `target` | Entity that can be hit, tapped, collected, or cleared. | Sphere, ring, or billboard target. |
| `obstacle` | Entity that causes miss, damage, or blocked movement. | Box, wall, cone, or lane marker. |
| `pickup` | Positive collectible or bonus. | Small sphere or gem-like primitive. |
| `projectile` | Launched or moving object. | Small sphere with trail-ready material. |
| `arena` | Floor, lane grid, board, or playfield. | Plane with grid/lane markings. |
| `hazard` | Timed or environmental danger. | Red translucent primitive. |
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
  GameRules.swift
  GameSceneController.swift
  GameView.swift
  AssetLoader.swift
  FallbackFactory.swift
  ResultView.swift
```

Responsibilities:

| File | Responsibility |
| --- | --- |
| `GameState.swift` | Value types for phase, score, timer, attempt, last event. |
| `SessionControl.swift` | Shared playing, reset, and result helpers for generated session lifecycle. |
| `FeedbackState.swift` | Shared last-event display text helper for generated overlays. |
| `InputIntent.swift` | Shared start/reset and primary action button labels for generated overlays. |
| `ScreenshotState.swift` | Typed release screenshot states and evidence paths derived from `release.screenshots`. |
| `GameRules.swift` | Pure scoring, session, spawn, and fail/win rules. |
| `GameSceneController.swift` | RealityKit scene lifecycle and per-archetype loop glue. |
| `GameView.swift` | SwiftUI/RealityKit bridge only. |
| `AssetLoader.swift` | Try accepted/imported USDZ by asset id; report fallback use. |
| `FallbackFactory.swift` | Role-based procedural primitives. |
| `ResultView.swift` | Result summary UI with reset action. |

Current `init-game` writes this module layout. The first implementation keeps gameplay simple, but the ownership boundaries are in place: `GameView` no longer loads assets directly, `GameSceneController` wires all declared asset roles into the scene, `SessionControl` owns shared playing/reset/result primitives and generated result/fail transitions route through `markResult`, `FeedbackState` owns generated last-event display text, `InputIntent` owns generated primary/reset button labels, `ScreenshotState` owns the typed release screenshot state ids, `ResultView` owns the generated result summary/reset overlay, `AssetLoader` owns USDZ loading, and `FallbackFactory` owns role-based procedural primitives. `stack_puzzle` has a playable SwiftUI overlay loop and RealityKit state binding for start, stable/unstable placement, collapse/result, reset, piece count, stable count, piece height/offset feedback, obstacle collapse feedback, result overlay, and scoring. `lane_dodger` has a minimal playable generated loop in SwiftUI and RealityKit state binding: start, drag lane change, dodge frame advance, player/obstacle lane movement, collision/result, reset, score, result overlay, and near-miss state. `wave_defense_lite` has a playable SwiftUI overlay loop and RealityKit state binding for start, fire, damage, wave progression, health/result, threat movement, low-health defender feedback, reset, result overlay, and scoring. `toss_physics` has a playable SwiftUI overlay loop and RealityKit state binding for start, power selection, throw resolution, projectile position, landing/result feedback, attempts, reset, result overlay, and scoring.

The state-bound scene generators share one entity setup helper for the repeated `AssetLoader.loadPrimaryEntity`, initial position, anchor attachment, and first matching role-to-entity-reference binding. Archetype-specific scene controllers now own only their state update formulas and entity reference names.

## CLI Roadmap

| Command | Purpose | First behavior |
| --- | --- | --- |
| `rkg list-archetypes` | Show registry ids and short descriptions. | Text and `--json`. |
| `rkg describe-archetype <id>` | Explain required roles, modules, screenshots, risk. | Text and `--json`. |
| `rkg validate-spec GameSpec.yaml` | Validate GameSpec and archetype support. | Nonzero on invalid. |
| `rkg plan-game GameSpec.yaml` | Print files/modules/assets/screenshots that `init-game` will generate. | Implemented; does not write files. |
| `rkg qa-plan GameSpec.yaml` | Print ordered screenshot capture steps from `screenshot_proofs`. | Text and `--json`; does not write files. |
| `rkg init-game GameSpec.yaml --output <dir>` | Generate project skeleton from registry. | Refuses non-empty output unless `--force`. |
| `rkg verify-game <dir>` | Run generated project tests, RKP doctor/release gate, and optional screenshot checks. | Implemented with command-only verification. |

Current `verify-game` behavior:

- Confirms `GameSpec.json`, `rkp.json`, `project.yml`, and `Tools/asset_manifest.json` exist.
- Runs generated Python tests only when `Tests/test*.py` exists.
- Runs `rkp doctor`.
- Runs `rkp release-check`.
- Stops at the first failing command.

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
      "variable": "targetBasic",
      "position": "[-0.45, 0.00, -1.25]"
    },
    {
      "asset_id": "arena_floor",
      "role": "arena",
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
      "expected_evidence": "Required roles visible: player, obstacle, arena",
      "capture_path": "Docs/screenshots/gameplay_start.jpg",
      "automation": "manual_capture"
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
| Generated modules | Pure rule tests for state transitions, scoring, archetype-specific state/rules, playable overlay loops for `lane_dodger`, `wave_defense_lite`, `toss_physics`, and `stack_puzzle`, plus scene binding tests for archetypes that move RealityKit entities from SwiftUI state. |
| Verification | Missing generated project fails clearly; valid project runs configured checks. |

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

`Docs/store/screenshot-qa.md` sequences the same states in capture order, with the generated interaction cue, expected visible roles, and final screenshot path for each row.

Current `init-game` writes all required store files through `src/rkg/store_pack.py`. `plan-game` includes those files and filtered `screenshot_proofs` in its dry-run output, so store scope and QA proof cues are visible before the project is generated.

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
