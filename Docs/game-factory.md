# RealityKit Game Factory

This document defines how to turn the asset pipeline into a repeatable commercial game workflow.

For executable architecture details, use `Docs/rkg-architecture.md`. This page stays high-level; the architecture doc owns registry, role, runtime module, CLI, verification, and store-pack contracts.

## Principle

RKP remains the RealityKit asset pipeline. RKG is the game factory layer above it.

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

RKG is not a target-shooter generator. It is a general RealityKit game factory for small, shippable mobile games.

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

Before writing a generated project, preview it:

```bash
python3 Tools/rkg.py validate-spec GameSpec.yaml
python3 Tools/rkg.py plan-game GameSpec.yaml
python3 Tools/rkg.py qa-plan GameSpec.yaml
```

`plan-game` is a dry run. It lists generated files, asset roles, and screenshot states without creating the output directory. Generated projects include `SessionControl.swift` for shared playing/reset/result primitives and `ScreenshotState.swift`, which turns `release.screenshots` into typed Swift cases and evidence paths for future capture automation. Archetype rules should use `SessionControl.markResult` for result/fail transitions after setting their own gameplay-specific flags.

`qa-plan` is the dry-run screenshot capture plan. It sequences `release.screenshots` with the generated proof cue, visible roles, Swift screenshot state case, and target evidence path. Use `--json` when another tool or future simulator automation needs to consume the plan.

### 2. Vertical Slice

The first playable uses procedural placeholders before custom art.

Required behavior:

- Start session.
- Core input.
- Score or progress feedback.
- Miss/fail behavior.
- Reset.
- Result state.
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

Metadata must describe the real game. Screenshots must show actual gameplay, not only title art. Generated screenshot checklists include a proof cue for each state, such as the button sequence or `GameSessionState` value that should be true before capture. The generated screenshot QA runbook sequences those cues into capture order with expected visible roles and evidence paths.

## Seed Archetypes

Start with small, replayable game shapes. The order below is not product priority; it is a set of early templates that exercise different mechanics.

| Archetype | Why it is first-wave friendly |
| --- | --- |
| Target shooter | Low asset count, clear scoring, fast session loop. |
| Lane dodger | Simple input, readable obstacles, good replayability. |
| Toss physics | RealityKit physics can create feel with few assets. |
| Stack puzzle | Short sessions and strong screenshot clarity. |
| Wave defense lite | Reuses target/spawn/scoring systems, but has higher scope. |

Avoid first-wave games that require multiplayer, large maps, complex animation, or moderation.

Before deepening one archetype, define the shared template contract:

| Contract | Required output |
| --- | --- |
| Runtime loop | Start, core action, feedback, fail/miss, reset, result. |
| Asset roles | Gameplay target, obstacle, player piece, arena, pickup, projectile, UI prop, or environment. |
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
