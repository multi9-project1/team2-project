import time
import urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

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
        "전체(원피스&스커트)":   "100",
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
        "label": "노멀 핏 + 실용적/편안함",
        "styles": ["캐주얼"],
        "style_ids": [MUSINSA_STYLE_ID_MAP["캐주얼"]],
        "description": "편안하고 실용적인 스타일을 선호하는 타입으로, 부담 없이 활용하기 좋은 티셔츠, 셔츠, 데님, 코튼 팬츠처럼 데일리한 아이템이 잘 어울립니다.",
    },
    "스트리트": {
        "label": "루즈 핏 + 독특/트렌디",
        "styles": ["스트릿"],
        "style_ids": [MUSINSA_STYLE_ID_MAP["스트릿"]],
        "description": "개성 있고 트렌디한 무드를 즐기는 타입으로, 오버핏 상의, 후드, 와이드 팬츠, 볼캡처럼 존재감 있고 감각적인 아이템이 잘 어울립니다.",
    },
    "오피스/소피스티케이티드": {
        "label": "노멀/타이트 핏 + 도시적/세련됨",
        "styles": ["프레피", "미니멀", "시크"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["프레피"],
            MUSINSA_STYLE_ID_MAP["미니멀"],
            MUSINSA_STYLE_ID_MAP["시크"],
        ],
        "description": "도시적이고 세련된 분위기를 선호하는 타입으로, 셔츠, 슬랙스, 블레이저, 니트처럼 단정하고 정돈된 아이템이 잘 어울립니다.",
    },
    "페미닌": {
        "label": "타이트/노멀 핏 + 여성적/부드러움",
        "styles": ["로맨틱", "걸리시"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["로맨틱"],
            MUSINSA_STYLE_ID_MAP["걸리시"],
        ],
        "description": "부드럽고 섬세한 분위기를 살리는 타입으로, 블라우스, 가디건, 스커트, 원피스처럼 유연한 실루엣과 따뜻한 무드의 아이템이 잘 어울립니다.",
    },
    "매니시": {
        "label": "노멀/루즈 핏 + 남성적/도시적",
        "styles": ["시크", "미니멀", "프레피"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["시크"],
            MUSINSA_STYLE_ID_MAP["미니멀"],
            MUSINSA_STYLE_ID_MAP["프레피"],
        ],
        "description": "중성적이고 구조적인 스타일을 선호하는 타입으로, 셔츠, 자켓, 와이드 슬랙스, 로퍼처럼 깔끔하고 힘 있는 인상의 아이템이 잘 어울립니다.",
    },
    "스포티": {
        "label": "루즈/노멀 핏 + 활동적/편안함",
        "styles": ["스포티", "고프코어"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["스포티"],
            MUSINSA_STYLE_ID_MAP["고프코어"],
        ],
        "description": "활동성과 편안함을 중요하게 생각하는 타입으로, 트랙팬츠, 바람막이, 스웻셔츠, 기능성 소재 아이템처럼 가볍고 실용적인 옷이 잘 어울립니다.",
    },
    "모던/미니멀": {
        "label": "노멀 핏 + 깔끔함/무난함",
        "styles": ["미니멀", "시크"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["미니멀"],
            MUSINSA_STYLE_ID_MAP["시크"],
        ],
        "description": "군더더기 없이 깔끔한 스타일을 선호하는 타입으로, 무채색 상하의, 미니멀한 셔츠, 슬랙스, 심플한 아우터처럼 정제된 아이템이 잘 어울립니다.",
    },
    "로맨틱": {
        "label": "노멀 핏 + 부드러움/발랄함",
        "styles": ["로맨틱", "걸리시"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["로맨틱"],
            MUSINSA_STYLE_ID_MAP["걸리시"],
        ],
        "description": "부드럽고 사랑스러운 무드를 선호하는 타입으로, 밝은 컬러, 플로럴 패턴, 가벼운 소재, 디테일이 살아 있는 아이템이 잘 어울립니다.",
    },
    "힙스터/펑크": {
        "label": "루즈/타이트 핏 + 개방적/화려함",
        "styles": ["스트릿", "레트로", "에스닉"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["스트릿"],
            MUSINSA_STYLE_ID_MAP["레트로"],
            MUSINSA_STYLE_ID_MAP["에스닉"],
        ],
        "description": "독특하고 실험적인 스타일을 즐기는 타입으로, 강한 디테일, 패턴, 레이어드, 빈티지 포인트가 살아 있는 아이템이 잘 어울립니다.",
    },
    "레트로/빈티지": {
        "label": "핏의 다양성 + 독특함/명도-채도의 특성",
        "styles": ["레트로", "에스닉"],
        "style_ids": [
            MUSINSA_STYLE_ID_MAP["레트로"],
            MUSINSA_STYLE_ID_MAP["에스닉"],
        ],
        "description": "시대감 있는 무드와 개성 있는 색감, 패턴을 선호하는 타입으로, 빈티지 데님, 패턴 셔츠, 클래식 자켓, 에스닉한 디테일의 아이템이 잘 어울립니다.",
    },
}

LEGACY_MAPCTI_ALIAS = {
    "미니멀/모던": "모던/미니멀",
    "캐주얼/스트릿": "캐주얼",
    "로맨틱/페미닌": "로맨틱",
    "스포티/고프코어": "스포티",
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

    return {
        "mapsiti": normalized_mapsiti,
        "input_style": mapsiti,
        "label": mapsiti_info["label"],
        "mapsiti_description": mapsiti_info["description"],
        "personal_color": personal_color,
        "color_description": color_info["description"],
        "recommended_styles": list(mapsiti_info["styles"]),
        "style_codes": list(mapsiti_info["style_ids"]),
        "recommended_colors": color_info["colors"],
        "gender": gender,
    }


def build_category_url(category_code: str, gender: str, colors: list[str], styles: list[int]) -> str:
    url = f"https://www.musinsa.com/category/{category_code}/goods?gf={gender}"
    if colors:
        url += f"&color={urllib.parse.quote(','.join(colors), safe='')}"
    if styles:
        url += f"&style={urllib.parse.quote(','.join(str(s) for s in styles), safe='')}"
    url += "&sortCode=SALE_ONE_WEEK_COUNT"
    return url


def crawl_musinsa(url: str, category_name: str, top_n: int, chrome_version: int = 146) -> list[dict]:
    print(f"\n  ▶ [{category_name}] 상품 정보를 무신사에서 가져오는 중...")

    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options, version_main=chrome_version)

    scraped = []

    try:
        driver.get(url)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = soup.select('a[data-item-id]')

        if not product_links:
            print(f"    ❗ [{category_name}] 검색 조건에 맞는 상품이 없거나 로딩되지 않았습니다.")
            return []

        seen_titles = set()

        for link in product_links:
            if len(scraped) >= top_n:
                break

            img_element = link.select_one('img')
            if not img_element:
                continue

            try:
                brand = link.get('data-item-brand', "브랜드 없음")
                raw_price = link.get('data-price', "0")
                price = f"{int(raw_price):,}" if raw_price.isdigit() else raw_price
                title = img_element.get('alt', '').strip()
                img_url = img_element.get('src', '')

                if img_url.startswith('//'):
                    img_url = 'https:' + img_url

                if not title or title in seen_titles:
                    continue

                seen_titles.add(title)
                scraped.append({
                    "brand": brand, "title": title, "price": price, "img_url": img_url
                })

            except Exception:
                continue

    except Exception as e:
        print(f"    🚨 크롤링 중 에러 발생: {e}")
    finally:
        driver.quit()

    print(f"    ✅ [{category_name}] {len(scraped)}개 추출 완료")
    return scraped


# ============================================================
# 4. 메인 실행 컨트롤러
# ============================================================
def recommend_outfit(mapsiti: str, personal_color: str, gender: str, target_categories: list[str], max_colors: int = 5, top_n: int = 5):
    profile = build_profile(mapsiti, personal_color, gender)
    gender_text = "남성" if gender == "M" else "여성"
    colors_to_use = profile["recommended_colors"][:max_colors]

    sep = "=" * 70
    print(f"\n{sep}")
    print(f" 🛍️  {gender_text} | 스타일: {profile['mapsiti']} ({profile['label']}) | 퍼스널컬러: {profile['personal_color']}")
    print(f" 💡 {profile['mapsiti_description']}")
    print(f" 🎨 {profile['color_description']}")
    print(f" 👗 무신사 필터 적용: [스타일: {', '.join(profile['recommended_styles'])}] / [색상: {', '.join(colors_to_use)}]")
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

        url = build_category_url(cat_code, gender, colors_to_use, profile["style_codes"])
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


if __name__ == "__main__":
    print("🚀 퍼스널컬러 & MAPSITI 매핑 테스트를 시작합니다...\n")

    # [테스트 1] 모던/미니멀 & 여름뮤트 (여성)
    recommend_outfit(
        mapsiti="모던/미니멀",
        personal_color="여름뮤트",
        gender="F",
        target_categories=["셔츠&블라우스", "슈트 팬츠&슬랙스"],
        top_n=2
    )

    # [테스트 2] 캐주얼 & 가을웜 (남성)
    recommend_outfit(
        mapsiti="캐주얼",
        personal_color="가을웜",
        gender="M",
        target_categories=["맨투맨&스웨트", "데님 팬츠"],
        top_n=2
    )

    # [테스트 3] 로맨틱 & 봄라이트 (여성)
    recommend_outfit(
        mapsiti="로맨틱",
        personal_color="봄라이트",
        gender="F",
        target_categories=["전체(원피스&스커트)", "니트&스웨터"],
        top_n=2
    )

    # [테스트 4] 스포티 & 겨울브라이트 (남성)
    recommend_outfit(
        mapsiti="스포티",
        personal_color="겨울브라이트",
        gender="M",
        target_categories=["트레이닝&조거 팬츠", "전체(상의)"],
        top_n=2
    )
