from __future__ import annotations

from typing import Any, Dict, List

from fashion_config import FIT_SCORE_MAP, PERSONAL_COLOR_TARGETS, STYLE_DISPLAY, STYLE_FEATURE_MAP


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
        final_score = compute_final_score(style_score, fit_score, color_score)

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
