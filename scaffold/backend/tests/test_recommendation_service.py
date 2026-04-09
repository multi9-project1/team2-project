"""
recommendation_service 단위 테스트
- RecommendationService 초기화
- create_deeplink_context()
- create_profile_response_payload()
- build_static_image_url()
- attach_recommendation_image_urls()
- _is_mock_recommendation_source()
"""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.recommendation_service import (
    create_deeplink_context,
    create_profile_response_payload,
    build_static_image_url,
    attach_recommendation_image_urls,
    _is_mock_recommendation_source,
)


# ──────────────────────────────────────────────
# 공통 픽스처
# ──────────────────────────────────────────────
@pytest.fixture
def sample_user_profile():
    return {
        "gender": "W",
        "personal_color": "winter_deep",
        "personal_color_display": "겨울 딥",
        "representative_colors": ["버건디", "포레스트 그린"],
        "primary_style": "sophisticated",
        "secondary_styles": ["feminine"],
        "fit_preference": "T",
        "style_scores": {"sophisticated": 4, "feminine": 2},
        "style_display": {"sophisticated": "소피스티케이티드"},
        "style_search_keywords": ["시크", "세련"],
        "color_search_keywords": ["다크", "딥"],
        "tpo_preference": "A",
    }


# ──────────────────────────────────────────────
# create_deeplink_context
# ──────────────────────────────────────────────
class TestCreateDeeplinkContext:
    def test_required_keys_present(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        required_keys = [
            "gender", "personal_color_code", "personal_color_display",
            "representative_colors", "color_search_keywords",
            "primary_style_code", "primary_style_display",
            "secondary_style_codes", "style_search_keywords",
            "fit_preference", "tpo_keyword",
            "musinsa_search_keywords", "zigzag_search_keywords",
        ]
        for key in required_keys:
            assert key in ctx, f"딥링크 컨텍스트에 '{key}' 키 누락"

    def test_gender_passed_through(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        assert ctx["gender"] == "W"

    def test_personal_color_code_matches(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        assert ctx["personal_color_code"] == "winter_deep"

    def test_primary_style_display_resolved(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        assert ctx["primary_style_display"] == "소피스티케이티드"

    def test_musinsa_search_keywords_is_combined(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        expected = sample_user_profile["color_search_keywords"] + sample_user_profile["style_search_keywords"]
        assert ctx["musinsa_search_keywords"] == expected

    def test_zigzag_search_keywords_is_combined(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        expected = sample_user_profile["color_search_keywords"] + sample_user_profile["style_search_keywords"]
        assert ctx["zigzag_search_keywords"] == expected

    def test_secondary_style_codes_list(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        assert isinstance(ctx["secondary_style_codes"], list)

    def test_tpo_keyword_is_string(self, sample_user_profile):
        ctx = create_deeplink_context(sample_user_profile)
        assert isinstance(ctx["tpo_keyword"], str)


# ──────────────────────────────────────────────
# create_profile_response_payload
# ──────────────────────────────────────────────
class TestCreateProfileResponsePayload:
    def test_has_user_profile_key(self, sample_user_profile):
        payload = create_profile_response_payload(sample_user_profile)
        assert "user_profile" in payload

    def test_has_deeplink_context_key(self, sample_user_profile):
        payload = create_profile_response_payload(sample_user_profile)
        assert "deeplink_context" in payload

    def test_user_profile_is_same_object(self, sample_user_profile):
        payload = create_profile_response_payload(sample_user_profile)
        assert payload["user_profile"] is sample_user_profile

    def test_deeplink_context_is_dict(self, sample_user_profile):
        payload = create_profile_response_payload(sample_user_profile)
        assert isinstance(payload["deeplink_context"], dict)


# ──────────────────────────────────────────────
# build_static_image_url
# ──────────────────────────────────────────────
class TestBuildStaticImageUrl:
    def test_none_image_path_returns_none(self, tmp_path):
        assert build_static_image_url("", str(tmp_path)) is None

    def test_none_dataset_dir_returns_none(self):
        assert build_static_image_url("some/path.jpg", None) is None

    def test_path_inside_dataset_dir_returns_relative_url(self, tmp_path):
        # 임시 파일 생성
        image_file = tmp_path / "item001.jpg"
        image_file.write_bytes(b"")
        url = build_static_image_url(str(image_file), str(tmp_path))
        assert url is not None
        assert url.startswith("/sample-files/")
        assert "item001.jpg" in url

    def test_path_outside_dataset_dir_returns_none(self, tmp_path):
        outside_path = Path("/nonexistent/path/image.jpg")
        url = build_static_image_url(str(outside_path), str(tmp_path))
        assert url is None


# ──────────────────────────────────────────────
# attach_recommendation_image_urls
# ──────────────────────────────────────────────
class TestAttachRecommendationImageUrls:
    def test_adds_image_url_key(self, tmp_path):
        items = [{"item_id": "001", "image_path": ""}]
        result = attach_recommendation_image_urls(items, str(tmp_path), "http://localhost:8000")
        assert "image_url" in result[0]

    def test_adds_image_full_url_key(self, tmp_path):
        items = [{"item_id": "001", "image_path": ""}]
        result = attach_recommendation_image_urls(items, str(tmp_path), "http://localhost:8000")
        assert "image_full_url" in result[0]

    def test_full_url_none_when_no_image_path(self, tmp_path):
        items = [{"item_id": "001", "image_path": ""}]
        result = attach_recommendation_image_urls(items, str(tmp_path), "http://localhost:8000")
        assert result[0]["image_full_url"] is None

    def test_full_url_constructed_with_base_url(self, tmp_path):
        image_file = tmp_path / "img.jpg"
        image_file.write_bytes(b"")
        items = [{"item_id": "001", "image_path": str(image_file)}]
        result = attach_recommendation_image_urls(items, str(tmp_path), "http://localhost:8000")
        if result[0]["image_url"]:
            assert result[0]["image_full_url"].startswith("http://localhost:8000")

    def test_empty_items_list(self, tmp_path):
        result = attach_recommendation_image_urls([], str(tmp_path), "http://localhost:8000")
        assert result == []

    def test_original_items_mutated_in_place(self, tmp_path):
        items = [{"item_id": "001", "image_path": ""}]
        result = attach_recommendation_image_urls(items, str(tmp_path), "http://localhost:8000")
        assert result is items  # 제자리 수정 확인


# ──────────────────────────────────────────────
# _is_mock_recommendation_source
# ──────────────────────────────────────────────
class TestIsMockRecommendationSource:
    def test_all_mock_items_returns_true(self):
        items = [
            {"item_id": "mock_001"},
            {"item_id": "mock_002"},
        ]
        assert _is_mock_recommendation_source(items) is True

    def test_mixed_items_returns_false(self):
        items = [
            {"item_id": "mock_001"},
            {"item_id": "real_002"},
        ]
        assert _is_mock_recommendation_source(items) is False

    def test_all_real_items_returns_false(self):
        items = [{"item_id": "real_001"}]
        assert _is_mock_recommendation_source(items) is False

    def test_empty_list_returns_false(self):
        assert _is_mock_recommendation_source([]) is False

    def test_item_without_item_id_field(self):
        items = [{"title": "some item"}]
        assert _is_mock_recommendation_source(items) is False
