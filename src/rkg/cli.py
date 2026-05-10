from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rkg.archetypes import describe_archetype, list_archetypes
from rkg.idea_score import load_idea, score_game_idea
from rkg.plan import build_game_plan
from rkg.qa_plan import build_qa_plan
from rkg.scaffold import init_game
from rkg.screenshot_status import build_screenshot_status, build_screenshot_status_for_project, load_qa_plan
from rkg.spec import GameSpecError, load_game_spec, validate_game_spec
from rkg.verify import verify_game


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

    validate = subparsers.add_parser("validate-spec", help="Validate a GameSpec against RKG rules")
    validate.add_argument("spec", help="Path to GameSpec.json or GameSpec.yaml")
    validate.add_argument("--json", action="store_true", help="Print machine-readable validation result")

    plan_game = subparsers.add_parser("plan-game", help="Preview generated game files without writing output")
    plan_game.add_argument("spec", help="Path to GameSpec.json or GameSpec.yaml")
    plan_game.add_argument("--json", action="store_true", help="Print machine-readable game plan")

    qa_plan = subparsers.add_parser("qa-plan", help="Print screenshot capture QA steps without writing output")
    qa_plan.add_argument("spec", help="Path to GameSpec.json or GameSpec.yaml")
    qa_plan.add_argument("--json", action="store_true", help="Print machine-readable screenshot QA plan")

    verify_screenshots = subparsers.add_parser("verify-screenshots", help="Verify generated screenshot evidence files")
    verify_screenshots.add_argument("project", help="Path to generated game directory")
    verify_screenshots.add_argument("--plan", help="Path to qa-plan JSON from `rkg qa-plan --json`")
    verify_screenshots.add_argument("--json", action="store_true", help="Print machine-readable screenshot status")

    verify = subparsers.add_parser("verify-game", help="Run verification gates for a generated RKG project")
    verify.add_argument("project", help="Path to generated game directory")

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

    if args.command == "validate-spec":
        try:
            issues = validate_game_spec(load_game_spec(Path(args.spec)))
        except (OSError, GameSpecError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = {"ok": not issues, "issues": issues}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif issues:
            print("invalid GameSpec")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("GameSpec ok")
        return 1 if issues else 0

    if args.command == "plan-game":
        try:
            payload = build_game_plan(load_game_spec(Path(args.spec)))
        except (OSError, GameSpecError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"game: {payload['display_name']} ({payload['game_id']})")
            print(f"archetype: {payload['archetype']['id']}")
            print("files:")
            for file_path in payload["files"]:
                print(f"- {file_path}")
            print("asset roles:")
            for asset_id, role in payload["asset_roles"].items():
                print(f"- {asset_id}: {role}")
            print("screenshots:")
            for state in payload["screenshot_states"]:
                print(f"- {state}")
        return 0

    if args.command == "qa-plan":
        try:
            payload = build_qa_plan(load_game_spec(Path(args.spec)))
        except (OSError, GameSpecError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"qa plan: {payload['display_name']} ({payload['game_id']})")
            for command in payload["preflight"]:
                print(f"preflight: {command}")
            print("steps:")
            for step in payload["steps"]:
                print(f"{step['order']}. {step['state']} -> {step['capture_path']}")
                print(f"   drive: {step['drive']}")
                print(f"   evidence: {step['expected_evidence']}")
        return 0

    if args.command == "verify-screenshots":
        try:
            project = Path(args.project)
            if args.plan:
                payload = build_screenshot_status(project, load_qa_plan(Path(args.plan)))
            else:
                payload = build_screenshot_status_for_project(project)
        except (OSError, GameSpecError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"screenshot status: {payload['display_name']} ({payload['game_id']})")
            for check in payload["checks"]:
                print(f"{check['order']}. {check['state']}: {check['status']} -> {check['capture_path']}")
        return 0 if payload["ok"] else 1

    if args.command == "verify-game":
        return verify_game(Path(args.project))

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
