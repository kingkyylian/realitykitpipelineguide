# RKG Generic Skeleton MVP Finish Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. In Codex, use `executing-plans` inline unless the user explicitly asks for subagents or parallel agent work. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the current RKG generic RealityKit skeleton MVP by adding projectile/shooting coverage, making adapter capabilities visible, and verifying generated projects across the supported custom adapters.

**Architecture:** `src/rkg/spec_templates.py` owns `new-game` spec generation, asset roles, and default loop text. `src/rkg/runtime_core.py` owns generated Swift feature flags. `src/rkg/custom_realitykit_runtime.py` owns custom RealityKit runtime adapters and should expose both Swift generation fragments and a machine-readable adapter capability matrix used by the CLI and docs.

**Tech Stack:** Python standard library CLI and tests, generated SwiftUI/RealityKit project files, XcodeGen-generated iOS project skeletons, `rtk` command wrapper.

---

### Task 1: Lock The Projectile Gap With Tests

**Files:**
- Modify: `Tests/test_rkg_new_game.py`
- Modify: `Tests/test_rkg_runtime_core.py`
- Modify: `Tests/test_rkg_custom_realitykit_runtime.py`
- Modify: `Tests/test_rkg_init_game.py`

- [x] **Step 1: Add a `new-game` projectile skeleton test**

Add a test that runs:

```bash
rtk ./.venv/bin/python -m unittest Tests.test_rkg_new_game.RkgNewGameTests.test_new_game_writes_projectile_realitykit_skeleton_spec
```

Expected before implementation: FAIL because the generated loop is still shooter-oriented or the target asset is missing.

The test should assert:
- `systems == ["projectile", "shooting", "score"]`
- `loop.player_action` contains `launch projectiles`
- assets include `weapon_proxy`, `projectile_proxy`, and `target_proxy`
- `target_proxy.role == "target"` and fallback is `procedural_rings`

- [x] **Step 2: Add a SystemFlags projectile test**

Add a test that calls `system_flags_swift()` with systems `["projectile", "shooting", "score"]`.

Expected before implementation: FAIL because `hasProjectile` and `hasShooting` do not exist yet.

The test should assert:
- `static let hasProjectile = true`
- `static let hasShooting = true`
- `static let hasWeapon = false`
- `static let hasScore = true`

- [x] **Step 3: Add runtime adapter registry and capability tests**

Extend `Tests/test_rkg_custom_realitykit_runtime.py` to require:
- adapter ids `["racing", "projectile", "shooter", "collector"]`
- projectile adapter systems `("projectile", "shooting", "score")`
- state field `var projectileShots: Int = 0`
- rule `static func launchProjectile(_ state: GameSessionState) -> GameSessionState`
- content button `Button("Launch")`
- scene property `projectileEntity`
- capability records returned by `custom_realitykit_adapter_capabilities()`

Expected before implementation: FAIL because the projectile adapter and capability API do not exist.

- [x] **Step 4: Add generated Swift projectile skeleton test**

Add a `custom_projectile_spec()` fixture and an `init-game` test that asserts generated files contain:
- `var projectileShots: Int = 0`
- `var projectileHits: Int = 0`
- `static let hasProjectile = true`
- `static func launchProjectile(_ state: GameSessionState) -> GameSessionState`
- `Button("Launch")`
- `private var projectileEntity: Entity?`
- `private var targetEntity: Entity?`
- `func updateProjectile(state: GameSessionState)`

Expected before implementation: FAIL because the generated Swift runtime has no projectile adapter.

### Task 2: Implement Projectile Runtime Coverage

**Files:**
- Modify: `src/rkg/spec_templates.py`
- Modify: `src/rkg/runtime_core.py`
- Modify: `src/rkg/custom_realitykit_runtime.py`

- [x] **Step 1: Update `new-game` templates**

Change projectile/shooting-only specs to describe a projectile loop before the generic shooter loop, and add a `target_proxy` asset with role `target` and fallback `procedural_rings`.

- [x] **Step 2: Split projectile flags from weapon flags**

Update `system_flags_swift()` so projectile games produce:

```swift
static let hasWeapon = false
static let hasProjectile = true
static let hasShooting = true
```

Keep shooter specs with `weapon` or `hitscan` mapped to `hasWeapon = true`.

- [x] **Step 3: Add the projectile adapter**

Add `_projectile_runtime_adapter()` to `custom_realitykit_runtime.py`, and register it before shooter:

```python
return (
    _racing_runtime_adapter(),
    _projectile_runtime_adapter(),
    _shooter_runtime_adapter(),
    _collector_runtime_adapter(),
)
```

The adapter should own projectile state, lane/charge rules, launch/advance/screenshot behavior, UI controls, scene entity bindings, and `updateProjectile(state:)`.

- [x] **Step 4: Add the capability matrix API**

Add:

```python
def custom_realitykit_adapter_capabilities() -> list[dict[str, object]]:
    ...
```

Each record must include `id`, `systems`, `state_fields`, `rule_members`, `scene_properties`, and `scene_roles`.

### Task 3: Expose Adapter Capabilities In The CLI

**Files:**
- Modify: `src/rkg/cli.py`
- Modify: `Tests/test_rkg_custom_realitykit_runtime.py` or add a focused CLI test

- [x] **Step 1: Add a `list-adapters` command**

Add:

```bash
rkg list-adapters
rkg list-adapters --json
```

Text output should show one adapter per line, for example:

```text
projectile: projectile, shooting, score
```

JSON output should be the exact capability matrix.

- [x] **Step 2: Verify the CLI command**

Run:

```bash
rtk ./.venv/bin/python -m unittest Tests.test_rkg_custom_realitykit_runtime
```

Expected after implementation: PASS.

### Task 4: Generated Project Verification

**Files:**
- Generated scratch projects under `Build/RKGGenerated/`

- [x] **Step 1: Generate and verify projectile, racing, shooter, and collector projects**

Run `new-game`, `validate-spec`, `init-game`, and `verify-game` for:
- projectile/shooting/score
- racing/lap_timer/collision
- weapon/hitscan/enemies/health/cover
- collect/score/timer

Expected after implementation: all generated projects pass `verify-game`.

### Task 5: Docs, Worklog, And Release Checks

**Files:**
- Modify: `Docs/WORKLOG.md`
- Modify: `Docs/ai-handoff.md`
- Modify: `Docs/features/rkg-game-factory.md`
- Modify: `Docs/CHANGELOG.md` if present

- [x] **Step 1: Document the new goal and coverage**

Record the projectile adapter, capability matrix command, generated project verification, and any remaining limitations.

- [x] **Step 2: Run full verification**

Run:

```bash
rtk ./.venv/bin/python -m unittest
rtk ./.venv/bin/python Tools/rkp.py release-check
```

Expected after implementation: both commands exit 0.

### Task 6: Commit, Push, And Monitor CI

**Files:**
- All changed source, tests, and docs

- [x] **Step 1: Review diff**

Run:

```bash
rtk git status -sb
rtk git diff --stat
```

- [ ] **Step 2: Commit**

Run:

```bash
rtk git add src/rkg Tests Docs
rtk git commit -m "feat: add RKG projectile runtime adapter"
```

- [ ] **Step 3: Push**

Run:

```bash
rtk git push
```

- [ ] **Step 4: Monitor CI**

Run:

```bash
rtk gh run list --limit 5
rtk gh run watch <run-id> --exit-status
```

Expected after implementation: pushed CI completes successfully or any failure is reported with the failing job/log evidence.
