from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class CiWorkflowTests(unittest.TestCase):
    def test_ci_installs_dev_dependencies_inside_virtualenv(self) -> None:
        workflow = read(".github/workflows/ci.yml")

        self.assertIn("python3 -m venv .venv", workflow)
        self.assertIn(".venv/bin/python -m pip install --upgrade pip", workflow)
        self.assertIn('.venv/bin/python -m pip install -e ".[dev]"', workflow)
        self.assertIn(".venv/bin/python -m ruff check src Tests Tools", workflow)
        self.assertIn(".venv/bin/python -m unittest discover -s Tests", workflow)
        self.assertNotIn('python3 -m pip install -e ".[dev]"', workflow)
