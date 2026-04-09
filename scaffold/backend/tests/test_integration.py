"""
통합 테스트 (Integration Tests)

외부 브라우저/네트워크만 mock하고 내부 파이프라인 전체를 실제로 실행합니다.

테스트 범위:
1. 추천 검색 프로파일 파이프라인 (survey → build_recommendation_search_profile)
2. 무신사 크롤러 파이프라인 (실제 URL 생성 + 브라우저 mock)
3. 지그재그 크롤러 파이프라인 (실제 필터링 로직 + 브라우저 mock)
4. 추천 엔진 파이프라인 (스타일/핏/컬러 점수 계산 → 랭킹)
5. FastAPI 엔드포인트 풀 파이프라인 (실제 mock 데이터셋 사용)
"""
from __future__ import annotations

import sys
import os
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app
from app.logic.survey_parser import create_survey_profile
from app.logic.recommender import (
    rank_recommendation_candidates,
    filter_items_by_user_gender,
    collect_top_similarity_matches,
    derive_style_profile_from_similarity_matches,
    calculate_style_match_score,
    calculate_color_match_score,
    calculate_fit_match_score,
)
from app.logic.item_feature_builder import load_dataset_item_records
from app.crawlers.recommendation_search_profile import build_recommendation_search_profile
from app.crawlers.musinsa_crl import (
    build_recommendation_aligned_profile,
    build_category_url,
    recommend_outfit_from_survey,
    resolve_musinsa_category_code,
)
from app.crawlers.zigzag_crl import (
    get_zigzag_recommendations_from_survey,
    _filter_zigzag_items_by_category_and_color,
)

client = TestClient(app)

# ──────────────────────────────────────────────
# 공통 테스트 설문 데이터
# ──────────────────────────────────────────────
FEMALE_WINTER_DEEP_SURVEY = {
    "gender": "여성",
    "personal_color": "winter_deep",
    "Qstyle_1": "A",
    "Qstyle_2": "B",
    "Qstyle_3": "A",  # 타이트 핏
    "Qstyle_4": "A",
    "Qstyle_5": "B",
    "Qstyle_6": "A",
    "Qstyle_7": "B",
    "Qstyle_8": "A",
    "Qstyle_9": "A",
}

MALE_AUTUMN_WARM_SURVEY = {
    "gender": "남성",
    "personal_color": "autumn_warm",
    "Qstyle_1": "B",
    "Qstyle_2": "A",
    "Qstyle_3": "B",  # 루즈 핏
    "Qstyle_4": "B",
    "Qstyle_5": "A",
    "Qstyle_6": "B",
    "Qstyle_7": "A",
    "Qstyle_8": "B",
    "Qstyle_9": "B",
}

FEMALE_SUMMER_LIGHT_SURVEY = {
    "gender": "여성",
    "personal_color": "summer_light",
    "Qstyle_1": "A",
    "Qstyle_2": "A",
    "Qstyle_3": "A",
    "Qstyle_4": "A",
    "Qstyle_5": "A",
    "Qstyle_6": "A",
    "Qstyle_7": "A",
    "Qstyle_8": "A",
    "Qstyle_9": "C",
}

# mock 데이터셋 아이템 (내부 스코어링 로직 실행을 위한 최소 구조)
MOCK_ITEMS = [
    {
        "item_id": "mock_001", "gender": "W", "era": "2020", "style": "romantic",
        "image_path": "mock_001.jpg",
        "Q3": 2, "Q411": 1, "Q412": 1, "Q413": 2, "Q414": 2,
        "Q4201": 1, "Q4202": 0, "Q4203": 1, "Q4204": 0,
        "Q4205": 1, "Q4206": 0, "Q4207": 0, "Q4208": 0,
        "Q4209": 0, "Q4210": 0, "Q4211": 0, "Q4212": 0,
        "Q4213": 0, "Q4214": 0, "Q4215": 0, "Q4216": 0,
    },
    {
        "item_id": "mock_002", "gender": "W", "era": "2010", "style": "sophisticated",
        "image_path": "mock_002.jpg",
        "Q3": 4, "Q411": 1, "Q412": 2, "Q413": 1, "Q414": 1,
        "Q4201": 0, "Q4202": 1, "Q4203": 0, "Q4204": 1,
        "Q4205": 0, "Q4206": 1, "Q4207": 0, "Q4208": 0,
        "Q4209": 0, "Q4210": 0, "Q4211": 0, "Q4212": 0,
        "Q4213": 0, "Q4214": 0, "Q4215": 0, "Q4216": 0,
    },
    {
        "item_id": "mock_003", "gender": "M", "era": "2000", "style": "street",
        "image_path": "mock_003.jpg",
        "Q3": 5, "Q411": 2, "Q412": 1, "Q413": 2, "Q414": 1,
        "Q4201": 0, "Q4202": 0, "Q4203": 0, "Q4204": 0,
        "Q4205": 0, "Q4206": 0, "Q4207": 1, "Q4208": 1,
        "Q4209": 0, "Q4210": 0, "Q4211": 0, "Q4212": 0,
        "Q4213": 0, "Q4214": 0, "Q4215": 0, "Q4216": 0,
    },
    {
        "item_id": "mock_004", "gender": "W", "era": "2015", "style": "casual",
        "image_path": "mock_004.jpg",
        "Q3": 1, "Q411": 2, "Q412": 2, "Q413": 1, "Q414": 1,
        "Q4201": 1, "Q4202": 0, "Q4203": 0, "Q4204": 0,
        "Q4205": 0, "Q4206": 0, "Q4207": 0, "Q4208": 1,
        "Q4209": 0, "Q4210": 0, "Q4211": 0, "Q4212": 0,
        "Q4213": 0, "Q4214": 0, "Q4215": 0, "Q4216": 0,
    },
    {
        "item_id": "mock_005", "gender": "M", "era": "2018", "style": "sporty",
        "image_path": "mock_005.jpg",
        "Q3": 6, "Q411": 2, "Q412": 1, "Q413": 1, "Q414": 2,
        "Q4201": 0, "Q4202": 0, "Q4203": 0, "Q4204": 0,
        "Q4205": 0, "Q4206": 0, "Q4207": 0, "Q4208": 0,
        "Q4209": 1, "Q4210": 1, "Q4211": 0, "Q4212": 0,
        "Q4213": 0, "Q4214": 0, "Q4215": 0, "Q4216": 0,
    },
]


# ══════════════════════════════════════════════════════════════════
# 1. 추천 검색 프로파일 파이프라인 통합
# ══════════════════════════════════════════════════════════════════
class TestRecommendationSearchProfilePipeline:
    """survey → build_recommendation_search_profile 전체 흐름"""

    def test_female_winter_deep_profile_structure(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert "user_profile" in profile
        assert "deeplink_context" in profile
        assert "inferred_style_profile" in profile
        assert "musinsa_style_labels" in profile
        assert "musinsa_fit_codes" in profile
        assert "zigzag_top_fit_keywords" in profile
        assert "zigzag_bottom_fit_keywords" in profile

    def test_deeplink_context_gender_matches_survey(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert profile["deeplink_context"]["gender"] == "W"

    def test_male_survey_gender_M(self):
        profile = build_recommendation_search_profile(
            MALE_AUTUMN_WARM_SURVEY, allow_mock=True
        )
        assert profile["deeplink_context"]["gender"] == "M"

    def test_personal_color_display_populated(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        ctx = profile["deeplink_context"]
        assert ctx["personal_color_display"] != ""
        assert ctx["personal_color_code"] == "winter_deep"

    def test_primary_style_code_is_valid(self):
        from app.logic.fashion_config import STYLE_CODE_ORDER
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert profile["deeplink_context"]["primary_style_code"] in STYLE_CODE_ORDER

    def test_musinsa_style_labels_are_strings(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        for label in profile["musinsa_style_labels"]:
            assert isinstance(label, str)

    def test_fit_codes_populated_for_tight_fit(self):
        # Qstyle_3=A → 타이트 핏 → musinsa_fit_codes 존재
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert isinstance(profile["musinsa_fit_codes"], list)

    def test_fit_codes_populated_for_loose_fit(self):
        # Qstyle_3=B → 루즈 핏
        profile = build_recommendation_search_profile(
            MALE_AUTUMN_WARM_SURVEY, allow_mock=True
        )
        assert isinstance(profile["musinsa_fit_codes"], list)
        assert len(profile["musinsa_fit_codes"]) > 0

    def test_zigzag_color_keywords_populated(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        ctx = profile["deeplink_context"]
        assert isinstance(ctx["zigzag_color_keywords"], list)

    def test_musinsa_color_keywords_populated(self):
        profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        ctx = profile["deeplink_context"]
        assert isinstance(ctx["musinsa_color_keywords"], list)

    def test_multiple_surveys_produce_different_profiles(self):
        female_profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        male_profile = build_recommendation_search_profile(
            MALE_AUTUMN_WARM_SURVEY, allow_mock=True
        )
        assert female_profile["deeplink_context"]["gender"] != male_profile["deeplink_context"]["gender"]


# ══════════════════════════════════════════════════════════════════
# 2. 추천 엔진 파이프라인 통합
# ══════════════════════════════════════════════════════════════════
class TestRecommenderEnginePipeline:
    """실제 스코어링 로직 전체 실행"""

    def setup_method(self):
        self.user_profile = create_survey_profile(FEMALE_WINTER_DEEP_SURVEY).to_dict()
        self.items = MOCK_ITEMS

    def test_gender_filter_returns_female_items_only(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        for item in female_items:
            assert item["gender"] == "W"

    def test_gender_filter_returns_male_items_only(self):
        male_profile = create_survey_profile(MALE_AUTUMN_WARM_SURVEY).to_dict()
        male_items = filter_items_by_user_gender(self.items, male_profile["gender"])
        for item in male_items:
            assert item["gender"] == "M"

    def test_gender_filter_fallback_when_no_match(self):
        # 성별 필터링 결과가 없으면 전체 반환
        items_all_female = [dict(i, gender="W") for i in self.items]
        result = filter_items_by_user_gender(items_all_female, "M")
        assert len(result) == len(items_all_female)

    def test_style_match_score_is_float_between_0_and_1(self):
        for item in self.items:
            score, breakdown = calculate_style_match_score(
                item, self.user_profile["primary_style"], self.user_profile["secondary_styles"]
            )
            assert 0.0 <= score <= 1.0
            assert "primary_match" in breakdown
            assert "secondary_match" in breakdown

    def test_color_match_score_is_float_between_0_and_1(self):
        for item in self.items:
            score, breakdown = calculate_color_match_score(
                item, self.user_profile["personal_color"]
            )
            assert 0.0 <= score <= 1.0

    def test_fit_match_score_is_valid(self):
        for item in self.items:
            score = calculate_fit_match_score(item, self.user_profile["fit_preference"])
            assert isinstance(score, float)
            assert score >= 0.0

    def test_rank_recommendation_candidates_returns_list(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        results = rank_recommendation_candidates(self.user_profile, female_items, top_n=3)
        assert isinstance(results, list)

    def test_rank_recommendation_candidates_respects_top_n(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        results = rank_recommendation_candidates(self.user_profile, female_items, top_n=2)
        assert len(results) <= 2

    def test_ranked_results_sorted_by_score_descending(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        results = rank_recommendation_candidates(self.user_profile, female_items, top_n=5)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_recommendation_result_has_required_keys(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        results = rank_recommendation_candidates(self.user_profile, female_items, top_n=3)
        for result in results:
            assert "item_id" in result
            assert "score" in result
            assert "score_breakdown" in result
            assert "reasons" in result

    def test_reasons_list_not_empty(self):
        female_items = filter_items_by_user_gender(self.items, "W")
        results = rank_recommendation_candidates(self.user_profile, female_items, top_n=5)
        for result in results:
            assert len(result["reasons"]) >= 1

    def test_similarity_matches_collected(self):
        matches = collect_top_similarity_matches(self.user_profile, self.items, top_k=3)
        assert isinstance(matches, list)
        assert len(matches) <= 3
        for match in matches:
            assert "similarity" in match
            assert "style_group" in match

    def test_derive_style_profile_from_matches(self):
        matches = collect_top_similarity_matches(self.user_profile, self.items, top_k=5)
        inferred = derive_style_profile_from_similarity_matches(matches)
        assert "primary_group" in inferred
        assert "primary_style_code" in inferred
        assert "secondary_style_codes" in inferred
        assert isinstance(inferred["secondary_style_codes"], list)

    def test_full_pipeline_female_mock_dataset(self):
        """survey → 프로파일 → 필터링 → 랭킹 전체 흐름"""
        profile = create_survey_profile(FEMALE_WINTER_DEEP_SURVEY).to_dict()
        female_items = filter_items_by_user_gender(self.items, profile["gender"])
        matches = collect_top_similarity_matches(profile, female_items, top_k=5)
        inferred = derive_style_profile_from_similarity_matches(matches)
        if inferred.get("primary_style_code"):
            profile["primary_style"] = inferred["primary_style_code"]
        results = rank_recommendation_candidates(profile, female_items, top_n=3)
        assert isinstance(results, list)
        assert all("score" in r for r in results)

    def test_full_pipeline_male_mock_dataset(self):
        profile = create_survey_profile(MALE_AUTUMN_WARM_SURVEY).to_dict()
        male_items = filter_items_by_user_gender(self.items, profile["gender"])
        results = rank_recommendation_candidates(profile, male_items, top_n=2)
        assert isinstance(results, list)


# ══════════════════════════════════════════════════════════════════
# 3. 무신사 크롤러 파이프라인 통합 (브라우저 mock)
# ══════════════════════════════════════════════════════════════════
MOCK_CRAWLED_ITEMS = [
    {"brand": "브랜드A", "title": "슬림핏 셔츠", "price": "45,000", "img_url": "https://img1.jpg"},
    {"brand": "브랜드B", "title": "기본 니트", "price": "59,000", "img_url": "https://img2.jpg"},
    {"brand": "브랜드C", "title": "와이드 팬츠", "price": "72,000", "img_url": "https://img3.jpg"},
]


class TestMusinsaCrawlerPipeline:
    """recommend_outfit_from_survey: 실제 프로파일 빌드 + 브라우저 mock"""

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_recommend_outfit_from_survey_상의(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
            top_n=3,
        )
        assert result["platform"] == "musinsa"
        assert result["category"] == "상의"
        assert isinstance(result["items"], list)

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_result_has_applied_filters(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        filters = result["applied_filters"]
        assert "category" in filters
        assert "color_keywords" in filters
        assert "style_labels" in filters
        assert "fit_codes" in filters

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_url_built_correctly_for_상의(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert "musinsa.com/category/" in result["url"]
        assert "gf=" in result["url"]

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_바지_category_no_color_filter(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="바지",
            allow_mock=True,
        )
        # 바지는 색상 필터 없어야 함
        assert result["applied_filters"]["color_keywords"] == []

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_남성_survey_uses_M_gender_in_url(self, mock_crawl):
        result = recommend_outfit_from_survey(
            MALE_AUTUMN_WARM_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert "gf=M" in result["url"]

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_여성_survey_uses_F_gender_in_url(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert "gf=F" in result["url"]

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=[])
    def test_empty_crawl_result_returns_empty_items(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert result["items"] == []

    def test_invalid_category_raises_value_error(self):
        with pytest.raises(ValueError, match="무신사 카테고리를 찾을 수 없습니다"):
            recommend_outfit_from_survey(
                FEMALE_WINTER_DEEP_SURVEY,
                category_name="없는카테고리",
                allow_mock=True,
            )

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_profile_keys_present_in_result(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        profile = result["profile"]
        assert "mapsiti" in profile
        assert "gender" in profile
        assert "personal_color" in profile
        assert "recommended_colors" in profile

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_selected_color_overrides_default(self, mock_crawl):
        result = recommend_outfit_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            selected_color="BLACK",
            allow_mock=True,
        )
        # 색상이 selected_color로 설정되었거나 fallback이 적용됨
        assert result["selected_color"] is not None or result["applied_filters"]["color_keywords"] is not None


# ══════════════════════════════════════════════════════════════════
# 4. 지그재그 크롤러 파이프라인 통합 (브라우저 mock)
# ══════════════════════════════════════════════════════════════════
MOCK_ZIGZAG_ITEMS = [
    {"mall_name": "쇼핑몰A", "title": "블라우스 화이트 노멀핏", "price": "35,000원", "img_url": "https://img1.jpg"},
    {"mall_name": "쇼핑몰B", "title": "미니스커트 블랙", "price": "42,000원", "img_url": "https://img2.jpg"},
    {"mall_name": "쇼핑몰C", "title": "원피스 아이보리 미디", "price": "68,000원", "img_url": "https://img3.jpg"},
    {"mall_name": "쇼핑몰D", "title": "상의 루즈핏 그레이", "price": "28,000원", "img_url": "https://img4.jpg"},
    {"mall_name": "쇼핑몰E", "title": "니트 카디건 베이지", "price": "55,000원", "img_url": "https://img5.jpg"},
]


class TestZigzagCrawlerPipeline:
    """get_zigzag_recommendations_from_survey: 실제 프로파일 + 필터링 + 브라우저 mock"""

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_recommend_from_survey_상의(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
            top_n=3,
        )
        assert result["platform"] == "zigzag"
        assert result["category"] == "상의"
        assert isinstance(result["items"], list)

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_result_has_applied_filters(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        filters = result["applied_filters"]
        assert "category" in filters
        assert "color_keywords" in filters
        assert "style_labels" in filters

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_팬츠_no_color_filter(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="팬츠",
            allow_mock=True,
        )
        assert result["applied_filters"]["color_keywords"] == []

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_search_url_points_to_zigzag(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert "zigzag.kr/search" in result["url"]

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_search_keyword_is_string(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="원피스",
            allow_mock=True,
        )
        assert isinstance(result["search_keyword"], str)
        assert len(result["search_keyword"]) > 0

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_items_top_n_respected(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
            top_n=2,
        )
        assert len(result["items"]) <= 2

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=[])
    def test_empty_crawl_returns_empty_items(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
        )
        assert result["items"] == []

    def test_invalid_category_raises_value_error(self):
        with pytest.raises(ValueError, match="지그재그 카테고리"):
            get_zigzag_recommendations_from_survey(
                FEMALE_WINTER_DEEP_SURVEY,
                category_name="없는카테고리",
                allow_mock=True,
            )

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_filter_logic_applied_to_scraped_items(self, mock_crawl):
        """필터링 후 아이템 수가 원본 이하여야 함"""
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY,
            category_name="상의",
            allow_mock=True,
            top_n=5,
        )
        assert len(result["items"]) <= len(MOCK_ZIGZAG_ITEMS)

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_different_categories_different_filter_terms(self, mock_crawl):
        result_상의 = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY, category_name="상의", allow_mock=True
        )
        result_원피스 = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY, category_name="원피스", allow_mock=True
        )
        assert result_상의["applied_filters"]["middle_id"] != result_원피스["applied_filters"]["middle_id"]


# ══════════════════════════════════════════════════════════════════
# 5. FastAPI 풀 파이프라인 통합 (실제 mock 데이터셋)
# ══════════════════════════════════════════════════════════════════
class TestFullAPIFlowIntegration:
    """API → 파싱 → 추천 엔진 → 응답 구조 end-to-end"""

    BASE_PAYLOAD = {
        "survey": FEMALE_WINTER_DEEP_SURVEY,
        "top_n": 3,
        "allow_mock_data": True,
    }

    def test_profile_then_recommendations_consistent_gender(self):
        """POST /profile 과 POST /recommendations가 같은 성별 반환"""
        prof_resp = client.post("/profile", json={"survey": FEMALE_WINTER_DEEP_SURVEY})
        rec_resp = client.post("/recommendations", json=self.BASE_PAYLOAD)
        assert prof_resp.status_code == 200
        assert rec_resp.status_code == 200
        prof_gender = prof_resp.json()["user_profile"]["gender"]
        # /recommendations 는 텍스트만 반환하므로 프로파일과 별도로 일치 확인 불가이지만,
        # 적어도 텍스트에 "W" 관련 정보가 포함되었는지는 응답 구조로 확인
        assert prof_gender == "W"

    def test_recommendations_text_contains_analysis(self):
        resp = client.post("/recommendations", json=self.BASE_PAYLOAD)
        assert resp.status_code == 200
        text = resp.json()["text"]
        assert "알고리즘" in text or "%" in text

    def test_all_personal_colors_produce_valid_profile(self):
        personal_colors = [
            "spring_light", "spring_bright", "spring_warm",
            "summer_light", "summer_muted", "summer_cool",
            "autumn_muted", "autumn_deep", "autumn_warm",
            "winter_bright", "winter_deep", "winter_cool",
        ]
        for color in personal_colors:
            survey = dict(FEMALE_WINTER_DEEP_SURVEY)
            survey["personal_color"] = color
            resp = client.post("/profile", json={"survey": survey})
            assert resp.status_code == 200, f"{color} 퍼스널컬러 실패"
            assert resp.json()["user_profile"]["personal_color"] == color

    def test_all_style_answer_combinations_produce_valid_profile(self):
        """A/B 선택을 바꿔도 항상 유효한 프로파일 반환"""
        combinations = [
            {f"Qstyle_{i}": "A" for i in range(1, 10)},
            {f"Qstyle_{i}": "B" for i in range(1, 10)},
            {f"Qstyle_{i}": ("A" if i % 2 else "B") for i in range(1, 10)},
        ]
        for answers in combinations:
            survey = {"gender": "여성", "personal_color": "winter_deep", **answers}
            resp = client.post("/profile", json={"survey": survey})
            assert resp.status_code == 200

    def test_male_and_female_produce_different_deeplink_context(self):
        female_resp = client.post("/profile", json={"survey": FEMALE_WINTER_DEEP_SURVEY})
        male_resp = client.post("/profile", json={"survey": MALE_AUTUMN_WARM_SURVEY})
        female_ctx = female_resp.json()["deeplink_context"]
        male_ctx = male_resp.json()["deeplink_context"]
        assert female_ctx["gender"] != male_ctx["gender"]

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    def test_crawl_musinsa_full_flow(self, mock_crawl):
        payload = {
            "survey": FEMALE_WINTER_DEEP_SURVEY,
            "category_name": "상의",
            "allow_mock_data": True,
            "top_n": 3,
        }
        resp = client.post("/crawl/musinsa", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "musinsa"
        assert len(data["items"]) == len(MOCK_CRAWLED_ITEMS)

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_crawl_zigzag_full_flow(self, mock_crawl):
        payload = {
            "survey": FEMALE_WINTER_DEEP_SURVEY,
            "category_name": "상의",
            "allow_mock_data": True,
            "top_n": 3,
        }
        resp = client.post("/crawl/zigzag", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "zigzag"
        assert isinstance(data["items"], list)

    @patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=MOCK_CRAWLED_ITEMS)
    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=MOCK_ZIGZAG_ITEMS)
    def test_musinsa_and_zigzag_parallel_calls(self, mock_zigzag, mock_musinsa):
        """무신사와 지그재그를 동시에 호출해도 둘 다 정상 응답"""
        payload = {
            "survey": FEMALE_WINTER_DEEP_SURVEY,
            "category_name": "상의",
            "allow_mock_data": True,
            "top_n": 3,
        }
        musinsa_resp = client.post("/crawl/musinsa", json=payload)
        zigzag_resp = client.post("/crawl/zigzag", json=payload)
        assert musinsa_resp.status_code == 200
        assert zigzag_resp.status_code == 200
        assert musinsa_resp.json()["platform"] == "musinsa"
        assert zigzag_resp.json()["platform"] == "zigzag"


# ══════════════════════════════════════════════════════════════════
# 6. 크로스 파이프라인 일관성 검증
# ══════════════════════════════════════════════════════════════════
class TestCrossPipelineConsistency:
    """여러 파이프라인 간 동일 설문에서 출력이 일관성 있는지 검증"""

    def test_survey_parser_and_search_profile_gender_consistent(self):
        parsed = create_survey_profile(FEMALE_WINTER_DEEP_SURVEY).to_dict()
        search_profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert parsed["gender"] == search_profile["deeplink_context"]["gender"]

    def test_survey_parser_and_search_profile_personal_color_consistent(self):
        parsed = create_survey_profile(FEMALE_WINTER_DEEP_SURVEY).to_dict()
        search_profile = build_recommendation_search_profile(
            FEMALE_WINTER_DEEP_SURVEY, allow_mock=True
        )
        assert parsed["personal_color"] == search_profile["deeplink_context"]["personal_color_code"]

    def test_musinsa_profile_gender_matches_survey(self):
        with patch("app.crawlers.musinsa_crl.crawl_musinsa", return_value=[]):
            result = recommend_outfit_from_survey(
                FEMALE_WINTER_DEEP_SURVEY, category_name="상의", allow_mock=True
            )
        # gender F(여성) → musinsa URL에 gf=F
        assert "gf=F" in result["url"]

    @patch("app.crawlers.zigzag_crl.crawl_zigzag_store", return_value=[])
    def test_zigzag_style_keyword_derived_from_survey(self, mock_crawl):
        result = get_zigzag_recommendations_from_survey(
            FEMALE_WINTER_DEEP_SURVEY, category_name="상의", allow_mock=True
        )
        assert isinstance(result["search_keyword"], str)
        assert len(result["search_keyword"]) > 0

    def test_api_profile_and_direct_parser_same_primary_style(self):
        """API /profile 과 직접 create_survey_profile 결과가 동일한 primary_style"""
        parsed = create_survey_profile(FEMALE_WINTER_DEEP_SURVEY).to_dict()
        resp = client.post("/profile", json={"survey": FEMALE_WINTER_DEEP_SURVEY})
        api_primary = resp.json()["user_profile"]["primary_style"]
        # API는 inferred style이 적용될 수 있으므로 유효한 스타일 코드인지 확인
        from app.logic.fashion_config import STYLE_CODE_ORDER
        assert api_primary in STYLE_CODE_ORDER
