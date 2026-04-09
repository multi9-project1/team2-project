"""
FastAPI 엔드포인트 통합 테스트
- GET  /health
- GET  /
- GET  /gallery-demo
- POST /profile
- POST /recommendations  (mock 데이터 사용)
- POST /crawl/musinsa    (크롤러 호출 mocking)
- POST /crawl/zigzag     (크롤러 호출 mocking)
- 에러 핸들링 (400, 500)
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ──────────────────────────────────────────────
# 공통 테스트 데이터
# ──────────────────────────────────────────────
VALID_SURVEY = {
    "gender": "여성",
    "personal_color": "winter_deep",
    "Qstyle_1": "A",
    "Qstyle_2": "B",
    "Qstyle_3": "B",
    "Qstyle_4": "A",
    "Qstyle_5": "B",
    "Qstyle_6": "A",
    "Qstyle_7": "B",
    "Qstyle_8": "A",
    "Qstyle_9": "A",
}

MALE_SURVEY = {
    "gender": "남성",
    "personal_color": "autumn_warm",
    "Qstyle_1": "B",
    "Qstyle_2": "A",
    "Qstyle_3": "A",
    "Qstyle_4": "B",
    "Qstyle_5": "A",
    "Qstyle_6": "B",
    "Qstyle_7": "A",
    "Qstyle_8": "B",
    "Qstyle_9": "B",
}


# ──────────────────────────────────────────────
# GET /health
# ──────────────────────────────────────────────
class TestHealthEndpoint:
    def test_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok_status(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_content_type_is_json(self):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]


# ──────────────────────────────────────────────
# GET /
# ──────────────────────────────────────────────
class TestHomeEndpoint:
    def test_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_returns_html(self):
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_html_contains_title(self):
        response = client.get("/")
        assert "패션" in response.text or "Fashion" in response.text


# ──────────────────────────────────────────────
# GET /gallery-demo
# ──────────────────────────────────────────────
class TestGalleryDemoEndpoint:
    def test_returns_200(self):
        response = client.get("/gallery-demo")
        assert response.status_code == 200

    def test_returns_html(self):
        response = client.get("/gallery-demo")
        assert "text/html" in response.headers["content-type"]

    def test_html_has_form(self):
        response = client.get("/gallery-demo")
        assert "<form" in response.text


# ──────────────────────────────────────────────
# POST /profile
# ──────────────────────────────────────────────
class TestProfileEndpoint:
    def test_returns_200_with_valid_survey(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        assert response.status_code == 200

    def test_response_has_user_profile(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        data = response.json()
        assert "user_profile" in data

    def test_response_has_deeplink_context(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        data = response.json()
        assert "deeplink_context" in data

    def test_response_has_meta(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        data = response.json()
        assert "meta" in data

    def test_gender_is_W_for_여성(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        data = response.json()
        assert data["user_profile"]["gender"] == "W"

    def test_gender_is_M_for_남성(self):
        response = client.post("/profile", json={"survey": MALE_SURVEY})
        data = response.json()
        assert data["user_profile"]["gender"] == "M"

    def test_personal_color_code_matches(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        data = response.json()
        assert data["user_profile"]["personal_color"] == "winter_deep"

    def test_deeplink_context_has_gender(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        ctx = response.json()["deeplink_context"]
        assert "gender" in ctx

    def test_deeplink_context_has_style_info(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        ctx = response.json()["deeplink_context"]
        assert "primary_style_code" in ctx
        assert "primary_style_display" in ctx

    def test_empty_survey_returns_200(self):
        # 빈 설문도 기본값으로 처리되어야 함
        response = client.post("/profile", json={"survey": {}})
        assert response.status_code == 200

    def test_meta_not_includes_dataset(self):
        response = client.post("/profile", json={"survey": VALID_SURVEY})
        meta = response.json()["meta"]
        assert meta["includes_dataset_recommendations"] is False


# ──────────────────────────────────────────────
# POST /recommendations (mock 데이터)
# ──────────────────────────────────────────────
class TestRecommendationsEndpoint:
    PAYLOAD = {
        "survey": VALID_SURVEY,
        "top_n": 3,
        "allow_mock_data": True,
    }

    def test_returns_200(self):
        response = client.post("/recommendations", json=self.PAYLOAD)
        assert response.status_code == 200

    def test_response_has_text(self):
        response = client.post("/recommendations", json=self.PAYLOAD)
        data = response.json()
        assert "text" in data

    def test_text_is_string(self):
        response = client.post("/recommendations", json=self.PAYLOAD)
        data = response.json()
        assert isinstance(data["text"], str)

    def test_text_not_empty(self):
        response = client.post("/recommendations", json=self.PAYLOAD)
        data = response.json()
        assert len(data["text"]) > 0

    def test_male_survey_also_works(self):
        payload = dict(self.PAYLOAD)
        payload["survey"] = MALE_SURVEY
        response = client.post("/recommendations", json=payload)
        assert response.status_code == 200

    def test_top_n_boundary_1(self):
        payload = dict(self.PAYLOAD)
        payload["top_n"] = 1
        response = client.post("/recommendations", json=payload)
        assert response.status_code == 200

    def test_top_n_boundary_20(self):
        payload = dict(self.PAYLOAD)
        payload["top_n"] = 20
        response = client.post("/recommendations", json=payload)
        assert response.status_code == 200

    def test_top_n_out_of_range_returns_422(self):
        payload = dict(self.PAYLOAD)
        payload["top_n"] = 0  # ge=1 위반
        response = client.post("/recommendations", json=payload)
        assert response.status_code == 422


# ──────────────────────────────────────────────
# POST /crawl/musinsa (크롤러 mock)
# ──────────────────────────────────────────────
CRAWL_PAYLOAD = {
    "survey": VALID_SURVEY,
    "category_name": "상의",
    "allow_mock_data": True,
    "top_n": 2,
}

MOCK_MUSINSA_RESULT = {
    "profile": {},
    "platform": "musinsa",
    "category": "상의",
    "selected_color": "WHITE",
    "search_keyword": "소피스티케이티드",
    "url": "https://www.musinsa.com/category/001/goods?gf=F",
    "applied_filters": {},
    "items": [
        {"brand": "브랜드A", "title": "상품1", "price": "39,000", "img_url": "https://img1.jpg"},
        {"brand": "브랜드B", "title": "상품2", "price": "55,000", "img_url": "https://img2.jpg"},
    ],
}

MOCK_ZIGZAG_RESULT = {
    "profile": {},
    "platform": "zigzag",
    "category": "상의",
    "selected_color": "화이트",
    "search_keyword": "미니멀 깔끔한",
    "url": "https://zigzag.kr/search?keyword=%EB%AF%B8%EB%8B%88%EB%A9%80",
    "applied_filters": {},
    "items": [
        {"mall_name": "쇼핑몰A", "title": "블라우스", "price": "35,000원", "img_url": "https://img3.jpg"},
    ],
}


class TestCrawlMusinsaEndpoint:
    # /crawl/musinsa 엔드포인트는 함수 내부에서 from app.crawlers.musinsa_crl import ... 로
    # 로컬 import 하므로 실제 모듈 경로를 패치해야 합니다.
    _MUSINSA_PATCH = "app.crawlers.musinsa_crl.recommend_outfit_from_survey"

    def test_returns_200_with_mocked_crawler(self):
        with patch(self._MUSINSA_PATCH, return_value=MOCK_MUSINSA_RESULT):
            response = client.post("/crawl/musinsa", json=CRAWL_PAYLOAD)
        assert response.status_code == 200

    def test_response_has_platform_musinsa(self):
        with patch(self._MUSINSA_PATCH, return_value=MOCK_MUSINSA_RESULT):
            response = client.post("/crawl/musinsa", json=CRAWL_PAYLOAD)
        assert response.json()["platform"] == "musinsa"

    def test_response_has_items(self):
        with patch(self._MUSINSA_PATCH, return_value=MOCK_MUSINSA_RESULT):
            response = client.post("/crawl/musinsa", json=CRAWL_PAYLOAD)
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_invalid_category_returns_400(self):
        with patch(
            self._MUSINSA_PATCH,
            side_effect=ValueError("무신사 카테고리를 찾을 수 없습니다: 없는카테고리"),
        ):
            payload = dict(CRAWL_PAYLOAD)
            payload["category_name"] = "없는카테고리"
            response = client.post("/crawl/musinsa", json=payload)
        assert response.status_code == 400


class TestCrawlZigzagEndpoint:
    _ZIGZAG_PATCH = "app.crawlers.zigzag_crl.get_zigzag_recommendations_from_survey"

    def test_returns_200_with_mocked_crawler(self):
        with patch(self._ZIGZAG_PATCH, return_value=MOCK_ZIGZAG_RESULT):
            response = client.post("/crawl/zigzag", json=CRAWL_PAYLOAD)
        assert response.status_code == 200

    def test_response_has_platform_zigzag(self):
        with patch(self._ZIGZAG_PATCH, return_value=MOCK_ZIGZAG_RESULT):
            response = client.post("/crawl/zigzag", json=CRAWL_PAYLOAD)
        assert response.json()["platform"] == "zigzag"

    def test_response_has_items(self):
        with patch(self._ZIGZAG_PATCH, return_value=MOCK_ZIGZAG_RESULT):
            response = client.post("/crawl/zigzag", json=CRAWL_PAYLOAD)
        data = response.json()
        assert "items" in data

    def test_invalid_category_returns_400(self):
        with patch(
            self._ZIGZAG_PATCH,
            side_effect=ValueError("지그재그 카테고리 맵이 없습니다: 없는카테고리"),
        ):
            payload = dict(CRAWL_PAYLOAD)
            payload["category_name"] = "없는카테고리"
            response = client.post("/crawl/zigzag", json=payload)
        assert response.status_code == 400

    def test_server_error_returns_500(self):
        with patch(
            self._ZIGZAG_PATCH,
            side_effect=RuntimeError("예상치 못한 오류"),
        ):
            response = client.post("/crawl/zigzag", json=CRAWL_PAYLOAD)
        assert response.status_code == 500


# ──────────────────────────────────────────────
# 스키마 유효성 검증 (422 테스트)
# ──────────────────────────────────────────────
class TestSchemaValidation:
    def test_profile_missing_survey_returns_422(self):
        response = client.post("/profile", json={})
        assert response.status_code == 422

    def test_recommendations_missing_survey_returns_422(self):
        response = client.post("/recommendations", json={"top_n": 5})
        assert response.status_code == 422

    def test_crawl_musinsa_missing_survey_returns_422(self):
        response = client.post("/crawl/musinsa", json={"category_name": "상의"})
        assert response.status_code == 422

    def test_crawl_zigzag_top_n_too_large_returns_422(self):
        payload = dict(CRAWL_PAYLOAD)
        payload["top_n"] = 999  # le=10 위반
        response = client.post("/crawl/zigzag", json=payload)
        assert response.status_code == 422
