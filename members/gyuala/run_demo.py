from __future__ import annotations

import json
from pathlib import Path

from item_feature_builder import build_item_feature_list
from recommender import rank_items
from survey_parser import build_user_profile


def run_example(name: str, survey_payload: dict, *, dataset_dir: str | None = None) -> None:
    profile = build_user_profile(survey_payload).to_dict()
    items = build_item_feature_list(dataset_dir=dataset_dir, allow_mock=True)
    ranked = rank_items(profile, items, top_n=5)

    print(f"\n=== {name} ===")
    print(json.dumps({"user_profile": profile, "top5": ranked}, ensure_ascii=False, indent=2))


def main() -> None:
    sample_dataset_dir = None
    project_root = Path(__file__).resolve().parent
    extracted_candidate = project_root / "Sample"
    if extracted_candidate.exists():
        sample_dataset_dir = str(extracted_candidate)

    run_example(
        "직접 퍼스널컬러 선택 예시",
        {
            "gender": "여성",
            "personal_color": "winter_deep",
            "Qstyle_1": "A",
            "Qstyle_2": "B",
            "Qstyle_3": "B",
            "Qstyle_4": "A",
            "Qstyle_5": "B",
            "Qstyle_6": "A",
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
            "Qstyle_2": "A",
            "Qstyle_3": "A",
            "Qstyle_4": "B",
            "Qstyle_5": "A",
            "Qstyle_6": "B",
        },
        dataset_dir=sample_dataset_dir,
    )


if __name__ == "__main__":
    main()
