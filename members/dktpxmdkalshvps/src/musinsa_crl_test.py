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

STYLES = {
    "캐주얼": 1, "스트릿": 2, "고프코어": 3, "프레피": 5,
    "스포티": 7, "로맨틱": 8, "걸리시": 9, "미니멀": 11,
    "시크": 12, "레트로": 13, "에스닉": 14,
}

FEMALE_ONLY_STYLES = {"걸리시", "로맨틱"}

# ============================================================
# 2. 퍼스널컬러 & MAPCTI 매핑 데이터
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

MAPCTI_STYLE_MAP = {
    "미니멀/모던": {"label": "도심 속 시크한 꾸안꾸족", "styles": ["미니멀", "시크"], "description": "깔끔한 실루엣과 절제된 디테일을 선호하는 타입으로, 슬랙스·셔츠·자켓처럼 단정하고 세련된 아이템이 잘 어울립니다."},
    "캐주얼/스트릿": {"label": "힙합 바이브, 자유로운 영혼", "styles": ["캐주얼", "스트릿"], "description": "편안하면서도 개성 있는 무드를 즐기는 타입으로, 맨투맨·후드티·와이드 팬츠 같은 여유로운 핏의 아이템이 잘 어울립니다."},
    "로맨틱/페미닌": {"label": "인간 벚꽃, 러블리 보스", "styles": ["로맨틱", "걸리시"], "description": "사랑스럽고 부드러운 분위기를 살리는 타입으로, 블라우스·원피스·롱스커트·플로럴 패턴처럼 여성스러운 아이템이 잘 어울립니다."},
    "스포티/고프코어": {"label": "실용성 갑, 트렌디 액티브", "styles": ["스포티", "고프코어"], "description": "활동성과 실용성을 중시하면서도 트렌디함을 놓치지 않는 타입으로, 나일론 팬츠·바람막이·트랙탑 같은 기능성 아이템이 잘 어울립니다."},
}

# ============================================================
# 3. 데이터 조립 및 크롤링 핵심 함수
# ============================================================
def build_profile(mapcti: str, personal_color: str, gender: str) -> dict:
    mapcti = mapcti.strip()
    mapcti_info = MAPCTI_STYLE_MAP.get(mapcti)
    color_info = PERSONAL_COLOR_MAP.get(personal_color)

    if not mapcti_info or not color_info:
        raise ValueError("잘못된 MAPCTI 또는 퍼스널컬러 입력입니다.")

    styles = list(mapcti_info["styles"])

    if gender == "M":
        styles = [s for s in styles if s not in FEMALE_ONLY_STYLES]
        if not styles:
            styles = ["캐주얼", "미니멀"] 

    style_codes = [STYLES[s] for s in styles if s in STYLES]

    return {
        "mapcti": mapcti, 
        "label": mapcti_info["label"], 
        "mapcti_description": mapcti_info["description"],
        "personal_color": personal_color, 
        "color_description": color_info["description"],
        "recommended_styles": styles, 
        "style_codes": style_codes,
        "recommended_colors": color_info["colors"],
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
def recommend_outfit(mapcti: str, personal_color: str, gender: str, target_categories: list[str], max_colors: int = 5, top_n: int = 5):
    profile = build_profile(mapcti, personal_color, gender)
    gender_text = "남성" if gender == "M" else "여성"
    colors_to_use = profile["recommended_colors"][:max_colors] 

    sep = "=" * 70
    print(f"\n{sep}")
    print(f" 🛍️  {gender_text} | 스타일: {profile['mapcti']} ({profile['label']}) | 퍼스널컬러: {profile['personal_color']}")
    print(f" 💡 {profile['mapcti_description']}")
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
    print("🚀 퍼스널컬러 & MAPCTI 매핑 테스트를 시작합니다...\n")

    # [테스트 1] 미니멀/모던 & 여름뮤트 (여성)
    recommend_outfit(
        mapcti="미니멀/모던",
        personal_color="여름뮤트",
        gender="F",
        target_categories=["셔츠&블라우스", "슈트 팬츠&슬랙스"],
        top_n=2
    )

    # [테스트 2] 캐주얼/스트릿 & 가을웜 (남성)
    recommend_outfit(
        mapcti="캐주얼/스트릿",
        personal_color="가을웜",
        gender="M",
        target_categories=["맨투맨&스웨트", "데님 팬츠"],
        top_n=2
    )

    # [테스트 3] 로맨틱/페미닌 & 봄라이트 (여성)
    recommend_outfit(
        mapcti="로맨틱/페미닌",
        personal_color="봄라이트",
        gender="F",
        target_categories=["전체(원피스&스커트)", "니트&스웨터"],
        top_n=2
    )

    # [테스트 4] 스포티/고프코어 & 겨울브라이트 (남성)
    recommend_outfit(
        mapcti="스포티/고프코어",
        personal_color="겨울브라이트",
        gender="M",
        target_categories=["트레이닝&조거 팬츠", "전체(상의)"],
        top_n=2
    )