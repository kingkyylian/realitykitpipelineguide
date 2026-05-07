from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rkg.idea_score import load_idea, score_game_idea
from rkg.scaffold import init_game
from rkg.spec import GameSpecError, load_game_spec


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="rkg",
        description="RealityKit Game Factory CLI for spec-driven game scaffolding.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-game", help="Create a new RealityKit game from a GameSpec")
    init.add_argument("spec", help="Path to GameSpec.json or GameSpec.yaml")
    init.add_argument("--output", required=True, help="Output game directory")
    init.add_argument("--force", action="store_true", help="Overwrite known generated files in the output directory")

    score_idea = subparsers.add_parser("score-idea", help="Evaluate a game idea before scaffolding")
    score_idea.add_argument("idea", help="Path to idea JSON or YAML")
    score_idea.add_argument("--json", action="store_true", help="Print machine-readable score output")

    args = parser.parse_args()

    if args.command == "init-game":
        try:
            spec = load_game_spec(Path(args.spec))
            init_game(spec, Path(args.output), force=args.force)
        except (GameSpecError, OSError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"initialized rkg game: {Path(args.output).resolve()}")
        return 0

    if args.command == "score-idea":
        try:
            result = score_game_idea(load_idea(Path(args.idea)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(f"score: {result.score}")
            print(f"verdict: {result.verdict}")
            if result.issues:
                print("issues:")
                for issue in result.issues:
                    print(f"- {issue}")
            if result.strengths:
                print("strengths:")
                for strength in result.strengths:
                    print(f"- {strength}")
        return 1 if result.verdict == "reject" else 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
