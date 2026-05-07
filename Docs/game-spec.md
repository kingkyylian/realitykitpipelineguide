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
- `game.session_seconds` must be a positive integer.
- First-wave arcade sessions must be 180 seconds or less.
- `game.monetization: external_unlock` is rejected for App Store builds.
- `loop.scoring` must be an object.
- `assets` must contain at least one asset.
- Every asset requires `type`, `budget`, and `fallback`.
- `assets.<id>.role` is optional for now, but when present it must be one of the selected archetype's required or optional asset roles.
- `release.devices` must contain at least one device.
- `release.screenshots` must contain at least one screenshot.
- Every screenshot state must be supported by the selected archetype.

Validate a spec before scaffolding:

```bash
python3 Tools/rkg.py validate-spec GameSpec.yaml
python3 Tools/rkg.py validate-spec GameSpec.yaml --json
```

Role-aware specs are preferred because they let RKG generate role-specific loaders, fallbacks, screenshots, and store checklists. RKP still owns the final asset acceptance state.

## Why Fallbacks Are Required

RKG generates playable projects before final art is accepted. Asset fallbacks keep the game loop testable when a USDZ is still planned, failed, or waiting for screenshot acceptance.
