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
            [
                "target_shooter",
                "lane_dodger",
                "toss_physics",
                "stack_puzzle",
                "wave_defense_lite",
                "fighter_2_5d",
                "flappy_side_scroller",
                "custom_realitykit",
            ],
        )

    def test_describe_archetype_exposes_roles_modules_and_screenshots(self) -> None:
        record = describe_archetype("lane_dodger")

        self.assertEqual(record["id"], "lane_dodger")
        self.assertIn("player", record["required_asset_roles"])
        self.assertIn("GameState", record["runtime_modules"])
        self.assertIn("mid_session", record["screenshot_states"])
        self.assertIn("near_miss", record["screenshot_proofs"])
        self.assertIn("state.nearMisses > 0", record["screenshot_proofs"]["near_miss"])

    def test_fighter_2_5d_exposes_duel_roles_input_and_screenshot_proofs(self) -> None:
        record = describe_archetype("fighter_2_5d")

        self.assertEqual(record["display_name"], "2.5D Fighter")
        self.assertEqual(record["required_asset_roles"], ["player", "opponent", "arena"])
        self.assertIn("tap_swipe", record["input"])
        self.assertIn("hit_vfx", record["optional_asset_roles"])
        self.assertIn("guard_cue", record["optional_asset_roles"])
        self.assertEqual(record["screenshot_states"], ["round_start", "mid_combo", "perfect_dodge", "knockout"])
        self.assertIn("state.comboCount > 0", record["screenshot_proofs"]["mid_combo"])
        self.assertIn("state.isKnockout == true", record["screenshot_proofs"]["knockout"])

    def test_flappy_side_scroller_exposes_flight_roles_input_and_screenshot_proofs(self) -> None:
        record = describe_archetype("flappy_side_scroller")

        self.assertEqual(record["display_name"], "Flappy Side Scroller")
        self.assertEqual(record["required_asset_roles"], ["player", "obstacle", "arena"])
        self.assertIn("tap", record["input"])
        self.assertEqual(
            record["screenshot_states"],
            ["gameplay_start", "mid_flight", "near_gap", "collision", "results"],
        )
        self.assertIn("state.birdY", record["screenshot_proofs"]["mid_flight"])
        self.assertIn("state.isCollision == true", record["screenshot_proofs"]["collision"])

    def test_custom_realitykit_archetype_exposes_composable_surface(self) -> None:
        record = describe_archetype("custom_realitykit")

        self.assertIn("first_person", record["camera"])
        self.assertIn("chase", record["camera"])
        self.assertIn("dual_stick", record["input"])
        self.assertIn("weapon", record["optional_asset_roles"])
        self.assertIn("vehicle", record["optional_asset_roles"])
        self.assertEqual(record["required_asset_roles"], ["player", "arena"])
        self.assertEqual(record["screenshot_states"], ["gameplay_start", "mid_action", "fail_or_hit", "results"])

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


if __name__ == "__main__":
    unittest.main()
