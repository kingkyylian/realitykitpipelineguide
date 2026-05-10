from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "Sources" / "RealityKitPipelineDemo"


class FixtureRefactorTests(unittest.TestCase):
    def test_game_ar_view_delegates_arena_targets_and_hit_effects(self) -> None:
        expected_files = [
            "ArenaBuilder.swift",
            "TargetFactory.swift",
            "HitEffectSystem.swift",
            "RealityMaterials.swift",
        ]
        for file_name in expected_files:
            self.assertTrue((SOURCE_DIR / file_name).exists(), file_name)

        game_ar_view = (SOURCE_DIR / "GameARView.swift").read_text(encoding="utf-8")
        target_factory = (SOURCE_DIR / "TargetFactory.swift").read_text(encoding="utf-8")

        self.assertLess(len(game_ar_view.splitlines()), 500)
        self.assertIn("ArenaBuilder.addShowcaseBackdrop", game_ar_view)
        self.assertIn("ArenaBuilder.addArena", game_ar_view)
        self.assertIn("targetFactory.makeTarget", game_ar_view)
        self.assertIn("hitEffectSystem.add", game_ar_view)

        textured_index = target_factory.index('"target_basic_textured"')
        basic_index = target_factory.index('"target_basic"')
        self.assertLess(textured_index, basic_index)

    def test_material_response_showcase_is_opt_in(self) -> None:
        showcase = SOURCE_DIR / "MaterialResponseShowcase.swift"
        game_ar_view = (SOURCE_DIR / "GameARView.swift").read_text(encoding="utf-8")
        target_factory = (SOURCE_DIR / "TargetFactory.swift").read_text(encoding="utf-8")

        self.assertTrue(showcase.exists())
        text = showcase.read_text(encoding="utf-8")
        self.assertIn('"material_response_targets"', text)
        self.assertIn("ImportedAssetLoader.loadModel", text)
        self.assertIn('"--material-response-mode"', game_ar_view)
        self.assertIn("MaterialResponseShowcase.add", game_ar_view)
        self.assertNotIn('"material_response_targets"', target_factory)


if __name__ == "__main__":
    unittest.main()
