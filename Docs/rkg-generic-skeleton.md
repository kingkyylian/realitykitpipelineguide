# RKG Generic RealityKit Skeleton

`rkg new-game` is the zero-to-skeleton path for game ideas that do not yet deserve a dedicated archetype.

Use it when the user says "racing game", "FPS", "weapon combat", "projectile game", "third-person prototype", "top-down collector", or another broad RealityKit game shape. The command writes a valid `custom_realitykit` GameSpec from four decisions:

- title
- camera rig
- input model
- gameplay systems

It does not make a finished racing or FPS game. It creates a generated RealityKit project with asset roles, procedural fallbacks, store/QA docs, screenshot states, and verification gates so each system adapter can deepen runtime behavior without starting from an empty Xcode project.

## Racing Skeleton

```bash
python3 Tools/rkg.py new-game \
  --title "Desert Chase" \
  --camera chase \
  --input tilt_tap \
  --systems racing,lap_timer,collision \
  --output Build/rkg-generic-racing/GameSpec.json

python3 Tools/rkg.py validate-spec Build/rkg-generic-racing/GameSpec.json
python3 Tools/rkg.py plan-game Build/rkg-generic-racing/GameSpec.json
python3 Tools/rkg.py init-game Build/rkg-generic-racing/GameSpec.json --output Build/rkg-generic-racing/DesertChase --force
python3 Tools/rkg.py verify-game Build/rkg-generic-racing/DesertChase
python3 Tools/rkg.py capture-screenshots Build/rkg-generic-racing/DesertChase --device booted
python3 Tools/rkg.py verify-screenshots Build/rkg-generic-racing/DesertChase
```

Generated roles:

| Asset id | Role | Purpose |
| --- | --- | --- |
| `player_vehicle` | `player` | Player-controlled vehicle proxy. |
| `race_track` | `arena` | Track/playfield proxy. |
| `track_obstacle` | `obstacle` | Collision proof role when `collision` is selected. |
| `checkpoint_gate` | `ui_prop` | Lap/timer proof role when `lap_timer` is selected. |

Generated runtime behavior:

- `GameSessionState` includes race distance, lap, checkpoint, vehicle lane, obstacle lane, and collision proof flags.
- `GameRules` starts a racing session, clamps lane steering, advances distance/checkpoints, scores lap progress, and marks collision/result states.
- `ContentView` shows lap/distance/checkpoint/lane HUD values and Left/Right lane controls.
- `GameSceneController` binds vehicle, track, obstacle, checkpoint, and camera rig entities; lane/distance/checkpoint/collision state changes produce visible RealityKit placement and scale changes.
- `capture-screenshots` launch states seed `gameplay_start`, `mid_action`, `fail_or_hit`, and `results` with different racing state.

## FPS / Shooter Skeleton

```bash
python3 Tools/rkg.py new-game \
  --title "Room Breach" \
  --camera first_person \
  --input dual_stick \
  --systems weapon,hitscan,enemies,health \
  --output Build/rkg-generic-fps/GameSpec.json

python3 Tools/rkg.py validate-spec Build/rkg-generic-fps/GameSpec.json
python3 Tools/rkg.py init-game Build/rkg-generic-fps/GameSpec.json --output Build/rkg-generic-fps/RoomBreach --force
python3 Tools/rkg.py verify-game Build/rkg-generic-fps/RoomBreach
python3 Tools/rkg.py capture-screenshots Build/rkg-generic-fps/RoomBreach --device booted
python3 Tools/rkg.py verify-screenshots Build/rkg-generic-fps/RoomBreach
```

Generated roles:

| Asset id | Role | Purpose |
| --- | --- | --- |
| `player_proxy` | `player` | Player/camera anchor proxy. |
| `arena_space` | `arena` | Test room or play space proxy. |
| `weapon_proxy` | `weapon` | First weapon placeholder. |
| `enemy_proxy` | `enemy` | First enemy target placeholder. |
| `cover_block` | `cover` | Health/cover proof role. |

Generated runtime behavior:

- `GameSessionState` includes health, enemy count, shots fired, aim lane, enemy lane, cover, defeated, and hit feedback flags.
- `GameRules` starts a shooter session, clamps aim steering, fires the weapon, applies health damage, toggles cover, and marks room-clear or health-depleted result states.
- `ContentView` shows health/enemies/shots/aim HUD values and Aim Left/Aim Right/Cover controls.
- `GameSceneController` binds player, weapon, enemy, cover, and camera rig entities; aim/enemy/cover/hit/defeated state changes produce visible RealityKit placement, scale, and enabled-state changes.
- `capture-screenshots` launch states seed `gameplay_start`, `mid_action`, `fail_or_hit`, and `results` with different shooter state.

## Collector / Score / Timer Skeleton

```bash
python3 Tools/rkg.py new-game \
  --title "Orb Sprint" \
  --camera top_down \
  --input tap_swipe \
  --systems collect,score,timer \
  --output Build/rkg-generic-collector/GameSpec.json

python3 Tools/rkg.py validate-spec Build/rkg-generic-collector/GameSpec.json
python3 Tools/rkg.py init-game Build/rkg-generic-collector/GameSpec.json --output Build/rkg-generic-collector/OrbSprint --force
python3 Tools/rkg.py verify-game Build/rkg-generic-collector/OrbSprint
python3 Tools/rkg.py capture-screenshots Build/rkg-generic-collector/OrbSprint --device booted
python3 Tools/rkg.py verify-screenshots Build/rkg-generic-collector/OrbSprint
```

Generated roles:

| Asset id | Role | Purpose |
| --- | --- | --- |
| `player_proxy` | `player` | Player collector proxy. |
| `arena_space` | `arena` | Top-down pickup space proxy. |
| `pickup_proxy` | `pickup` | Collectible proof role when `collect` is selected. |
| `timer_gate` | `ui_prop` | Timer pressure proof role when `timer` is selected. |

Generated runtime behavior:

- `GameSessionState` includes collected item count, remaining items, timer, combo streak, collector lane, pickup lane, and timeout proof flags.
- `GameRules` starts a collector session, clamps lane movement, resolves pickup collection, scores combo progress, marks collection-complete results, and marks timer-expired fail states.
- `ContentView` shows item/timer/combo/lane HUD values plus Move Left, Move Right, and Collect controls.
- `GameSceneController` binds player, arena, pickup, timer, and camera rig entities; lane, combo, pickup, and timeout state changes produce visible RealityKit placement, scale, and enabled-state changes.
- `capture-screenshots` launch states seed `gameplay_start`, `mid_action`, `fail_or_hit`, and `results` with different collector state.

## Projectile / Shooting / Score Skeleton

```bash
python3 Tools/rkg.py new-game \
  --title "Arc Volley" \
  --camera third_person \
  --input drag \
  --systems projectile,shooting,score \
  --output Build/rkg-generic-projectile/GameSpec.json

python3 Tools/rkg.py validate-spec Build/rkg-generic-projectile/GameSpec.json
python3 Tools/rkg.py init-game Build/rkg-generic-projectile/GameSpec.json --output Build/rkg-generic-projectile/ArcVolley --force
python3 Tools/rkg.py verify-game Build/rkg-generic-projectile/ArcVolley
```

Generated roles:

| Asset id | Role | Purpose |
| --- | --- | --- |
| `player_proxy` | `player` | Player launcher proxy. |
| `arena_space` | `arena` | Third-person projectile range proxy. |
| `weapon_proxy` | `weapon` | Launcher or aim-source placeholder. |
| `projectile_proxy` | `projectile` | Moving projectile proof role. |
| `target_proxy` | `target` | Impact target lane proof role. |

Generated runtime behavior:

- `GameSessionState` includes projectile shots, hits, charge, aim lane, target lane, travel, in-flight, and hit feedback flags.
- `SystemFlags` separates `hasProjectile` and `hasShooting` from `hasWeapon`, so projectile-only games do not route through the FPS/shooter adapter.
- `GameRules` starts a projectile session, clamps lane aim, charges shots, launches projectiles, scores charged hits, marks clear/spent result states, and seeds screenshot states.
- `ContentView` shows shots/hits/charge/aim HUD values plus Aim Left, Aim Right, Charge, and Launch controls.
- `GameSceneController` binds player, arena, weapon, projectile, target, and camera rig entities; aim lane, target lane, charge, travel, and hit state produce visible RealityKit placement and scale changes.

## Adapter Capability Matrix

Use `list-adapters` when a caller needs to understand what the generic skeleton currently supports before choosing systems:

```bash
python3 Tools/rkg.py list-adapters
python3 Tools/rkg.py list-adapters --json
```

The JSON output lists each `CustomRealityKitRuntimeAdapter` id, supported systems, generated state fields, rule members, scene properties, and bound scene roles. Current adapter ids are `racing`, `projectile`, `shooter`, and `collector`.

## Supported Axes

Camera:

```text
fixed_non_ar, chase, first_person, third_person, top_down
```

Input:

```text
tap, drag, tilt_tap, dual_stick, gamepad_touch, tap_swipe
```

Gameplay systems:

```text
racing, lap_timer, collision, vehicle, weapon, hitscan, projectile,
shooting, enemies, enemy_ai, health, cover, collect, score, timer, physics
```

`new-game` rejects unsupported systems, cameras, and input models before writing the spec.

## Current Boundary

`custom_realitykit` now gives a valid generated project, declared fallback-driven placeholder meshes, generated asset briefs, store docs, screenshot QA, simulator capture, `CameraRig.swift`, `InputController.swift`, `SystemFlags.swift`, and `verify-game`/`verify-screenshots` gates. The generic overlay is state-bound, so launch screenshot states can seed `gameplay_start`, `mid_action`, `fail_or_hit`, and `results` instead of capturing four identical idle launches.

The current system adapters are racing, projectile/shooting/score, FPS/shooter, and collector/score/timer. They prove vehicle lane movement, checkpoint/lap progress, collision/result state, projectile charge/travel/impact state, first-person aim/fire state, enemy/health/cover proof, pickup collection, combo/timer proof, and camera rig entity binding. Their state/rule/UI/scene generator surface lives behind `CustomRealityKitRuntimeAdapter` registry entries in `src/rkg/custom_realitykit_runtime.py`, and `rkg list-adapters --json` exposes that registry as a capability matrix. Generated games are still skeletons, not genre-complete gameplay.
