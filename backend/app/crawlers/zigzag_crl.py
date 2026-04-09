from __future__ import annotations

import time
import urllib.parse
import random
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

try:
    from app.crawlers.recommendation_search_profile import build_recommendation_search_profile
except ImportError:
    try:
        from .recommendation_search_profile import build_recommendation_search_profile
    except ImportError:
        from recommendation_search_profile import build_recommendation_search_profile

# ... (카테고리 맵 설정 유지) ...
ZIGZAG_MASTER_MAP = {
    "상의": {"middle_id": 474, "title": "의류", "sub_categories": {"전체": None, "긴소매 티셔츠": 2792, "반소매 티셔츠": 2791, "셔츠": 489, "블라우스": 498, "니트/스웨터": 482, "맨투맨": 494, "후드": 495, "슬리브리스": 499}},
    "아우터": {"middle_id": 436, "title": "아우터", "sub_categories": {"전체": 436, "카디건": 437, "재킷": 438, "점퍼": 454, "레더재킷": 442, "트렌치코트": 447, "트위드재킷": 441, "사파리재킷": 460, "베스트": 461, "숏코트": 2787, "하프코트": 2788, "롱코트": 2789, "숏패딩": 463, "롱패딩": 464, "경량패딩": 466, "퍼코트": 451, "무스탕": 445, "레인코트": 453}},
    "팬츠": {"middle_id": 547, "title": "팬츠", "sub_categories": {"전체": None, "데님팬츠": 2796, "일자팬츠": 548, "슬랙스팬츠": 549, "와이드팬츠": 551, "스키니팬츠": 552, "부츠컷팬츠": 553, "조거팬츠": 554, "숏팬츠": 550, "점프수트": 556, "레깅스": 559, "기타팬츠": 2756}},
    "원피스": {"middle_id": 507, "title": "원피스", "sub_categories": {"전체": None, "미니원피스": 508, "미디원피스": 518, "롱원피스": 528}},
    "니트/카디건": {"middle_id": 2757, "title": "니트/카디건", "sub_categories": {"전체": 2757, "카디건": 2759, "라운드 니트": 483, "브이넥 니트": 484, "터틀넥 니트": 485, "오프숄더 니트": 487, "스퀘어넥 니트": 488, "카라니트": 2793, "집업니트": 2795, "후드니트": 2794, "니트 베스트": 486}},
    "스커트": {"middle_id": 560, "title": "스커트", "sub_categories": {"전체": None, "미니스커트": 561, "미디스커트": 568, "롱스커트": 575}},
    "트레이닝": {"middle_id": 833, "title": "트레이닝", "sub_categories": {"전체": None, "트레이닝 상의": 834, "트레이닝 하의": 839, "레깅스": 3388, "세트": 844}},
    "투피스/세트": {"middle_id": 538, "title": "투피스/세트", "sub_categories": {"전체": None, "스커트 세트": 539, "팬츠 세트": 540, "원피스 세트": 541, "시밀러룩": 546}}
}

STYLE_TO_ZIGZAG_MAP = {
    "캐주얼": {"search_prefix": "캐주얼", "top_fit": ["노멀핏", "루즈핏"], "bottom_fit": ["일자핏", "와이드핏"], "recommend_cats": [("상의", "반소매 티셔츠")]},
    "스트리트": {"search_prefix": "스트릿", "top_fit": ["루즈핏", "오버핏"], "bottom_fit": ["와이드핏", "조거핏"], "recommend_cats": [("상의", "반소매 티셔츠")]},
    "오피스/소피스티케이티드": {"search_prefix": "오피스룩 세련된", "top_fit": ["노멀핏", "타이트핏"], "bottom_fit": ["일자핏", "슬림핏"]},
    "페미닌": {"search_prefix": "페미닌", "top_fit": ["타이트핏", "슬림핏"], "bottom_fit": ["슬림핏", "부츠컷"]},
    "매니시": {"search_prefix": "매니시", "top_fit": ["노멀핏", "루즈핏"], "bottom_fit": ["일자핏", "와이드핏"]},
    "스포티": {"search_prefix": "스포티 편안한", "top_fit": ["루즈핏", "노멀핏"], "bottom_fit": ["와이드핏", "조거핏"]},
    "모던/미니멀": {"search_prefix": "미니멀 깔끔한", "top_fit": ["노멀핏", "스탠다드핏"], "bottom_fit": ["일자핏", "와이드핏"]},
    "로맨틱": {"search_prefix": "로맨틱 러블리", "top_fit": ["노멀핏", "타이트핏"], "bottom_fit": ["일자핏", "부츠컷"]},
    "힙스터/펑크": {"search_prefix": "유니크 힙스터", "top_fit": ["루즈핏", "타이트핏"], "bottom_fit": ["와이드핏", "스키니핏"]},
    "레트로/빈티지": {"search_prefix": "빈티지 레트로", "top_fit": ["노멀핏", "타이트핏"], "bottom_fit": ["와이드핏", "부츠컷"]}
}

RECOMMENDATION_STYLE_TO_ZIGZAG_STYLE = {
    "소피스티케이티드": "오피스/소피스티케이티드", "페미닌": "페미닌", "로맨틱": "로맨틱", "모던/미니멀": "모던/미니멀",
    "캐주얼": "캐주얼", "매니시": "매니시", "스트리트": "스트리트", "스포티": "스포티", "힙스터/펑크": "힙스터/펑크", "레트로": "레트로/빈티지"
}

def crawl_zigzag_store(url, keyword, top_n=3, max_attempts=2):
    for attempt_index in range(1, max_attempts + 1):
        driver = None
        scraped_data = []
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            driver = uc.Chrome(options=options, version_main=146)
            driver.get(url)
            time.sleep(12)
            
            for _ in range(4):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            # 모든 이미지를 다 뒤져서 필터링
            images = soup.find_all("img")
            seen_titles = set()
            
            for img in images:
                if len(scraped_data) >= top_n: break
                
                src = img.get("src") or img.get("data-src") or ""
                if not src or "data:" in src or not src.startswith("http"): continue
                
                # 1. 명백한 광고/아이콘 제외
                if any(word in src.lower() for word in ["facebook", "pixel", "icon", "logo", "banner"]): continue
                
                # 2. 부모를 타고 올라가며 텍스트 추출 (최대 10단계)
                parent = img.parent
                product_text = ""
                found_container = None
                for _ in range(10):
                    text = parent.get_text(separator=" | ", strip=True)
                    # 가격(숫자)과 원 단위가 포함된 진짜 상품 상자 찾기
                    if "원" in text or "₩" in text or any(c.isdigit() for c in text.split("|")[-1]):
                        if len(text) > 15:
                            product_text = text
                            found_container = parent
                            break
                    parent = parent.parent
                    if not parent: break
                
                if not product_text: continue
                
                # 3. 텍스트 정제 (앱 광고 등 필터링)
                if any(word in product_text for word in ["앱으로", "설치", "매일직진", "로그인"]): continue
                
                parts = [p.strip() for p in product_text.split(" | ") if p.strip()]
                if len(parts) < 2: continue
                
                mall_name = parts[0]
                title = parts[1] if len(parts) > 1 else parts[0]
                
                # 가격 추출 (숫자만 골라내기)
                price = "0"
                for p in parts:
                    num_only = "".join(filter(str.isdigit, p))
                    if num_only and 1000 < int(num_only) < 1000000:
                        price = f"{int(num_only):,}"
                        break
                
                if title in seen_titles or price == "0": continue
                
                seen_titles.add(title)
                scraped_data.append({
                    "mall_name": mall_name,
                    "title": title,
                    "price": price,
                    "img_url": src
                })

            if scraped_data:
                print(f"    ✅ 지그재그 {len(scraped_data)}개 추출 성공!")
                return scraped_data
                
        except Exception as e:
            print(f"    🚨 지그재그 시도 {attempt_index} 실패: {e}")
        finally:
            if driver: driver.quit()
    return []

def get_zigzag_recommendations_from_survey(survey_answers: dict, category_name: str, *, selected_color: str | None = None, dataset_dir: str | None = None, allow_mock: bool = True, top_n: int = 5) -> dict:
    search_profile = build_recommendation_search_profile(survey_answers, dataset_dir=dataset_dir, allow_mock=allow_mock)
    deeplink_context = search_profile["deeplink_context"]
    style_display = deeplink_context["primary_style_display"]
    zigzag_style_key = RECOMMENDATION_STYLE_TO_ZIGZAG_STYLE.get(style_display, style_display)
    zigzag_style_info = STYLE_TO_ZIGZAG_MAP.get(zigzag_style_key)

    style_keyword = zigzag_style_info["search_prefix"].split()[0]
    full_query = f"{style_keyword} {category_name}".strip()
    encoded_keyword = urllib.parse.quote_plus(full_query)
    search_url = f"https://zigzag.kr/search?keyword={encoded_keyword}&order=SCORE_DESC"
    
    scraped_items = crawl_zigzag_store(search_url, full_query, top_n=top_n)

    return {
        "profile": search_profile, "platform": "zigzag", "category": category_name,
        "search_keyword": full_query, "url": search_url, "items": scraped_items
    }

if __name__ == "__main__":
    test_survey = {"gender": "W", "personal_color": "summer_light", "Qstyle_1": "A"}
    res = get_zigzag_recommendations_from_survey(test_survey, "원피스", top_n=3)
    print(res)
