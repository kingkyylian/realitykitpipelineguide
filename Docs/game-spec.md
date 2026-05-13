# GameSpec

`GameSpec` is the small contract RKG uses before generating a RealityKit game.

The spec is intentionally strict for first-wave arcade games. A game should be small enough to reach a playable vertical slice quickly, and every runtime asset must have a fallback so the app can keep running before imported art is accepted.

## Required Shape

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

## Validation Rules

- `game.id` must be `snake_case`.
- `game.archetype` must exist in the RKG archetype registry.
- `game.input` must be supported by the selected archetype registry entry.
- `game.camera` must be supported by the selected archetype registry entry.
- `game.session_seconds` must be a positive integer.
- First-wave arcade sessions must be 180 seconds or less.
- `game.monetization: external_unlock` is rejected for App Store builds.
- `loop.scoring` must be an object.
- `assets` must contain at least one asset.
- Every asset requires `type`, `budget`, and `fallback`.
- Every role listed in the selected archetype's `required_asset_roles` must be present in `assets`.
- `assets.<id>.role` must be one of the selected archetype's required or optional asset roles when present.
- `release.devices` must contain at least one device.
- `release.screenshots` must contain at least one screenshot.
- Every screenshot state must be supported by the selected archetype.

Validate a spec before scaffolding:

```bash
python3 Tools/rkg.py validate-spec GameSpec.yaml
python3 Tools/rkg.py validate-spec GameSpec.yaml --json
```

Role-aware specs are preferred because they let RKG generate role-specific loaders, fallbacks, screenshots, and store checklists. RKP still owns the final asset acceptance state.

## Starter Specs

Use `rkg new-spec` when starting from zero instead of hand-writing `GameSpec.json`.

```bash
python3 Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output GameSpec.json
python3 Tools/rkg.py new-spec flappy_side_scroller --title "Flappy Reef" --output GameSpec.json
python3 Tools/rkg.py validate-spec GameSpec.json
```

Use `rkg new-game` when the idea is broader than a built-in archetype and should begin as a composable RealityKit skeleton.

```bash
python3 Tools/rkg.py new-game --title "Desert Chase" --camera chase --input tilt_tap --systems racing,lap_timer,collision --output GameSpec.json
python3 Tools/rkg.py validate-spec GameSpec.json
```

`new-game` writes `game.archetype: custom_realitykit` and rejects unsupported camera rigs, input models, and gameplay systems before it writes the file.

## Custom RealityKit Skeleton Example

`custom_realitykit` is the generic path for racing, FPS, shooter, projectile, collector, top-down, and other early RealityKit prototypes before they become native archetypes. Racing uses `racing,lap_timer,collision` for lane/lap/checkpoint/collision state, steering controls, state-to-scene binding, and screenshot-state proof. Projectile uses `projectile,shooting,score` for charge/launch/hit state, projectile and target role binding, lane controls, and screenshot-state proof. FPS/shooter uses `weapon,hitscan,enemies,health,cover` for aim/fire/health/cover/enemy state, controls, scene binding, and screenshot-state proof. Collector uses `collect,score,timer` for pickup/timer/combo state, lane controls, state-to-scene binding, and screenshot-state proof. Run `rkg list-adapters --json` to inspect the current custom adapter capability matrix.

```yaml
game:
  id: desert_chase
  display_name: Desert Chase
  archetype: custom_realitykit
  session_seconds: 60
  camera: chase
  input: tilt_tap
  monetization: paid
  systems:
    - racing
    - lap_timer
    - collision

loop:
  player_action: steer through the course, avoid obstacles, and complete laps
  fail_condition: collision or timer pressure ends the run
  scoring:
    hit: 10
    perfect: 25
    lap: 100

assets:
  player_vehicle:
    type: vehicle_proxy
    role: player
    budget: "1800 tris / 512 texture"
    fallback: procedural_vehicle
  race_track:
    type: environment
    role: arena
    budget: "1200 tris / 512 texture"
    fallback: procedural_track
  track_obstacle:
    type: hazard
    role: obstacle
    budget: "700 tris / 512 texture"
    fallback: procedural_block
  checkpoint_gate:
    type: ui_prop
    role: ui_prop
    budget: "500 tris / 512 texture"
    fallback: procedural_gate

release:
  devices:
    - iPhone 15
    - iPad
  screenshots:
    - gameplay_start
    - mid_action
    - fail_or_hit
    - results
```

## 2.5D Fighter Example

`fighter_2_5d` is the first native duel archetype. It requires `player`, `opponent`, and `arena` roles, can bind optional `hit_vfx`, `guard_cue`, `telegraph`, `ui_prop`, and `environment` roles, and can launch directly into each screenshot state with `--rkg-screenshot-state <state>`.

```yaml
game:
  id: neon_ring_duel
  display_name: Neon Ring Duel
  archetype: fighter_2_5d
  session_seconds: 90
  camera: fixed_non_ar
  input: tap_swipe
  monetization: paid

loop:
  player_action: attack and dodge in a fixed side-view duel
  fail_condition: player health reaches zero
  scoring:
    hit: 10
    combo_bonus: true
    perfect_dodge: 5

assets:
  fighter_player:
    type: character_proxy
    role: player
    budget: "1200 tris / 512 texture"
    fallback: procedural_capsule
  fighter_opponent:
    type: character_proxy
    role: opponent
    budget: "1200 tris / 512 texture"
    fallback: procedural_box
  duel_arena:
    type: environment
    role: arena
    budget: "900 tris / 512 texture"
    fallback: procedural_grid
  hit_spark:
    type: vfx_proxy
    role: hit_vfx
    budget: "300 tris / 256 texture"
    fallback: procedural_spark
  guard_ring:
    type: vfx_proxy
    role: guard_cue
    budget: "300 tris / 256 texture"
    fallback: procedural_guard

release:
  devices:
    - iPhone 15
  screenshots:
    - round_start
    - mid_combo
    - perfect_dodge
    - knockout
```

## Flappy Side Scroller Example

`flappy_side_scroller` is the native Flappy-like archetype. It requires `player`, `obstacle`, and `arena` roles, generates tap-to-flap gravity state, timer-driven obstacle advance, frame-interval session timing, speed ramp, scrolling obstacle/gap state, collision/result proof, and launch-state screenshot seeding for `gameplay_start`, `mid_flight`, `near_gap`, `collision`, and `results`.

```yaml
game:
  id: flappy_reef
  display_name: Flappy Reef
  archetype: flappy_side_scroller
  session_seconds: 60
  camera: fixed_non_ar
  input: tap
  monetization: paid

loop:
  player_action: tap to flap through scrolling pipe gaps
  fail_condition: hit a pipe or leave the flight band
  scoring:
    hit: 10
    perfect: 25
    clear: 100

assets:
  bird_player:
    type: gameplay_actor
    role: player
    budget: "900 tris / 512 texture"
    fallback: procedural_capsule
  pipe_gate:
    type: prop
    role: obstacle
    budget: "700 tris / 512 texture"
    fallback: procedural_gate
  reef_lane:
    type: environment
    role: arena
    budget: "1200 tris / 512 texture"
    fallback: procedural_arena

release:
  devices:
    - iPhone 15
    - iPad
  screenshots:
    - gameplay_start
    - mid_flight
    - near_gap
    - collision
    - results
```

## Why Fallbacks Are Required

RKG generates playable projects before final art is accepted. Asset fallbacks keep the game loop testable when a USDZ is still planned, failed, or waiting for screenshot acceptance.
