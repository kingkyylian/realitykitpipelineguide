import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class RkpPackageTests(unittest.TestCase):
    def test_make_asset_subprocesses_use_package_modules(self) -> None:
        from rkp import cli

        commands: list[list[str]] = []

        def capture(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 0

        args = Namespace(
            id="portable_module",
            prompt="red target",
            type="gameplay_target",
            build=True,
            screenshot="Docs/screenshots/portable_module.jpg",
            release_check=True,
            force=False,
        )

        with patch.object(cli, "run", side_effect=capture):
            result = cli.run_make_asset(args)

        self.assertEqual(result, 0)
        self.assertEqual(
            commands,
            [
                [
                    sys.executable,
                    "-m",
                    "rkp.prompt_asset",
                    "portable_module",
                    "--prompt",
                    "red target",
                    "--type",
                    "gameplay_target",
                ],
                [sys.executable, "-m", "rkp.build_asset", "--id", "portable_module"],
                [
                    sys.executable,
                    "-m",
                    "rkp.accept_asset",
                    "--id",
                    "portable_module",
                    "--screenshot",
                    "Docs/screenshots/portable_module.jpg",
                ],
                [sys.executable, "-m", "rkp.cli", "release-check"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
