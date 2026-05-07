from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


JsonDict = dict[str, Any]

REQUIRED_IDEA_FIELDS = [
    "title",
    "player_action",
    "differentiator",
    "first_playable_assets",
    "video_hook",
    "app_review_risk",
    "monetization",
]
DISALLOWED_FIRST_WAVE_SCOPE = {
    "backend",
    "heavy_character_animation",
    "moderation",
    "multiplayer",
    "open_world",
    "user_generated_content",
}


@dataclass(frozen=True)
class IdeaScore:
    score: int
    verdict: str
    issues: list[str]
    strengths: list[str]

    def to_dict(self) -> JsonDict:
        return {
            "score": self.score,
            "verdict": self.verdict,
            "issues": self.issues,
            "strengths": self.strengths,
        }


def load_idea(path: Path) -> JsonDict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text)
    else:
        value = _load_yaml_if_available(text)
    if not isinstance(value, dict):
        raise ValueError("idea root must be an object")
    return value


def score_game_idea(payload: Mapping[str, Any]) -> IdeaScore:
    idea = payload.get("idea")
    if not isinstance(idea, Mapping):
        return IdeaScore(score=0, verdict="reject", issues=["idea is required"], strengths=[])

    score = 100
    issues: list[str] = []
    strengths: list[str] = []

    for field in REQUIRED_IDEA_FIELDS:
        value = idea.get(field)
        if value is None or value == "" or value == []:
            issues.append(f"idea.{field} is required")

    assets = idea.get("first_playable_assets")
    if isinstance(assets, list) and all(isinstance(asset, str) for asset in assets):
        if 3 <= len(assets) <= 5:
            strengths.append("small first playable asset count")
        else:
            issues.append("first_playable_assets should contain 3 to 5 asset classes")
            score -= 25
    elif assets is not None:
        issues.append("idea.first_playable_assets must be a list of strings")
        score -= 25

    scope_flags = idea.get("scope_flags", [])
    if not isinstance(scope_flags, list) or not all(isinstance(flag, str) for flag in scope_flags):
        issues.append("idea.scope_flags must be a list of strings")
        score -= 20
        scope_flags = []

    for flag in sorted(set(scope_flags) & DISALLOWED_FIRST_WAVE_SCOPE):
        issues.append(f"scope flag {flag} is too large for the first factory wave")
        score -= 45

    app_review_risk = idea.get("app_review_risk")
    if app_review_risk == "low":
        strengths.append("low App Review risk")
    elif app_review_risk == "high":
        issues.append("app_review_risk high needs a smaller or clearer first version")
        score -= 20

    if idea.get("monetization") == "external_unlock":
        issues.append("external_unlock is not allowed for App Store builds")
        score -= 30
    elif idea.get("monetization") in {"paid", "free", "iap", "ads"}:
        strengths.append("store-compatible monetization")

    if idea.get("video_hook"):
        strengths.append("30-second hook is stated")
    if idea.get("player_action"):
        strengths.append("3-second player action is stated")
    if idea.get("differentiator"):
        strengths.append("difference from previous game is stated")

    if any(issue.startswith("idea.") and issue.endswith("is required") for issue in issues):
        score = min(score, 50)

    score = max(0, min(100, score))
    verdict = _verdict(score, issues)
    return IdeaScore(score=score, verdict=verdict, issues=issues, strengths=strengths)


def _verdict(score: int, issues: list[str]) -> str:
    if score < 60:
        return "reject"
    if any("too large for the first factory wave" in issue for issue in issues):
        return "reject"
    if score < 80 or issues:
        return "revise"
    return "pass"


def _load_yaml_if_available(text: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ValueError("YAML idea files require PyYAML; use JSON or install PyYAML") from exc
    return yaml.safe_load(text)
