"""
무신사 크롤러 순수 함수 단위 테스트 (브라우저 불필요)
- build_profile(), build_category_url(), resolve_musinsa_category_code()
- should_apply_musinsa_color_filter(), _resolve_selected_color_keywords()
- _normalize_filter_keyword(), _resolve_legacy_* helpers
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.crawlers.musinsa_crl import (
    MAPSITI_STYLE_MAP,
    PERSONAL_COLOR_MAP,
    build_category_url,
    build_profile,
    resolve_musinsa_category_code,
    should_apply_musinsa_color_filter,
    _normalize_filter_keyword,
    _resolve_selected_color_keywords,
    _resolve_legacy_musinsa_style_name,
    _resolve_legacy_personal_color_key,
)


# ──────────────────────────────────────────────
# build_profile
# ──────────────────────────────────────────────
class TestBuildProfile:
    def test_valid_modern_minimal_summer_muted_female(self):
        profile = build_profile("모던/미니멀", "여름뮤트", "F")
        assert profile["mapsiti"] == "모던/미니멀"
        assert profile["gender"] == "F"
        assert profile["personal_color"] == "여름뮤트"
        assert isinstance(profile["style_codes"], list)
        assert isinstance(profile["fit_codes"], list)
        assert isinstance(profile["recommended_colors"], list)
        assert len(profile["recommended_colors"]) > 0

    def test_valid_street_autumn_warm_male(self):
        profile = build_profile("스트리트", "가을웜", "M")
        assert profile["gender"] == "M"
        assert "스트릿" in profile["recommended_styles"]
        # 스트리트 → 루즈 핏 → 오버사이즈 코드
        assert "2^90" in profile["fit_codes"]

    def test_invalid_mapsiti_raises_value_error(self):
        with pytest.raises(ValueError, match="잘못된 MAPSITI"):
            build_profile("없는스타일", "여름뮤트", "F")

    def test_invalid_personal_color_raises_value_error(self):
        with pytest.raises(ValueError, match="잘못된 MAPSITI"):
            build_profile("모던/미니멀", "없는색상", "F")

    def test_legacy_alias_resolution(self):
        # "미니멀/모던" → "모던/미니멀" 로 정규화되어야 함
        profile = build_profile("미니멀/모던", "여름뮤트", "F")
        assert profile["mapsiti"] == "모던/미니멀"

    def test_all_style_map_keys_build_successfully(self):
        sample_color = "겨울쿨"
        for style_key in MAPSITI_STYLE_MAP:
            profile = build_profile(style_key, sample_color, "F")
            assert profile["mapsiti"] == style_key or profile["input_style"] == style_key

    def test_all_personal_color_keys_build_successfully(self):
        sample_style = "캐주얼"
        for color_key in PERSONAL_COLOR_MAP:
            profile = build_profile(sample_style, color_key, "M")
            assert len(profile["recommended_colors"]) > 0


# ──────────────────────────────────────────────
# build_category_url
# ──────────────────────────────────────────────
class TestBuildCategoryUrl:
    def test_url_contains_category_code(self):
        url = build_category_url("001", "F", ["WHITE"], [11])
        assert "/category/001/" in url
        assert "gf=F" in url

    def test_url_encodes_colors(self):
        url = build_category_url("003", "M", ["NAVY", "GRAY"], [1])
        assert "color=" in url

    def test_url_encodes_styles(self):
        url = build_category_url("001", "F", [], [1, 2])
        assert "style=" in url

    def test_url_contains_sort_code(self):
        url = build_category_url("001", "F", [], [])
        assert "sortCode=SALE_ONE_WEEK_COUNT" in url

    def test_url_no_fit_code_when_omitted(self):
        url = build_category_url("001", "F", ["WHITE"], [11], fit_codes=None)
        assert "attributeFit" not in url

    def test_url_includes_fit_code_when_provided(self):
        url = build_category_url("001", "F", ["WHITE"], [11], fit_codes=["2^87"])
        assert "attributeFit=" in url

    def test_url_empty_colors_no_color_param(self):
        url = build_category_url("001", "F", [], [11])
        assert "color=" not in url


# ──────────────────────────────────────────────
# resolve_musinsa_category_code
# ──────────────────────────────────────────────
class TestResolveCategoryCode:
    def test_top_level_상의(self):
        assert resolve_musinsa_category_code("상의") == "001"

    def test_top_level_바지(self):
        assert resolve_musinsa_category_code("바지") == "003"

    def test_sub_category_맨투맨(self):
        assert resolve_musinsa_category_code("맨투맨&스웨트") == "001005"

    def test_sub_category_데님팬츠(self):
        assert resolve_musinsa_category_code("데님 팬츠") == "003002"

    def test_sub_category_미니원피스(self):
        assert resolve_musinsa_category_code("미니원피스") == "100001"

    def test_unknown_category_returns_none(self):
        assert resolve_musinsa_category_code("없는카테고리") is None


# ──────────────────────────────────────────────
# should_apply_musinsa_color_filter
# ──────────────────────────────────────────────
class TestColorFilterApplication:
    def test_상의_applies_color(self):
        assert should_apply_musinsa_color_filter("셔츠&블라우스") is True

    def test_원피스_applies_color(self):
        assert should_apply_musinsa_color_filter("미니원피스") is True

    def test_바지_skips_color(self):
        assert should_apply_musinsa_color_filter("바지") is False

    def test_팬츠_skips_color(self):
        assert should_apply_musinsa_color_filter("팬츠") is False

    def test_데님팬츠_skips_color(self):
        assert should_apply_musinsa_color_filter("데님 팬츠") is False

    def test_슬랙스_skips_color(self):
        assert should_apply_musinsa_color_filter("슈트 팬츠&슬랙스") is False


# ──────────────────────────────────────────────
# _normalize_filter_keyword
# ──────────────────────────────────────────────
class TestNormalizeFilterKeyword:
    def test_strips_whitespace(self):
        assert _normalize_filter_keyword("  WHITE  ") == "white"

    def test_lowercases(self):
        assert _normalize_filter_keyword("NAVY") == "navy"

    def test_removes_internal_spaces(self):
        assert _normalize_filter_keyword("DARK BLUE") == "darkblue"

    def test_empty_string(self):
        assert _normalize_filter_keyword("") == ""

    def test_none_returns_empty(self):
        assert _normalize_filter_keyword(None) == ""


# ──────────────────────────────────────────────
# _resolve_selected_color_keywords
# ──────────────────────────────────────────────
class TestResolveSelectedColorKeywords:
    AVAILABLE = ["WHITE", "NAVY", "GRAY"]

    def test_no_selected_color_returns_first(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, None, allow_color_filter=True)
        assert result == ["WHITE"]

    def test_matching_color_returned(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "NAVY", allow_color_filter=True)
        assert result == ["NAVY"]

    def test_case_insensitive_match(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "navy", allow_color_filter=True)
        assert result == ["NAVY"]

    def test_unmatched_color_falls_back_to_first(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "PINK", allow_color_filter=True)
        assert result == ["WHITE"]

    def test_color_filter_disabled_returns_empty(self):
        result = _resolve_selected_color_keywords(self.AVAILABLE, "NAVY", allow_color_filter=False)
        assert result == []

    def test_empty_available_returns_empty(self):
        result = _resolve_selected_color_keywords([], None, allow_color_filter=True)
        assert result == []


# ──────────────────────────────────────────────
# _resolve_legacy_* helpers
# ──────────────────────────────────────────────
class TestLegacyResolvers:
    def test_resolve_legacy_style_소피스티케이티드(self):
        result = _resolve_legacy_musinsa_style_name("소피스티케이티드")
        assert result == "오피스/소피스티케이티드"

    def test_resolve_legacy_style_레트로(self):
        result = _resolve_legacy_musinsa_style_name("레트로")
        assert result == "레트로/빈티지"

    def test_resolve_legacy_style_unknown_passthrough(self):
        result = _resolve_legacy_musinsa_style_name("알수없는스타일")
        assert result == "알수없는스타일"

    def test_resolve_legacy_personal_color_봄_라이트(self):
        result = _resolve_legacy_personal_color_key("봄 라이트")
        assert result == "봄라이트"

    def test_resolve_legacy_personal_color_겨울_쿨(self):
        result = _resolve_legacy_personal_color_key("겨울 쿨")
        assert result == "겨울쿨"

    def test_resolve_legacy_personal_color_unknown_raises(self):
        with pytest.raises(ValueError, match="무신사 퍼스널컬러 매핑이 없습니다"):
            _resolve_legacy_personal_color_key("없는색상")
