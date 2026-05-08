# RealityKit Game Production Playbook

This playbook is the reusable operating manual for future RealityKit games built from this repo. Use `Docs/guide.md` when learning the pipeline; use this file when planning and shipping real work.

## North Star

Every gameplay or asset change must answer four questions:

| Question | Required answer |
| --- | --- |
| What player-facing problem does this solve? | One sentence tied to gameplay, readability, or production speed. |
| What asset/runtime contract changes? | File path, manifest id, scale, origin, collision, loader order, or UI state. |
| How is it verified? | Build, manifest validation, simulator/device screenshot, short video, or profiling note. |
| What did the team learn? | Worklog note that makes the next similar task faster. |

If a task cannot answer these, it is not ready to start.

## Production Loop

```text
Feature brief
-> gameplay contract
-> asset contract
-> implementation
-> local verification
-> visual evidence
-> worklog
-> CI
-> release note
```

## Game Factory Boundary

The pipeline is split into two layers:

| Layer | Responsibility |
| --- | --- |
| RKP | Asset contracts, Blender/USDZ output, manifest health, RealityKit verification, screenshot acceptance, and release checks. |
| RKG | Commercial game specs, archetype templates, reusable gameplay modules, QA orchestration, store-pack generation, and variant review. |

Keep RKP narrow. It should answer whether an asset is planned, built, verified, and accepted. RKG can call RKP, but it must not bypass RKP's manifest, budget, fallback, or screenshot gates.

Future games should start from `Docs/game-factory.md` before code or art work begins.

## Commercial Variant Rule

Do not ship shallow reskins as separate apps. A new Bundle ID needs a material difference in at least one of these areas:

- Core mechanic or input pattern.
- Progression structure.
- Audience or fantasy.
- Level/content depth.
- Art direction that changes readability and game feel, not only colors or names.

If a variant only changes title, icon, palette, or a few meshes, keep it as an update, level pack, or IAP inside the existing app instead of creating another app.

## Game Factory Gates

Every new game moves through these gates:

| Gate | Pass condition |
| --- | --- |
| Idea score | `python3 Tools/rkg.py score-idea idea.json` returns `pass` or `revise`; rejected ideas stop before scaffolding. |
| Vertical slice | Procedural placeholders support start, core action, score/result, reset, and one repeatable session. |
| Asset acceptance | First gameplay-relevant USDZ is loaded in RealityKit and accepted with screenshot evidence. |
| QA | Spec validation, `qa-plan`, manifest validation, tests, simulator build, screenshots, privacy notes, and metadata checks pass. |
| Store pack | Review notes, screenshots, privacy notes, support URL checklist, monetization notes, and honest metadata are ready. |

Kill weak games at the gate. The factory is for repeatable quality, not automatic submissions.

## Codex Skill Mode

This repo includes an installable skill:

```bash
make install-skill
```

After installation, use the `realitykit-pipeline-guide` skill when asking an AI agent to work on RealityKit asset imports, gameplay features, release polish, or new game startup tasks. The skill keeps agents on the same contracts and verification gates as this playbook.

### 1. Feature Brief

Start with `Prompts/game-feature-brief.md` or `Prompts/asset-brief.md`.

Minimum brief:

- Player goal
- Required asset ids
- Runtime behavior
- Acceptance screenshot or video
- Mobile budget risk
- Rollback/fallback behavior

For a new asset, scaffold the contract first:

```bash
python3 Tools/rkp.py new-asset enemy_drone --type gameplay_target
```

This creates the manifest entry, `Docs/assets/<id>.md`, and `Tools/blender/create_<id>.py`.

After editing the Blender script or source asset, build the USDZ:

```bash
python3 Tools/rkp.py build-asset enemy_drone
```

This verifies the USDZ file exists, but does not mark the asset imported. Acceptance still requires RealityKit visual verification.

After verifying the asset in the simulator, accept it with required screenshot evidence:

```bash
python3 Tools/rkp.py accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

This marks the manifest entry imported, updates the asset brief when present, prepends a worklog acceptance record, and runs the pipeline doctor.

### 2. Gameplay Contract

Before writing code, define:

- Game state affected: `idle`, `playing`, `waveCleared`, `gameOver`, or `paused`.
- Input source: tap, drag, button, gesture, controller, or AI/system event.
- Output: score, spawn, VFX, sound, haptic, UI text, or persistence.
- Failure behavior: miss, timeout, missing asset, duplicate event, old simulator cache.

### 3. Asset Contract

Every imported asset must have:

- `asset_id` in `snake_case`.
- File path: `Assets/Imported/<asset_id>.usdz`.
- Manifest entry in `Tools/asset_manifest.json`.
- Scale statement: real-world meters or intentional runtime scale.
- Origin/pivot statement.
- UV/material statement.
- Texture budget.
- Collision expectation.
- Runtime fallback.
- Evidence screenshot.

### 4. Implementation

Default engineering rules:

- Keep procedural fallback until the imported asset is proven.
- Prefer deterministic test scenes over random scenes while teaching or debugging.
- Do not couple visual mesh bounds directly to gameplay scoring without documenting the mapping.
- Keep public CI on the oldest supported SDK baseline.
- Avoid latest Apple APIs unless the repository can compile with the CI Xcode version.

### 5. Verification

Use this minimum gate before commit:

```bash
make doctor
make release-check
```

For visual or gameplay changes, also run the app on simulator and capture evidence under `Docs/screenshots` only when it is useful for the guide. Temporary screenshots stay in `Build/`.

### 6. Worklog

Every meaningful change should add a short `Docs/WORKLOG.md` note with:

- goal
- changed files or asset ids
- verification
- lesson learned

Do not write diary prose. Write future debugging material.

## Definition of Done

| Work type | Done means |
| --- | --- |
| Code-only fix | Build passes, behavior verified, worklog updated if the bug taught a reusable lesson. |
| Gameplay feature | Build passes, interaction tested, score/state edge cases checked, screenshot/video if visual. |
| Imported asset | Manifest updated, USDZ in `Assets/Imported`, loader path verified, screenshot captured, worklog note written. |
| Documentation | README/guide links updated, stale claims removed, commands tested when possible. |
| Public release | CI green, release notes accurate, screenshots/PDF links valid, tag points to the intended commit. |

## Decision Records

Use this format in `Docs/WORKLOG.md` for decisions:

```text
Decision:
Context:
Options:
Choice:
Why:
Tradeoff:
Revisit when:
```

Example:

```text
Decision: Keep iOS deployment target at 18.0.
Context: The repo should be usable by more learners and CI runs Xcode 16.
Options: Raise to iOS 26, or keep iOS 18 and avoid SDK-only symbols.
Choice: Keep iOS 18.
Why: Better public compatibility.
Tradeoff: Some latest RealityKit APIs are avoided or need fallback.
Revisit when: The repo intentionally becomes an iOS 26 API showcase.
```

## Quality Gates

### Asset Gate

- `asset_id` matches file name.
- USDZ opens outside the app.
- Texture is embedded or intentionally external and documented.
- UV direction is verified.
- Origin and scale are verified in gameplay camera.
- Collision shape matches gameplay, not just mesh bounds.
- Fallback path still works.

### Gameplay Gate

- Input cannot trigger through HUD or controls.
- Duplicate collision events cannot double-score.
- Projectiles or temporary effects expire.
- Misses have a defined behavior.
- Reset clears scene state.
- The same test can be repeated deterministically.

### Public Repo Gate

- `README.md` tells a new user what this is within 10 seconds.
- Quick Start has only public commands.
- Internal wrappers such as `rtk` are explained as non-dependencies.
- CI is green.
- License exists.
- Release exists for the current public milestone.

## Review Checklist

Before merging or publishing, ask:

- Does this make the repo easier to use six months from now?
- Did we update the canonical doc instead of creating a duplicate explanation?
- Can Kyylian and Mehmet both explain the asset/runtime contract?
- Would a new AI agent understand the current state from `AGENTS.md` and `Docs/ai-handoff.md`?
- Is the screenshot evidence still true after this change?
