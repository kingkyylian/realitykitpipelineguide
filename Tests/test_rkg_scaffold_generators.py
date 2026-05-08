import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rkg.scaffold as scaffold


class RkgScaffoldGeneratorTests(unittest.TestCase):
    def test_state_bound_game_view_generator_is_archetype_neutral(self) -> None:
        self.assertTrue(hasattr(scaffold, "_state_bound_game_view_swift"))
        self.assertFalse(hasattr(scaffold, "_lane_dodger_game_view_swift"))

        game_view = scaffold._state_bound_game_view_swift()

        self.assertIn("let state: GameSessionState", game_view)
        self.assertIn("func makeCoordinator() -> Coordinator", game_view)
        self.assertIn("context.coordinator.controller.update(state: state)", game_view)


if __name__ == "__main__":
    unittest.main()
