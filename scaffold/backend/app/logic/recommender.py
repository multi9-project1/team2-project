from __future__ import annotations

import math
from typing import Any, Dict, List

from app.logic.fashion_config import (
    DATASET_STYLE_GROUP_LABELS,
    FIT_PREFERENCE_TO_Q411_SCORE,
    PERSONAL_COLOR_DATASET_TARGETS,
    STYLE_CODE_ORDER,
    STYLE_DATASET_FEATURE_MAP,
    STYLE_GROUP_TO_STYLE_CODE,
    STYLE_LABELS,
    STYLE_RANKING_WEIGHT_MAP,
    TPO_OPTION_TO_DATASET_Q3_VALUES,
)


def calculate_style_match_score(
    item: Dict[str, Any],
    primary_style_code: str,
    secondary_style_codes: List[str],
) -> tuple[float, Dict[str, float]]:
    primary_feature_codes = STYLE_DATASET_FEATURE_MAP.get(primary_style_code, [])
    primary_match_ratio = _calculate_feature_activation_ratio(item, primary_feature_codes)

    secondary_feature_codes: List[str] = []
    for style_code in secondary_style_codes:
        secondary_feature_codes.extend(STYLE_DATASET_FEATURE_MAP.get(style_code, []))
    secondary_match_ratio = _calculate_feature_activation_ratio(item, secondary_feature_codes)

    style_match_score = (0.75 * primary_match_ratio) + (0.25 * secondary_match_ratio)
    return style_match_score, {
        "primary_match": round(primary_match_ratio, 4),
        "secondary_match": round(secondary_match_ratio, 4),
    }


def _calculate_feature_activation_ratio(item: Dict[str, Any], feature_codes: List[str]) -> float:
    if not feature_codes:
        return 0.0
    matched_feature_count = sum(1 for code in feature_codes if float(item.get(code, 0) or 0) > 0)
    return matched_feature_count / len(feature_codes)


def calculate_fit_match_score(item: Dict[str, Any], fit_preference_code: str) -> float:
    q411_value = int(item.get("Q411", 0) or 0)
    return FIT_PREFERENCE_TO_Q411_SCORE.get(fit_preference_code, {}).get(q411_value, 0.0)


def calculate_color_match_score(item: Dict[str, Any], personal_color_code: str) -> tuple[float, Dict[str, float]]:
    target_color_values = PERSONAL_COLOR_DATASET_TARGETS.get(personal_color_code)
    if not target_color_values:
        return 0.0, {"q412_match": 0.0, "q413_match": 0.0, "q414_match": 0.0}

    q412_match = 1.0 if int(item.get("Q412", 0) or 0) == target_color_values[0] else 0.0
    q413_match = 1.0 if int(item.get("Q413", 0) or 0) == target_color_values[1] else 0.0
    q414_match = 1.0 if int(item.get("Q413", 0) or 0) == target_color_values[2] else 0.0
    color_match_score = (0.4 * q412_match) + (0.3 * q413_match) + (0.3 * q414_match)
    return color_match_score, {
        "q412_match": q412_match,
        "q413_match": q413_match,
        "q414_match": q414_match,
    }


def calculate_base_recommendation_score(style_score: float, fit_score: float, color_score: float) -> float:
    return (0.55 * style_score) + (0.15 * fit_score) + (0.30 * color_score)


def calculate_weighted_recommendation_score(
    *,
    style_score: float,
    fit_score: float,
    color_score: float,
    primary_style_code: str,
    item_style_code: str,
) -> tuple[float, Dict[str, float]]:
    ranking_weights = STYLE_RANKING_WEIGHT_MAP.get(primary_style_code, STYLE_RANKING_WEIGHT_MAP["default"])
    item_style_group = DATASET_STYLE_GROUP_LABELS.get(str(item_style_code).lower(), "기타 스타일")
    item_style_group_code = STYLE_GROUP_TO_STYLE_CODE.get(item_style_group)
    group_bonus = ranking_weights.get("group_bonus", 0.0) if item_style_group_code == primary_style_code else 0.0
    final_score = (
        (ranking_weights["style"] * style_score)
        + (ranking_weights["fit"] * fit_score)
        + (ranking_weights["color"] * color_score)
        + group_bonus
    )
    return final_score, {
        "style_weight": round(ranking_weights["style"], 4),
        "fit_weight": round(ranking_weights["fit"], 4),
        "color_weight": round(ranking_weights["color"], 4),
        "group_bonus": round(group_bonus, 4),
    }


def generate_recommendation_reasons(
    *,
    style_score: float,
    fit_score: float,
    color_score: float,
    primary_style_code: str,
    secondary_style_codes: List[str],
) -> List[str]:
    reasons: List[str] = []
    if style_score >= 0.6:
        primary_display = STYLE_LABELS.get(primary_style_code, primary_style_code)
        reasons.append(f"대표 스타일인 {primary_display} 감성과 유사한 이미지 특성이 있습니다.")
    elif secondary_style_codes:
        secondary_display = ", ".join(STYLE_LABELS.get(code, code) for code in secondary_style_codes)
        reasons.append(f"보조 스타일인 {secondary_display} 요소가 일부 반영되어 있습니다.")

    if fit_score >= 0.8:
        reasons.append("선호 핏과 잘 맞는 실루엣입니다.")
    elif fit_score >= 0.4:
        reasons.append("핏 선호와 부분적으로 맞는 아이템입니다.")

    if color_score >= 0.7:
        reasons.append("퍼스널컬러 톤과 잘 어울리는 색감입니다.")
    elif color_score >= 0.3:
        reasons.append("퍼스널컬러와 일부 맞는 색감 요소가 있습니다.")

    if not reasons:
        reasons.append("스타일과 컬러 기준에서 기본 조건을 충족한 아이템입니다.")
    return reasons


def rank_recommendation_candidates(
    user_profile: Dict[str, Any],
    items: List[Dict[str, Any]],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    ranked_recommendations: List[Dict[str, Any]] = []
    for item in items:
        style_score, style_breakdown = calculate_style_match_score(
            item,
            user_profile["primary_style"],
            user_profile.get("secondary_styles", []),
        )
        fit_score = calculate_fit_match_score(item, user_profile["fit_preference"])
        color_score, color_breakdown = calculate_color_match_score(item, user_profile["personal_color"])
        final_score, final_weight_breakdown = calculate_weighted_recommendation_score(
            style_score=style_score,
            fit_score=fit_score,
            color_score=color_score,
            primary_style_code=user_profile["primary_style"],
            item_style_code=str(item.get("style", "")),
        )

        ranked_recommendations.append(
            {
                "item_id": item.get("item_id"),
                "image_path": item.get("image_path"),
                "gender": item.get("gender"),
                "era": item.get("era"),
                "style": item.get("style"),
                "score": round(final_score, 4),
                "score_breakdown": {
                    "style": round(style_score, 4),
                    "fit": round(fit_score, 4),
                    "color": round(color_score, 4),
                    **style_breakdown,
                    **color_breakdown,
                    **final_weight_breakdown,
                },
                "matched_features": {
                    "q411": item.get("Q411"),
                    "q412": item.get("Q412"),
                    "q413": item.get("Q413"),
                    "q414": item.get("Q414"),
                },
                "reasons": generate_recommendation_reasons(
                    style_score=style_score,
                    fit_score=fit_score,
                    color_score=color_score,
                    primary_style_code=user_profile["primary_style"],
                    secondary_style_codes=user_profile.get("secondary_styles", []),
                ),
            }
        )

    ranked_recommendations.sort(key=lambda item: item["score"], reverse=True)
    return deduplicate_recommendations_by_image_path(ranked_recommendations, top_n=top_n)


def deduplicate_recommendations_by_image_path(recommendations: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    deduplicated_recommendations: List[Dict[str, Any]] = []
    seen_image_keys: set[str] = set()

    for recommendation in recommendations:
        image_key = str(recommendation.get("image_path") or recommendation.get("item_id") or "").strip()
        if not image_key or image_key in seen_image_keys:
            continue
        seen_image_keys.add(image_key)
        deduplicated_recommendations.append(recommendation)
        if len(deduplicated_recommendations) >= top_n:
            break

    return deduplicated_recommendations


def filter_image_available_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [item for item in items if str(item.get("image_path", "")).lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]


def filter_items_by_user_gender(items: List[Dict[str, Any]], user_gender: str) -> List[Dict[str, Any]]:
    normalized_gender_code = str(user_gender or "U").upper()
    if normalized_gender_code not in {"W", "M"}:
        return items

    gender_matched_items = [item for item in items if str(item.get("gender", "")).upper() == normalized_gender_code]
    return gender_matched_items or items


def build_user_style_score_vector(user_profile: Dict[str, Any]) -> List[float]:
    style_score_map = user_profile.get("style_scores", {})
    return [float(style_score_map.get(style_code, 0)) for style_code in STYLE_CODE_ORDER]


def build_item_style_feature_vector(item: Dict[str, Any]) -> List[float]:
    item_style_vector: List[float] = []
    for style_code in STYLE_CODE_ORDER:
        feature_codes = STYLE_DATASET_FEATURE_MAP.get(style_code, [])
        if not feature_codes:
            item_style_vector.append(0.0)
            continue
        item_style_vector.append(sum(float(item.get(code, 0) or 0) for code in feature_codes) / len(feature_codes))
    return item_style_vector


def build_user_tpo_preference_vector(tpo_answer: str) -> List[float]:
    preferred_q3_values = TPO_OPTION_TO_DATASET_Q3_VALUES.get(str(tpo_answer or "").upper(), [])
    return [1.0 if q3_value in preferred_q3_values else 0.0 for q3_value in range(1, 8)]


def build_item_tpo_feature_vector(item: Dict[str, Any]) -> List[float]:
    item_q3_value = int(item.get("Q3", 0) or 0)
    return [1.0 if q3_value == item_q3_value else 0.0 for q3_value in range(1, 8)]


def calculate_cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_highest_similarity_item_match(user_profile: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
    user_style_vector = build_user_style_score_vector(user_profile)
    user_tpo_vector = build_user_tpo_preference_vector(user_profile.get("tpo_preference", ""))
    combined_user_vector = user_style_vector + user_tpo_vector
    best_match: Dict[str, Any] | None = None

    for item in items:
        item_style_vector = build_item_style_feature_vector(item)
        item_tpo_vector = build_item_tpo_feature_vector(item)
        similarity = calculate_cosine_similarity(combined_user_vector, item_style_vector + item_tpo_vector)
        candidate = {
            "item_id": item.get("item_id"),
            "era": item.get("era"),
            "style": item.get("style"),
            "gender": item.get("gender"),
            "image_path": item.get("image_path"),
            "similarity": similarity,
            "similarity_percent": round(similarity * 100),
            "q3": item.get("Q3"),
            "tpo_match": int(item.get("Q3", 0) or 0)
            in TPO_OPTION_TO_DATASET_Q3_VALUES.get(user_profile.get("tpo_preference", ""), []),
        }
        if best_match is None or candidate["similarity"] > best_match["similarity"]:
            best_match = candidate

    return best_match or {
        "item_id": None,
        "era": "unknown",
        "style": "unknown",
        "gender": None,
        "image_path": None,
        "similarity": 0.0,
        "similarity_percent": 0,
        "q3": None,
    }


def collect_top_similarity_matches(
    user_profile: Dict[str, Any],
    items: List[Dict[str, Any]],
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    user_style_vector = build_user_style_score_vector(user_profile)
    user_tpo_vector = build_user_tpo_preference_vector(user_profile.get("tpo_preference", ""))
    combined_user_vector = user_style_vector + user_tpo_vector
    similarity_matches: List[Dict[str, Any]] = []

    for item in items:
        item_style_vector = build_item_style_feature_vector(item)
        item_tpo_vector = build_item_tpo_feature_vector(item)
        similarity = calculate_cosine_similarity(combined_user_vector, item_style_vector + item_tpo_vector)
        similarity_matches.append(
            {
                "item_id": item.get("item_id"),
                "era": item.get("era"),
                "style": item.get("style"),
                "style_group": DATASET_STYLE_GROUP_LABELS.get(str(item.get("style", "")).lower(), "기타 스타일"),
                "similarity": similarity,
                "similarity_percent": round(similarity * 100),
            }
        )

    similarity_matches.sort(key=lambda item: item["similarity"], reverse=True)
    return similarity_matches[:top_k]


def derive_style_profile_from_similarity_matches(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    style_group_scores: Dict[str, float] = {}
    for match in matches:
        style_group = match.get("style_group", "기타 스타일")
        style_group_scores[style_group] = style_group_scores.get(style_group, 0.0) + float(match.get("similarity", 0.0))

    ranked_style_groups = sorted(style_group_scores.items(), key=lambda item: item[1], reverse=True)
    primary_style_group = ranked_style_groups[0][0] if ranked_style_groups else "기타 스타일"
    secondary_style_groups = [group for group, _ in ranked_style_groups[1:3]]

    return {
        "primary_group": primary_style_group,
        "primary_style_code": STYLE_GROUP_TO_STYLE_CODE.get(primary_style_group),
        "secondary_groups": secondary_style_groups,
        "secondary_style_codes": [
            STYLE_GROUP_TO_STYLE_CODE[group]
            for group in secondary_style_groups
            if group in STYLE_GROUP_TO_STYLE_CODE
        ],
        "group_scores": {group: round(score, 4) for group, score in ranked_style_groups},
    }