from __future__ import annotations

import math
from typing import Any, Dict, List

from fashion_config import (
    DATASET_STYLE_TO_GROUP,
    FIT_SCORE_MAP,
    GROUP_DISPLAY_TO_STYLE_CODE,
    PERSONAL_COLOR_TARGETS,
    STYLE_CODES,
    STYLE_DISPLAY,
    STYLE_FEATURE_MAP,
    STYLE_RANKING_WEIGHTS,
    TPO_Q3_MAP,
)


def compute_style_score(item: Dict[str, Any], primary_style: str, secondary_styles: List[str]) -> tuple[float, Dict[str, float]]:
    primary_features = STYLE_FEATURE_MAP.get(primary_style, [])
    primary_match = _feature_match_ratio(item, primary_features)

    secondary_feature_list: List[str] = []
    for style_code in secondary_styles:
        secondary_feature_list.extend(STYLE_FEATURE_MAP.get(style_code, []))
    secondary_match = _feature_match_ratio(item, secondary_feature_list)

    score = (0.75 * primary_match) + (0.25 * secondary_match)
    return score, {
        "primary_match": round(primary_match, 4),
        "secondary_match": round(secondary_match, 4),
    }


def _feature_match_ratio(item: Dict[str, Any], feature_codes: List[str]) -> float:
    if not feature_codes:
        return 0.0
    hits = sum(1 for code in feature_codes if float(item.get(code, 0) or 0) > 0)
    return hits / len(feature_codes)


def compute_fit_score(item: Dict[str, Any], fit_preference: str) -> float:
    q411 = int(item.get("Q411", 0) or 0)
    return FIT_SCORE_MAP.get(fit_preference, {}).get(q411, 0.0)


def compute_color_score(item: Dict[str, Any], personal_color: str) -> tuple[float, Dict[str, float]]:
    target = PERSONAL_COLOR_TARGETS.get(personal_color)
    if not target:
        return 0.0, {"q412_match": 0.0, "q413_match": 0.0, "q414_match": 0.0}

    q412_match = 1.0 if int(item.get("Q412", 0) or 0) == target[0] else 0.0
    q413_match = 1.0 if int(item.get("Q413", 0) or 0) == target[1] else 0.0
    q414_match = 1.0 if int(item.get("Q414", 0) or 0) == target[2] else 0.0
    score = (0.4 * q412_match) + (0.3 * q413_match) + (0.3 * q414_match)
    return score, {
        "q412_match": q412_match,
        "q413_match": q413_match,
        "q414_match": q414_match,
    }


def compute_final_score(style_score: float, fit_score: float, color_score: float) -> float:
    return (0.55 * style_score) + (0.15 * fit_score) + (0.30 * color_score)


def compute_weighted_final_score(
    *,
    style_score: float,
    fit_score: float,
    color_score: float,
    primary_style: str,
    item_style: str,
) -> tuple[float, Dict[str, float]]:
    weights = STYLE_RANKING_WEIGHTS.get(primary_style, STYLE_RANKING_WEIGHTS["default"])
    item_group = DATASET_STYLE_TO_GROUP.get(str(item_style).lower(), "기타 스타일")
    item_group_code = GROUP_DISPLAY_TO_STYLE_CODE.get(item_group)
    group_bonus = weights.get("group_bonus", 0.0) if item_group_code == primary_style else 0.0
    final_score = (
        (weights["style"] * style_score)
        + (weights["fit"] * fit_score)
        + (weights["color"] * color_score)
        + group_bonus
    )
    return final_score, {
        "style_weight": round(weights["style"], 4),
        "fit_weight": round(weights["fit"], 4),
        "color_weight": round(weights["color"], 4),
        "group_bonus": round(group_bonus, 4),
    }


def build_reasons(
    *,
    style_score: float,
    fit_score: float,
    color_score: float,
    primary_style: str,
    secondary_styles: List[str],
) -> List[str]:
    reasons: List[str] = []
    if style_score >= 0.6:
        primary_display = STYLE_DISPLAY.get(primary_style, primary_style)
        reasons.append(f"대표 스타일인 {primary_display} 감성과 유사한 이미지 특성이 있습니다.")
    elif secondary_styles:
        secondary_display = ", ".join(STYLE_DISPLAY.get(code, code) for code in secondary_styles)
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


def rank_items(user_profile: Dict[str, Any], items: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    recommendations: List[Dict[str, Any]] = []
    for item in items:
        style_score, style_breakdown = compute_style_score(
            item,
            user_profile["primary_style"],
            user_profile.get("secondary_styles", []),
        )
        fit_score = compute_fit_score(item, user_profile["fit_preference"])
        color_score, color_breakdown = compute_color_score(item, user_profile["personal_color"])
        final_score, final_weight_breakdown = compute_weighted_final_score(
            style_score=style_score,
            fit_score=fit_score,
            color_score=color_score,
            primary_style=user_profile["primary_style"],
            item_style=str(item.get("style", "")),
        )

        recommendations.append(
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
                "reasons": build_reasons(
                    style_score=style_score,
                    fit_score=fit_score,
                    color_score=color_score,
                    primary_style=user_profile["primary_style"],
                    secondary_styles=user_profile.get("secondary_styles", []),
                ),
            }
        )

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return dedupe_recommendations_by_image(recommendations, top_n=top_n)


def dedupe_recommendations_by_image(recommendations: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen_image_keys: set[str] = set()

    for item in recommendations:
        image_key = str(item.get("image_path") or item.get("item_id") or "").strip()
        if not image_key or image_key in seen_image_keys:
            continue
        seen_image_keys.add(image_key)
        deduped.append(item)
        if len(deduped) >= top_n:
            break

    return deduped


def filter_items_with_images(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [item for item in items if str(item.get("image_path", "")).lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]


def filter_items_by_gender(items: List[Dict[str, Any]], user_gender: str) -> List[Dict[str, Any]]:
    normalized_user_gender = str(user_gender or "U").upper()
    if normalized_user_gender not in {"W", "M"}:
        return items

    filtered = [item for item in items if str(item.get("gender", "")).upper() == normalized_user_gender]
    return filtered or items


def build_user_style_vector(user_profile: Dict[str, Any]) -> List[float]:
    style_scores = user_profile.get("style_scores", {})
    return [float(style_scores.get(style_code, 0)) for style_code in STYLE_CODES]


def build_item_style_vector(item: Dict[str, Any]) -> List[float]:
    vector: List[float] = []
    for style_code in STYLE_CODES:
        feature_codes = STYLE_FEATURE_MAP.get(style_code, [])
        if not feature_codes:
            vector.append(0.0)
            continue
        vector.append(sum(float(item.get(code, 0) or 0) for code in feature_codes) / len(feature_codes))
    return vector


def build_user_tpo_vector(tpo_answer: str) -> List[float]:
    preferred_q3_values = TPO_Q3_MAP.get(str(tpo_answer or "").upper(), [])
    return [1.0 if q3_value in preferred_q3_values else 0.0 for q3_value in range(1, 8)]


def build_item_tpo_vector(item: Dict[str, Any]) -> List[float]:
    item_q3 = int(item.get("Q3", 0) or 0)
    return [1.0 if q3_value == item_q3 else 0.0 for q3_value in range(1, 8)]


def compute_cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_top_style_match(user_profile: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
    user_style_vector = build_user_style_vector(user_profile)
    user_tpo_vector = build_user_tpo_vector(user_profile.get("tpo_preference", ""))
    user_vector = user_style_vector + user_tpo_vector
    best_match: Dict[str, Any] | None = None

    for item in items:
        item_style_vector = build_item_style_vector(item)
        item_tpo_vector = build_item_tpo_vector(item)
        similarity = compute_cosine_similarity(user_vector, item_style_vector + item_tpo_vector)
        candidate = {
            "item_id": item.get("item_id"),
            "era": item.get("era"),
            "style": item.get("style"),
            "gender": item.get("gender"),
            "image_path": item.get("image_path"),
            "similarity": similarity,
            "similarity_percent": round(similarity * 100),
            "q3": item.get("Q3"),
            "tpo_match": int(item.get("Q3", 0) or 0) in TPO_Q3_MAP.get(user_profile.get("tpo_preference", ""), []),
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


def collect_top_style_matches(user_profile: Dict[str, Any], items: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
    user_style_vector = build_user_style_vector(user_profile)
    user_tpo_vector = build_user_tpo_vector(user_profile.get("tpo_preference", ""))
    user_vector = user_style_vector + user_tpo_vector
    matches: List[Dict[str, Any]] = []

    for item in items:
        item_style_vector = build_item_style_vector(item)
        item_tpo_vector = build_item_tpo_vector(item)
        similarity = compute_cosine_similarity(user_vector, item_style_vector + item_tpo_vector)
        matches.append(
            {
                "item_id": item.get("item_id"),
                "era": item.get("era"),
                "style": item.get("style"),
                "style_group": DATASET_STYLE_TO_GROUP.get(str(item.get("style", "")).lower(), "기타 스타일"),
                "similarity": similarity,
                "similarity_percent": round(similarity * 100),
            }
        )

    matches.sort(key=lambda item: item["similarity"], reverse=True)
    return matches[:top_k]


def infer_style_profile_from_matches(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    group_scores: Dict[str, float] = {}
    for match in matches:
        style_group = match.get("style_group", "기타 스타일")
        group_scores[style_group] = group_scores.get(style_group, 0.0) + float(match.get("similarity", 0.0))

    ranked_groups = sorted(group_scores.items(), key=lambda item: item[1], reverse=True)
    primary_group = ranked_groups[0][0] if ranked_groups else "기타 스타일"
    secondary_groups = [group for group, _ in ranked_groups[1:3]]

    return {
        "primary_group": primary_group,
        "primary_style_code": GROUP_DISPLAY_TO_STYLE_CODE.get(primary_group),
        "secondary_groups": secondary_groups,
        "secondary_style_codes": [GROUP_DISPLAY_TO_STYLE_CODE[group] for group in secondary_groups if group in GROUP_DISPLAY_TO_STYLE_CODE],
        "group_scores": {group: round(score, 4) for group, score in ranked_groups},
    }
