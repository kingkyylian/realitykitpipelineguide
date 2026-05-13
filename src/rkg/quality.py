from __future__ import annotations

from collections.abc import Mapping
from typing import Any

JsonDict = dict[str, Any]


def quality_contract_from_spec(spec: Mapping[str, Any]) -> JsonDict:
    value = spec.get("quality")
    if not isinstance(value, Mapping):
        return {}

    contract: JsonDict = {}
    feel = _string_map(value.get("feel"))
    feedback = _feedback_map(value.get("feedback"))
    style = _string_map(value.get("style"))
    if feel:
        contract["feel"] = feel
    if feedback:
        contract["feedback"] = feedback
    if style:
        contract["style"] = style
    return contract


def quality_contract_for_archetype(archetype_id: str) -> JsonDict:
    if archetype_id == "fighter_2_5d":
        return _contract(
            movement="snappy",
            input_response="instant",
            collision_forgiveness="medium",
            difficulty_curve="round_pressure",
            score=["combo_pop", "knockout_sting"],
            hit=["hit_spark", "camera_kick", "haptic_hook"],
            fail=["guard_break_flash", "freeze_frame", "result_transition"],
            mood="neon_duel",
            palette="high_contrast_rings",
            shape_language="readable_duel_silhouettes",
        )
    if archetype_id == "flappy_side_scroller":
        return _contract(
            movement="floaty",
            input_response="single_tap_lift",
            collision_forgiveness="low",
            difficulty_curve="speed_ramp",
            score=["gap_clear_pop", "score_chime"],
            hit=["near_gap_glint", "lane_pulse"],
            fail=["collision_flash", "freeze_frame", "result_transition"],
            mood="bright_arcade",
            palette="bright_readable_lanes",
            shape_language="simple_side_silhouettes",
        )
    return _generic_contract()


def quality_contract_for_systems(systems: list[str]) -> JsonDict:
    system_set = set(systems)
    if "racing" in system_set:
        return _contract(
            movement="momentum",
            input_response="responsive",
            collision_forgiveness="medium",
            difficulty_curve="lap_pressure",
            score=["lap_pop", "checkpoint_chime"],
            hit=["impact_flash", "camera_kick", "haptic_hook"],
            fail=["slow_motion_bump", "result_transition"],
            mood="speed_arcade",
            palette="track_contrast",
            shape_language="bold_vehicle_readability",
        )
    if system_set & {"projectile", "shooting"}:
        return _contract(
            movement="anchored",
            input_response="charged_release",
            collision_forgiveness="medium",
            difficulty_curve="target_density_ramp",
            score=["score_pop", "lane_clear_chime"],
            hit=["target_flash", "projectile_spark", "haptic_hook"],
            fail=["miss_trail_fade", "result_transition"],
            mood="skill_arcade",
            palette="high_contrast_targets",
            shape_language="clear_projectile_lanes",
        )
    if system_set & {"weapon", "hitscan", "enemies"}:
        return _contract(
            movement="tactical",
            input_response="immediate_fire",
            collision_forgiveness="medium",
            difficulty_curve="wave_pressure",
            score=["enemy_clear_pop", "streak_chime"],
            hit=["muzzle_flash", "hit_spark", "haptic_hook"],
            fail=["low_health_flash", "result_transition"],
            mood="focused_combat",
            palette="threat_readable_contrast",
            shape_language="cover_enemy_silhouettes",
        )
    if system_set & {"collect", "score", "timer"}:
        return _contract(
            movement="nimble",
            input_response="instant",
            collision_forgiveness="medium",
            difficulty_curve="timer_ramp",
            score=["combo_pop", "timer_bonus_chime"],
            hit=["pickup_burst", "combo_tick", "haptic_hook"],
            fail=["timer_flash", "result_transition"],
            mood="bright_chase",
            palette="pickup_contrast",
            shape_language="clean_pickup_silhouettes",
        )
    return _generic_contract()


def _generic_contract() -> JsonDict:
    return _contract(
        movement="snappy",
        input_response="instant",
        collision_forgiveness="medium",
        difficulty_curve="ramping",
        score=["score_pop", "sound_hook"],
        hit=["flash", "shake", "haptic_hook"],
        fail=["freeze_frame", "result_transition"],
        mood="arcade",
        palette="high_contrast",
        shape_language="readable_silhouettes",
    )


def _contract(
    *,
    movement: str,
    input_response: str,
    collision_forgiveness: str,
    difficulty_curve: str,
    score: list[str],
    hit: list[str],
    fail: list[str],
    mood: str,
    palette: str,
    shape_language: str,
) -> JsonDict:
    return {
        "feel": {
            "movement": movement,
            "input_response": input_response,
            "collision_forgiveness": collision_forgiveness,
            "difficulty_curve": difficulty_curve,
        },
        "feedback": {
            "score": score,
            "hit": hit,
            "fail": fail,
        },
        "style": {
            "mood": mood,
            "palette": palette,
            "shape_language": shape_language,
        },
    }


def _string_map(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): str(item) for key, item in value.items() if isinstance(key, str) and isinstance(item, str)}


def _feedback_map(value: object) -> dict[str, list[str]]:
    if not isinstance(value, Mapping):
        return {}
    feedback: dict[str, list[str]] = {}
    for key, items in value.items():
        if isinstance(key, str) and isinstance(items, list) and all(isinstance(item, str) for item in items):
            feedback[key] = list(items)
    return feedback
