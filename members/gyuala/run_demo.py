from __future__ import annotations

import json
from pathlib import Path

from item_feature_builder import load_dataset_item_records
from recommender import (
    collect_top_similarity_matches,
    derive_style_profile_from_similarity_matches,
    filter_items_by_user_gender,
    find_highest_similarity_item_match,
    rank_recommendation_candidates,
)
from survey_parser import create_survey_profile


def run_demo_scenario(scenario_name: str, survey_answers: dict, *, dataset_dir: str | None = None) -> None:
    survey_profile = create_survey_profile(survey_answers).to_dict()
    dataset_items = load_dataset_item_records(dataset_dir=dataset_dir, allow_mock=True)
    gender_filtered_items = filter_items_by_user_gender(dataset_items, survey_profile["gender"])
    top_similarity_matches = collect_top_similarity_matches(survey_profile, gender_filtered_items or dataset_items, top_k=20)
    inferred_style_profile = derive_style_profile_from_similarity_matches(top_similarity_matches)
    ranked_recommendations = rank_recommendation_candidates(survey_profile, gender_filtered_items or dataset_items, top_n=5)
    top_match = find_highest_similarity_item_match(survey_profile, gender_filtered_items or dataset_items)

    print(f"\n=== {scenario_name} ===")
    print(
        json.dumps(
            {
                "user_profile": survey_profile,
                "analysis_text": f"알고리즘 분석 결과, 당신의 취향은 **[{top_match['era']}년대]**의 **[{inferred_style_profile['primary_group']}]**과 {top_match['similarity_percent']}% 일치합니다",
                "top5": ranked_recommendations,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def run_demo() -> None:
    sample_dataset_dir = None
    project_root = Path(__file__).resolve().parent
    extracted_candidate = project_root / "sample_data"
    if extracted_candidate.exists():
        sample_dataset_dir = str(extracted_candidate)

    run_demo_scenario(
        "직접 퍼스널컬러 선택 예시",
        {
            "gender": "여성",
            "personal_color": "winter_deep",
            "Qstyle_1": "A",
            "Qstyle_2": "A",
            "Qstyle_3": "B",
            "Qstyle_4": "A",
            "Qstyle_5": "A",
            "Qstyle_6": "A",
            "Qstyle_7": "B",
            "Qstyle_8": "B",
            "Qstyle_9": "A",
        },
        dataset_dir=sample_dataset_dir,
    )

    run_demo_scenario(
        "모르겠음 분기 예시",
        {
            "gender": "남성",
            "personal_color": "모르겠음",
            "Q1": "A",
            "Q2": "A",
            "Q3": "B",
            "Qwarm": "D",
            "Qstyle_1": "B",
            "Qstyle_2": "B",
            "Qstyle_3": "A",
            "Qstyle_4": "B",
            "Qstyle_5": "A",
            "Qstyle_6": "B",
            "Qstyle_7": "A",
            "Qstyle_8": "A",
            "Qstyle_9": "D",
        },
        dataset_dir=sample_dataset_dir,
    )


if __name__ == "__main__":
    run_demo()
