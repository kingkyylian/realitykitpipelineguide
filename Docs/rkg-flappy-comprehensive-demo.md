# RKG Flappy Comprehensive Demo

This dogfood run proves the Flappy-like native archetype through the broader RKG/RKP demo toolchain, not only through a hand-written fixture.

## Goal

Generate a Flappy Bird-style RealityKit demo from an idea, verify the generated app, capture deterministic simulator screenshots, run screenshot QA, and accept all generated gameplay assets through the RKP asset gate.

## Project

- Idea: `Build/rkg-flappy-comprehensive-v1/idea.json`
- Generated project: `Build/rkg-flappy-comprehensive-v1/FlappyReefDemo`
- Game id: `flappy_reef_demo`
- Archetype: `flappy_side_scroller`
- Input: `tap`
- Required roles: `player`, `obstacle`, `arena`
- Assets: `bird_player`, `pipe_gate`, `reef_lane`

`Build/` is scratch output. Public evidence copied from the run lives under `Docs/screenshots`.

## Toolchain Used

```text
rtk ./.venv/bin/python Tools/rkg.py start-game Build/rkg-flappy-comprehensive-v1/idea.json --output Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --force --json
rtk ./.venv/bin/python Tools/rkg.py validate-spec Build/rkg-flappy-comprehensive-v1/FlappyReefDemo/GameSpec.json
rtk ./.venv/bin/python Tools/rkg.py plan-game Build/rkg-flappy-comprehensive-v1/FlappyReefDemo/GameSpec.json --json
rtk ./.venv/bin/python Tools/rkg.py qa-plan Build/rkg-flappy-comprehensive-v1/FlappyReefDemo/GameSpec.json --json
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --device booted --dry-run --json
rtk ./.venv/bin/python Tools/rkg.py verify-game Build/rkg-flappy-comprehensive-v1/FlappyReefDemo
rtk ./.venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --device booted --json
rtk ./.venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --json
rtk ./.venv/bin/python Tools/rkg.py accept-assets Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --device booted --dry-run --json
rtk ./.venv/bin/python Tools/rkg.py accept-assets Build/rkg-flappy-comprehensive-v1/FlappyReefDemo --device booted --json
```

The `start-game` run scored the idea at `100/pass`, routed it to `flappy_side_scroller`, emitted a five-step QA plan, and produced three RKP asset tasks. During this run a QA-plan gap was fixed: Flappy screenshot states now use `launch_arg --rkg-screenshot-state <state>` instead of `manual_capture`.

## Screenshot Evidence

| State | Public evidence |
| --- | --- |
| `gameplay_start` | `Docs/screenshots/rkg_flappy_demo_gameplay_start.jpg` |
| `mid_flight` | `Docs/screenshots/rkg_flappy_demo_mid_flight.jpg` |
| `near_gap` | `Docs/screenshots/rkg_flappy_demo_near_gap.jpg` |
| `collision` | `Docs/screenshots/rkg_flappy_demo_collision.jpg` |
| `results` | `Docs/screenshots/rkg_flappy_demo_results.jpg` |

All five generated screenshots were captured at `1206x2622` and passed `verify-screenshots` with status `ok`.

## Accepted Assets

| Asset | Role | Inspect result | Public evidence |
| --- | --- | --- | --- |
| `bird_player` | `player` | 296 / 900 triangles, 512 base color, UV present | `Docs/screenshots/rkg_flappy_demo_bird_player_imported.jpg` |
| `pipe_gate` | `obstacle` | 2 / 700 triangles, 512 base color, UV present | `Docs/screenshots/rkg_flappy_demo_pipe_gate_imported.jpg` |
| `reef_lane` | `arena` | 50 / 1200 triangles, 512 base color, UV present | `Docs/screenshots/rkg_flappy_demo_reef_lane_imported.jpg` |

`accept-assets` completed `make-asset`, `build-asset`, `inspect-usdz`, one screenshot capture pass, screenshot verification, evidence copy, `accept-asset` for all three assets, and `rkp release-check --assets`.

## Verification Result

```text
rkg verify-game: ok
rkg capture-screenshots --device booted --json: ok; 5 screenshots
rkg verify-screenshots --json: ok; 5 checks
rkg accept-assets --device booted --json: ok; 18 workflow steps
rkp release-check --assets from generated project: ok
```

## Remaining Product Gap

This proves the demo toolchain can produce and verify a Flappy-like generated project with imported draft assets. It does not make the game shipping-ready. The next useful product pass is gameplay feel: stronger bird silhouette, pipe/gap art, flap animation, hit VFX, sound/haptics, and level variety.
