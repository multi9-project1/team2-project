from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from app.logic.fashion_config import (
    COOL_PERSONAL_COLOR_BRANCH_MAP,
    PERSONAL_COLOR_ALIASES,
    PERSONAL_COLOR_KEYWORD_MAP,
    PERSONAL_COLOR_LABELS,
    PERSONAL_COLOR_REPRESENTATIVE_COLORS,
    STYLE_CODE_ORDER,
    STYLE_KEYWORD_MAP,
    STYLE_LABELS,
    STYLE_QUESTION_OPTION_STYLE_MAP,
    WARM_PERSONAL_COLOR_BRANCH_MAP,
)


@dataclass
class SurveyProfile:
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


def normalize_survey_gender(value: str | None) -> str:
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


def normalize_choice_answer(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def normalize_personal_color_code(value: str | None) -> str:
    if value is None:
        return "unknown"
    normalized = str(value).strip()
    return PERSONAL_COLOR_ALIASES.get(normalized, PERSONAL_COLOR_ALIASES.get(normalized.lower(), "unknown"))


def resolve_personal_color_code(responses: Dict[str, Any]) -> str:
    selected = normalize_personal_color_code(responses.get("personal_color"))
    if selected != "unknown":
        return selected

    warm_votes = sum(normalize_choice_answer(responses.get(key)) == "A" for key in ("Q1", "Q2", "Q3"))
    cool_votes = sum(normalize_choice_answer(responses.get(key)) == "B" for key in ("Q1", "Q2", "Q3"))

    if warm_votes == cool_votes:
        return "unknown"

    if warm_votes > cool_votes:
        return WARM_PERSONAL_COLOR_BRANCH_MAP.get(normalize_choice_answer(responses.get("Qwarm")), "unknown")

    return COOL_PERSONAL_COLOR_BRANCH_MAP.get(normalize_choice_answer(responses.get("Qcool")), "unknown")


def calculate_style_score_map(responses: Dict[str, Any]) -> Dict[str, int]:
    style_score_map = {style_code: 0 for style_code in STYLE_CODE_ORDER}
    for question_code, answer_style_map in STYLE_QUESTION_OPTION_STYLE_MAP.items():
        selected_option = normalize_choice_answer(responses.get(question_code))
        for style_code in answer_style_map.get(selected_option, []):
            style_score_map[style_code] += 1
    return style_score_map


def determine_ranked_style_preferences(style_score_map: Dict[str, int]) -> tuple[str, List[str]]:
    ranked_style_scores = sorted(
        style_score_map.items(),
        key=lambda ranked_entry: (-ranked_entry[1], STYLE_CODE_ORDER.index(ranked_entry[0])),
    )
    primary_style_code = ranked_style_scores[0][0]
    primary_style_score = ranked_style_scores[0][1]

    secondary_style_codes: List[str] = []
    for style_code, style_score in ranked_style_scores[1:]:
        if style_score <= 0:
            continue
        if len(secondary_style_codes) >= 2:
            break
        if (
            style_score == primary_style_score
            or not secondary_style_codes
            or style_score == ranked_style_scores[1][1]
        ):
            secondary_style_codes.append(style_code)
    return primary_style_code, secondary_style_codes


def determine_fit_preference(responses: Dict[str, Any]) -> str:
    fit_answer = normalize_choice_answer(responses.get("Qstyle_3"))
    if fit_answer == "A":
        return "T"
    if fit_answer == "B":
        return "L"
    return "T"


def create_survey_profile(responses: Dict[str, Any]) -> SurveyProfile:
    personal_color_code = resolve_personal_color_code(responses)
    style_score_map = calculate_style_score_map(responses)
    primary_style_code, secondary_style_codes = determine_ranked_style_preferences(style_score_map)
    fit_preference_code = determine_fit_preference(responses)

    return SurveyProfile(
        gender=normalize_survey_gender(responses.get("gender")),
        personal_color=personal_color_code,
        personal_color_display=PERSONAL_COLOR_LABELS.get(personal_color_code, "모르겠음"),
        representative_colors=PERSONAL_COLOR_REPRESENTATIVE_COLORS.get(personal_color_code, []),
        primary_style=primary_style_code,
        secondary_styles=secondary_style_codes,
        fit_preference=fit_preference_code,
        style_scores=style_score_map,
        style_display={primary_style_code: STYLE_LABELS.get(primary_style_code, primary_style_code)},
        style_search_keywords=collect_style_search_keywords(primary_style_code, secondary_style_codes),
        color_search_keywords=PERSONAL_COLOR_KEYWORD_MAP.get(personal_color_code, []),
        tpo_preference=normalize_choice_answer(responses.get("Qstyle_9")),
    )


def collect_style_search_keywords(primary_style_code: str, secondary_style_codes: List[str]) -> List[str]:
    keywords: List[str] = []
    for style_code in [primary_style_code, *secondary_style_codes]:
        for keyword in STYLE_KEYWORD_MAP.get(style_code, []):
            if keyword not in keywords:
                keywords.append(keyword)
    return keywords