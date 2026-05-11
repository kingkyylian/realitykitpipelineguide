# RKG Generic RealityKit Skeleton

`rkg new-game` is the zero-to-skeleton path for game ideas that do not yet deserve a dedicated archetype.

Use it when the user says "racing game", "FPS", "weapon combat", "third-person prototype", "top-down collector", or another broad RealityKit game shape. The command writes a valid `custom_realitykit` GameSpec from four decisions:

- title
- camera rig
- input model
- gameplay systems

It does not make a finished racing or FPS game. It creates a generated RealityKit project with asset roles, procedural fallbacks, store/QA docs, screenshot states, and verification gates so the next slice can deepen runtime behavior without starting from an empty Xcode project.

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

`custom_realitykit` is the first generic skeleton slice. It gives a valid generated project, declared fallback-driven placeholder meshes, generated asset briefs, store docs, screenshot QA, simulator capture, and `verify-game`/`verify-screenshots` gates.

The next runtime slice should add generated modules such as `CameraRig.swift`, `InputController.swift`, and system adapters for vehicle movement, first-person aiming, projectile/hitscan, and health. Until that lands, racing and FPS skeletons are scaffolded RealityKit projects with composable roles, not genre-complete gameplay.
