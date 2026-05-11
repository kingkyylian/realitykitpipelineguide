# RKG Fighter Zero-to-Skeleton Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. In Codex, use `executing-plans` inline unless the user explicitly asks for subagents or parallel agent work. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A fresh user can create, verify, and screenshot-capture a RealityKit-backed `fighter_2_5d` game skeleton without hand-writing a GameSpec.

**Architecture:** Keep RKG as the experimental factory layer and RKP as the asset acceptance source of truth. Add a generated spec path, role asset briefs, and simulator screenshot automation around the existing `init-game`, `verify-game`, and `verify-screenshots` gates instead of replacing them.

**Tech Stack:** Python CLI (`Tools/rkg.py`, `src/rkg`), SwiftUI + RealityKit generated projects, XcodeGen, `xcodebuild`, `xcrun simctl`, local `unittest`.

---

## Current Baseline

Today the fighter path can generate and verify a skeleton if the user already has a valid `GameSpec.json`.

Known good evidence:

- `fighter_2_5d` archetype exists with `player`, `opponent`, `arena`, optional `hit_vfx`, `guard_cue`, `telegraph`, `ui_prop`, and `environment` roles.
- Generated fighter runtime has attack, dodge, damage test input, health, combo, guard meter, knockout/result state, hit VFX binding, guard cue binding, and launch-state screenshot seeding.
- `qa-plan --json` emits `launch_arg --rkg-screenshot-state <state>` for fighter screenshots.
- `verify-screenshots` verifies captured files, but does not drive simulator capture.

Main gaps:

1. A zero-context user must still hand-write or copy a fighter GameSpec.
2. Generated projects do not write role-specific asset briefs, so the next RKP asset step is not obvious.
3. Screenshot capture is documented but not automated by RKG.
4. `verify-screenshots` can accept tiny header-only image files; it should distinguish real simulator screenshots from placeholder bytes.
5. Public docs do not yet show a single fresh-user fighter walkthrough.

## Target User Flow

After this plan:

```bash
rtk .venv/bin/python Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter/GameSpec.json
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-fighter/GameSpec.json
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter/GameSpec.json --output Build/rkg-fighter/NeonRingDuel --force
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter/NeonRingDuel
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-fighter/NeonRingDuel --device booted
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter/NeonRingDuel
```

Expected result:

- Generated RealityKit project exists.
- GameSpec, manifest, Xcode project, Swift runtime files, store pack, asset briefs, and screenshot evidence exist.
- `verify-game` passes.
- `verify-screenshots` passes only after real-size screenshots exist.

---

### Task 1: Generate Fighter GameSpec From Archetype

**Files:**
- Create: `src/rkg/spec_templates.py`
- Create: `Tests/test_rkg_new_spec.py`
- Modify: `src/rkg/cli.py`
- Modify: `Docs/game-spec.md`
- Modify: `Docs/game-factory.md`

- [ ] **Step 1: Write the failing CLI test**

Create `Tests/test_rkg_new_spec.py`:

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkgNewSpecTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_new_spec_writes_valid_fighter_game_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"

            result = self.run_rkg(
                root,
                "new-spec",
                "fighter_2_5d",
                "--title",
                "Neon Ring Duel",
                "--output",
                str(spec_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "neon_ring_duel")
            self.assertEqual(spec["game"]["display_name"], "Neon Ring Duel")
            self.assertEqual(spec["game"]["archetype"], "fighter_2_5d")
            self.assertEqual(spec["game"]["input"], "tap_swipe")
            self.assertEqual(spec["assets"]["fighter_player"]["role"], "player")
            self.assertEqual(spec["assets"]["fighter_opponent"]["role"], "opponent")
            self.assertEqual(spec["assets"]["duel_arena"]["role"], "arena")
            self.assertEqual(spec["release"]["screenshots"], ["round_start", "mid_combo", "perfect_dodge", "knockout"])

    def test_new_spec_refuses_unknown_archetype(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg(root, "new-spec", "open_world_mmo", "--title", "Too Big", "--output", "GameSpec.json")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown archetype", result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_new_spec
```

Expected:

```text
error: argument command: invalid choice: 'new-spec'
FAILED
```

- [ ] **Step 3: Add `src/rkg/spec_templates.py`**

Create `src/rkg/spec_templates.py`:

```python
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from rkg.archetypes import describe_archetype


JsonDict = dict[str, Any]


def slug_id(title: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return value or "untitled_game"


def build_spec_template(archetype_id: str, title: str) -> JsonDict:
    archetype = describe_archetype(archetype_id)
    if archetype["id"] == "fighter_2_5d":
        return _fighter_spec(title)
    raise ValueError(f"unknown archetype template: {archetype_id}")


def _fighter_spec(title: str) -> JsonDict:
    game_id = slug_id(title)
    return {
        "game": {
            "id": game_id,
            "display_name": title,
            "archetype": "fighter_2_5d",
            "session_seconds": 90,
            "camera": "fixed_non_ar",
            "input": "tap_swipe",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap attack, swipe dodge, and time guard windows",
            "fail_condition": "fighter health reaches zero",
            "scoring": {"hit": 10, "perfect": 25, "knockout": 100},
        },
        "assets": {
            "fighter_player": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "fighter_opponent": {
                "type": "gameplay_actor",
                "role": "opponent",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "duel_arena": {
                "type": "environment",
                "role": "arena",
                "budget": "900 tris / 512 texture",
                "fallback": "procedural_lane",
            },
            "hit_spark": {
                "type": "vfx",
                "role": "hit_vfx",
                "budget": "300 tris / procedural material",
                "fallback": "procedural_spark",
            },
            "guard_ring": {
                "type": "gameplay_cue",
                "role": "guard_cue",
                "budget": "400 tris / 512 texture",
                "fallback": "procedural_ring",
            },
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["round_start", "mid_combo", "perfect_dodge", "knockout"],
        },
    }
```

- [ ] **Step 4: Wire the `new-spec` CLI command**

Modify `src/rkg/cli.py`:

```python
from rkg.spec_templates import build_spec_template
```

Add parser:

```python
    new_spec = subparsers.add_parser("new-spec", help="Write a starter GameSpec for an archetype")
    new_spec.add_argument("archetype", help="Archetype id")
    new_spec.add_argument("--title", required=True, help="Display title for the generated game")
    new_spec.add_argument("--output", required=True, help="Output GameSpec.json path")
```

Add command branch before `init-game`:

```python
    if args.command == "new-spec":
        try:
            payload = build_spec_template(args.archetype, args.title)
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except (OSError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"wrote GameSpec: {Path(args.output)}")
        return 0
```

- [ ] **Step 5: Run targeted tests**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_new_spec Tests.test_rkg_validate_spec
```

Expected:

```text
OK
```

- [ ] **Step 6: Update docs**

In `Docs/game-spec.md`, add a short “Generate a starter spec” section:

```markdown
## Starter Specs

Use `rkg new-spec` when starting from zero instead of hand-writing `GameSpec.json`.

```bash
python3 Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output GameSpec.json
python3 Tools/rkg.py validate-spec GameSpec.json
```
```

In `Docs/game-factory.md`, add the command to the preflight sequence before `validate-spec`.

- [ ] **Step 7: Commit**

```bash
rtk git add src/rkg/spec_templates.py src/rkg/cli.py Tests/test_rkg_new_spec.py Docs/game-spec.md Docs/game-factory.md
rtk git commit -m "feat: add rkg starter specs"
```

---

### Task 2: Write Role Asset Briefs During `init-game`

**Files:**
- Create: `src/rkg/asset_briefs.py`
- Modify: `src/rkg/scaffold.py`
- Modify: `Tests/test_rkg_init_game.py`
- Modify: `Docs/rkg-architecture.md`

- [ ] **Step 1: Write the failing test**

Append to `Tests/test_rkg_init_game.py`:

```python
    def test_init_game_writes_role_asset_briefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, fighter_spec())
            output = root / "NeonRingDuel"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            player_brief = output / "Docs" / "assets" / "fighter_player.md"
            opponent_brief = output / "Docs" / "assets" / "fighter_opponent.md"
            self.assertTrue(player_brief.exists())
            self.assertTrue(opponent_brief.exists())
            text = player_brief.read_text(encoding="utf-8")
            self.assertIn("# Asset Brief: fighter_player", text)
            self.assertIn("- Role: player", text)
            self.assertIn("- Fallback: procedural_capsule", text)
            self.assertIn("- [ ] Runtime screenshot evidence captured before imported status.", text)
```

- [ ] **Step 2: Run the failing test**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_writes_role_asset_briefs
```

Expected:

```text
AssertionError: False is not true
```

- [ ] **Step 3: Add asset brief generator**

Create `src/rkg/asset_briefs.py`:

```python
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def asset_brief(asset_id: str, asset: Mapping[str, Any]) -> str:
    role = str(asset.get("role") or asset.get("type") or "prop")
    asset_type = str(asset.get("type") or "prop")
    budget = str(asset.get("budget") or "1500 tris / 512 texture")
    fallback = str(asset.get("fallback") or "procedural_fallback")
    return f"""# Asset Brief: {asset_id}

## Gameplay Need

Provide the `{role}` role for the generated RealityKit game while keeping the procedural fallback available until imported art is accepted.

## Contract

- Asset id: {asset_id}
- Type: {asset_type}
- Role: {role}
- Budget: {budget}
- Fallback: {fallback}
- Runtime file: `Assets/Imported/{asset_id}.usdz`
- Scale: 1 Blender unit = 1 meter
- Origin: centered for runtime placement unless this brief is updated
- Collision: match gameplay role, not raw mesh bounds

## Acceptance Checklist

- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.
- [ ] Manifest entry remains aligned with this role and budget.
- [ ] `rkp inspect-usdz {asset_id} --json` passes.
- [ ] Runtime screenshot evidence captured before imported status.
- [ ] `rkp accept-asset {asset_id} --screenshot <path>` passes.
"""
```

- [ ] **Step 4: Write briefs from scaffold**

Modify `src/rkg/scaffold.py`:

```python
from rkg.asset_briefs import asset_brief
```

Inside `init_game`, after manifest write:

```python
    for asset_id, asset in spec["assets"].items():
        _write_text(output / "Docs" / "assets" / f"{asset_id}.md", asset_brief(str(asset_id), asset))
```

- [ ] **Step 5: Run targeted tests**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_writes_role_asset_briefs Tests.test_rkg_init_game.RkgInitGameTests.test_init_game_generates_fighter_state_and_rules
```

Expected:

```text
OK
```

- [ ] **Step 6: Update architecture doc**

In `Docs/rkg-architecture.md`, update the scaffold output responsibility:

```markdown
Generated projects also write `Docs/assets/<asset_id>.md` for every declared role. These are not acceptance records; they are RKP handoff briefs for the later asset import loop.
```

- [ ] **Step 7: Commit**

```bash
rtk git add src/rkg/asset_briefs.py src/rkg/scaffold.py Tests/test_rkg_init_game.py Docs/rkg-architecture.md
rtk git commit -m "feat: write rkg role asset briefs"
```

---

### Task 3: Add Dry-Run Screenshot Capture Planning Command

**Files:**
- Create: `src/rkg/capture.py`
- Create: `Tests/test_rkg_capture.py`
- Modify: `src/rkg/cli.py`
- Modify: `Docs/rkg-architecture.md`

- [ ] **Step 1: Write the failing dry-run test**

Create `Tests/test_rkg_capture.py`:

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fighter_spec() -> dict:
    return {
        "game": {
            "id": "neon_ring_duel",
            "display_name": "Neon Ring Duel",
            "archetype": "fighter_2_5d",
            "session_seconds": 90,
            "camera": "fixed_non_ar",
            "input": "tap_swipe",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap attack and swipe dodge",
            "fail_condition": "fighter health reaches zero",
            "scoring": {"hit": 10, "perfect": 25, "knockout": 100},
        },
        "assets": {
            "fighter_player": {"type": "gameplay_actor", "role": "player", "budget": "1800 tris / 512 texture", "fallback": "procedural_capsule"},
            "fighter_opponent": {"type": "gameplay_actor", "role": "opponent", "budget": "1800 tris / 512 texture", "fallback": "procedural_capsule"},
            "duel_arena": {"type": "environment", "role": "arena", "budget": "900 tris / 512 texture", "fallback": "procedural_lane"},
        },
        "release": {"devices": ["iPhone 15"], "screenshots": ["round_start", "mid_combo", "perfect_dodge", "knockout"]},
    }


class RkgCaptureTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_capture_screenshots_dry_run_lists_fighter_launch_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"
            spec_path.write_text(json.dumps(fighter_spec(), indent=2) + "\n", encoding="utf-8")
            project = root / "NeonRingDuel"
            init_result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(project))
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = self.run_rkg(root, "capture-screenshots", str(project), "--device", "booted", "--dry-run", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["project"], str(project))
            self.assertEqual(payload["device"], "booted")
            self.assertEqual(payload["steps"][1]["state"], "mid_combo")
            self.assertIn("--rkg-screenshot-state", payload["steps"][1]["launch"])
            self.assertTrue(payload["steps"][1]["screenshot"].endswith("Docs/screenshots/mid_combo.jpg"))
```

- [ ] **Step 2: Run the failing test**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_capture
```

Expected:

```text
invalid choice: 'capture-screenshots'
FAILED
```

- [ ] **Step 3: Add capture plan builder**

Create `src/rkg/capture.py`:

```python
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.qa_plan import build_qa_plan
from rkg.spec import load_game_spec


JsonDict = dict[str, Any]


def build_capture_plan(project: Path, *, device: str) -> JsonDict:
    project = project.resolve()
    spec = load_game_spec(project / "GameSpec.json")
    qa = build_qa_plan(spec)
    swift_name = _swift_name(str(spec["game"]["id"]))
    bundle_id = "com.kyylian." + "".join(ch for ch in str(spec["game"]["id"]).lower() if ch.isalnum())
    app_path = project / "Build" / "DerivedData" / "Build" / "Products" / "Debug-iphonesimulator" / f"{swift_name}.app"
    steps = []
    for step in qa["steps"]:
        state = str(step["state"])
        capture_path = project / str(step["capture_path"])
        steps.append(
            {
                "order": step["order"],
                "state": state,
                "launch": ["xcrun", "simctl", "launch", "--terminate-running-process", device, bundle_id, "--rkg-screenshot-state", state],
                "screenshot": str(capture_path),
            }
        )
    return {
        "project": str(project),
        "device": device,
        "build": [
            "xcodebuild",
            "-quiet",
            "-project",
            f"{swift_name}.xcodeproj",
            "-scheme",
            swift_name,
            "-destination",
            "generic/platform=iOS Simulator",
            "-derivedDataPath",
            "Build/DerivedData",
            "build",
        ],
        "install": ["xcrun", "simctl", "install", device, str(app_path)],
        "steps": steps,
    }


def _swift_name(game_id: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in game_id.split("_") if part)
```

- [ ] **Step 4: Wire dry-run CLI**

Modify `src/rkg/cli.py`:

```python
from rkg.capture import build_capture_plan
```

Add parser:

```python
    capture = subparsers.add_parser("capture-screenshots", help="Capture generated screenshot states on a simulator")
    capture.add_argument("project", help="Path to generated game directory")
    capture.add_argument("--device", default="booted", help="Simulator UDID or 'booted'")
    capture.add_argument("--dry-run", action="store_true", help="Print planned commands without running them")
    capture.add_argument("--json", action="store_true", help="Print machine-readable capture plan")
```

Add command branch:

```python
    if args.command == "capture-screenshots":
        try:
            payload = build_capture_plan(Path(args.project), device=args.device)
        except (OSError, GameSpecError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"capture plan: {payload['project']}")
            print("build: " + " ".join(payload["build"]))
            print("install: " + " ".join(payload["install"]))
            for step in payload["steps"]:
                print(f"{step['order']}. {step['state']}: {' '.join(step['launch'])}")
                print(f"   screenshot: {step['screenshot']}")
        if not args.dry_run:
            print("error: capture execution is not implemented until Task 4; pass --dry-run", file=sys.stderr)
            return 1
        return 0
```

- [ ] **Step 5: Run targeted tests**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_capture Tests.test_rkg_qa_plan
```

Expected:

```text
OK
```

- [ ] **Step 6: Commit**

```bash
rtk git add src/rkg/capture.py src/rkg/cli.py Tests/test_rkg_capture.py Docs/rkg-architecture.md
rtk git commit -m "feat: plan rkg screenshot capture"
```

---

### Task 4: Execute Simulator Screenshot Capture

**Files:**
- Modify: `src/rkg/capture.py`
- Modify: `src/rkg/cli.py`
- Modify: `Tests/test_rkg_capture.py`
- Modify: `Docs/game-factory.md`

- [ ] **Step 1: Add unit test with fake runner**

Append to `Tests/test_rkg_capture.py`:

```python
    def test_capture_execution_runs_build_install_launch_and_screenshot_steps(self) -> None:
        from rkg.capture import execute_capture_plan

        plan = {
            "project": "/tmp/Generated",
            "device": "booted",
            "build": ["xcodebuild", "build"],
            "install": ["xcrun", "simctl", "install", "booted", "App.app"],
            "steps": [
                {
                    "order": 1,
                    "state": "round_start",
                    "launch": ["xcrun", "simctl", "launch", "booted", "com.example.game", "--rkg-screenshot-state", "round_start"],
                    "screenshot": "/tmp/Generated/Docs/screenshots/round_start.jpg",
                }
            ],
        }
        calls = []

        def fake_runner(command, cwd):
            calls.append((command, cwd))
            return 0

        result = execute_capture_plan(plan, runner=fake_runner, sleep_seconds=0)

        self.assertTrue(result["ok"])
        self.assertEqual(calls[0][0], ["xcodebuild", "build"])
        self.assertEqual(calls[1][0], ["xcrun", "simctl", "install", "booted", "App.app"])
        self.assertEqual(calls[2][0][-1], "round_start")
        self.assertEqual(calls[3][0], ["xcrun", "simctl", "io", "booted", "screenshot", "/tmp/Generated/Docs/screenshots/round_start.jpg"])
```

- [ ] **Step 2: Run the failing test**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_capture.RkgCaptureTests.test_capture_execution_runs_build_install_launch_and_screenshot_steps
```

Expected:

```text
ImportError: cannot import name 'execute_capture_plan'
```

- [ ] **Step 3: Implement execution helper**

Modify `src/rkg/capture.py`:

```python
import subprocess
import time
from collections.abc import Callable
```

Add:

```python
CommandRunner = Callable[[list[str], Path], int]


def execute_capture_plan(
    plan: Mapping[str, Any],
    *,
    runner: CommandRunner | None = None,
    sleep_seconds: float = 1.0,
) -> JsonDict:
    project = Path(str(plan["project"]))
    run = runner or _run_command
    commands = [list(plan["build"]), list(plan["install"])]
    for step in plan["steps"]:
        commands.append(list(step["launch"]))
        commands.append(["xcrun", "simctl", "io", str(plan["device"]), "screenshot", str(step["screenshot"])])
    completed = []
    for command in commands:
        exit_code = run(command, project)
        completed.append({"command": command, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}
        if command[:4] == ["xcrun", "simctl", "launch", "--terminate-running-process"]:
            time.sleep(sleep_seconds)
    return {"ok": True, "completed": completed}


def _run_command(command: list[str], cwd: Path) -> int:
    return subprocess.run(command, cwd=cwd).returncode
```

- [ ] **Step 4: Wire execution into CLI**

Modify `src/rkg/cli.py`:

```python
from rkg.capture import build_capture_plan, execute_capture_plan
```

Replace the non-dry-run error branch:

```python
        if args.dry_run:
            return 0
        result = execute_capture_plan(payload)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            for completed in result["completed"]:
                print(("ok" if completed["exit_code"] == 0 else "fail") + ": " + " ".join(completed["command"]))
        return 0 if result["ok"] else 1
```

- [ ] **Step 5: Run targeted tests**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_capture
```

Expected:

```text
OK
```

- [ ] **Step 6: Run a real fighter capture smoke**

Use the current booted simulator:

```bash
rtk .venv/bin/python Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter-capture/GameSpec.json
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-capture/GameSpec.json --output Build/rkg-fighter-capture/NeonRingDuel --force
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-capture/NeonRingDuel
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-fighter-capture/NeonRingDuel --device booted
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter-capture/NeonRingDuel
```

Expected:

```text
verify-game ok
screenshot status: Neon Ring Duel (neon_ring_duel)
1. round_start: ok -> Docs/screenshots/round_start.jpg
2. mid_combo: ok -> Docs/screenshots/mid_combo.jpg
3. perfect_dodge: ok -> Docs/screenshots/perfect_dodge.jpg
4. knockout: ok -> Docs/screenshots/knockout.jpg
```

- [ ] **Step 7: Update docs and commit**

Add `capture-screenshots` to `Docs/game-factory.md`.

```bash
rtk git add src/rkg/capture.py src/rkg/cli.py Tests/test_rkg_capture.py Docs/game-factory.md
rtk git commit -m "feat: capture rkg screenshots"
```

---

### Task 5: Harden Screenshot Evidence Validation

**Files:**
- Modify: `src/rkg/screenshot_status.py`
- Modify: `Tests/test_rkg_screenshot_status.py`
- Modify: `Docs/rkg-architecture.md`

- [ ] **Step 1: Write failing tests for tiny fake images**

Add to `Tests/test_rkg_screenshot_status.py`:

```python
    def test_verify_screenshots_rejects_header_only_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.make_project(root)
            fake = project / "Docs" / "screenshots" / "gameplay_start.jpg"
            fake.parent.mkdir(parents=True, exist_ok=True)
            fake.write_bytes(b"\xff\xd8fake\xff\xd9")

            payload = build_screenshot_status_for_project(project)

            first = payload["checks"][0]
            self.assertFalse(payload["ok"])
            self.assertEqual(first["status"], "invalid_dimensions")
```

- [ ] **Step 2: Run failing test**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_screenshot_status
```

Expected:

```text
AssertionError: 'ok' != 'invalid_dimensions'
```

- [ ] **Step 3: Implement PNG/JPEG dimension parser**

In `src/rkg/screenshot_status.py`, add helpers:

```python
def _image_dimensions(data: bytes) -> tuple[int, int] | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data.startswith(b"\xff\xd8"):
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(data):
                return None
            length = int.from_bytes(data[index:index + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2} and index + 7 < len(data):
                height = int.from_bytes(data[index + 3:index + 5], "big")
                width = int.from_bytes(data[index + 5:index + 7], "big")
                return width, height
            index += max(length, 2)
    return None
```

Update the image check so valid headers still require dimensions at least `300x300`:

```python
dimensions = _image_dimensions(data)
if dimensions is None or dimensions[0] < 300 or dimensions[1] < 300:
    status = "invalid_dimensions"
```

- [ ] **Step 4: Run screenshot tests**

```bash
rtk .venv/bin/python -m unittest Tests.test_rkg_screenshot_status
```

Expected:

```text
OK
```

- [ ] **Step 5: Commit**

```bash
rtk git add src/rkg/screenshot_status.py Tests/test_rkg_screenshot_status.py Docs/rkg-architecture.md
rtk git commit -m "fix: require real screenshot dimensions"
```

---

### Task 6: Public Fighter Walkthrough

**Files:**
- Create: `Docs/rkg-fighter-walkthrough.md`
- Modify: `Docs/game-factory.md`
- Modify: `Docs/ai-handoff.md`
- Modify: `Docs/WORKLOG.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write the walkthrough**

Create `Docs/rkg-fighter-walkthrough.md`:

```markdown
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
```

- [ ] **Step 2: Link from game factory docs**

Add to `Docs/game-factory.md` near the fighter archetype section:

```markdown
For the end-to-end fighter skeleton path, see `Docs/rkg-fighter-walkthrough.md`.
```

- [ ] **Step 3: Update handoff and changelog**

In `Docs/ai-handoff.md`, add:

```markdown
| Fighter zero-to-skeleton walkthrough | Complete | `rkg new-spec`, `init-game`, `verify-game`, `capture-screenshots`, `verify-screenshots` |
```

In `CHANGELOG.md`, add:

```markdown
- Added the zero-to-skeleton RKG fighter walkthrough and screenshot capture path.
```

- [ ] **Step 4: Commit**

```bash
rtk git add Docs/rkg-fighter-walkthrough.md Docs/game-factory.md Docs/ai-handoff.md Docs/WORKLOG.md CHANGELOG.md
rtk git commit -m "docs: add rkg fighter walkthrough"
```

---

### Task 7: Final Verification and Push

**Files:**
- No new source files. Verification only.

- [ ] **Step 1: Run full tests**

```bash
rtk .venv/bin/python -m unittest discover -s Tests
```

Expected:

```text
OK
```

- [ ] **Step 2: Run RKP release gate**

```bash
rtk .venv/bin/python Tools/rkp.py release-check
```

Expected:

```text
release-check ok
```

- [ ] **Step 3: Run a fresh fighter walkthrough smoke**

```bash
rtk .venv/bin/python Tools/rkg.py new-spec fighter_2_5d --title "Neon Ring Duel" --output Build/rkg-fighter-final/GameSpec.json
rtk .venv/bin/python Tools/rkg.py validate-spec Build/rkg-fighter-final/GameSpec.json
rtk .venv/bin/python Tools/rkg.py init-game Build/rkg-fighter-final/GameSpec.json --output Build/rkg-fighter-final/NeonRingDuel --force
rtk .venv/bin/python Tools/rkg.py verify-game Build/rkg-fighter-final/NeonRingDuel
rtk .venv/bin/python Tools/rkg.py capture-screenshots Build/rkg-fighter-final/NeonRingDuel --device booted
rtk .venv/bin/python Tools/rkg.py verify-screenshots Build/rkg-fighter-final/NeonRingDuel
```

Expected:

```text
GameSpec ok
initialized rkg game
verify-game ok
screenshot status: Neon Ring Duel (neon_ring_duel)
1. round_start: ok
2. mid_combo: ok
3. perfect_dodge: ok
4. knockout: ok
```

- [ ] **Step 4: Check whitespace and status**

```bash
rtk proxy git diff --check
rtk git status -sb
```

Expected:

```text
no diff-check output
branch ahead only by planned commits
```

- [ ] **Step 5: Push**

```bash
rtk git push
rtk gh run watch <run-id> --exit-status
```

Expected:

```text
CI success
```

---

## Acceptance Checklist

- [ ] Fresh user can generate fighter GameSpec without copying JSON from tests.
- [ ] Generated fighter project includes role-specific asset briefs.
- [ ] Generated fighter project passes `rkg verify-game`.
- [ ] RKG can drive simulator screenshot capture for all fighter screenshot states.
- [ ] `verify-screenshots` rejects placeholder image bytes and accepts real simulator screenshots.
- [ ] Public docs show the exact zero-to-skeleton fighter command flow.
- [ ] Full tests, release-check, simulator screenshot capture, and GitHub CI pass.

## Residual Non-Goals

- No imported fighter character art in this plan.
- No skeletal animation system in this plan.
- No commercial balancing or monetization polish in this plan.
- No App Store submission claim in this plan.

The deliverable is a trustworthy RealityKit fighter skeleton factory path, not a shippable fighting game.
