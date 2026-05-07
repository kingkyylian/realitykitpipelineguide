import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.verify import required_project_files, verification_commands, verify_game


class RkgVerifyGameTests(unittest.TestCase):
    def run_rkg(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def make_generated_project(self, root: Path) -> Path:
        output = root / "RingDash"
        (output / "Tools").mkdir(parents=True)
        (output / "Tests").mkdir()
        (output / "Tests" / "test_smoke.py").write_text(
            "import unittest\n\nclass SmokeTests(unittest.TestCase):\n    def test_smoke(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        for rel_path in required_project_files():
            path = output / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel_path.suffix == ".json":
                path.write_text(json.dumps({}) + "\n", encoding="utf-8")
            else:
                path.write_text("generated\n", encoding="utf-8")
        return output

    def test_verify_game_cli_rejects_missing_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg("verify-game", str(root / "MissingGame"))

            self.assertEqual(result.returncode, 1)
            self.assertIn("generated project does not exist", result.stderr)

    def test_verification_commands_include_tests_doctor_and_release_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = self.make_generated_project(Path(tmp))

            commands = verification_commands(output)

            self.assertIn([sys.executable, "-m", "unittest", "discover", "-s", "Tests"], commands)
            self.assertIn(["rkp", "doctor"], commands)
            self.assertIn(["rkp", "release-check"], commands)

    def test_verify_game_reports_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = self.make_generated_project(Path(tmp))
            (output / "project.yml").unlink()

            result = verify_game(output)

            self.assertEqual(result, 1)

    def test_verify_game_runs_command_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = self.make_generated_project(Path(tmp))
            calls: list[list[str]] = []

            def capture(command: list[str], cwd: Path) -> int:
                calls.append(command)
                return 0

            with patch("rkg.verify.run_command", side_effect=capture):
                result = verify_game(output)

            self.assertEqual(result, 0)
            self.assertEqual(calls, verification_commands(output))

    def test_verification_commands_skip_empty_tests_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = self.make_generated_project(Path(tmp))
            (output / "Tests" / "test_smoke.py").unlink()

            commands = verification_commands(output)

            self.assertNotIn([sys.executable, "-m", "unittest", "discover", "-s", "Tests"], commands)


if __name__ == "__main__":
    unittest.main()
