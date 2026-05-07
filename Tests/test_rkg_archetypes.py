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


if __name__ == "__main__":
    unittest.main()
