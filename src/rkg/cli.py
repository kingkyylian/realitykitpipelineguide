from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rkg.archetypes import describe_archetype, list_archetypes
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

    list_parser = subparsers.add_parser("list-archetypes", help="List built-in RKG archetypes")
    list_parser.add_argument("--json", action="store_true", help="Print machine-readable archetype records")

    describe = subparsers.add_parser("describe-archetype", help="Describe one RKG archetype")
    describe.add_argument("id", help="Archetype id")
    describe.add_argument("--json", action="store_true", help="Print machine-readable archetype record")

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

    if args.command == "list-archetypes":
        records = list_archetypes()
        if args.json:
            print(json.dumps(records, indent=2, sort_keys=True))
        else:
            for record in records:
                print(f"{record['id']}: {record['mechanic']}")
        return 0

    if args.command == "describe-archetype":
        try:
            record = describe_archetype(args.id)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(record, indent=2, sort_keys=True))
        else:
            print(f"{record['id']}: {record['mechanic']}")
            print("required roles: " + ", ".join(record["required_asset_roles"]))
            print("screenshots: " + ", ".join(record["screenshot_states"]))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
