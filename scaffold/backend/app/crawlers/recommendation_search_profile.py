from __future__ import annotations

from typing import Any, Dict, List

try:
    from app.logic.fashion_config import PERSONAL_COLOR_PLATFORM_KEYWORD_MAP, STYLE_LABELS, TPO_OPTION_TO_DEEPLINK_KEYWORD
    from logic.item_feature_builder import load_dataset_item_records
    from logic.recommender import (
        collect_top_similarity_matches,
        derive_style_profile_from_similarity_matches,
        filter_items_by_user_gender,
    )
    from app.logic.survey_parser import collect_style_search_keywords, create_survey_profile
except ImportError:
    from app.logic.fashion_config import PERSONAL_COLOR_PLATFORM_KEYWORD_MAP, STYLE_LABELS, TPO_OPTION_TO_DEEPLINK_KEYWORD
    from app.logic.item_feature_builder import load_dataset_item_records
    from app.logic.recommender import (
        collect_top_similarity_matches,
        derive_style_profile_from_similarity_matches,
        filter_items_by_user_gender,
    )
    from app.logic.survey_parser import collect_style_search_keywords, create_survey_profile

MUSINSA_STYLE_ID_MAP: Dict[str, int] = {
    "캐주얼": 1,
    "스트릿": 2,
    "고프코어": 3,
    "프레피": 5,
    "스포티": 7,
    "로맨틱": 8,
    "걸리시": 9,
    "미니멀": 11,
    "시크": 12,
    "레트로": 13,
    "에스닉": 14,
}

STYLE_CODE_TO_MUSINSA_LABELS: Dict[str, List[str]] = {
    "sophisticated": ["시크", "미니멀", "프레피"],
    "feminine": ["걸리시", "로맨틱"],
    "romantic": ["로맨틱", "걸리시"],
    "modern_minimal": ["미니멀", "시크"],
    "casual": ["캐주얼", "프레피"],
    "mannish": ["시크", "미니멀", "프레피"],
    "street": ["스트릿"],
    "sporty": ["스포티", "고프코어"],
    "hipster_punk": ["스트릿", "레트로", "에스닉"],
    "retro": ["레트로", "에스닉"],
}

FIT_PREFERENCE_TO_MUSINSA_CODES: Dict[str, List[str]] = {
    "T": ["2^87", "2^88"],
    "L": ["2^90"],
}

FIT_PREFERENCE_TO_ZIGZAG_TOP_FITS: Dict[str, List[str]] = {
    "T": ["타이트핏", "슬림핏", "노멀핏"],
    "L": ["루즈핏", "오버핏", "와이드핏"],
}

FIT_PREFERENCE_TO_ZIGZAG_BOTTOM_FITS: Dict[str, List[str]] = {
    "T": ["슬림핏", "일자핏", "부츠컷"],
    "L": ["와이드핏", "조거핏", "일자핏"],
}


def build_recommendation_search_profile(
    survey_answers: Dict[str, Any],
    *,
    dataset_dir: str | None = None,
    allow_mock: bool = True,
) -> Dict[str, Any]:
    user_profile = create_survey_profile(survey_answers).to_dict()
    dataset_items = load_dataset_item_records(dataset_dir=dataset_dir, allow_mock=allow_mock)
    gender_filtered_items = filter_items_by_user_gender(dataset_items, user_profile["gender"])
    top_similarity_matches = collect_top_similarity_matches(user_profile, gender_filtered_items or dataset_items, top_k=20)
    inferred_style_profile = derive_style_profile_from_similarity_matches(top_similarity_matches)

    if inferred_style_profile.get("primary_style_code"):
        primary_style_code = inferred_style_profile["primary_style_code"]
        secondary_style_codes = inferred_style_profile["secondary_style_codes"]
        user_profile["primary_style"] = primary_style_code
        user_profile["secondary_styles"] = secondary_style_codes
        user_profile["style_display"] = {primary_style_code: STYLE_LABELS.get(primary_style_code, primary_style_code)}
        user_profile["style_search_keywords"] = collect_style_search_keywords(primary_style_code, secondary_style_codes)

    primary_style_code = user_profile["primary_style"]
    secondary_style_codes = user_profile.get("secondary_styles", [])
    tpo_keyword = TPO_OPTION_TO_DEEPLINK_KEYWORD.get(user_profile.get("tpo_preference", ""), "")
    musinsa_style_labels = _collect_musinsa_style_labels(primary_style_code, secondary_style_codes)
    musinsa_style_ids = [
        MUSINSA_STYLE_ID_MAP[musinsa_style_label]
        for musinsa_style_label in musinsa_style_labels
        if musinsa_style_label in MUSINSA_STYLE_ID_MAP
    ]

    deeplink_context = {
        "gender": user_profile["gender"],
        "personal_color_code": user_profile["personal_color"],
        "personal_color_display": user_profile["personal_color_display"],
        "representative_colors": user_profile["representative_colors"],
        "color_search_keywords": user_profile["color_search_keywords"],
        "musinsa_color_keywords": _resolve_platform_color_keywords(user_profile["personal_color_display"], platform_name="musinsa"),
        "zigzag_color_keywords": _resolve_platform_color_keywords(user_profile["personal_color_display"], platform_name="zigzag"),
        "primary_style_code": primary_style_code,
        "primary_style_display": user_profile["style_display"].get(primary_style_code, primary_style_code),
        "secondary_style_codes": secondary_style_codes,
        "style_search_keywords": user_profile["style_search_keywords"],
        "fit_preference": user_profile["fit_preference"],
        "tpo_keyword": tpo_keyword,
        "musinsa_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
        "zigzag_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
    }

    return {
        "user_profile": user_profile,
        "deeplink_context": deeplink_context,
        "inferred_style_profile": inferred_style_profile,
        "musinsa_style_labels": musinsa_style_labels,
        "musinsa_style_ids": musinsa_style_ids,
        "musinsa_fit_codes": FIT_PREFERENCE_TO_MUSINSA_CODES.get(user_profile["fit_preference"], []),
        "zigzag_top_fit_keywords": FIT_PREFERENCE_TO_ZIGZAG_TOP_FITS.get(user_profile["fit_preference"], []),
        "zigzag_bottom_fit_keywords": FIT_PREFERENCE_TO_ZIGZAG_BOTTOM_FITS.get(user_profile["fit_preference"], []),
    }


def _collect_musinsa_style_labels(primary_style_code: str, secondary_style_codes: List[str]) -> List[str]:
    musinsa_style_labels: List[str] = []
    for style_code in [primary_style_code, *secondary_style_codes]:
        for musinsa_style_label in STYLE_CODE_TO_MUSINSA_LABELS.get(style_code, []):
            if musinsa_style_label not in musinsa_style_labels:
                musinsa_style_labels.append(musinsa_style_label)
    return musinsa_style_labels


def _resolve_platform_color_keywords(personal_color_display: str, *, platform_name: str) -> List[str]:
    platform_color_map = PERSONAL_COLOR_PLATFORM_KEYWORD_MAP.get(personal_color_display, {})
    return list(platform_color_map.get(platform_name, []))
