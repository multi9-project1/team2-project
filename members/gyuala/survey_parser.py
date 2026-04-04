from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from fashion_config import (
    COOL_BRANCH_MAP,
    PERSONAL_COLOR_DISPLAY,
    PERSONAL_COLOR_NORMALIZATION,
    PERSONAL_COLOR_SEARCH_KEYWORDS,
    REPRESENTATIVE_COLORS,
    STYLE_CODES,
    STYLE_DISPLAY,
    STYLE_SEARCH_KEYWORDS,
    STYLE_QUESTION_RULES,
    WARM_BRANCH_MAP,
)


@dataclass
class UserProfile:
    gender: str
    personal_color: str
    personal_color_display: str
    representative_colors: List[str]
    primary_style: str
    secondary_styles: List[str]
    fit_preference: str
    style_scores: Dict[str, int]
    style_display: Dict[str, str]
    style_search_keywords: List[str]
    color_search_keywords: List[str]
    tpo_preference: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_gender(value: str | None) -> str:
    if not value:
        return "U"
    normalized = str(value).strip().upper()
    aliases = {
        "F": "W",
        "FEMALE": "W",
        "WOMAN": "W",
        "W": "W",
        "여성": "W",
        "M": "M",
        "MALE": "M",
        "MAN": "M",
        "남성": "M",
        "U": "U",
        "UNISEX": "U",
        "ALL": "U",
    }
    return aliases.get(normalized, "U")


def normalize_answer(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def normalize_personal_color(value: str | None) -> str:
    if value is None:
        return "unknown"
    normalized = str(value).strip()
    return PERSONAL_COLOR_NORMALIZATION.get(normalized, PERSONAL_COLOR_NORMALIZATION.get(normalized.lower(), "unknown"))


def infer_personal_color(responses: Dict[str, Any]) -> str:
    selected = normalize_personal_color(responses.get("personal_color"))
    if selected != "unknown":
        return selected

    warm_votes = sum(normalize_answer(responses.get(key)) == "A" for key in ("Q1", "Q2", "Q3"))
    cool_votes = sum(normalize_answer(responses.get(key)) == "B" for key in ("Q1", "Q2", "Q3"))

    if warm_votes == cool_votes:
        return "unknown"

    if warm_votes > cool_votes:
        return WARM_BRANCH_MAP.get(normalize_answer(responses.get("Qwarm")), "unknown")

    return COOL_BRANCH_MAP.get(normalize_answer(responses.get("Qcool")), "unknown")


def compute_style_scores(responses: Dict[str, Any]) -> Dict[str, int]:
    scores = {style: 0 for style in STYLE_CODES}
    for question, options in STYLE_QUESTION_RULES.items():
        answer = normalize_answer(responses.get(question))
        for style_code in options.get(answer, []):
            scores[style_code] += 1
    return scores


def resolve_primary_and_secondary_styles(style_scores: Dict[str, int]) -> tuple[str, List[str]]:
    ranked = sorted(style_scores.items(), key=lambda item: (-item[1], STYLE_CODES.index(item[0])))
    primary_style = ranked[0][0]
    primary_score = ranked[0][1]

    secondary_styles: List[str] = []
    for style_code, score in ranked[1:]:
        if score <= 0:
            continue
        if len(secondary_styles) >= 2:
            break
        if score == primary_score or not secondary_styles or score == ranked[1][1]:
            secondary_styles.append(style_code)
    return primary_style, secondary_styles


def infer_fit_preference(responses: Dict[str, Any]) -> str:
    answer = normalize_answer(responses.get("Qstyle_3"))
    if answer == "A":
        return "T"
    if answer == "B":
        return "L"
    return "T"


def build_user_profile(responses: Dict[str, Any]) -> UserProfile:
    personal_color = infer_personal_color(responses)
    style_scores = compute_style_scores(responses)
    primary_style, secondary_styles = resolve_primary_and_secondary_styles(style_scores)
    fit_preference = infer_fit_preference(responses)

    return UserProfile(
        gender=normalize_gender(responses.get("gender")),
        personal_color=personal_color,
        personal_color_display=PERSONAL_COLOR_DISPLAY.get(personal_color, "모르겠음"),
        representative_colors=REPRESENTATIVE_COLORS.get(personal_color, []),
        primary_style=primary_style,
        secondary_styles=secondary_styles,
        fit_preference=fit_preference,
        style_scores=style_scores,
        style_display={primary_style: STYLE_DISPLAY.get(primary_style, primary_style)},
        style_search_keywords=_build_style_search_keywords(primary_style, secondary_styles),
        color_search_keywords=PERSONAL_COLOR_SEARCH_KEYWORDS.get(personal_color, []),
        tpo_preference=normalize_answer(responses.get("Qstyle_9")),
    )


def _build_style_search_keywords(primary_style: str, secondary_styles: List[str]) -> List[str]:
    keywords: List[str] = []
    for style_code in [primary_style, *secondary_styles]:
        for keyword in STYLE_SEARCH_KEYWORDS.get(style_code, []):
            if keyword not in keywords:
                keywords.append(keyword)
    return keywords
