from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rkp.rkp_project import ProjectPaths, load_project


@dataclass(frozen=True)
class CleanupCandidate:
    path: Path
    rel_path: str
    kind: str


def _candidate(project: ProjectPaths, path: Path, kind: str) -> CleanupCandidate:
    return CleanupCandidate(path=path, rel_path=project.rel(path), kind=kind)


def collect_candidates(project: ProjectPaths | None = None) -> list[CleanupCandidate]:
    active_project = project or load_project()
    root = active_project.root
    candidates: list[CleanupCandidate] = []

    for rel in ("Build",):
        path = root / rel
        if path.exists():
            candidates.append(_candidate(active_project, path, "directory"))

    for path in root.rglob("__pycache__"):
        if path.is_dir():
            candidates.append(_candidate(active_project, path, "directory"))

    for path in root.rglob("*.egg-info"):
        if path.is_dir():
            candidates.append(_candidate(active_project, path, "directory"))

    for path in root.rglob(".DS_Store"):
        if path.is_file():
            candidates.append(_candidate(active_project, path, "file"))

    imported = root / "Assets" / "Imported"
    if imported.exists():
        for path in imported.glob("(A Document Being Saved By usdzip*)"):
            if path.is_dir() and not any(path.iterdir()):
                candidates.append(_candidate(active_project, path, "directory"))

    return sorted(candidates, key=lambda candidate: candidate.rel_path)


def apply_candidates(candidates: list[CleanupCandidate]) -> None:
    for candidate in candidates:
        if candidate.path.is_dir():
            shutil.rmtree(candidate.path)
        elif candidate.path.exists():
            candidate.path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="List or remove ignored local RKP scratch files.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="List cleanup candidates without removing them")
    mode.add_argument("--apply", action="store_true", help="Remove cleanup candidates")
    args = parser.parse_args()

    candidates = collect_candidates()
    if not candidates:
        print("clean: no candidates")
        return 0

    for candidate in candidates:
        print(f"{candidate.kind}: {candidate.rel_path}")

    if args.apply:
        apply_candidates(candidates)
        print(f"clean: removed {len(candidates)} candidate(s)")
    else:
        print(f"clean: {len(candidates)} candidate(s), dry run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
