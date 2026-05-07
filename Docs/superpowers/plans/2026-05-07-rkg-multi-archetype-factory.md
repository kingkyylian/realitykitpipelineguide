# RKG Multi-Archetype Factory Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. In Codex, use `executing-plans` inline unless the user explicitly asks for subagents or parallel agent work. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn RKG from a first scaffold command into a reusable multi-archetype RealityKit game factory.

**Architecture:** Add a registry-first RKG core. `GameSpec` validation reads archetype records, `plan-game` previews generation, `init-game` uses shared module contracts, and `verify-game` proves generated projects with command gates. RKP remains the only asset acceptance authority.

**Tech Stack:** Python 3.10+, unittest, SwiftUI, RealityKit, XcodeGen, existing RKP CLI.

---

## File Structure

Create:

- `src/rkg/archetypes.py`: built-in archetype registry and role definitions.
- `src/rkg/plan.py`: dry-run project generation plan model.
- `src/rkg/store_pack.py`: store-pack file content generation.
- `Tests/test_rkg_archetypes.py`: registry command and API tests.
- `Tests/test_rkg_plan_game.py`: `plan-game` behavior tests.
- `Tests/test_rkg_validate_spec.py`: CLI validation tests.

Modify:

- `src/rkg/spec.py`: validate `game.archetype`, asset roles, and screenshot states against the registry.
- `src/rkg/scaffold.py`: generate module-based Swift layout.
- `src/rkg/cli.py`: add `list-archetypes`, `describe-archetype`, `validate-spec`, `plan-game`, and later `verify-game`.
- `Tests/test_rkg_init_game.py`: assert generated module layout and role fallback wiring.
- `Docs/rkg-architecture.md`: keep contracts current after code lands.
- `Docs/game-factory.md`: link to the architecture doc and keep high-level only.
- `Docs/WORKLOG.md`: append sprint records after each task group.

## Task 1: Archetype Registry

**Files:**

- Create: `src/rkg/archetypes.py`
- Create: `Tests/test_rkg_archetypes.py`
- Modify: `src/rkg/cli.py`

- [ ] **Step 1: Write failing tests**

Add `Tests/test_rkg_archetypes.py`:

```python
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.archetypes import describe_archetype, list_archetypes


class RkgArchetypeTests(unittest.TestCase):
    def run_rkg(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_registry_lists_seed_archetypes(self) -> None:
        ids = [record["id"] for record in list_archetypes()]

        self.assertEqual(
            ids,
            ["target_shooter", "lane_dodger", "toss_physics", "stack_puzzle", "wave_defense_lite"],
        )

    def test_describe_archetype_exposes_roles_modules_and_screenshots(self) -> None:
        record = describe_archetype("lane_dodger")

        self.assertEqual(record["id"], "lane_dodger")
        self.assertIn("player", record["required_asset_roles"])
        self.assertIn("GameState", record["runtime_modules"])
        self.assertIn("mid_session", record["screenshot_states"])

    def test_unknown_archetype_raises_clear_error(self) -> None:
        with self.assertRaises(ValueError) as context:
            describe_archetype("city_builder")

        self.assertIn("unknown archetype: city_builder", str(context.exception))

    def test_list_archetypes_cli_prints_json(self) -> None:
        result = self.run_rkg("list-archetypes", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload[0]["id"], "target_shooter")
        self.assertIn("required_asset_roles", payload[0])

    def test_describe_archetype_cli_rejects_unknown_id(self) -> None:
        result = self.run_rkg("describe-archetype", "city_builder", "--json")

        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown archetype: city_builder", result.stderr)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'rkg.archetypes'`.

- [ ] **Step 3: Implement registry**

Create `src/rkg/archetypes.py`:

```python
from __future__ import annotations

from copy import deepcopy
from typing import Any


JsonDict = dict[str, Any]

RUNTIME_MODULES = [
    "GameState",
    "GameRules",
    "GameSceneController",
    "AssetLoader",
    "FallbackFactory",
]

ARCHETYPES: list[JsonDict] = [
    {
        "id": "target_shooter",
        "display_name": "Target Shooter",
        "mechanic": "tap or aim at spawned targets before time expires",
        "input": ["tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["target", "arena"],
        "optional_asset_roles": ["projectile", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["gameplay_start", "mid_session", "results"],
        "scope_risk": "low",
    },
    {
        "id": "lane_dodger",
        "display_name": "Lane Dodger",
        "mechanic": "move between lanes to avoid hazards and collect pickups",
        "input": ["drag", "tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "obstacle", "arena"],
        "optional_asset_roles": ["pickup", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["gameplay_start", "mid_session", "near_miss", "results"],
        "scope_risk": "low",
    },
    {
        "id": "toss_physics",
        "display_name": "Toss Physics",
        "mechanic": "drag and release a physics object toward a scoring zone",
        "input": ["drag"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "projectile", "target", "arena"],
        "optional_asset_roles": ["obstacle", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["aiming", "mid_flight", "landing", "results"],
        "scope_risk": "medium",
    },
    {
        "id": "stack_puzzle",
        "display_name": "Stack Puzzle",
        "mechanic": "place pieces into a stable stack before the session ends",
        "input": ["tap", "drag"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "obstacle", "arena"],
        "optional_asset_roles": ["pickup", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["first_piece", "mid_stack", "collapse_or_clear", "results"],
        "scope_risk": "medium",
    },
    {
        "id": "wave_defense_lite",
        "display_name": "Wave Defense Lite",
        "mechanic": "survive small waves by clearing threats before health runs out",
        "input": ["tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "target", "arena"],
        "optional_asset_roles": ["projectile", "hazard", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["wave_start", "mid_wave", "low_health", "results"],
        "scope_risk": "medium",
    },
]


def list_archetypes() -> list[JsonDict]:
    return deepcopy(ARCHETYPES)


def describe_archetype(archetype_id: str) -> JsonDict:
    for record in ARCHETYPES:
        if record["id"] == archetype_id:
            return deepcopy(record)
    raise ValueError(f"unknown archetype: {archetype_id}")
```

- [ ] **Step 4: Add CLI commands**

Modify `src/rkg/cli.py`:

```python
from rkg.archetypes import describe_archetype, list_archetypes
```

Add parsers:

```python
list_parser = subparsers.add_parser("list-archetypes", help="List built-in RKG archetypes")
list_parser.add_argument("--json", action="store_true", help="Print machine-readable archetype records")

describe = subparsers.add_parser("describe-archetype", help="Describe one RKG archetype")
describe.add_argument("id", help="Archetype id")
describe.add_argument("--json", action="store_true", help="Print machine-readable archetype record")
```

Add handlers before the final help:

```python
if args.command == "list-archetypes":
    records = list_archetypes()
    if args.json:
        print(json.dumps(records, indent=2, sort_keys=True))
    else:
        for record in records:
            print(f"{record['id']}: {record['mechanic']}")
    return 0

if args.command == "describe-archetype":
    try:
        record = describe_archetype(args.id)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(record, indent=2, sort_keys=True))
    else:
        print(f"{record['id']}: {record['mechanic']}")
        print("required roles: " + ", ".join(record["required_asset_roles"]))
        print("screenshots: " + ", ".join(record["screenshot_states"]))
    return 0
```

- [ ] **Step 5: Run tests**

Run:

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_archetypes.py
```

Expected: OK.

- [ ] **Step 6: Commit**

```bash
git add src/rkg/archetypes.py src/rkg/cli.py Tests/test_rkg_archetypes.py
git commit -m "Add RKG archetype registry"
```

## Task 2: Registry-Aware GameSpec Validation

**Files:**

- Modify: `src/rkg/spec.py`
- Create: `Tests/test_rkg_validate_spec.py`
- Modify: `src/rkg/cli.py`
- Modify: `Docs/game-spec.md`

- [ ] **Step 1: Write failing tests**

Add tests that verify:

```python
def test_validate_spec_rejects_unknown_archetype() -> None:
    spec = valid_spec()
    spec["game"]["archetype"] = "city_builder"
    issues = validate_game_spec(spec)
    self.assertIn("game.archetype is not supported: city_builder", issues)

def test_validate_spec_requires_asset_roles_supported_by_archetype() -> None:
    spec = valid_spec()
    spec["assets"]["hero"] = {
        "type": "gameplay_actor",
        "role": "player",
        "budget": "1000 tris / 512 texture",
        "fallback": "procedural_capsule",
    }
    issues = validate_game_spec(spec)
    self.assertIn("assets.hero role player is not used by target_shooter", issues)
```

Add CLI test:

```python
def test_validate_spec_cli_returns_zero_for_valid_spec(self) -> None:
    result = self.run_rkg("validate-spec", str(spec_path), "--json")
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(json.loads(result.stdout)["ok"], True)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py
```

Expected: FAIL because validation is not registry-aware and `validate-spec` does not exist.

- [ ] **Step 3: Implement validation**

In `src/rkg/spec.py`:

- Import `describe_archetype`.
- After required game fields, reject unsupported `game.archetype`.
- If an asset contains `role`, require it to be in required or optional roles for that archetype.
- Keep `role` optional in this task to avoid breaking existing specs.

- [ ] **Step 4: Add CLI**

Add `rkg validate-spec <path> [--json]`:

- Load JSON/YAML.
- Run `validate_game_spec`.
- Print `{"ok": true, "issues": []}` for valid specs.
- Return `1` when issues exist.

- [ ] **Step 5: Update docs**

In `Docs/game-spec.md`, add:

```yaml
assets:
  player_ship:
    type: gameplay_actor
    role: player
    budget: "1200 tris / 512 texture"
    fallback: procedural_capsule
```

State that `role` becomes required when an archetype template needs role-specific generation.

- [ ] **Step 6: Run tests and commit**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py
git add src/rkg/spec.py src/rkg/cli.py Tests/test_rkg_spec.py Tests/test_rkg_validate_spec.py Docs/game-spec.md
git commit -m "Validate GameSpec against archetypes"
```

## Task 3: Dry-Run Game Plan

**Files:**

- Create: `src/rkg/plan.py`
- Create: `Tests/test_rkg_plan_game.py`
- Modify: `src/rkg/cli.py`

- [ ] **Step 1: Write failing tests**

Test expected `plan-game` payload:

```python
payload = build_game_plan(valid_spec())
self.assertEqual(payload["archetype"]["id"], "target_shooter")
self.assertIn("Sources/RingDash/GameState.swift", payload["files"])
self.assertEqual(payload["asset_roles"]["target_basic"], "target")
self.assertIn("gameplay_start", payload["screenshot_states"])
```

Test CLI does not create output:

```python
result = self.run_rkg("plan-game", str(spec_path), "--json")
self.assertEqual(result.returncode, 0, result.stderr)
self.assertFalse((root / "RingDash").exists())
```

- [ ] **Step 2: Run tests to verify failure**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py
```

Expected: FAIL because `rkg.plan` and `plan-game` are missing.

- [ ] **Step 3: Implement planner**

`build_game_plan(spec)` returns:

```json
{
  "game_id": "ring_dash",
  "swift_name": "RingDash",
  "archetype": { "id": "target_shooter" },
  "files": [
    "GameSpec.json",
    "project.yml",
    "Sources/RingDash/GameState.swift"
  ],
  "asset_roles": {
    "target_basic": "target"
  },
  "screenshot_states": ["gameplay_start", "mid_session", "results"]
}
```

- [ ] **Step 4: Add CLI**

Add `rkg plan-game GameSpec.yaml [--json]`.

- [ ] **Step 5: Run tests and commit**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_plan_game.py
git add src/rkg/plan.py src/rkg/cli.py Tests/test_rkg_plan_game.py
git commit -m "Add RKG dry-run game planning"
```

## Task 4: Module-Based Swift Scaffold

**Files:**

- Modify: `src/rkg/scaffold.py`
- Modify: `Tests/test_rkg_init_game.py`

- [ ] **Step 1: Write failing tests**

Extend scaffold tests:

```python
self.assertTrue((output / "Sources" / "RingDash" / "GameState.swift").exists())
self.assertTrue((output / "Sources" / "RingDash" / "GameRules.swift").exists())
self.assertTrue((output / "Sources" / "RingDash" / "AssetLoader.swift").exists())
self.assertTrue((output / "Sources" / "RingDash" / "FallbackFactory.swift").exists())
```

Assert generated `GameView.swift` no longer owns asset loading directly:

```python
content = (output / "Sources" / "RingDash" / "GameView.swift").read_text(encoding="utf-8")
self.assertIn("GameSceneController()", content)
self.assertNotIn("Entity.load(named:", content)
```

- [ ] **Step 2: Run tests to verify failure**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py
```

Expected: FAIL because generated modules do not exist.

- [ ] **Step 3: Generate new modules**

Add templates:

- `GameState.swift`: phase enum and session state.
- `GameRules.swift`: pure scoring/session helper.
- `AssetLoader.swift`: `try? Entity.load(named:)`.
- `FallbackFactory.swift`: role-based primitive fallback.
- `GameSceneController.swift`: scene setup and fallback wiring.
- `ResultView.swift`: minimal result UI.

- [ ] **Step 4: Run tests and commit**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_init_game.py
git add src/rkg/scaffold.py Tests/test_rkg_init_game.py
git commit -m "Generate shared RKG Swift modules"
```

## Task 5: Store Pack Contract

**Files:**

- Create: `src/rkg/store_pack.py`
- Create: `Tests/test_rkg_store_pack.py`
- Modify: `src/rkg/scaffold.py`

- [ ] **Step 1: Write failing tests**

Verify generated files:

```python
self.assertTrue((output / "Docs" / "store" / "screenshots.md").exists())
self.assertTrue((output / "Docs" / "store" / "monetization.md").exists())
screenshots = (output / "Docs" / "store" / "screenshots.md").read_text(encoding="utf-8")
self.assertIn("| gameplay_start |", screenshots)
self.assertIn("Docs/screenshots/gameplay_start.jpg", screenshots)
```

- [ ] **Step 2: Run tests to verify failure**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py
```

Expected: FAIL because screenshot/monetization store files are not generated.

- [ ] **Step 3: Implement store pack generator**

Move metadata, review, privacy, screenshots, and monetization draft content into `src/rkg/store_pack.py`.

- [ ] **Step 4: Run tests and commit**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py
git add src/rkg/store_pack.py src/rkg/scaffold.py Tests/test_rkg_store_pack.py Tests/test_rkg_init_game.py
git commit -m "Generate RKG store pack checklist"
```

## Task 6: Generated Game Verification

**Files:**

- Create: `src/rkg/verify.py`
- Create: `Tests/test_rkg_verify_game.py`
- Modify: `src/rkg/cli.py`

- [ ] **Step 1: Write failing tests**

Verify missing project fails clearly:

```python
result = self.run_rkg("verify-game", str(root / "MissingGame"))
self.assertEqual(result.returncode, 1)
self.assertIn("generated project does not exist", result.stderr)
```

Verify command plan can be mocked:

```python
commands = verification_commands(output)
self.assertIn(["python3", "Tools/rkp.py", "doctor"], commands)
```

- [ ] **Step 2: Run tests to verify failure**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_verify_game.py
```

Expected: FAIL because `verify-game` is missing.

- [ ] **Step 3: Implement command-only verification**

`verify-game` should:

- Confirm `GameSpec.json`, `rkp.json`, `project.yml`, and `Tools/asset_manifest.json` exist.
- Run generated project tests if `Tests/` exists.
- Run `python3 Tools/rkp.py doctor`.
- Run `python3 Tools/rkp.py release-check`.

- [ ] **Step 4: Run tests and commit**

```bash
/opt/homebrew/bin/python3.12 -m unittest Tests/test_rkg_verify_game.py
git add src/rkg/verify.py src/rkg/cli.py Tests/test_rkg_verify_game.py
git commit -m "Add RKG generated game verification"
```

## Final Verification

Run after all tasks:

```bash
/opt/homebrew/bin/python3.12 -m unittest discover -s Tests
/opt/homebrew/bin/python3.12 -m compileall -q src Tools Tests
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
/opt/homebrew/bin/python3.12 Tools/rkp.py doctor
/opt/homebrew/bin/python3.12 Tools/rkp.py release-check
```

Expected:

```text
unittest: OK
compileall: no output, exit 0
manifest ok
pipeline doctor: ok
release-check ok
```

CoreSimulator warnings during Xcode build are acceptable only when `release-check ok` is printed.

## Self-Review

Spec coverage:

- Multi-archetype direction: Task 1.
- Asset role taxonomy and registry: Tasks 1 and 2.
- Shared runtime state and Swift module plan: Task 4.
- CLI roadmap: Tasks 1, 2, 3, and 6.
- Generated project verification: Task 6.
- Store pack contract: Task 5.
- Decision rule and docs: tracked in `Docs/rkg-architecture.md`.

Placeholder scan:

- No `TBD`, `TODO`, or unspecified test steps remain.

Type consistency:

- Registry records use `id`, `required_asset_roles`, `optional_asset_roles`, `runtime_modules`, and `screenshot_states`.
- GameSpec validation and planner should use the same field names.
