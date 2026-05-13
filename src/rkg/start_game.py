from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.asset_pipeline import build_asset_pipeline
from rkg.idea_score import score_game_idea
from rkg.qa_plan import build_qa_plan
from rkg.scaffold import init_game
from rkg.spec_templates import build_game_template, build_spec_template

JsonDict = dict[str, Any]


def recommend_start_from_idea(payload: Mapping[str, Any]) -> JsonDict:
    idea = payload.get("idea")
    if not isinstance(idea, Mapping):
        return _recommendation(
            title="Untitled Game",
            archetype="custom_realitykit",
            camera="fixed_non_ar",
            input_model="tap",
            systems=["collect", "score", "timer"],
            reason="fallback recommendation because idea payload is missing",
        )

    title = str(idea.get("title") or "Untitled Game")
    text = _idea_search_text(idea)
    if _matches(text, ["fighter", "fight", "duel", "combo", "dodge", "guard", "knockout"]):
        return _recommendation(
            title=title,
            archetype="fighter_2_5d",
            camera="fixed_non_ar",
            input_model="tap_swipe",
            systems=[],
            reason="fighter keywords map to the native fighter_2_5d archetype",
        )
    if _matches(text, ["race", "racing", "lap", "drift", "track", "vehicle", "car", "chase"]):
        return _recommendation(
            title=title,
            archetype="custom_realitykit",
            camera="chase",
            input_model="tilt_tap",
            systems=["racing", "lap_timer", "collision"],
            reason="racing keywords map to chase camera, tilt/tap input, and racing/lap/collision systems",
        )
    if _matches(text, ["projectile", "volley", "slingshot", "arc", "charge", "launch", "throw"]):
        return _recommendation(
            title=title,
            archetype="custom_realitykit",
            camera="third_person",
            input_model="drag",
            systems=["projectile", "shooting", "score"],
            reason="projectile keywords map to third-person drag aiming with projectile/shooting/score systems",
        )
    if _matches(text, ["fps", "shooter", "shoot", "gun", "weapon", "enemy", "enemies", "cover", "breach"]):
        return _recommendation(
            title=title,
            archetype="custom_realitykit",
            camera="first_person",
            input_model="dual_stick",
            systems=["weapon", "hitscan", "enemies", "health", "cover"],
            reason="shooter keywords map to first-person dual-stick weapon/enemy/health/cover systems",
        )
    if _matches(text, ["collect", "pickup", "orb", "gem", "timer", "sprint", "route"]):
        return _recommendation(
            title=title,
            archetype="custom_realitykit",
            camera="top_down",
            input_model="tap_swipe",
            systems=["collect", "score", "timer"],
            reason="collector keywords map to top-down pickup/score/timer systems",
        )
    return _recommendation(
        title=title,
        archetype="custom_realitykit",
        camera="fixed_non_ar",
        input_model="tap",
        systems=["collect", "score", "timer"],
        reason="default recommendation keeps the first playable small with score and timer proof roles",
    )


def start_game_from_idea(payload: Mapping[str, Any], output: Path, *, force: bool = False) -> JsonDict:
    score = score_game_idea(payload)
    recommendation = recommend_start_from_idea(payload)
    result: JsonDict = {
        "ok": score.verdict == "pass",
        "score": score.to_dict(),
        "recommendation": recommendation,
        "paths": {"project": str(output.resolve()), "spec": str((output / "GameSpec.json").resolve())},
    }
    if score.verdict != "pass":
        return result

    spec = _spec_from_recommendation(recommendation, payload)
    init_game(spec, output, force=force)
    result["qa_plan"] = build_qa_plan(spec)
    result["asset_pipeline"] = build_asset_pipeline(spec, output)
    return result


def _spec_from_recommendation(recommendation: Mapping[str, Any], payload: Mapping[str, Any]) -> JsonDict:
    archetype = str(recommendation["archetype"])
    title = str(recommendation["title"])
    if archetype == "fighter_2_5d":
        spec = build_spec_template("fighter_2_5d", title)
    else:
        spec = build_game_template(
            title,
            str(recommendation["camera"]),
            str(recommendation["input"]),
            [",".join(str(system) for system in recommendation.get("systems", []))],
        )
    monetization = _idea_monetization(payload)
    if monetization:
        spec["game"]["monetization"] = monetization
    return spec


def _idea_monetization(payload: Mapping[str, Any]) -> str | None:
    idea = payload.get("idea")
    if not isinstance(idea, Mapping):
        return None
    value = idea.get("monetization")
    if isinstance(value, str) and value in {"paid", "free", "iap", "ads"}:
        return value
    return None


def _recommendation(
    *,
    title: str,
    archetype: str,
    camera: str,
    input_model: str,
    systems: list[str],
    reason: str,
) -> JsonDict:
    return {
        "title": title,
        "archetype": archetype,
        "camera": camera,
        "input": input_model,
        "systems": systems,
        "reason": reason,
    }


def _idea_search_text(idea: Mapping[str, Any]) -> str:
    values = [
        idea.get("title"),
        idea.get("player_action"),
        idea.get("differentiator"),
        idea.get("video_hook"),
    ]
    assets = idea.get("first_playable_assets")
    if isinstance(assets, list):
        values.extend(assets)
    return " ".join(str(value).lower() for value in values if value)


def _matches(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
