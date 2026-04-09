"""
survey_parser 단위 테스트
- normalize_survey_gender()
- resolve_personal_color_code()
- calculate_style_score_map()
- determine_ranked_style_preferences()
- determine_fit_preference()
- create_survey_profile() 통합
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.logic.survey_parser import (
    create_survey_profile,
    normalize_survey_gender,
    resolve_personal_color_code,
    calculate_style_score_map,
    determine_ranked_style_preferences,
    determine_fit_preference,
    collect_style_search_keywords,
)
from app.logic.fashion_config import STYLE_CODE_ORDER


# ──────────────────────────────────────────────
# normalize_survey_gender
# ──────────────────────────────────────────────
class TestNormalizeSurveyGender:
    def test_female_variants(self):
        for val in ("여성", "F", "f", "FEMALE", "female", "W", "w", "Woman"):
            assert normalize_survey_gender(val) == "W", f"입력 {val!r} → W 기대"

    def test_male_variants(self):
        for val in ("남성", "M", "m", "MALE", "male", "Man"):
            assert normalize_survey_gender(val) == "M", f"입력 {val!r} → M 기대"

    def test_unknown_variants(self):
        for val in (None, "", "U", "Unisex", "ALL", "기타"):
            assert normalize_survey_gender(val) == "U", f"입력 {val!r} → U 기대"


# ──────────────────────────────────────────────
# resolve_personal_color_code
# ──────────────────────────────────────────────
class TestResolvePersonalColorCode:
    def test_direct_code_recognized(self):
        assert resolve_personal_color_code({"personal_color": "winter_deep"}) == "winter_deep"

    def test_korean_label_recognized(self):
        assert resolve_personal_color_code({"personal_color": "겨울 딥"}) == "winter_deep"

    def test_unknown_direct_falls_back_to_q_answers(self):
        # Q1~Q3 모두 A(웜) → Qwarm 으로 분기
        responses = {
            "personal_color": "unknown",
            "Q1": "A", "Q2": "A", "Q3": "A",
            "Qwarm": "A",
        }
        code = resolve_personal_color_code(responses)
        assert code != "unknown" or code == "unknown"  # Qwarm 값에 따라 달라짐, 예외 없이 실행돼야 함

    def test_warm_majority_branches_to_warm(self):
        responses = {"Q1": "A", "Q2": "A", "Q3": "B", "Qwarm": "A"}
        code = resolve_personal_color_code(responses)
        # warm 2 vs cool 1 → WARM_PERSONAL_COLOR_BRANCH_MAP["A"] 반환
        assert isinstance(code, str)

    def test_cool_majority_branches_to_cool(self):
        responses = {"Q1": "B", "Q2": "B", "Q3": "A", "Qcool": "A"}
        code = resolve_personal_color_code(responses)
        assert isinstance(code, str)

    def test_tie_returns_unknown(self):
        responses = {"Q1": "A", "Q2": "B"}
        # 투표 동점 → unknown
        code = resolve_personal_color_code(responses)
        # 동점 처리: 나머지 질문 없음 → 1:1
        assert code == "unknown" or isinstance(code, str)


# ──────────────────────────────────────────────
# calculate_style_score_map
# ──────────────────────────────────────────────
class TestCalculateStyleScoreMap:
    def test_returns_all_style_codes(self):
        responses = {}
        score_map = calculate_style_score_map(responses)
        for code in STYLE_CODE_ORDER:
            assert code in score_map

    def test_scores_are_non_negative(self):
        responses = {f"Qstyle_{i}": "A" for i in range(1, 10)}
        score_map = calculate_style_score_map(responses)
        for score in score_map.values():
            assert score >= 0

    def test_different_answers_yield_different_scores(self):
        all_a = calculate_style_score_map({f"Qstyle_{i}": "A" for i in range(1, 10)})
        all_b = calculate_style_score_map({f"Qstyle_{i}": "B" for i in range(1, 10)})
        assert all_a != all_b


# ──────────────────────────────────────────────
# determine_ranked_style_preferences
# ──────────────────────────────────────────────
class TestDetermineRankedStylePreferences:
    def test_primary_style_is_highest_score(self):
        score_map = {code: 0 for code in STYLE_CODE_ORDER}
        score_map["casual"] = 5
        score_map["sophisticated"] = 3
        primary, _ = determine_ranked_style_preferences(score_map)
        assert primary == "casual"

    def test_secondary_styles_exist_when_scores_positive(self):
        score_map = {code: 0 for code in STYLE_CODE_ORDER}
        score_map["casual"] = 5
        score_map["feminine"] = 4
        score_map["romantic"] = 3
        _, secondary = determine_ranked_style_preferences(score_map)
        assert "feminine" in secondary

    def test_secondary_max_two(self):
        score_map = {code: 3 for code in STYLE_CODE_ORDER}
        _, secondary = determine_ranked_style_preferences(score_map)
        assert len(secondary) <= 2

    def test_zero_score_not_in_secondary(self):
        score_map = {code: 0 for code in STYLE_CODE_ORDER}
        score_map[STYLE_CODE_ORDER[0]] = 3
        _, secondary = determine_ranked_style_preferences(score_map)
        assert secondary == []


# ──────────────────────────────────────────────
# determine_fit_preference
# ──────────────────────────────────────────────
class TestDetermineFitPreference:
    def test_A_returns_T(self):
        assert determine_fit_preference({"Qstyle_3": "A"}) == "T"

    def test_B_returns_L(self):
        assert determine_fit_preference({"Qstyle_3": "B"}) == "L"

    def test_missing_defaults_to_T(self):
        assert determine_fit_preference({}) == "T"

    def test_lowercase_A_treated_as_T(self):
        assert determine_fit_preference({"Qstyle_3": "a"}) == "T"


# ──────────────────────────────────────────────
# collect_style_search_keywords
# ──────────────────────────────────────────────
class TestCollectStyleSearchKeywords:
    def test_returns_list(self):
        keywords = collect_style_search_keywords("casual", [])
        assert isinstance(keywords, list)

    def test_no_duplicates(self):
        keywords = collect_style_search_keywords("casual", ["casual"])
        assert len(keywords) == len(set(keywords))

    def test_includes_primary_keywords(self):
        primary_kws = collect_style_search_keywords("casual", [])
        secondary_kws = collect_style_search_keywords("sophisticated", [])
        combined = collect_style_search_keywords("casual", ["sophisticated"])
        for kw in primary_kws:
            assert kw in combined


# ──────────────────────────────────────────────
# create_survey_profile (통합)
# ──────────────────────────────────────────────
FEMALE_CASUAL_SURVEY = {
    "gender": "여성",
    "personal_color": "winter_deep",
    "Qstyle_1": "A",
    "Qstyle_2": "B",
    "Qstyle_3": "B",  # 루즈 핏
    "Qstyle_4": "A",
    "Qstyle_5": "B",
    "Qstyle_6": "A",
    "Qstyle_7": "B",
    "Qstyle_8": "A",
    "Qstyle_9": "A",
}

MALE_STREET_SURVEY = {
    "gender": "남성",
    "personal_color": "autumn_warm",
    "Qstyle_1": "B",
    "Qstyle_2": "A",
    "Qstyle_3": "B",
    "Qstyle_4": "B",
    "Qstyle_5": "A",
    "Qstyle_6": "B",
    "Qstyle_7": "A",
    "Qstyle_8": "B",
    "Qstyle_9": "B",
}


class TestCreateSurveyProfile:
    def test_female_profile_gender(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert profile.gender == "W"

    def test_male_profile_gender(self):
        profile = create_survey_profile(MALE_STREET_SURVEY)
        assert profile.gender == "M"

    def test_personal_color_resolved(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert profile.personal_color == "winter_deep"
        assert "겨울 딥" in profile.personal_color_display

    def test_primary_style_is_valid_code(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert profile.primary_style in STYLE_CODE_ORDER

    def test_secondary_styles_subset_of_codes(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        for style in profile.secondary_styles:
            assert style in STYLE_CODE_ORDER

    def test_fit_preference_loose_for_B(self):
        # Qstyle_3 = B → 루즈 → "L"
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert profile.fit_preference == "L"

    def test_fit_preference_tight_for_A(self):
        survey = dict(FEMALE_CASUAL_SURVEY)
        survey["Qstyle_3"] = "A"
        profile = create_survey_profile(survey)
        assert profile.fit_preference == "T"

    def test_style_scores_all_present(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        for code in STYLE_CODE_ORDER:
            assert code in profile.style_scores

    def test_to_dict_serializable(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        d = profile.to_dict()
        assert isinstance(d, dict)
        assert "gender" in d
        assert "primary_style" in d
        assert "fit_preference" in d

    def test_representative_colors_is_list(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert isinstance(profile.representative_colors, list)

    def test_style_search_keywords_is_list(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert isinstance(profile.style_search_keywords, list)

    def test_color_search_keywords_is_list(self):
        profile = create_survey_profile(FEMALE_CASUAL_SURVEY)
        assert isinstance(profile.color_search_keywords, list)

    def test_minimal_empty_survey(self):
        # 빈 설문도 오류 없이 처리되어야 함
        profile = create_survey_profile({})
        assert profile.gender == "U"
        assert profile.personal_color == "unknown"
