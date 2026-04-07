from __future__ import annotations

import time
import urllib.parse

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

try:
    from app.crawlers.recommendation_search_profile import build_recommendation_search_profile
except ImportError:
    try:
        from .recommendation_search_profile import build_recommendation_search_profile
    except ImportError:
        from recommendation_search_profile import build_recommendation_search_profile

# ============================================================
# 1. 지그재그 카테고리 마스터 맵
# ============================================================
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

# ============================================================
# 2. 통합 매핑 맵 (키워드 + 핏 + 계절별 카테고리)
# ============================================================
STYLE_TO_ZIGZAG_MAP = {
    "캐주얼": {
        "search_prefix": "캐주얼", 
        "top_fit": ["노멀핏", "루즈핏"],
        "bottom_fit": ["일자핏", "와이드핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("팬츠", "숏팬츠"), ("상의", "맨투맨"), ("상의", "후드"), ("아우터", "숏패딩"), ("아우터", "점퍼"), ("팬츠", "데님팬츠"), ("상의", "긴소매 티셔츠"), ("팬츠", "와이드팬츠")]
    },
    "스트리트": {
        "search_prefix": "스트릿", 
        "top_fit": ["루즈핏", "오버핏"],
        "bottom_fit": ["와이드핏", "조거핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("상의", "슬리브리스"), ("팬츠", "숏팬츠"), ("상의", "후드"), ("아우터", "점퍼"), ("아우터", "숏패딩"), ("아우터", "무스탕"), ("팬츠", "와이드팬츠"), ("팬츠", "조거팬츠"), ("팬츠", "데님팬츠")]
    },
    "오피스/소피스티케이티드": {
        "search_prefix": "오피스룩 세련된", 
        "top_fit": ["노멀핏", "타이트핏", "슬림핏"],
        "bottom_fit": ["일자핏", "슬림핏", "부츠컷"],
        "recommend_cats": [("상의", "블라우스"), ("상의", "반소매 티셔츠"), ("스커트", "미디스커트"), ("니트/카디건", "터틀넥 니트"), ("아우터", "재킷"), ("아우터", "롱코트"), ("아우터", "트렌치코트"), ("상의", "셔츠"), ("팬츠", "슬랙스팬츠"), ("팬츠", "일자팬츠")]
    },
    "페미닌": {
        "search_prefix": "페미닌", 
        "top_fit": ["타이트핏", "슬림핏", "노멀핏"],
        "bottom_fit": ["슬림핏", "부츠컷", "일자핏"],
        "recommend_cats": [("상의", "블라우스"), ("상의", "슬리브리스"), ("원피스", "미니원피스"), ("스커트", "미니스커트"), ("니트/카디건", "브이넥 니트"), ("아우터", "트위드재킷"), ("아우터", "롱코트"), ("아우터", "카디건"), ("원피스", "롱원피스"), ("스커트", "롱스커트")]
    },
    "매니시": {
        "search_prefix": "매니시", 
        "top_fit": ["노멀핏", "루즈핏", "오버핏"],
        "bottom_fit": ["일자핏", "와이드핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("상의", "셔츠"), ("팬츠", "와이드팬츠"), ("아우터", "재킷"), ("아우터", "레더재킷"), ("아우터", "롱코트"), ("아우터", "무스탕"), ("팬츠", "슬랙스팬츠"), ("팬츠", "일자팬츠")]
    },
    "스포티": {
        "search_prefix": "스포티 편안한", 
        "top_fit": ["루즈핏", "노멀핏", "타이트핏"],
        "bottom_fit": ["와이드핏", "조거핏", "스키니핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("상의", "슬리브리스"), ("팬츠", "숏팬츠"), ("트레이닝", "세트"), ("아우터", "점퍼"), ("아우터", "숏패딩"), ("팬츠", "조거팬츠"), ("트레이닝", "레깅스"), ("트레이닝", "트레이닝 상의")] 
    },
    "모던/미니멀": {
        "search_prefix": "미니멀 깔끔한", 
        "top_fit": ["노멀핏", "스탠다드핏"],
        "bottom_fit": ["일자핏", "와이드핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("상의", "셔츠"), ("원피스", "롱원피스"), ("니트/카디건", "라운드 니트"), ("아우터", "재킷"), ("아우터", "롱코트"), ("아우터", "숏코트"), ("팬츠", "일자팬츠"), ("팬츠", "와이드팬츠"), ("팬츠", "슬랙스팬츠")]
    },
    "로맨틱": {
        "search_prefix": "로맨틱 러블리", 
        "top_fit": ["노멀핏", "타이트핏"],
        "bottom_fit": ["일자핏", "부츠컷"],
        "recommend_cats": [("상의", "블라우스"), ("원피스", "미니원피스"), ("스커트", "미니스커트"), ("니트/카디건", "카디건"), ("아우터", "트위드재킷"), ("아우터", "퍼코트"), ("아우터", "하프코트"), ("원피스", "미디원피스"), ("스커트", "롱스커트")]
    },
    "힙스터/펑크": {
        "search_prefix": "유니크 힙스터", 
        "top_fit": ["루즈핏", "타이트핏", "크롭핏"],
        "bottom_fit": ["와이드핏", "스키니핏"],
        "recommend_cats": [("상의", "슬리브리스"), ("상의", "반소매 티셔츠"), ("팬츠", "숏팬츠"), ("아우터", "레더재킷"), ("아우터", "점퍼"), ("아우터", "무스탕"), ("상의", "후드"), ("팬츠", "와이드팬츠"), ("스커트", "미니스커트"), ("팬츠", "데님팬츠")]
    },
    "레트로/빈티지": {
        "search_prefix": "빈티지 레트로", 
        "top_fit": ["노멀핏", "타이트핏", "루즈핏"],
        "bottom_fit": ["와이드핏", "부츠컷", "일자핏"],
        "recommend_cats": [("상의", "반소매 티셔츠"), ("상의", "블라우스"), ("스커트", "미디스커트"), ("니트/카디건", "카디건"), ("아우터", "레더재킷"), ("아우터", "사파리재킷"), ("아우터", "무스탕"), ("팬츠", "데님팬츠"), ("팬츠", "와이드팬츠"), ("원피스", "롱원피스")]
    }
}

RECOMMENDATION_STYLE_TO_ZIGZAG_STYLE = {
    "소피스티케이티드": "오피스/소피스티케이티드",
    "페미닌": "페미닌",
    "로맨틱": "로맨틱",
    "모던/미니멀": "모던/미니멀",
    "캐주얼": "캐주얼",
    "매니시": "매니시",
    "스트리트": "스트리트",
    "스포티": "스포티",
    "힙스터/펑크": "힙스터/펑크",
    "레트로": "레트로/빈티지",
}

global_driver = None

# ============================================================
# 3. 크롤링 코어 로직
# ============================================================
def get_driver():
    global global_driver
    if global_driver is None:
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1440,1200")
        
        global_driver = uc.Chrome(options=options, version_main=146)
    return global_driver

def crawl_zigzag_store(url, keyword, top_n=3, max_attempts=2):
    last_error_message = ""

    for attempt_index in range(1, max_attempts + 1):
        driver = None
        scraped_data = []

        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(5)

            products = driver.find_elements(By.CSS_SELECTOR, ".product-card")

            for product in products:
                if len(scraped_data) >= top_n:
                    break
                try:
                    mall_name = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomr8").text
                    title = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomrc").text
                    price = product.find_element(By.CSS_SELECTOR, ".zds4_1jsf80i3").text
                    img_url = product.find_element(By.CSS_SELECTOR, ".product-card-thumbnail img").get_attribute("src")

                    scraped_data.append({"mall_name": mall_name, "title": title, "price": price, "img_url": img_url})
                except Exception:
                    continue

            return scraped_data
        except Exception as error:
            last_error_message = f"{type(error).__name__}: {error}"
            print(f"크롤링 중 오류 발생 ({attempt_index}/{max_attempts}): {last_error_message}")
            if attempt_index < max_attempts:
                print("한 번 더 재시도합니다.")
                time.sleep(1)
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
            global global_driver
            global_driver = None

    print(f"지그재그 크롤링 최종 실패: {last_error_message}")
    return []

def get_style_recommendations(selected_styles: list, target_categories: list = ["전체"]):
    """
    스타일 리스트와 옷 종류 리스트를 받아 크롤링합니다.
    """
    # 💡 입력이 문자열이면 리스트로 변환 (안전장치)
    if isinstance(selected_styles, str):
        selected_styles = [selected_styles]
    if isinstance(target_categories, str):
        target_categories = [target_categories]

    styles_str = ", ".join(selected_styles)
    cat_str = ", ".join(target_categories)
    print(f"\n✨ [{styles_str}] 스타일의 [{cat_str}] 코디를 구성 중입니다...\n")
    
    all_search_tasks = []

    # 💡 여러 스타일을 순회
    for style in selected_styles:
        style_info = STYLE_TO_ZIGZAG_MAP.get(style)
        if not style_info:
            print(f"❗ '{style}'은(는) 등록되지 않은 스타일입니다. 건너뜁니다.")
            continue
        
        top_fits = style_info["top_fit"]
        bottom_fits = style_info["bottom_fit"]
        all_categories = style_info["recommend_cats"]
        
        filtered_categories = []
        
        for main_cat, sub_cat in all_categories:
            if "전체" in target_categories:
                filtered_categories.append((main_cat, sub_cat))
                continue
                
            if "상의" in target_categories and (main_cat in ["상의", "니트/카디건"] or (main_cat == "트레이닝" and sub_cat == "트레이닝 상의")):
                filtered_categories.append((main_cat, sub_cat))
                
            elif "하의" in target_categories and (main_cat in ["팬츠", "스커트"] or (main_cat == "트레이닝" and sub_cat in ["트레이닝 하의", "레깅스"])):
                filtered_categories.append((main_cat, sub_cat))
                
            elif main_cat in target_categories: 
                filtered_categories.append((main_cat, sub_cat))
                
            elif "세트" in target_categories or "트레이닝" in target_categories:
                if main_cat in ["투피스/세트", "트레이닝"] or sub_cat == "세트":
                    filtered_categories.append((main_cat, sub_cat))

        filtered_categories = list(set(filtered_categories))

        if not filtered_categories:
             print(f"❗ '{style}' 스타일에 해당하는 카테고리 정보가 없습니다.")
             continue
             
        # 크롤링할 작업 리스트 구성
        for main_cat, sub_cat in filtered_categories:
            fit_keyword = ""
            if main_cat in ["상의", "아우터", "원피스", "니트/카디건", "투피스/세트"] or (main_cat == "트레이닝" and sub_cat in ["트레이닝 상의", "세트"]):
                fit_keyword = random.choice(top_fits)
            elif main_cat in ["팬츠", "스커트"] or (main_cat == "트레이닝" and sub_cat in ["트레이닝 하의", "레깅스"]):
                fit_keyword = random.choice(bottom_fits)
                
            item_name = sub_cat if sub_cat != '전체' else main_cat
            search_keyword = f"{fit_keyword} {item_name}".strip()
            
            # (스타일 이름, 검색어) 형태로 저장
            all_search_tasks.append((style, search_keyword))

    all_results = {}
    
    # 중복 검색어 제거를 위해 집합 사용, 출력 형식을 맞추기 위해 리스트 변환 
    unique_search_tasks = []
    seen = set()
    for style, keyword in all_search_tasks:
        if keyword not in seen:
            unique_search_tasks.append((style, keyword))
            seen.add(keyword)

    if not unique_search_tasks:
         return {}

    for style, search_keyword in unique_search_tasks:
        encoded_keyword = urllib.parse.quote_plus(search_keyword)
        url = f"https://zigzag.kr/search?keyword={encoded_keyword}&order=SCORE_DESC"
        
        print(f"🔍 [{style}] 검색 중: {search_keyword}")
        items = crawl_zigzag_store(url, search_keyword, top_n=2)
        
        if items:
            all_results[f"[{style}] {search_keyword}"] = items
            
    return all_results


def get_zigzag_recommendations_from_survey(
    survey_answers: dict,
    category_name: str,
    *,
    selected_color: str | None = None,
    dataset_dir: str | None = None,
    allow_mock: bool = True,
    top_n: int = 5,
) -> dict:
    search_profile = build_recommendation_search_profile(
        survey_answers,
        dataset_dir=dataset_dir,
        allow_mock=allow_mock,
    )
    deeplink_context = search_profile["deeplink_context"]
    style_display = deeplink_context["primary_style_display"]
    zigzag_style_key = RECOMMENDATION_STYLE_TO_ZIGZAG_STYLE.get(style_display, style_display)
    zigzag_style_info = STYLE_TO_ZIGZAG_MAP.get(zigzag_style_key)

    if not zigzag_style_info:
        raise ValueError(f"지그재그 스타일 매핑이 없습니다: {style_display}")

    style_keyword = zigzag_style_info["search_prefix"].strip()
    if category_name not in ZIGZAG_MASTER_MAP:
        raise ValueError(f"지그재그 카테고리 맵이 없습니다: {category_name}")

    available_color_keywords = deeplink_context.get("zigzag_color_keywords", [])
    category_filter_info = _resolve_zigzag_category_filter_info(
        category_name=category_name,
        zigzag_style_info=zigzag_style_info,
    )
    category_color_keywords = _resolve_selected_color_keywords(
        available_color_keywords,
        selected_color,
        allow_color_filter=should_apply_zigzag_color_filter(category_name),
    )
    encoded_keyword = urllib.parse.quote_plus(style_keyword)
    search_url = f"https://zigzag.kr/search?keyword={encoded_keyword}&order=SCORE_DESC"
    print(f"🔍 [{category_name}] 검색 중: {style_keyword}")
    print(f"   - 카테고리 필터: {', '.join(category_filter_info['preferred_subcategories']) or '없음'}")
    print(f"   - 색상 필터: {', '.join(category_color_keywords) or '없음'}")

    scraped_items = crawl_zigzag_store(search_url, style_keyword, top_n=max(top_n * 10, 40))
    filtered_items = _filter_zigzag_items_by_category_and_color(
        scraped_items=scraped_items,
        category_filter_terms=category_filter_info["filter_terms"],
        color_filter_terms=category_color_keywords,
        top_n=top_n,
    )

    return {
        "profile": search_profile,
        "platform": "zigzag",
        "category": category_name,
        "selected_color": category_color_keywords[0] if category_color_keywords else None,
        "search_keyword": style_keyword,
        "url": search_url,
        "applied_filters": {
            "category": category_name,
            "middle_id": category_filter_info["middle_id"],
            "preferred_subcategories": category_filter_info["preferred_subcategories"],
            "color_keywords": category_color_keywords,
            "style_labels": [zigzag_style_key],
            "fit_codes": [],
            "tpo_keyword": deeplink_context["tpo_keyword"],
        },
        "items": filtered_items,
    }


def _resolve_zigzag_fit_keyword(
    *,
    category_name: str,
    zigzag_style_info: dict,
    search_profile: dict,
) -> str:
    if category_name in ["팬츠", "스커트"]:
        fit_keywords = search_profile.get("zigzag_bottom_fit_keywords") or zigzag_style_info["bottom_fit"]
    else:
        fit_keywords = search_profile.get("zigzag_top_fit_keywords") or zigzag_style_info["top_fit"]
    return fit_keywords[0] if fit_keywords else ""


def _build_zigzag_category_search_keyword(
    *,
    style_keyword: str,
    color_keyword: str,
    fit_keyword: str,
    category_name: str,
) -> str:
    return " ".join(
        keyword
        for keyword in [style_keyword, color_keyword, fit_keyword, category_name]
        if keyword
    )


def _resolve_zigzag_category_filter_info(*, category_name: str, zigzag_style_info: dict) -> dict:
    master_category_info = ZIGZAG_MASTER_MAP[category_name]
    recommended_subcategories = [
        sub_category_name
        for main_category_name, sub_category_name in zigzag_style_info["recommend_cats"]
        if main_category_name == category_name and sub_category_name in master_category_info["sub_categories"]
    ]
    if not recommended_subcategories:
        recommended_subcategories = [
            sub_category_name
            for sub_category_name in master_category_info["sub_categories"]
            if sub_category_name != "전체"
        ]

    filter_terms = [category_name, *recommended_subcategories]
    if category_name == "니트/카디건":
        filter_terms.extend(["니트", "카디건"])
    elif category_name == "트레이닝":
        filter_terms.extend(["트레이닝", "조거", "레깅스"])

    deduplicated_filter_terms: list[str] = []
    for filter_term in filter_terms:
        if filter_term and filter_term not in deduplicated_filter_terms:
            deduplicated_filter_terms.append(filter_term)

    return {
        "middle_id": master_category_info["middle_id"],
        "preferred_subcategories": recommended_subcategories,
        "filter_terms": deduplicated_filter_terms,
    }


def should_apply_zigzag_color_filter(category_name: str) -> bool:
    return category_name != "팬츠"


def _resolve_selected_color_keywords(
    available_color_keywords: list[str],
    selected_color: str | None,
    *,
    allow_color_filter: bool,
) -> list[str]:
    if not allow_color_filter:
        return []
    if not available_color_keywords:
        return []
    if not selected_color:
        return [available_color_keywords[0]]

    normalized_selected_color = _normalize_filter_keyword(selected_color)
    for available_color_keyword in available_color_keywords:
        if _normalize_filter_keyword(available_color_keyword) == normalized_selected_color:
            return [available_color_keyword]
    return [available_color_keywords[0]]


def _normalize_filter_keyword(raw_keyword: str) -> str:
    return str(raw_keyword or "").strip().lower().replace(" ", "")


def _filter_zigzag_items_by_category_and_color(
    *,
    scraped_items: list[dict],
    category_filter_terms: list[str],
    color_filter_terms: list[str],
    top_n: int,
) -> list[dict]:
    ranked_items: list[tuple[int, dict]] = []
    for scraped_item in scraped_items:
        product_text = " ".join(
            str(scraped_item.get(field_name, ""))
            for field_name in ["title", "mall_name"]
        ).lower()
        category_match_count = sum(
            1
            for category_filter_term in category_filter_terms
            if category_filter_term and category_filter_term.lower() in product_text
        )
        color_match_count = sum(
            1
            for color_filter_term in color_filter_terms
            if color_filter_term and color_filter_term.lower() in product_text
        )
        ranked_items.append((category_match_count * 10 + color_match_count, scraped_item))

    strict_matches = [
        scraped_item
        for ranking_score, scraped_item in ranked_items
        if ranking_score >= 11
    ]
    if len(strict_matches) >= top_n:
        return strict_matches[:top_n]

    category_matches = [
        scraped_item
        for ranking_score, scraped_item in ranked_items
        if ranking_score >= 10
    ]
    if len(category_matches) >= top_n:
        return category_matches[:top_n]

    ranked_items.sort(key=lambda ranked_item: ranked_item[0], reverse=True)
    return [scraped_item for _, scraped_item in ranked_items[:top_n]]
def _resolve_requested_zigzag_main_categories(requested_categories: list[str]) -> list[str]:
    if "전체" in requested_categories:
        return ["상의", "아우터", "팬츠", "니트/카디건", "트레이닝"]

    resolved_categories: list[str] = []
    for category_name in requested_categories:
        if category_name == "하의":
            for mapped_category in ["팬츠", "스커트"]:
                if mapped_category not in resolved_categories:
                    resolved_categories.append(mapped_category)
            continue
        if category_name == "세트":
            for mapped_category in ["투피스/세트", "트레이닝"]:
                if mapped_category not in resolved_categories:
                    resolved_categories.append(mapped_category)
            continue
        if category_name in ZIGZAG_MASTER_MAP and category_name not in resolved_categories:
            resolved_categories.append(category_name)

    return resolved_categories

# ============================================================
# 4. 메인 실행 테스트
# ============================================================
if __name__ == "__main__":
    # 💡 [핵심 수정] 스타일도 리스트 형태로 입력!
    USER_INPUT_STYLES = ["로맨틱", "모던/미니멀"]
    
    # 카테고리도 리스트 형태로 입력!
    USER_INPUT_CATEGORIES = ["상의", "하의"] 
    
    results = get_style_recommendations(USER_INPUT_STYLES, USER_INPUT_CATEGORIES)
    
    print("\n==================================================")
    print(f" 🛍️ 맞춤 코디 세트 제안")
    print("==================================================")
    
    if results:
        for category_keyword, items in results.items():
            print(f"\n📍 검색 키워드: {category_keyword}")
            for idx, item in enumerate(items, 1):
                print(f"  {idx}. [{item['mall_name']}] {item['title']} - {item['price']}")
                print(f"     🔗 {item['img_url']}")
    else:
        print("수집된 데이터가 없습니다.")
            
    print("\n✅ 모든 작업이 완료되었습니다. ")
