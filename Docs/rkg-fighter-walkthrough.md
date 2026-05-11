# RKG Fighter Walkthrough

This walkthrough starts from zero and creates a generated RealityKit fighter skeleton.

## Commands

```bash
python3 Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter/GameSpec.json
python3 Tools/rkg.py validate-spec Build/rkg-fighter/GameSpec.json
python3 Tools/rkg.py plan-game Build/rkg-fighter/GameSpec.json
python3 Tools/rkg.py qa-plan Build/rkg-fighter/GameSpec.json
python3 Tools/rkg.py init-game Build/rkg-fighter/GameSpec.json --output Build/rkg-fighter/NeonRingDuel --force
python3 Tools/rkg.py verify-game Build/rkg-fighter/NeonRingDuel
python3 Tools/rkg.py capture-screenshots Build/rkg-fighter/NeonRingDuel --device booted
python3 Tools/rkg.py verify-screenshots Build/rkg-fighter/NeonRingDuel
```

## What This Produces

- A SwiftUI + RealityKit generated app.
- Fighter state/rules for attack, dodge, guard, combo, damage, and knockout.
- Procedural role fallbacks for player, opponent, arena, hit VFX, and guard cue.
- Store screenshot QA files.
- Runtime screenshot evidence under `Docs/screenshots`.
- Role asset briefs under `Docs/assets`.

## Boundary

This is a skeleton, not a shippable fighter. Production still needs imported fighter art, animation polish, audio, frame-time/device QA, App Store metadata review, and human product judgment.
