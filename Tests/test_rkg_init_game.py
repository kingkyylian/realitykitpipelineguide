import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def valid_spec() -> dict:
    return {
        "game": {
            "id": "ring_dash",
            "display_name": "Ring Dash",
            "archetype": "target_shooter",
            "session_seconds": 60,
            "camera": "fixed_non_ar",
            "input": "tap",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap targets before they expire",
            "fail_condition": "time expires",
            "scoring": {"hit": 10, "perfect": 25, "streak_bonus": True},
        },
        "assets": {
            "target_basic": {
                "type": "gameplay_target",
                "role": "target",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_rings",
            },
            "arena_floor": {
                "type": "environment",
                "role": "arena",
                "budget": "800 tris / 512 texture",
                "fallback": "procedural_grid",
            }
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_session", "results"],
        },
    }


def lane_dodger_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "lane_dash"
    spec["game"]["display_name"] = "Lane Dash"
    spec["game"]["archetype"] = "lane_dodger"
    spec["game"]["input"] = "drag"
    spec["loop"]["player_action"] = "drag between lanes to dodge obstacles"
    spec["loop"]["fail_condition"] = "hit an obstacle"
    spec["assets"] = {
        "runner": {
            "type": "character",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "crate": {
            "type": "hazard",
            "role": "obstacle",
            "budget": "900 tris / 512 texture",
            "fallback": "procedural_box",
        },
        "lane_floor": {
            "type": "environment",
            "role": "arena",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_grid",
        },
    }
    spec["release"]["screenshots"] = ["gameplay_start", "mid_session", "near_miss", "results"]
    return spec


def wave_defense_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "wave_gate"
    spec["game"]["display_name"] = "Wave Gate"
    spec["game"]["archetype"] = "wave_defense_lite"
    spec["loop"]["player_action"] = "tap threats before health runs out"
    spec["loop"]["fail_condition"] = "health reaches zero"
    spec["assets"] = {
        "guardian": {
            "type": "character",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "threat": {
            "type": "gameplay_target",
            "role": "target",
            "budget": "1200 tris / 512 texture",
            "fallback": "procedural_sphere",
        },
        "arena_floor": {
            "type": "environment",
            "role": "arena",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_grid",
        },
    }
    spec["release"]["screenshots"] = ["wave_start", "mid_wave", "low_health", "results"]
    return spec


def toss_physics_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "toss_arc"
    spec["game"]["display_name"] = "Toss Arc"
    spec["game"]["archetype"] = "toss_physics"
    spec["game"]["input"] = "drag"
    spec["loop"]["player_action"] = "drag and release toward the scoring zone"
    spec["loop"]["fail_condition"] = "attempts run out"
    spec["assets"] = {
        "thrower": {
            "type": "character",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "ball": {
            "type": "projectile",
            "role": "projectile",
            "budget": "600 tris / 512 texture",
            "fallback": "procedural_sphere",
        },
        "hoop": {
            "type": "gameplay_target",
            "role": "target",
            "budget": "1200 tris / 512 texture",
            "fallback": "procedural_rings",
        },
        "arena_floor": {
            "type": "environment",
            "role": "arena",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_grid",
        },
    }
    spec["release"]["screenshots"] = ["aiming", "mid_flight", "landing", "results"]
    return spec


def stack_puzzle_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "stack_tower"
    spec["game"]["display_name"] = "Stack Tower"
    spec["game"]["archetype"] = "stack_puzzle"
    spec["game"]["input"] = "drag"
    spec["loop"]["player_action"] = "place pieces into a stable tower"
    spec["loop"]["fail_condition"] = "stack collapses"
    spec["assets"] = {
        "block": {
            "type": "gameplay_piece",
            "role": "player",
            "budget": "1000 tris / 512 texture",
            "fallback": "procedural_box",
        },
        "bumper": {
            "type": "hazard",
            "role": "obstacle",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_box",
        },
        "board": {
            "type": "environment",
            "role": "arena",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_grid",
        },
    }
    spec["release"]["screenshots"] = ["first_piece", "mid_stack", "collapse_or_clear", "results"]
    return spec


class RkgInitGameTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def write_spec(self, root: Path, spec: dict) -> Path:
        path = root / "GameSpec.json"
        path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        return path

    def test_init_game_creates_realitykit_project_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())
            output = root / "RingDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "GameSpec.json").exists())
            self.assertTrue((output / "project.yml").exists())
            self.assertTrue((output / "rkp.json").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "RingDashApp.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "ContentView.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "GameView.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "GameState.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "GameRules.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "GameSceneController.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "AssetLoader.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "FallbackFactory.swift").exists())
            self.assertTrue((output / "Sources" / "RingDash" / "ResultView.swift").exists())
            self.assertTrue((output / "Tests" / "test_smoke.py").exists())
            self.assertTrue((output / "Docs" / "store" / "metadata.md").exists())
            self.assertTrue((output / "Docs" / "store" / "review-notes.md").exists())
            self.assertTrue((output / "Docs" / "store" / "privacy.md").exists())
            self.assertTrue((output / "Docs" / "store" / "screenshots.md").exists())
            self.assertTrue((output / "Docs" / "store" / "monetization.md").exists())

    def test_init_game_writes_planned_manifest_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())
            output = root / "RingDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "Tools" / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project"], "Ring Dash")
            self.assertEqual(manifest["assets"][0]["id"], "target_basic")
            self.assertEqual(manifest["assets"][0]["status"], "planned")
            self.assertEqual(manifest["assets"][0]["file"], "target_basic.usdz")
            self.assertEqual(manifest["assets"][0]["fallback"], "procedural_rings")
            self.assertEqual(manifest["assets"][0]["maxTriangles"], 1500)
            self.assertEqual(manifest["assets"][0]["maxTextureSize"], 512)
            self.assertEqual(manifest["assets"][1]["id"], "arena_floor")
            self.assertEqual(manifest["assets"][1]["role"], "arena")

    def test_init_game_writes_store_pack_screenshot_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())
            output = root / "RingDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            screenshots = (output / "Docs" / "store" / "screenshots.md").read_text(encoding="utf-8")
            self.assertIn("| gameplay_start |", screenshots)
            self.assertIn("Docs/screenshots/gameplay_start.jpg", screenshots)
            monetization = (output / "Docs" / "store" / "monetization.md").read_text(encoding="utf-8")
            self.assertIn("Model: paid", monetization)

    def test_init_game_escapes_swift_string_literals_from_spec_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["game"]["display_name"] = 'Ring "Dash"'
            spec["loop"]["player_action"] = "tap targets\nbefore they expire"
            spec_path = self.write_spec(root, spec)
            output = root / "RingDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (output / "Sources" / "RingDash" / "ContentView.swift").read_text(encoding="utf-8")
            self.assertIn('Text("Ring \\"Dash\\"")', content)
            self.assertIn('Text("tap targets\\nbefore they expire")', content)

    def test_init_game_generated_modules_reference_planned_asset_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())
            output = root / "RingDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            game_view = (output / "Sources" / "RingDash" / "GameView.swift").read_text(encoding="utf-8")
            asset_loader = (output / "Sources" / "RingDash" / "AssetLoader.swift").read_text(encoding="utf-8")
            scene_controller = (output / "Sources" / "RingDash" / "GameSceneController.swift").read_text(encoding="utf-8")
            fallback_factory = (output / "Sources" / "RingDash" / "FallbackFactory.swift").read_text(encoding="utf-8")
            self.assertIn("GameSceneController()", game_view)
            self.assertNotIn("Entity.load(named:", game_view)
            self.assertIn("try? Entity.load(named: assetId)", asset_loader)
            self.assertIn('loadPrimaryEntity(assetId: "target_basic", role: "target")', scene_controller)
            self.assertNotIn("cameraTransform =", scene_controller)
            self.assertIn("makeFallback(role: String)", fallback_factory)

    def test_init_game_generated_scene_loads_all_declared_required_roles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())
            output = root / "LaneDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            scene_controller = (output / "Sources" / "LaneDash" / "GameSceneController.swift").read_text(encoding="utf-8")
            self.assertIn('loadPrimaryEntity(assetId: "runner", role: "player")', scene_controller)
            self.assertIn('loadPrimaryEntity(assetId: "crate", role: "obstacle")', scene_controller)
            self.assertIn('loadPrimaryEntity(assetId: "lane_floor", role: "arena")', scene_controller)
            self.assertNotIn('FallbackFactory.makeFallback(role: "arena")', scene_controller)

    def test_init_game_generates_wave_defense_state_and_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, wave_defense_spec())
            output = root / "WaveGate"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = (output / "Sources" / "WaveGate" / "GameState.swift").read_text(encoding="utf-8")
            rules = (output / "Sources" / "WaveGate" / "GameRules.swift").read_text(encoding="utf-8")
            self.assertIn("var health: Int = GameRules.startingHealth", state)
            self.assertIn("var wave: Int = 1", state)
            self.assertIn("var threatsRemaining: Int = 0", state)
            self.assertIn("static let startingHealth = 3", rules)
            self.assertIn("static func healthAfterDamage(_ health: Int, damage: Int = 1) -> Int", rules)
            self.assertIn("static func isDefeated(health: Int) -> Bool", rules)
            self.assertIn("static func nextWave(after wave: Int) -> Int", rules)

    def test_init_game_generates_lane_dodger_state_and_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())
            output = root / "LaneDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = (output / "Sources" / "LaneDash" / "GameState.swift").read_text(encoding="utf-8")
            rules = (output / "Sources" / "LaneDash" / "GameRules.swift").read_text(encoding="utf-8")
            self.assertIn("var currentLane: Int = 1", state)
            self.assertIn("var nearMisses: Int = 0", state)
            self.assertIn("var distance: Int = 0", state)
            self.assertIn("static let laneCount = 3", rules)
            self.assertIn("static let nearMissBonus = 5", rules)
            self.assertIn("static func clampedLane(_ lane: Int) -> Int", rules)
            self.assertIn("static func isCollision(playerLane: Int, obstacleLane: Int) -> Bool", rules)
            self.assertIn("static func scoreForDistance(_ distance: Int, nearMisses: Int) -> Int", rules)

    def test_init_game_generates_playable_lane_dodger_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())
            output = root / "LaneDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (output / "Sources" / "LaneDash" / "ContentView.swift").read_text(encoding="utf-8")
            state = (output / "Sources" / "LaneDash" / "GameState.swift").read_text(encoding="utf-8")
            rules = (output / "Sources" / "LaneDash" / "GameRules.swift").read_text(encoding="utf-8")
            self.assertIn("@State private var state = GameSessionState()", content)
            self.assertIn('Text("Score \\(state.score)")', content)
            self.assertIn('Text("Lane \\(state.currentLane + 1)/\\(GameRules.laneCount)")', content)
            self.assertIn('Text("Obstacle \\(state.obstacleLane + 1)")', content)
            self.assertIn("Text(state.lastEvent.capitalized)", content)
            self.assertIn('Button(isPlaying ? "Dodge" : "Start")', content)
            self.assertIn("state = GameRules.startLaneDodgerSession(sessionSeconds: state.sessionSeconds)", content)
            self.assertIn("state = GameRules.advanceLaneDodgerFrame(state)", content)
            self.assertIn('Button("Reset")', content)
            self.assertIn("DragGesture(minimumDistance: 20).onEnded", content)
            self.assertIn("moveLane(value.translation.width > 0 ? 1 : -1)", content)
            self.assertIn("var obstacleLane: Int = 0", state)
            self.assertIn("var isDefeated: Bool = false", state)
            self.assertIn("static func laneAfterMove(currentLane: Int, direction: Int) -> Int", rules)
            self.assertIn("static func nextObstacleLane(after distance: Int) -> Int", rules)
            self.assertIn("static func startLaneDodgerSession(sessionSeconds: Int) -> GameSessionState", rules)
            self.assertIn("static func advanceLaneDodgerFrame(_ state: GameSessionState) -> GameSessionState", rules)
            self.assertIn("static func isNearMiss(playerLane: Int, obstacleLane: Int) -> Bool", rules)
            self.assertIn("next.phase = .result", rules)
            self.assertIn("next.isDefeated = true", rules)
            self.assertIn('next.lastEvent = "hit obstacle"', rules)

    def test_init_game_binds_lane_dodger_state_to_realitykit_scene(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())
            output = root / "LaneDash"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (output / "Sources" / "LaneDash" / "ContentView.swift").read_text(encoding="utf-8")
            game_view = (output / "Sources" / "LaneDash" / "GameView.swift").read_text(encoding="utf-8")
            scene_controller = (output / "Sources" / "LaneDash" / "GameSceneController.swift").read_text(encoding="utf-8")
            self.assertIn("GameView(state: state)", content)
            self.assertIn("let state: GameSessionState", game_view)
            self.assertIn("func makeCoordinator() -> Coordinator", game_view)
            self.assertIn("context.coordinator.controller.update(state: state)", game_view)
            self.assertIn("private var playerEntity: Entity?", scene_controller)
            self.assertIn("private var obstacleEntity: Entity?", scene_controller)
            self.assertIn("playerEntity = runner", scene_controller)
            self.assertIn("obstacleEntity = crate", scene_controller)
            self.assertIn("func update(state: GameSessionState)", scene_controller)
            self.assertIn("playerEntity?.position.x = xPosition(forLane: state.currentLane)", scene_controller)
            self.assertIn("obstacleEntity?.position.x = xPosition(forLane: state.obstacleLane)", scene_controller)
            self.assertIn("private func xPosition(forLane lane: Int) -> Float", scene_controller)

    def test_init_game_generates_toss_physics_state_and_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, toss_physics_spec())
            output = root / "TossArc"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = (output / "Sources" / "TossArc" / "GameState.swift").read_text(encoding="utf-8")
            rules = (output / "Sources" / "TossArc" / "GameRules.swift").read_text(encoding="utf-8")
            self.assertIn("var attemptsRemaining: Int = GameRules.maxAttempts", state)
            self.assertIn("var lastThrowPower: Double = 0", state)
            self.assertIn("var landedInZone: Bool = false", state)
            self.assertIn("static let maxAttempts = 3", rules)
            self.assertIn("static func clampedThrowPower(_ power: Double) -> Double", rules)
            self.assertIn("static func consumeAttempt(_ attemptsRemaining: Int) -> Int", rules)
            self.assertIn("static func scoreForLanding(inZone: Bool, power: Double) -> Int", rules)

    def test_init_game_generates_stack_puzzle_state_and_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, stack_puzzle_spec())
            output = root / "StackTower"

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = (output / "Sources" / "StackTower" / "GameState.swift").read_text(encoding="utf-8")
            rules = (output / "Sources" / "StackTower" / "GameRules.swift").read_text(encoding="utf-8")
            self.assertIn("var piecesPlaced: Int = 0", state)
            self.assertIn("var stablePieces: Int = 0", state)
            self.assertIn("var collapsed: Bool = false", state)
            self.assertIn("static let maxPieces = 8", rules)
            self.assertIn("static func nextPieceIndex(after piecesPlaced: Int) -> Int", rules)
            self.assertIn("static func isStable(stablePieces: Int, piecesPlaced: Int) -> Bool", rules)
            self.assertIn("static func scoreForStack(piecesPlaced: Int, stablePieces: Int) -> Int", rules)

    def test_init_game_refuses_non_empty_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())
            output = root / "RingDash"
            output.mkdir()
            (output / "keep.txt").write_text("keep\n", encoding="utf-8")

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(output))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output directory is not empty", result.stderr)
            self.assertEqual((output / "keep.txt").read_text(encoding="utf-8"), "keep\n")

    def test_init_game_rejects_invalid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            del spec["assets"]["target_basic"]["fallback"]
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(root / "BadGame"))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("assets.target_basic.fallback is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
