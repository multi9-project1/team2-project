from __future__ import annotations

import json
from pathlib import Path

from item_feature_builder import build_item_feature_list
from recommender import filter_items_by_gender, filter_items_by_tpo, find_top_style_match, rank_items
from survey_parser import build_user_profile


def run_example(name: str, survey_payload: dict, *, dataset_dir: str | None = None) -> None:
    profile = build_user_profile(survey_payload).to_dict()
    items = build_item_feature_list(dataset_dir=dataset_dir, allow_mock=True)
    filtered_items = filter_items_by_gender(filter_items_by_tpo(items, profile.get("tpo_preference", "")), profile["gender"])
    ranked = rank_items(profile, filtered_items or items, top_n=5)
    top_match = find_top_style_match(profile, filtered_items or items)

    print(f"\n=== {name} ===")
    print(
        json.dumps(
            {
                "user_profile": profile,
                "analysis_text": f"알고리즘 분석 결과, 당신의 취향은 **[{top_match['era']}년대]**의 **[{top_match['style']}]**과 {top_match['similarity_percent']}% 일치합니다",
                "top5": ranked,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    sample_dataset_dir = None
    project_root = Path(__file__).resolve().parent
    extracted_candidate = project_root / "sample_data"
    if extracted_candidate.exists():
        sample_dataset_dir = str(extracted_candidate)

    run_example(
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

    run_example(
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
    main()
