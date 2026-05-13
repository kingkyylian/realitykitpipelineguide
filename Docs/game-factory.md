# RealityKit Game Factory

> **Experimental labs:** RKG explores game-factory workflows on top of the RKP asset pipeline. It is not the main product, not a finished app factory, and not the default path for contributors. Use RKP first unless the task explicitly asks for generated games, archetypes, store packs, or RKG screenshot QA.

This document defines how to turn the asset pipeline into a repeatable commercial game workflow.

For executable architecture details, use `Docs/rkg-architecture.md`. This page stays high-level; the architecture doc owns registry, role, runtime module, CLI, verification, and store-pack contracts.

## Principle

RKP remains the stable RealityKit asset pipeline. RKG is the experimental labs layer above it.

RKP owns:

- Asset manifest entries.
- Blender and USDZ generation.
- Asset budgets.
- Procedural fallbacks.
- USDZ inspection.
- Runtime screenshot acceptance.
- Release checks.

RKG owns:

- Game specs.
- Archetype templates.
- Reusable gameplay modules.
- QA orchestration.
- Store metadata packs.
- Variant review.

RKG can call RKP commands. It cannot mark assets accepted without RKP screenshot evidence.

## Product Scope

RKG is not a target-shooter generator. It is the experimental game-factory layer for small RealityKit projects.

Maturity boundary:

- RKP is the more stable product surface today.
- RKG can score ideas, validate specs, scaffold fixed-camera projects, generate store/QA docs, and verify generated projects.
- RKG is not yet a finished commercial game factory. Generated projects still need human product review, visual QA, screenshots, App Store metadata review, and production polish before shipping.

The target-shooter fixture is only the first reference archetype because it is easy to verify: one input, clear scoring, simple assets, and screenshot-friendly states. Do not let that fixture shape the product boundary. Any RKG feature should either support multiple archetypes directly or improve the shared factory layer that every archetype needs.

Shared factory layer:

- Game idea scoring.
- GameSpec validation.
- Project scaffolding.
- Asset role mapping.
- Procedural fallback contracts.
- Reusable Swift gameplay modules.
- Generated-project verification.
- Screenshot and store-pack orchestration.

Archetype-specific templates sit under that layer. They are plugins, not the product.

## Anti-Spam Rule

Each shipped game must be meaningfully distinct. A new app must change at least one of these:

- Core mechanic.
- Input model.
- Progression.
- Audience fantasy.
- Level structure.
- Content depth.
- Art direction tied to readability and game feel.

Palette swaps, renamed enemies, new icons, or one exchanged mesh are not enough for a separate app. Those belong in the original app as updates, level packs, or in-app purchases.

## Factory Gates

### 1. Idea Score

Score the idea before generating a project.

Required answers:

- What does the player do every 3 seconds?
- What makes this different from the previous game?
- Can the first playable ship with 3 to 5 asset classes?
- Can a 30-second video explain the hook?
- What is the App Review risk?
- What is the monetization model?

Reject ideas that need multiplayer, open worlds, heavy character animation, user-generated content, or backend systems in the first version.

Machine gate:

```bash
python3 Tools/rkg.py score-idea idea.json
```

Minimum idea file:

```json
{
  "idea": {
    "title": "Ring Dash",
    "player_action": "tap moving targets every few seconds",
    "differentiator": "precision rings shrink as the streak grows",
    "first_playable_assets": ["target_basic", "arena_floor", "timer_gate"],
    "video_hook": "a thirty-second clip shows shrinking rings, streaks, and the result screen",
    "app_review_risk": "low",
    "monetization": "paid",
    "scope_flags": []
  }
}
```

`score-idea` returns `pass`, `revise`, or `reject`. Rejected ideas should not reach `rkg init-game`.

For the shortest zero-to-skeleton path, let RKG score the idea, infer the starting runtime shape, scaffold the project, and return the QA plan:

```bash
python3 Tools/rkg.py start-game idea.json --output GeneratedGame --json
```

`start-game` refuses `revise` or `reject` ideas without writing a project. For `pass` ideas it chooses a native archetype or `custom_realitykit` camera/input/systems recommendation from the idea text, writes `GameSpec.json`, initializes the generated project, and prints score, recommendation, paths, `qa_plan`, and `asset_pipeline` in one JSON payload.

The `asset_pipeline` section is the bridge back to RKP. It does not accept assets or mark art imported. It lists the generated project working directory and one task per declared asset role, including the brief path, runtime USDZ path, acceptance screenshot path, and ordered `rkp make-asset`, `rkp build-asset`, `rkp inspect-usdz --json`, and `rkp accept-asset --screenshot ...` command arrays.

The first dogfood bridge accepted `target_proxy` from the generated `Shard Volley Start` project. The useful sequence was: run the task's `make-asset`, `build-asset`, and `inspect-usdz --json`; capture generated gameplay screenshots; verify the screenshots; copy the relevant state screenshot to the task's `screenshot_path`; run `accept-asset`; then run `rkp release-check --assets` from the generated project root.

Use `accept-first-asset` to run that sequence as one workflow:

```bash
python3 Tools/rkg.py accept-first-asset GeneratedGame --dry-run --json
python3 Tools/rkg.py accept-first-asset GeneratedGame --device booted --json
```

By default it chooses the highest-priority gameplay role, such as `target` before background or arena roles. It skips the prompt/make step when the generated Blender script already exists, so it can resume a partially completed run. Use `--asset-id <id>` for a specific role and `--source-state <state>` when the best acceptance screenshot is not the default state.

The fresh `Shard Volley Start` demo dogfood uses this path end to end. `accept-first-asset` produced a 288-triangle, 512x512-textured bullseye `target_proxy`, captured the four release screenshots, copied `fail_or_hit.jpg` to `target_proxy_imported.jpg`, accepted the asset, and finished `rkp release-check --assets`. During execution the runner keeps the plan readable as `rkp`/`rkg` commands, but dispatches those entrypoints through the workspace modules (`python -m rkp.cli` / `python -m rkg.cli`) with the workspace `src` path in `PYTHONPATH`, so dogfood exercises the current source tree instead of an older installed binary.

Use `accept-assets` when the goal is a fuller generated demo rather than a single proof asset:

```bash
python3 Tools/rkg.py accept-assets GeneratedGame --dry-run --json
python3 Tools/rkg.py accept-assets GeneratedGame --device booted --json
```

It builds and inspects each selected asset, captures the release screenshot states once, verifies them once, copies the best state screenshot to each asset's acceptance evidence path, accepts each asset through RKP, and finishes with one `rkp release-check --assets`. The full `Shard Volley Start` dogfood accepted `player_proxy`, `arena_space`, `weapon_proxy`, `projectile_proxy`, and `target_proxy`; all five ended `imported` and `ready`.

For lower-level control, either start from a native archetype template or compose a generic RealityKit skeleton manually:

```bash
python3 Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output GameSpec.json
python3 Tools/rkg.py new-spec flappy_side_scroller --title "Flappy Reef" --output GameSpec.json
python3 Tools/rkg.py validate-spec GameSpec.json
python3 Tools/rkg.py plan-game GameSpec.json
python3 Tools/rkg.py qa-plan GameSpec.json
```

```bash
python3 Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output GameSpec.json
python3 Tools/rkg.py validate-spec GameSpec.json
python3 Tools/rkg.py plan-game GameSpec.json
python3 Tools/rkg.py qa-plan GameSpec.json
```

`plan-game` is a dry run. It lists generated files, asset roles, and screenshot states without creating the output directory. Generated projects include `SessionControl.swift` for shared playing/reset/result primitives, `FeedbackState.swift` for last-event display text, `InputIntent.swift` for primary/reset button labels, `ScreenshotState.swift`, which turns `release.screenshots` into typed Swift cases and evidence paths for future capture automation, and `RuntimeSceneSnapshot.swift`, which writes runtime scene-role evidence during screenshot-state launches. The seed archetypes, including `target_shooter`, use the same shared state/result surface before adding deeper mechanics. Native `flappy_side_scroller` adds gravity/flap state, auto-loop frame advance, frame-interval session timing, speed ramp, scrolling obstacle-gap state, collision/result proof, score, Flap/Reset controls, screenshot-state seeding, and RealityKit bird/obstacle/arena binding. `custom_realitykit` also emits `CameraRig.swift`, `InputController.swift`, `SystemFlags.swift`, and `WorldRig.swift`; the world rig owns lighting, backdrop, arena lanes, adapter-specific projectile feedback props, and a small `SceneEvents.Update` idle-motion hook. When `racing,lap_timer,collision` is selected it adds lane steering, lap/checkpoint state, collision/result proof, and RealityKit vehicle/track/obstacle/checkpoint binding. When `projectile,shooting,score` is selected it adds projectile charge/launch/hit state, target lane proof, controls, screenshot proof, and RealityKit player/weapon/projectile/target binding. When `weapon,hitscan,enemies,health,cover` is selected it adds aim/fire/health/cover/enemy state, controls, screenshot proof, and RealityKit player/weapon/enemy/cover binding. When `collect,score,timer` is selected it adds pickup/timer/combo state, lane controls, screenshot proof, and RealityKit player/pickup/timer binding. Those custom adapter generator strings are owned by `src/rkg/custom_realitykit_runtime.py`, not by the native archetype runtime/content/scaffold files; `rkg list-adapters --json` exposes the same registry as a capability matrix. Archetype rules should use `SessionControl.markResult` for result/fail transitions after setting their own gameplay-specific flags.

`qa-plan` is the dry-run screenshot capture plan. It sequences `release.screenshots` with the generated proof cue, visible roles, Swift screenshot state case, target evidence path, capture automation hint, and `semantic_visual_contract` thresholds. Use `--json` when another tool or future simulator automation needs to consume the plan. `fighter_2_5d`, `flappy_side_scroller`, and `custom_realitykit` generated apps can be launched directly into a screenshot state with `--rkg-screenshot-state <state>`. For `custom_realitykit`, the proof cue is selected from the active system adapter, so projectile, racing, shooter, and collector skeletons describe their own state values instead of generic archetype prose.

After capture, verify the generated screenshot evidence:

```bash
python3 Tools/rkg.py verify-screenshots GeneratedGame
python3 Tools/rkg.py qa-plan GameSpec.yaml --json > qa-plan.json
python3 Tools/rkg.py verify-screenshots GeneratedGame --plan qa-plan.json --json
```

`capture-screenshots` generates the Xcode project from `project.yml` when needed, builds the generated project, installs it on a simulator, launches each screenshot state, and writes the capture files. It also writes `Docs/screenshots/<state>.json` sidecars that record the game id, state, screenshot-state case, expected visible roles, proof cue, automation hint, screenshot path, and runtime scene snapshot path. The running generated app writes `Documents/rkg-scene-snapshot-<state>.json`; capture copies it to `Docs/screenshots/<state>.scene.json`. `verify-screenshots` then checks that every QA plan capture path exists under the generated project, has a supported JPEG or PNG image with readable dimensions, has a matching sidecar, and has runtime scene-role evidence for the expected roles. Expected roles must be backed by enabled `rkg|...` entities with finite position metadata and measurable `visual_bounds.extents`; disabled or zero-bound expected roles fail as `scene_role_not_visible`. PNG captures are sampled directly, and JPEG captures are sampled through the macOS `sips` rasterizer when available. Near-solid or blank evidence is rejected as `blank_or_solid`; repeated visual evidence across different release states is rejected as `duplicate_visual_evidence`. First-pass semantic screenshot failures are reported as `semantic_debug_overlay`, `semantic_control_occlusion`, `semantic_flat_scene`, or `semantic_scene_too_dark`.

### 2. Vertical Slice

The first playable uses procedural placeholders before custom art.

Required behavior:

- Start session.
- Core input.
- Score or progress feedback.
- Miss/fail behavior.
- Reset.
- Result state through the generated `ResultView` overlay when `SessionControl.isResult(state)`.
- Deterministic repeatability for QA.

### 3. Asset Acceptance

The first imported asset must be gameplay-relevant, not decorative.

Acceptance requires:

- Manifest entry.
- Runtime USDZ under `Assets/Imported`.
- Scale/origin/material notes.
- Texture and triangle budget.
- Fallback behavior.
- RealityKit screenshot evidence.
- `rkp accept-asset`.

### 4. QA

Minimum command gate:

```bash
python3 -m unittest discover -s Tests
python3 Tools/rkp.py doctor
python3 Tools/rkp.py release-check
```

For player-facing changes, also run the app in simulator or on device and capture evidence under `Docs/screenshots` when the screenshot documents a lasting state.

### 5. Store Pack

The store pack must exist before TestFlight submission:

```text
Docs/store/metadata.md
Docs/store/review-notes.md
Docs/store/privacy.md
Docs/store/screenshots.md
Docs/store/screenshot-qa.md
Docs/store/monetization.md
```

Metadata must describe the real game. Screenshots must show actual gameplay, not only title art. Generated screenshot checklists include a proof cue for each state, such as the button sequence or `GameSessionState` value that should be true before capture. The generated screenshot QA runbook sequences those cues into capture order with expected visible roles and evidence paths, then points QA to `rkg verify-screenshots .` after capture.

## Seed Archetypes

Start with small, replayable game shapes. The order below is not product priority; it is a set of early templates that exercise different mechanics.

| Archetype | Why it is first-wave friendly |
| --- | --- |
| Target shooter | Low asset count, clear scoring, fast session loop. |
| Lane dodger | Simple input, readable obstacles, good replayability. |
| Toss physics | RealityKit physics can create feel with few assets. |
| Stack puzzle | Short sessions and strong screenshot clarity. |
| Wave defense lite | Reuses target/spawn/scoring systems, but has higher scope. |
| 2.5D fighter | Fixed side-view duel loop with attack, dodge, health, combo, and knockout states. |
| Flappy side scroller | Fixed side-view tap timing, gravity, gap collision, pass scoring, and screenshot-friendly states. |
| Custom RealityKit skeleton | Composable camera/input/system starter for racing, FPS, shooter, collector, or other broad prototypes before a native archetype exists. |

For the end-to-end fighter skeleton path, see `Docs/rkg-fighter-walkthrough.md`.
For the Flappy-like proof, see `Docs/screenshots/rkg_flappy_*.jpg` and Sprint 136 in `Docs/WORKLOG.md`.

For a broad `custom_realitykit` dogfood run that starts from an idea and reaches simulator screenshot evidence, see `Docs/rkg-shard-volley-dogfood.md`.
For generic racing/FPS examples, see `Docs/rkg-generic-skeleton.md`.

Avoid first-wave games that require multiplayer, large maps, complex animation, or moderation.

Before deepening one archetype, define the shared template contract:

| Contract | Required output |
| --- | --- |
| Runtime loop | Start, core action, feedback, fail/miss, reset, result. |
| Asset roles | Gameplay target, player piece, vehicle, weapon, enemy, cover, opponent, obstacle, arena, pickup, projectile, hit VFX, guard cue, UI prop, or environment. |
| Fallbacks | Every role has a procedural fallback until RKP accepts imported art. |
| Verification | Generated project can run tests, build, and capture the required screenshot states. |
| Store pack | Metadata and screenshots describe actual generated gameplay. |

Each archetype owns screenshot proof cues in the registry. `rkg plan-game --json` exposes the selected cues under `screenshot_proofs`, and `rkg init-game` writes them into `Docs/store/screenshots.md` and `Docs/store/screenshot-qa.md` so QA knows how to drive the generated project into every required capture state.

## GameSpec Contract

Every generated game starts with `GameSpec.yaml`:

```yaml
game:
  id: ring_dash
  display_name: Ring Dash
  archetype: target_shooter
  session_seconds: 60
  camera: fixed_non_ar
  input: tap
  monetization: paid

loop:
  player_action: tap targets before they expire
  fail_condition: time expires
  scoring:
    hit: 10
    perfect: 25
    streak_bonus: true

assets:
  target_basic:
    type: gameplay_target
    role: target
    budget: "1500 tris / 512 texture"
    fallback: procedural_rings
  arena_floor:
    type: environment
    role: arena
    budget: "800 tris / 512 texture"
    fallback: procedural_grid

release:
  devices:
    - iPhone 15
    - iPad
  screenshots:
    - gameplay_start
    - mid_session
    - results
```

The spec is intentionally small. Add gameplay only after the first session works.

## Weekly Cadence

| Day | Output |
| ---: | --- |
| 0 | Score five ideas and pick one. |
| 1 | Generate project and procedural first playable. |
| 2 | Implement mechanic, scoring, reset, and result state. |
| 3 | Build and accept the first gameplay asset. |
| 4 | Add progression, audio, haptics, and polish. |
| 5 | QA, device check, and performance pass. |
| 6 | Store pack and TestFlight build. |
| 7 | Submit, iterate, or kill. |

The default decision is to kill weak prototypes. Shipping fewer stronger games is safer than filling the store with thin variants.
