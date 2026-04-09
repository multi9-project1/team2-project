import time
import traceback
import urllib.parse

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

try:
    from app.crawlers.recommendation_search_profile import build_recommendation_search_profile
except ImportError:
    try:
        from .recommendation_search_profile import build_recommendation_search_profile
    except ImportError:
        from recommendation_search_profile import build_recommendation_search_profile


# ============================================================
# 1. 카테고리 & 스타일 코드 정의 (무신사 기준)
# ============================================================
CATEGORIES = {
    "상의": {
        "전체(상의)":        "001",
        "맨투맨&스웨트":     "001005",
        "후드티셔츠":        "001004",
        "반소매 티셔츠":     "001001",
        "긴소매 티셔츠":     "001010",
        "니트&스웨터":       "001006",
        "셔츠&블라우스":     "001002",
    },
    "바지": {
        "전체(바지)":            "003",
        "트레이닝&조거 팬츠":    "003004",
        "데님 팬츠":             "003002",
        "슈트 팬츠&슬랙스":      "003008",
        "코튼 팬츠":             "003007",
        "숏 팬츠":               "003009",
        "기타 하의":             "003006",
        "점프 슈트&오버올":      "003010",
        "레깅스":                "003005",
    },
    "원피스&스커트": {
        "원피스":   "100",
        "스커트":   "100",
        "미디원피스":            "100002",
        "맥시원피스":            "100003",
        "미니원피스":            "100001",
        "미디스커트":            "100005",
        "미니스커트":            "100004",
        "롱스커트":              "100006",
    }
}

MUSINSA_STYLE_ID_MAP = {
    "캐주얼": 1,
    "스트릿": 2,
    "고프코어": 3,
    "프레피": 5,
    "스포티": 7,
    "로맨틱": 8,
    "걸리시": 9,
    "미니멀": 11,
    "시크": 12,
    "레트로": 13,
    "에스닉": 14,
}

FIT_CODE_MAP = {
    "오버사이즈": "2^90",
    "레귤러": "2^88",
    "슬림": "2^87",
}

# MAPSITI의 핏 표기를 무신사 FIT_CODE_MAP 키로 변환하기 위한 맵핑
FIT_DISPLAY_TO_KEY = {
    "루즈": "오버사이즈",
    "노멀": "레귤러",
    "타이트": "슬림"
}

# ============================================================
# 2. 퍼스널컬러 & MAPSITI 매핑 데이터
# ============================================================
PERSONAL_COLOR_MAP = {
    "봄라이트": {"description": "맑고 밝은 봄 라이트 타입 — 고명도의 화사하고 부드러운 컬러가 잘 어울립니다.", "colors": ["WHITE", "IVORY", "LIGHTPINK", "PEACH", "PALEPINK", "LIGHTYELLOW", "LIME"]},
    "봄브라이트": {"description": "선명하고 생기 있는 봄 브라이트 타입 — 에너제틱한 원색과 또렷한 컬러가 잘 어울립니다.", "colors": ["PINK", "ORANGE", "RED", "MINT", "GREEN", "YELLOW", "LIME", "CLEAR"]},
    "봄웜": {"description": "따뜻하고 화사한 봄 웜 타입 — 노란 기가 도는 밝고 부드러운 컬러가 잘 어울립니다.", "colors": ["IVORY", "BEIGE", "ORANGE", "MUSTARD", "SAND", "LIGHTORANGE", "GOLD"]},
    "여름라이트": {"description": "부드럽고 연한 여름 라이트 타입 — 우유 탄 듯 은은하고 시원한 컬러가 잘 어울립니다.", "colors": ["WHITE", "LIGHTPINK", "SKYBLUE", "LAVENDER", "PALEPINK"]},
    "여름뮤트": {"description": "차분하고 오묘한 여름 뮤트 타입 — 회색빛이 감도는 소프트한 컬러가 잘 어울립니다.", "colors": ["GRAY", "LIGHTGREY", "BLUE", "DENIM", "SILVER"]},
    "여름쿨": {"description": "청량하고 시원한 여름 쿨 타입 — 푸른 기가 도는 맑고 차분한 컬러가 잘 어울립니다.", "colors": ["WHITE", "BLUE", "NAVY", "DARKBLUE", "SILVER"]},
    "가을뮤트": {"description": "편안하고 내추럴한 가을 뮤트 타입 — 채도가 낮은 어스톤 계열이 잘 어울립니다.", "colors": ["BEIGE", "DARKBEIGE", "KHAKI", "KHAKIBEIGE", "OATMEAL", "OLIVEGREEN", "SAND"]},
    "가을딥": {"description": "깊고 진한 가을 딥 타입 — 무게감 있고 농도 짙은 컬러가 잘 어울립니다.", "colors": ["DARKBROWN", "DEEPRED", "BURGUNDY", "BRICK", "DARKBLUE", "BLACKDENIM"]},
    "가을웜": {"description": "따뜻하고 성숙한 가을 웜 타입 — 황색도가 높은 깊은 웜 컬러가 잘 어울립니다.", "colors": ["CAMEL", "MUSTARD", "DARKORANGE", "BROWN", "LIGHTBROWN", "GOLD"]},
    "겨울브라이트": {"description": "강렬하고 또렷한 겨울 브라이트 타입 — 대비감이 큰 선명한 컬러가 잘 어울립니다.", "colors": ["BLACK", "WHITE", "RED", "BLUE", "PURPLE", "SILVER", "CLEAR"]},
    "겨울딥": {"description": "묵직하고 도시적인 겨울 딥 타입 — 아주 어둡고 깊이 있는 컬러가 잘 어울립니다.", "colors": ["BLACK", "DARKNAVY", "DARKGREEN", "DARKBLUE", "BURGUNDY", "DEEPRED", "BLACKDENIM"]},
    "겨울쿨": {"description": "차갑고 세련된 겨울 쿨 타입 — 시리고 푸른 계열의 절제된 컬러가 잘 어울립니다.", "colors": ["WHITE", "NAVY", "SILVER", "DENIM"]},
}

MAPSITI_STYLE_MAP = {
    "캐주얼": {
        "title": "캐주얼 (Casual)",
        "fit_display": ["노멀"],
        "styles": ["캐주얼"],
        "description": "노멀 핏 + 실용적/편안함",
        "detail": "편안하고 실용적인 데일리 무드에 잘 맞는 유형으로, 티셔츠·셔츠·데님·코튼 팬츠처럼 부담 없이 활용하기 좋은 아이템을 중심으로 추천합니다.",
    },
    "스트리트": {
        "title": "스트리트 (Street)",
        "fit_display": ["루즈"],
        "styles": ["스트릿"],
        "description": "루즈 핏 + 독특/트랜디",
        "detail": "여유 있는 실루엣과 존재감 있는 포인트를 살리는 유형으로, 후드·오버핏 상의·와이드 팬츠 중심의 트렌디한 아이템을 추천합니다.",
    },
    "오피스/소피스티케이티드": {
        "title": "오피스/소피스티케이티드 (Sophisticated)",
        "fit_display": ["노멀", "타이트"],
        "styles": ["프레피", "미니멀", "시크"],
        "description": "노멀/타이트 핏 + 도시적/세련됨",
        "detail": "도시적이고 정돈된 분위기를 선호하는 유형으로, 셔츠·슬랙스·블레이저·니트처럼 단정하고 세련된 아이템을 추천합니다.",
    },
    "페미닌": {
        "title": "페미닌 (Feminine)",
        "fit_display": ["타이트", "노멀"],
        "styles": ["로맨틱", "걸리시"],
        "description": "타이트/노멀 핏 + 여성적/부드러움",
        "detail": "부드럽고 섬세한 무드를 살리는 유형으로, 블라우스·가디건·스커트·원피스처럼 유연한 실루엣의 아이템을 추천합니다.",
    },
    "매니시": {
        "title": "매니시 (Mannish)",
        "fit_display": ["노멀", "루즈"],
        "styles": ["시크", "미니멀", "프레피"],
        "description": "노멀/루즈 핏 + 남성적/도시적",
        "detail": "중성적이고 구조적인 무드를 선호하는 유형으로, 셔츠·자켓·와이드 슬랙스처럼 힘 있는 인상의 아이템을 추천합니다.",
    },
    "스포티": {
        "title": "스포티 (Sporty)",
        "fit_display": ["루즈", "노멀"],
        "styles": ["스포티", "고프코어"],
        "description": "루즈/노멀 핏 + 활동적/편안함",
        "detail": "활동성과 편안함을 중요하게 보는 유형으로, 스웻셔츠·트랙팬츠·바람막이 등 가볍고 실용적인 아이템을 추천합니다.",
    },
    "모던/미니멀": {
        "title": "모던/미니멀 (Modern/Minimal)",
        "fit_display": ["노멀"],
        "styles": ["미니멀", "시크"],
        "description": "노멀 핏 + 깔끔함/무난함",
        "detail": "과한 장식 없이 정제된 무드를 선호하는 유형으로, 무채색 상하의·슬랙스·심플한 아우터 등 깔끔한 아이템을 추천합니다.",
    },
    "로맨틱": {
        "title": "로맨틱 (Romantic)",
        "fit_display": ["노멀"],
        "styles": ["로맨틱", "걸리시"],
        "description": "노멀 핏 + 부드러움/발랄함",
        "detail": "부드럽고 사랑스러운 분위기를 선호하는 유형으로, 밝은 컬러감과 섬세한 디테일이 있는 아이템을 추천합니다.",
    },
    "힙스터/펑크": {
        "title": "힙스터/펑크 (Hipster)",
        "fit_display": ["루즈", "타이트"],
        "styles": ["스트릿", "레트로", "에스닉"],
        "description": "루즈/타이트 핏 + 개방적/화려함",
        "detail": "강한 개성과 실험적인 분위기를 즐기는 유형으로, 레이어드·패턴·빈티지 포인트가 있는 아이템을 추천합니다.",
    },
    "레트로/빈티지": {
        "title": "레트로/빈티지 (Retro)",
        "fit_display": ["루즈", "노멀", "타이트"],
        "styles": ["레트로", "에스닉"],
        "description": "핏의 다양성 + 독특함/명도-채도의 특성",
        "detail": "시대감 있는 무드와 개성 있는 색감·패턴을 선호하는 유형으로, 빈티지 데님·패턴 셔츠·클래식 자켓류를 추천합니다.",
    },
}

LEGACY_MAPCTI_ALIAS = {
    "미니멀/모던": "모던/미니멀",
    "캐주얼/스트릿": "캐주얼",
    "로맨틱/페미닌": "로맨틱",
    "스포티/고프코어": "스포티",
}

RECOMMENDATION_STYLE_TO_LEGACY_STYLE = {
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

PERSONAL_COLOR_DISPLAY_TO_LEGACY_KEY = {
    "봄 라이트": "봄라이트",
    "봄 브라이트": "봄브라이트",
    "봄 웜": "봄웜",
    "여름 라이트": "여름라이트",
    "여름 뮤트": "여름뮤트",
    "여름 쿨": "여름쿨",
    "가을 뮤트": "가을뮤트",
    "가을 딥": "가을딥",
    "가을 웜": "가을웜",
    "겨울 브라이트": "겨울브라이트",
    "겨울 딥": "겨울딥",
    "겨울 쿨": "겨울쿨",
}

TOP_LEVEL_CATEGORY_CODE_MAP = {
    "상의": "001",
    "아우터": "002",
    "팬츠": "003",
    "바지": "003",
    "니트/카디건": "001006",
    "트레이닝": "003004",
}

# ============================================================
# 3. 데이터 조립 및 크롤링 핵심 함수
# ============================================================
def build_profile(mapsiti: str, personal_color: str, gender: str) -> dict:
    normalized_mapsiti = LEGACY_MAPCTI_ALIAS.get(mapsiti.strip(), mapsiti.strip())
    mapsiti_info = MAPSITI_STYLE_MAP.get(normalized_mapsiti)
    color_info = PERSONAL_COLOR_MAP.get(personal_color)

    if not mapsiti_info or not color_info:
        raise ValueError("잘못된 MAPSITI 또는 퍼스널컬러 입력입니다.")

    # 추천 스타일 무신사 코드로 변환
    style_codes = [MUSINSA_STYLE_ID_MAP[s] for s in mapsiti_info["styles"] if s in MUSINSA_STYLE_ID_MAP]
    
    # 핏 디스플레이 텍스트를 무신사 핏 코드로 변환
    fit_codes = []
    for fit_text in mapsiti_info["fit_display"]:
        fit_key = FIT_DISPLAY_TO_KEY.get(fit_text)
        if fit_key and fit_key in FIT_CODE_MAP:
            fit_codes.append(FIT_CODE_MAP[fit_key])

    return {
        "mapsiti": normalized_mapsiti,
        "input_style": mapsiti,
        "title": mapsiti_info["title"],
        "description": mapsiti_info["description"],
        "detail": mapsiti_info["detail"],
        "fit_display": mapsiti_info["fit_display"],
        "fit_codes": fit_codes,
        "personal_color": personal_color,
        "color_description": color_info["description"],
        "recommended_styles": mapsiti_info["styles"],
        "style_codes": style_codes,
        "recommended_colors": color_info["colors"],
        "gender": gender,
    }

def build_recommendation_aligned_profile(
    survey_answers: dict,
    *,
    dataset_dir: str | None = None,
    allow_mock: bool = True,
) -> dict:
    search_profile = build_recommendation_search_profile(
        survey_answers,
        dataset_dir=dataset_dir,
        allow_mock=allow_mock,
    )
    deeplink_context = search_profile["deeplink_context"]

    legacy_style_name = _resolve_legacy_musinsa_style_name(
        deeplink_context["primary_style_display"]
    )
    legacy_personal_color_key = _resolve_legacy_personal_color_key(
        deeplink_context["personal_color_display"]
    )
    legacy_gender_code = "F" if deeplink_context["gender"] == "W" else "M"

    legacy_profile = build_profile(
        legacy_style_name,
        legacy_personal_color_key,
        legacy_gender_code,
    )
    legacy_profile["deeplink_context"] = deeplink_context
    legacy_profile["recommendation_primary_style_display"] = deeplink_context["primary_style_display"]
    legacy_profile["recommendation_secondary_style_codes"] = deeplink_context["secondary_style_codes"]
    legacy_profile["recommendation_tpo_keyword"] = deeplink_context["tpo_keyword"]
    return legacy_profile


def resolve_musinsa_category_code(category_name: str) -> str | None:
    if category_name in TOP_LEVEL_CATEGORY_CODE_MAP:
        return TOP_LEVEL_CATEGORY_CODE_MAP[category_name]

    for grouped_categories in CATEGORIES.values():
        if category_name in grouped_categories:
            return grouped_categories[category_name]

    return None


def should_apply_musinsa_color_filter(category_name: str) -> bool:
    return category_name not in {
        "팬츠",
        "바지",
        "데님 팬츠",
        "슈트 팬츠&슬랙스",
        "코튼 팬츠",
        "숏 팬츠",
        "트레이닝&조거 팬츠",
    }


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


def _resolve_legacy_musinsa_style_name(recommendation_style_display: str) -> str:
    return RECOMMENDATION_STYLE_TO_LEGACY_STYLE.get(
        recommendation_style_display,
        recommendation_style_display,
    )


def _resolve_legacy_personal_color_key(personal_color_display: str) -> str:
    resolved_key = PERSONAL_COLOR_DISPLAY_TO_LEGACY_KEY.get(personal_color_display)
    if not resolved_key:
        raise ValueError(f"무신사 퍼스널컬러 매핑이 없습니다: {personal_color_display}")
    return resolved_key


def build_category_url(
    category_code: str,
    gender: str,
    colors: list[str],
    styles: list[int],
    fit_codes: list[str] | None = None,
) -> str:
    url = f"https://www.musinsa.com/category/{category_code}/goods?gf={gender}"

    if fit_codes:
        url += f"&attributeFit={urllib.parse.quote(','.join(fit_codes), safe='')}"

    if colors:
        url += f"&color={urllib.parse.quote(','.join(colors), safe='')}"

    if styles:
        url += f"&style={urllib.parse.quote(','.join(str(s) for s in styles), safe='')}"

    url += "&sortCode=SALE_ONE_WEEK_COUNT"
    return url

import tempfile

def create_driver(chrome_version: int = 146):
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1200")
    options.add_argument("--disable-popup-blocking")
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp(prefix='uc_profile_')}")
    return uc.Chrome(options=options, version_main=chrome_version)

def crawl_musinsa(
    url: str,
    category_name: str,
    top_n: int,
    chrome_version: int = 146,
    max_attempts: int = 2,
) -> list[dict]:
    print(f"\n  ▶ [{category_name}] 상품 정보를 무신사에서 가져오는 중...")
    print(f"    🔗 요청 URL: {url}")

    last_exception: Exception | None = None

    for attempt_index in range(1, max_attempts + 1):
        print(f"    🔄 시도 {attempt_index}/{max_attempts}")
        driver = None
        scraped_items: list[dict] = []

        try:
            driver = create_driver(chrome_version)
            driver.get(url)
            time.sleep(5)

            current_url = driver.current_url
            print(f"    📍 실제 접속 URL: {current_url}")

            driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(3)

            page_source = driver.page_source
            print(f"    📄 페이지 소스 길이: {len(page_source)}")
            soup = BeautifulSoup(page_source, "html.parser")
            product_links = soup.select("a[data-item-id]")
            print(f"    🧾 감지된 상품 링크 수: {len(product_links)}")

            if not product_links:
                page_preview = " ".join(page_source[:300].split())
                print(f"    ❗ [{category_name}] 상품 링크를 찾지 못했습니다.")
                print(f"    📝 페이지 미리보기: {page_preview}")
                return []

            seen_titles = set()

            for product_link in product_links:
                if len(scraped_items) >= top_n:
                    break

                image_element = product_link.select_one("img")
                if not image_element:
                    continue

                try:
                    brand = product_link.get("data-item-brand", "브랜드 없음")
                    raw_price = product_link.get("data-price", "0")
                    price = f"{int(raw_price):,}" if raw_price.isdigit() else raw_price
                    title = image_element.get("alt", "").strip()
                    image_url = image_element.get("src", "")

                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

                    if not title or title in seen_titles:
                        continue

                    seen_titles.add(title)
                    scraped_items.append(
                        {
                            "brand": brand,
                            "title": title,
                            "price": price,
                            "img_url": image_url,
                        }
                    )
                except Exception:
                    continue

            print(f"    ✅ [{category_name}] {len(scraped_items)}개 추출 완료")
            return scraped_items

        except Exception as exc:
            last_exception = exc
            print(f"    🚨 시도 {attempt_index} 실패: {type(exc).__name__}: {exc}")
            print("    🪵 스택트레이스:")
            for trace_line in traceback.format_exc().strip().splitlines():
                print(f"       {trace_line}")
            if attempt_index < max_attempts:
                print("    ⏳ 브라우저를 새로 열어 한 번 더 시도합니다.")
                time.sleep(2)

        finally:
            if driver is not None:
                try:
                    driver.quit()
                except OSError:
                    pass
                except Exception:
                    pass
                driver = None

    print(f"    ❌ [{category_name}] 모든 재시도 실패")
    if last_exception is not None:
        print(f"    📌 최종 실패 원인: {type(last_exception).__name__}: {last_exception}")
    return []

# ============================================================
# 4. 메인 실행 컨트롤러
# ============================================================
def recommend_outfit(mapsiti: str, personal_color: str, gender: str, target_categories: list[str], max_colors: int = 5, top_n: int = 5):
    profile = build_profile(mapsiti, personal_color, gender)
    gender_text = "남성" if gender == "M" else "여성"
    colors_to_use = profile["recommended_colors"][:max_colors]

    sep = "=" * 70
    print(f"\n{sep}")
    print(f" 🛍️  {gender_text} | 스타일: {profile['title']} | 퍼스널컬러: {profile['personal_color']}")
    print(f" 💡 {profile['description']}")
    print(f" 📝 {profile['detail']}")
    print(f" 🎨 {profile['color_description']}")
    print(f" 👗 무신사 필터 적용: [스타일: {', '.join(profile['recommended_styles'])}] / [핏: {', '.join(profile['fit_display'])}] / [색상: {', '.join(colors_to_use)}]")
    print(sep)

    all_results = {}

    for cat_name in target_categories:
        cat_code = None
        for group_cats in CATEGORIES.values():
            if cat_name in group_cats:
                cat_code = group_cats[cat_name]
                break

        if not cat_code:
            print(f"  ⚠️ '{cat_name}' 카테고리를 찾을 수 없어 건너뜁니다.")
            continue

        # 추출된 핏 코드를 build_category_url에 전달
        url = build_category_url(
            category_code=cat_code,
            gender=gender,
            colors=colors_to_use,
            styles=profile["style_codes"],
            fit_codes=profile["fit_codes"]
        )
        
        items = crawl_musinsa(url, cat_name, top_n=top_n)

        if items:
            all_results[cat_name] = items

    print(f"\n{sep}")
    print(" ✨ AI 맞춤 추천 상품 리스트 ✨")
    print(sep)

    if not all_results:
        print("\n  ❌ 조건에 맞는 상품을 수집하지 못했습니다.")
        return

    for cat_name, items in all_results.items():
        print(f"\n 📦 카테고리: [{cat_name}]")
        print(" " + "-" * 60)
        for idx, item in enumerate(items, 1):
            print(f"  {idx}위. [{item['brand']}] {item['title']}")
            print(f"       💰 {item['price']}원")
            print(f"       🖼️  {item['img_url']}\n")


def recommend_outfit_from_survey(
    survey_answers: dict,
    category_name: str,
    *,
    selected_color: str | None = None,
    dataset_dir: str | None = None,
    allow_mock: bool = True,
    top_n: int = 5,
) -> dict:
    print("\n" + "=" * 80)
    print("[recommend_outfit_from_survey] INPUT")
    print("survey_answers =", survey_answers)
    print("category_name =", category_name)
    print("selected_color =", selected_color)
    print("dataset_dir =", dataset_dir)
    print("allow_mock =", allow_mock)
    print("top_n =", top_n)
    print("=" * 80)

    recommendation_profile = build_recommendation_aligned_profile(
        survey_answers,
        dataset_dir=dataset_dir,
        allow_mock=allow_mock,
    )
    deeplink_context = recommendation_profile["deeplink_context"]
    gender_text = "남성" if recommendation_profile["gender"] == "M" else "여성"
    available_color_keywords = recommendation_profile["recommended_colors"]

    applied_color_keywords = _resolve_selected_color_keywords(
        available_color_keywords,
        selected_color,
        allow_color_filter=should_apply_musinsa_color_filter(category_name),
    )

    separator_line = "=" * 70
    print(f"\n{separator_line}")
    print(
        f" 🛍️  {gender_text} | 스타일: {recommendation_profile['title']} | "
        f"퍼스널컬러: {recommendation_profile['personal_color']}"
    )
    print(f" 💡 {recommendation_profile['description']}")
    print(f" 📝 {recommendation_profile['detail']}")
    print(f" 🎨 {recommendation_profile['color_description']}")
    print(
        f" 👗 무신사 필터 적용: [스타일: {', '.join(recommendation_profile['recommended_styles'])}] / "
        f"[핏코드: {', '.join(recommendation_profile['fit_codes'])}] / "
        f"[색상: {', '.join(applied_color_keywords) or '없음'}] / "
        f"[TPO: {deeplink_context['tpo_keyword']}]"
    )
    print(separator_line)

    category_code = resolve_musinsa_category_code(category_name)
    if not category_code:
        raise ValueError(f"무신사 카테고리를 찾을 수 없습니다: {category_name}")

    category_url = build_category_url(
        category_code=category_code,
        gender=recommendation_profile["gender"],
        colors=applied_color_keywords,
        styles=recommendation_profile["style_codes"],
        fit_codes=recommendation_profile["fit_codes"],
    )
    print("[recommend_outfit_from_survey] category_url =", category_url)

    scraped_items = crawl_musinsa(category_url, category_name, top_n=top_n)

    return {
        "profile": recommendation_profile,
        "platform": "musinsa",
        "category": category_name,
        "selected_color": applied_color_keywords[0] if applied_color_keywords else None,
        "search_keyword": recommendation_profile["title"],
        "url": category_url,
        "applied_filters": {
            "category": category_name,
            "color_keywords": applied_color_keywords,
            "style_labels": recommendation_profile["recommended_styles"],
            "fit_codes": recommendation_profile["fit_codes"],
            "tpo_keyword": deeplink_context["tpo_keyword"],
        },
        "items": scraped_items,
    }


if __name__ == "__main__":
    print("🚀 퍼스널컬러 & STYLE_FIT 매핑 테스트를 시작합니다...\n")

    # [테스트 1] 모던/미니멀 & 여름뮤트 (여성)
    recommend_outfit(
        mapsiti="모던/미니멀",
        personal_color="여름뮤트",
        gender="F",
        target_categories=["셔츠&블라우스", "슈트 팬츠&슬랙스"],
        top_n=2
    )

    # [테스트 2] 스트리트 & 가을웜 (남성)
    recommend_outfit(
        mapsiti="스트리트",
        personal_color="가을웜",
        gender="M",
        target_categories=["맨투맨&스웨트", "데님 팬츠"],
        top_n=2
    )