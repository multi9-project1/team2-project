from typing import Any, Dict, List, Optional
from pathlib import Path

from app.logic.fashion_config import FIT_PREFERENCE_TO_Q411_SCORE, STYLE_LABELS, TPO_OPTION_TO_DEEPLINK_KEYWORD
from app.logic.item_feature_builder import ensure_dataset_archive_extracted, load_dataset_item_records
from app.logic.recommender import (
    collect_top_similarity_matches,
    derive_style_profile_from_similarity_matches,
    filter_image_available_items,
    filter_items_by_user_gender,
    find_highest_similarity_item_match,
    rank_recommendation_candidates,
)
from app.logic.survey_parser import collect_style_search_keywords, create_survey_profile
from app.schemas.recommendation import RecommendationQueryRequest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SAMPLE_ZIP = PROJECT_ROOT / "Sample.zip"
DEFAULT_DATASET_DIR = PROJECT_ROOT / "sample_data"

GENDER_DISPLAY_LABELS = {"M": "남성", "W": "여성", "U": "공용"}
FIT_Q411_DISPLAY_LABELS = {1: "루즈 핏", 2: "노멀 핏", 3: "타이트 핏"}

def resolve_style_display_label(style_group: str, style_code: Optional[str]) -> str:
    if style_code and style_code in STYLE_LABELS:
        return STYLE_LABELS[style_code]
    return style_group or "기타 스타일"

def resolve_fit_chip_labels(fit_preference_code: str, top_n: int = 2) -> List[str]:
    fit_score_map = FIT_PREFERENCE_TO_Q411_SCORE.get(fit_preference_code, {})
    ranked = sorted(fit_score_map.items(), key=lambda item: (-float(item[1]), item[0]))
    labels = [FIT_Q411_DISPLAY_LABELS.get(q411_value, str(q411_value)) for q411_value, score in ranked if score > 0]
    return labels[:top_n] or ["노멀 핏"]

def build_analysis_summary_payload(
    user_profile: Dict[str, Any],
    top_match: Dict[str, Any],
    inferred_style_profile: Dict[str, Any],
) -> Dict[str, Any]:
    style_label = resolve_style_display_label(
        inferred_style_profile.get("primary_group", ""),
        inferred_style_profile.get("primary_style_code"),
    )
    era = str(top_match.get("era") or "unknown")
    era_label = f"{era}년대" if era not in {"", "unknown", "None"} else "취향 분석 기준"
    similarity_percent = int(top_match.get("similarity_percent", 0) or 0)
    fit_labels = resolve_fit_chip_labels(user_profile.get("fit_preference", "T"))
    chips = [
        {
            "key": "gender",
            "label": "성별",
            "code": user_profile.get("gender", "U"),
            "value": GENDER_DISPLAY_LABELS.get(user_profile.get("gender", "U"), "공용"),
        },
        {
            "key": "personal_color",
            "label": "퍼스널컬러",
            "code": user_profile.get("personal_color", "unknown"),
            "value": user_profile.get("personal_color_display", "모르겠음"),
        },
        {
            "key": "fit",
            "label": "핏",
            "code": user_profile.get("fit_preference", "T"),
            "value": " / ".join(fit_labels),
        },
    ]
    description = f"알고리즘 분석 결과, 당신의 취향은 [{era_label} | {style_label}]와 {similarity_percent}% 일치합니다."
    return {
        "title": "분석 요약",
        "description": description,
        "era": era,
        "era_label": era_label,
        "style": style_label,
        "similarity_percent": similarity_percent,
        "fit_profile": {
            "preference_code": user_profile.get("fit_preference", "T"),
            "chip_labels": fit_labels,
        },
        "chips": chips,
    }

def create_deeplink_context(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "gender": user_profile["gender"],
        "personal_color_code": user_profile["personal_color"],
        "personal_color_display": user_profile["personal_color_display"],
        "representative_colors": user_profile["representative_colors"],
        "color_search_keywords": user_profile["color_search_keywords"],
        "primary_style_code": user_profile["primary_style"],
        "primary_style_display": user_profile["style_display"].get(user_profile["primary_style"], user_profile["primary_style"]),
        "secondary_style_codes": user_profile["secondary_styles"],
        "style_search_keywords": user_profile["style_search_keywords"],
        "fit_preference": user_profile["fit_preference"],
        "tpo_keyword": TPO_OPTION_TO_DEEPLINK_KEYWORD.get(user_profile.get("tpo_preference", ""), ""),
        "musinsa_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
        "zigzag_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
    }

def create_profile_response_payload(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_profile": user_profile,
        "deeplink_context": create_deeplink_context(user_profile),
    }

def resolve_dataset_input_paths(request: RecommendationQueryRequest) -> tuple[Optional[str], Optional[str], Optional[str]]:
    zip_path = request.zip_path
    extract_dir = request.extract_dir
    dataset_dir = request.dataset_dir

    if not zip_path and DEFAULT_SAMPLE_ZIP.exists():
        zip_path = str(DEFAULT_SAMPLE_ZIP)
    if not extract_dir and zip_path:
        extract_dir = str(DEFAULT_DATASET_DIR)
    if not dataset_dir and DEFAULT_DATASET_DIR.exists():
        dataset_dir = str(DEFAULT_DATASET_DIR)

    return zip_path, extract_dir, dataset_dir

def build_static_image_url(image_path: str, dataset_dir: Optional[str]) -> Optional[str]:
    if not image_path or not dataset_dir:
        return None

    dataset_root = Path(dataset_dir).resolve()
    candidate = Path(image_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / image_path).resolve()

    try:
        relative_path = candidate.relative_to(dataset_root)
    except ValueError:
        return None

    return f"/sample-files/{relative_path.as_posix()}"

def attach_recommendation_image_urls(
    recommendations: List[Dict[str, Any]],
    dataset_dir: Optional[str],
    base_url: str,
) -> List[Dict[str, Any]]:
    for item in recommendations:
        relative_url = build_static_image_url(str(item.get("image_path", "")), dataset_dir)
        item["image_url"] = relative_url
        item["image_full_url"] = f"{base_url.rstrip('/')}{relative_url}" if relative_url else None
    return recommendations

def _is_mock_recommendation_source(items: List[Dict[str, Any]]) -> bool:
    return bool(items) and all(str(item.get("item_id", "")).startswith("mock_") for item in items)

def generate_dataset_recommendation_response(
    request: RecommendationQueryRequest,
    base_url: str,
) -> Dict[str, Any]:
    user_profile = create_survey_profile(request.survey.model_dump()).to_dict()
    zip_path, extract_dir, dataset_dir = resolve_dataset_input_paths(request)

    if request.prefer_extracted_dataset and zip_path and extract_dir:
        extracted_path = ensure_dataset_archive_extracted(zip_path, extract_dir)
        dataset_dir = str(extracted_path)

    dataset_items = load_dataset_item_records(
        zip_path=zip_path,
        extract_dir=extract_dir,
        dataset_dir=dataset_dir,
        allow_mock=request.allow_mock_data,
    )
    gender_filtered_items = filter_items_by_user_gender(dataset_items, user_profile["gender"])
    image_ready_items = filter_image_available_items(gender_filtered_items)
    candidate_items = image_ready_items or gender_filtered_items or dataset_items
    top_similarity_matches = collect_top_similarity_matches(user_profile, gender_filtered_items or dataset_items, top_k=20)
    inferred_style_profile = derive_style_profile_from_similarity_matches(top_similarity_matches)
    
    if inferred_style_profile.get("primary_style_code"):
        primary_style_code = inferred_style_profile["primary_style_code"]
        secondary_style_codes = inferred_style_profile["secondary_style_codes"]
        user_profile["primary_style"] = primary_style_code
        user_profile["secondary_styles"] = secondary_style_codes
        user_profile["style_display"] = {primary_style_code: STYLE_LABELS.get(primary_style_code, primary_style_code)}
        user_profile["style_search_keywords"] = collect_style_search_keywords(primary_style_code, secondary_style_codes)

    top_match = find_highest_similarity_item_match(user_profile, gender_filtered_items or dataset_items)
    recommendations = attach_recommendation_image_urls(
        rank_recommendation_candidates(user_profile, candidate_items, top_n=request.top_n),
        dataset_dir,
        base_url,
    )

    response = create_profile_response_payload(user_profile)
    response["recommendation_results"] = recommendations
    analysis_summary = build_analysis_summary_payload(user_profile, top_match, inferred_style_profile)
    response["preference_analysis"] = {
        "era": analysis_summary["era"],
        "era_label": analysis_summary["era_label"],
        "style": analysis_summary["style"],
        "similarity_percent": analysis_summary["similarity_percent"],
        "text": analysis_summary["description"],
    }
    response["analysis_summary"] = analysis_summary
    response["meta"] = {
        "includes_dataset_recommendations": True,
        "item_count": len(dataset_items),
        "gender_filtered_item_count": len(gender_filtered_items),
        "image_ready_item_count": len(image_ready_items),
        "mock_data_used": _is_mock_recommendation_source(dataset_items),
        "resolved_zip_path": zip_path,
        "resolved_dataset_dir": dataset_dir or extract_dir,
        "sample_files_base_url": "/sample-files" if dataset_dir else None,
        "recommended_usage": "analysis-or-demo",
        "tpo_scoring_enabled": True,
    }
    return response