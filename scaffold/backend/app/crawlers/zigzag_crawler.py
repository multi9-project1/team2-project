import time
import random
import urllib.parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# ============================================================
# 1. 카테고리별 마스터 맵 & 상세 핏 필터
# ============================================================
ZIGZAG_MASTER_MAP = {
    "상의": {
        "fits": ["슬림핏", "루즈핏", "오버핏", "크롭핏", "박시핏", "레귤러핏"]
    },
    "아우터": {
        "fits": ["오버핏", "루즈핏", "슬림핏", "크롭핏", "롱라인", "벨티드"]
    },
    "팬츠": {
        "fits": ["와이드핏", "슬림핏", "스트레이트핏", "부츠컷", "조거핏", "테이퍼드핏", "하이웨스트"]
    },
    "원피스": {
        "fits": ["A라인", "H라인", "플레어", "머메이드", "슬림핏", "루즈핏", "랩핏", "셔츠핏"]
    },
    "니트/카디건": {
        "fits": ["루즈핏", "슬림핏", "오버핏", "크롭핏", "레귤러핏"]
    },
    "스커트": {
        "fits": ["A라인", "H라인", "플레어", "머메이드", "타이트핏", "랩핏", "플리츠"]
    },
    "트레이닝": {
        "fits": ["루즈핏", "오버핏", "조거핏", "세미슬림"]
    },
    "투피스/세트": {
        "fits": ["셋업핏", "루즈핏", "슬림핏", "크롭셋업", "트레이닝핏"]
    }
}

# ============================================================
# 2. [수정됨] 스타일별 타겟 핏 데이터 (features 제거, 핏만 남김)
# ============================================================
STYLE_FIT_MAP = {
    "캐주얼": ["레귤러핏", "스트레이트핏", "세미슬림"],
    "스트리트": ["오버핏", "루즈핏", "박시핏", "와이드핏"],
    "오피스/소피스티케이티드": ["슬림핏", "레귤러핏", "H라인"],
    "페미닌": ["슬림핏", "A라인", "랩핏", "플레어"],
    "매니시": ["레귤러핏", "루즈핏", "스트레이트핏"],
    "스포티": ["조거핏", "루즈핏", "트레이닝핏"],
    "모던/미니멀": ["레귤러핏", "슬림핏", "스트레이트핏"],
    "로맨틱": ["A라인", "플레어", "크롭핏"],
    "힙스터/펑크": ["오버핏", "타이트핏", "크롭핏", "와이드핏"],
    "레트로/빈티지": ["부츠컷", "테이퍼드핏", "롱라인"]
}

global_driver = None

# ============================================================
# 3. 크롤링 엔진
# ============================================================
def get_driver():
    global global_driver
    if global_driver is None:
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        global_driver = uc.Chrome(options=options, version_main=146)
    return global_driver

def crawl_zigzag(url, keyword, top_n=2):
    driver = get_driver()
    scraped = []
    try:
        driver.get(url)
        time.sleep(5)
        cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")
        for card in cards[:top_n]:
            try:
                mall = card.find_element(By.CSS_SELECTOR, ".zds4_1kdomr8").text
                title = card.find_element(By.CSS_SELECTOR, ".zds4_1kdomrc").text
                price = card.find_element(By.CSS_SELECTOR, ".zds4_1jsf80i3").text
                img = card.find_element(By.CSS_SELECTOR, ".product-card-thumbnail img").get_attribute("src")
                scraped.append({"mall": mall, "title": title, "price": price, "img": img})
            except: continue
    except Exception as e: print(f"Error: {e}")
    finally:
        driver.quit()
        global global_driver
        global_driver = None
    return scraped

# ============================================================
# 4. 핵심 로직: 지능형 키워드 생성 (스타일 핏 + 카테고리명)
# ============================================================
def get_smart_recommendations(styles: list, categories: list):
    final_tasks = []
    
    for style in styles:
        target_fits = STYLE_FIT_MAP.get(style)
        if not target_fits: continue
        
        # 사용자가 선택한 카테고리(MY_CATS)들 순회
        for main_cat in categories:
            if main_cat not in ZIGZAG_MASTER_MAP: continue
            
            # 1. 해당 카테고리가 가질 수 있는 모든 핏 필터 가져오기
            possible_fits = ZIGZAG_MASTER_MAP[main_cat]["fits"]
            
            # 2. 스타일(MY_STYLES)의 지향 핏과 카테고리의 가능 핏 교집합 찾기
            valid_fits = [f for f in possible_fits if any(tf in f for tf in target_fits)]
            
            # 3. 핏 선정 (교집합이 없으면 카테고리 기본 핏 중 랜덤 선택)
            selected_fit = random.choice(valid_fits) if valid_fits else random.choice(possible_fits)
            
            # 4. 최종 검색어 조합: [스타일에 맞는 핏] + [MY_CATS 카테고리 이름]
            # 예: "오버핏 상의", "슬림핏 팬츠", "A라인 원피스" 등
            keyword = f"{selected_fit} {main_cat}".strip()
            final_tasks.append((style, keyword))

    results = {}
    
    # 중복 검색어 방지 (예: 같은 '오버핏 상의'가 여러 번 나오는 것 방지)
    unique_tasks = []
    seen_keywords = set()
    for style, kw in final_tasks:
        if kw not in seen_keywords:
            unique_tasks.append((style, kw))
            seen_keywords.add(kw)

    for style, kw in unique_tasks:
        encoded = urllib.parse.quote_plus(kw)
        url = f"https://zigzag.kr/search?keyword={encoded}&order=SCORE_DESC"
        print(f"🔍 [{style}] 검색 키워드 생성 완료: {kw}")
        data = crawl_zigzag(url, kw)
        if data: results[f"[{style}] {kw}"] = data
            
    return results

# ============================================================
# 5. 실행
# ============================================================
if __name__ == "__main__":
    # 테스트 입력
    MY_STYLES = ["로맨틱", "오피스/소피스티케이티드"]
    MY_CATS = ["상의", "팬츠"]
    
    final_res = get_smart_recommendations(MY_STYLES, MY_CATS)
    
    print("\n" + "="*50)
    print("🛍️ 핏 + 카테고리 기반 맞춤형 코디 결과")
    print("="*50)
    for kw, items in final_res.items():
        print(f"\n📌 {kw}")
        for i, item in enumerate(items, 1):
            print(f"   {i}. [{item['mall']}] {item['title']} ({item['price']})")