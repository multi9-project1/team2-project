"""
지그재그 크롤러 순수 함수 단위 테스트 (브라우저 불필요)
- _filter_zigzag_items_by_category_and_color()
- _resolve_zigzag_category_filter_info()
- should_apply_zigzag_color_filter()
- _normalize_filter_keyword()
- _resolve_selected_color_keywords()
- _resolve_requested_zigzag_main_categories()
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.crawlers.zigzag_crl import (
    STYLE_TO_ZIGZAG_MAP,
    ZIGZAG_MASTER_MAP,
    _filter_zigzag_items_by_category_and_color,
    _normalize_filter_keyword,
    _resolve_requested_zigzag_main_categories,
    _resolve_selected_color_keywords,
    _resolve_zigzag_category_filter_info,
    should_apply_zigzag_color_filter,
)


# ──────────────────────────────────────────────
# _filter_zigzag_items_by_category_and_color
# ──────────────────────────────────────────────
class TestFilterZigzagItemsByCategoryAndColor:
    ITEMS = [
        {"title": "블라우스 노멀핏 화이트", "mall_name": "패션샵"},
        {"title": "데님팬츠 와이드핏 블루", "mall_name": "청바지몰"},
        {"title": "미니원피스 핑크 플로럴", "mall_name": "드레스샵"},
        {"title": "트레이닝 상의 루즈핏 그린", "mall_name": "스포츠몰"},
        {"title": "슬랙스 화이트 노멀핏", "mall_name": "오피스몰"},
    ]

    def test_category_filter_narrows_results(self):
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=self.ITEMS,
            category_filter_terms=["블라우스"],
            color_filter_terms=[],
            top_n=5,
        )
        # 블라우스 포함 항목이 상위에 와야 함
        assert result[0]["title"] == "블라우스 노멀핏 화이트"

    def test_color_filter_boosts_matching_items(self):
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=self.ITEMS,
            category_filter_terms=["원피스"],
            color_filter_terms=["핑크"],
            top_n=5,
        )
        # 원피스+핑크 동시 매칭 항목이 최상위
        titles = [item["title"] for item in result]
        assert "미니원피스 핑크 플로럴" in titles[:2]

    def test_top_n_limits_results(self):
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=self.ITEMS,
            category_filter_terms=[],
            color_filter_terms=[],
            top_n=2,
        )
        assert len(result) == 2

    def test_empty_items_returns_empty(self):
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=[],
            category_filter_terms=["블라우스"],
            color_filter_terms=["화이트"],
            top_n=5,
        )
        assert result == []

    def test_no_filter_returns_all_up_to_top_n(self):
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=self.ITEMS,
            category_filter_terms=[],
            color_filter_terms=[],
            top_n=10,
        )
        assert len(result) == len(self.ITEMS)

    def test_strict_match_category_and_color_prioritized(self):
        # 카테고리+색상 둘 다 매칭되는 항목이 먼저 나와야 함
        items = [
            {"title": "블라우스", "mall_name": "A"},           # 카테고리만
            {"title": "블라우스 화이트", "mall_name": "B"},    # 카테고리+색상
            {"title": "청바지", "mall_name": "C"},              # 매칭 없음
        ]
        result = _filter_zigzag_items_by_category_and_color(
            scraped_items=items,
            category_filter_terms=["블라우스"],
            color_filter_terms=["화이트"],
            top_n=3,
        )
        assert result[0]["title"] == "블라우스 화이트"


# ──────────────────────────────────────────────
# _resolve_zigzag_category_filter_info
# ──────────────────────────────────────────────
class TestResolveZigzagCategoryFilterInfo:
    def test_상의_returns_correct_middle_id(self):
        zigzag_style_info = STYLE_TO_ZIGZAG_MAP["캐주얼"]
        info = _resolve_zigzag_category_filter_info(
            category_name="상의",
            zigzag_style_info=zigzag_style_info,
        )
        assert info["middle_id"] == ZIGZAG_MASTER_MAP["상의"]["middle_id"]

    def test_니트카디건_includes_extra_filter_terms(self):
        zigzag_style_info = STYLE_TO_ZIGZAG_MAP["모던/미니멀"]
        info = _resolve_zigzag_category_filter_info(
            category_name="니트/카디건",
            zigzag_style_info=zigzag_style_info,
        )
        assert "니트" in info["filter_terms"]
        assert "카디건" in info["filter_terms"]

    def test_트레이닝_includes_extra_filter_terms(self):
        zigzag_style_info = STYLE_TO_ZIGZAG_MAP["스포티"]
        info = _resolve_zigzag_category_filter_info(
            category_name="트레이닝",
            zigzag_style_info=zigzag_style_info,
        )
        assert "트레이닝" in info["filter_terms"]
        assert "조거" in info["filter_terms"]

    def test_preferred_subcategories_are_deduplicated(self):
        zigzag_style_info = STYLE_TO_ZIGZAG_MAP["페미닌"]
        info = _resolve_zigzag_category_filter_info(
            category_name="원피스",
            zigzag_style_info=zigzag_style_info,
        )
        subcats = info["preferred_subcategories"]
        assert len(subcats) == len(set(subcats))

    def test_filter_terms_have_no_duplicates(self):
        zigzag_style_info = STYLE_TO_ZIGZAG_MAP["캐주얼"]
        info = _resolve_zigzag_category_filter_info(
            category_name="팬츠",
            zigzag_style_info=zigzag_style_info,
        )
        assert len(info["filter_terms"]) == len(set(info["filter_terms"]))


# ──────────────────────────────────────────────
# should_apply_zigzag_color_filter
# ──────────────────────────────────────────────
class TestShouldApplyZigzagColorFilter:
    def test_상의_applies_color(self):
        assert should_apply_zigzag_color_filter("상의") is True

    def test_원피스_applies_color(self):
        assert should_apply_zigzag_color_filter("원피스") is True

    def test_스커트_applies_color(self):
        assert should_apply_zigzag_color_filter("스커트") is True

    def test_팬츠_skips_color(self):
        assert should_apply_zigzag_color_filter("팬츠") is False

    def test_아우터_applies_color(self):
        assert should_apply_zigzag_color_filter("아우터") is True


# ──────────────────────────────────────────────
# _normalize_filter_keyword
# ──────────────────────────────────────────────
class TestNormalizeFilterKeyword:
    def test_strips_whitespace(self):
        assert _normalize_filter_keyword("  화이트  ") == "화이트"

    def test_lowercases_english(self):
        assert _normalize_filter_keyword("WHITE") == "white"

    def test_removes_internal_spaces(self):
        assert _normalize_filter_keyword("다크 블루") == "다크블루"

    def test_none_returns_empty(self):
        assert _normalize_filter_keyword(None) == ""

    def test_empty_string_returns_empty(self):
        assert _normalize_filter_keyword("") == ""


# ──────────────────────────────────────────────
# _resolve_selected_color_keywords
# ──────────────────────────────────────────────
class TestResolveSelectedColorKeywords:
    AVAILABLE = ["화이트", "네이비", "그레이"]

    def test_no_selected_returns_first(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, None, allow_color_filter=True)
        assert result == ["화이트"]

    def test_matching_selected_returned(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "네이비", allow_color_filter=True)
        assert result == ["네이비"]

    def test_unmatched_falls_back_to_first(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "핑크", allow_color_filter=True)
        assert result == ["화이트"]

    def test_filter_disabled_returns_empty(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "네이비", allow_color_filter=False)
        assert result == []

    def test_empty_available_returns_empty(self):
        result = _resolve_selected_color_keywords([], None, allow_color_filter=True)
        assert result == []


# ──────────────────────────────────────────────
# _resolve_requested_zigzag_main_categories
# ──────────────────────────────────────────────
class TestResolveRequestedZigzagMainCategories:
    def test_전체_expands_to_default_categories(self):
        result = _resolve_requested_zigzag_main_categories(["전체"])
        assert "상의" in result
        assert "팬츠" in result

    def test_하의_maps_to_팬츠_and_스커트(self):
        result = _resolve_requested_zigzag_main_categories(["하의"])
        assert "팬츠" in result
        assert "스커트" in result

    def test_세트_maps_to_투피스세트_and_트레이닝(self):
        result = _resolve_requested_zigzag_main_categories(["세트"])
        assert "투피스/세트" in result
        assert "트레이닝" in result

    def test_valid_single_category(self):
        result = _resolve_requested_zigzag_main_categories(["원피스"])
        assert result == ["원피스"]

    def test_unknown_category_excluded(self):
        result = _resolve_requested_zigzag_main_categories(["없는카테고리"])
        assert result == []

    def test_no_duplicates_in_result(self):
        result = _resolve_requested_zigzag_main_categories(["하의", "팬츠"])
        assert len(result) == len(set(result))


# ──────────────────────────────────────────────
# STYLE_TO_ZIGZAG_MAP 데이터 무결성
# ──────────────────────────────────────────────
class TestStyleToZigzagMapIntegrity:
    def test_all_styles_have_required_keys(self):
        required_keys = {"search_prefix", "top_fit", "bottom_fit", "recommend_cats"}
        for style_name, style_info in STYLE_TO_ZIGZAG_MAP.items():
            missing = required_keys - style_info.keys()
            assert not missing, f"'{style_name}' 스타일에 키 누락: {missing}"

    def test_recommend_cats_are_tuples_of_two(self):
        for style_name, style_info in STYLE_TO_ZIGZAG_MAP.items():
            for cat_tuple in style_info["recommend_cats"]:
                assert len(cat_tuple) == 2, f"'{style_name}' recommend_cats 항목이 2-튜플이 아님: {cat_tuple}"

    def test_recommend_cats_main_category_in_master_map(self):
        for style_name, style_info in STYLE_TO_ZIGZAG_MAP.items():
            for main_cat, _ in style_info["recommend_cats"]:
                assert main_cat in ZIGZAG_MASTER_MAP, (
                    f"'{style_name}' recommend_cats의 main_cat '{main_cat}'이 ZIGZAG_MASTER_MAP에 없음"
                )
