import streamlit as st
from dotenv import load_dotenv
import os
import urllib.parse
import time
import random
from logic import analyze_fashion_style
from bs4 import BeautifulSoup

# --- Crawling Imports ---
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 환경 변수 로드
load_dotenv()

# ============================================================
# 0. 크롤링 엔진 (무신사 전용)
# ============================================================
def get_musinsa_previews(keyword, gender="A", top_n=5):
    options = uc.ChromeOptions()
    options.add_argument('--headless=new') # 최신 크롬용 강력한 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu') # GPU 가속 비활성화 (창 방지)
    options.add_argument("--window-size=1920,1080") # 가상 윈도우 크기 설정
    options.add_argument('--disable-popup-blocking')
    # 봇 탐지 회피를 위한 User-Agent 설정 강화
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36')
    
    try:
        driver = uc.Chrome(options=options, version_main=146)
        encoded_keyword = urllib.parse.quote_plus(keyword)
        # 인기순 정렬 유지
        url = f"https://www.musinsa.com/search/goods?keyword={encoded_keyword}&keywordType=keyword&gf={gender}&sortCode=SALE_ONE_WEEK_COUNT"
        
        driver.get(url)
        # 💡 단계별 스크롤 및 충분한 대기 (이미지 로딩 유도)
        time.sleep(6) 
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
        
        # 💡 [핵심] 모든 상품 요소를 포괄적으로 탐색 (data-item-id 기반)
        items = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id]")
        
        scraped = []
        for el in items:
            if len(scraped) == top_n: break
            
            try:
                # 1. 이미지 및 타이틀 (img 태그)
                img_el = el.find_element(By.CSS_SELECTOR, "img")
                title = img_el.get_attribute("alt") or img_el.get_attribute("title")
                img_url = img_el.get_attribute("src")
                
                # 지연 로딩(Lazy Loading) 이미지 처리
                if not img_url or "base64" in img_url:
                    img_url = img_el.get_attribute("data-original") or img_el.get_attribute("data-src")
                
                if not title or not img_url: continue
                
                # 2. 브랜드 및 가격 (데이터 속성 활용)
                brand = el.get_attribute("data-item-brand") or "Musinsa"
                raw_price = el.get_attribute("data-price") or "0"
                price = f"{int(raw_price):,}" if raw_price.isdigit() else raw_price
                
                # 3. 상세 페이지 링크 (절대 경로 보장)
                product_url = el.get_attribute("href")
                if product_url and not product_url.startswith("http"):
                    if product_url.startswith("//"):
                        product_url = "https:" + product_url
                    else:
                        product_url = "https://www.musinsa.com" + ("" if product_url.startswith("/") else "/") + product_url
                
                # 중복 데이터 제거
                if any(res['title'] == title for res in scraped): continue
                
                scraped.append({
                    "mall": brand, 
                    "title": title.strip(), 
                    "price": price, 
                    "img": img_url,
                    "link": product_url
                })
            except: continue
            
        driver.quit()
        return scraped
    except Exception as e:
        st.error(f"무신사 크롤링 엔진 오류: {e}")
        return []

# ============================================================
# 0. 크롤링 엔진 (지그재그 전용)
# ============================================================
def get_zigzag_previews(keyword, top_n=5):
    options = uc.ChromeOptions()
    options.add_argument('--headless=new') # 최신 크롬용 강력한 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-popup-blocking')
    
    try:
        driver = uc.Chrome(options=options, version_main=146)
        encoded = urllib.parse.quote_plus(keyword)
        url = f"https://zigzag.kr/search?keyword={encoded}&order=SCORE_DESC"
        
        driver.get(url)
        time.sleep(6) 
        
        # 💡 지그재그 검색 결과 영역 내의 실제 상품 카드만 타겟팅 (광고 제외 시도)
        products = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='product-list'] .product-card")
        if not products: # fallback
            products = driver.find_elements(By.CSS_SELECTOR, ".product-card")

        scraped = []
        for product in products:
            if len(scraped) == top_n:
                break
            try:
                mall = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomr8").text
                title = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomrc").text
                price = product.find_element(By.CSS_SELECTOR, ".zds4_1jsf80i3").text
                
                img_element = product.find_element(By.CSS_SELECTOR, ".product-card-thumbnail img")
                img = img_element.get_attribute("src")
                
                try:
                    product_link_el = product if product.tag_name == "a" else product.find_element(By.CSS_SELECTOR, "a")
                    product_url = product_link_el.get_attribute("href")
                except:
                    product_url = "#"
                
                scraped.append({
                    "mall": mall, 
                    "title": title, 
                    "price": price, 
                    "img": img,
                    "link": product_url
                })
            except: continue
            
        driver.quit()
        return scraped
    except Exception as e:
        st.error(f"지그재그 크롤링 엔진 오류: {e}")
        return []

# Page configuration
st.set_page_config(
    page_title="Mapsi-TI · AI 퍼스널 스타일 큐레이션", 
    layout="wide", 
    page_icon="🧪",
    initial_sidebar_state="collapsed"
)

# ── Data Definitions ──────────────────────────────────────
# 고도화된 카테고리별 마스터 맵
ZIGZAG_MASTER_MAP = {
    "상의": {"fits": ["슬림핏", "루즈핏", "오버핏", "크롭핏", "박시핏", "레귤러핏"]},
    "아우터": {"fits": ["오버핏", "루즈핏", "슬림핏", "크롭핏", "롱라인", "벨티드"]},
    "팬츠": {"fits": ["와이드핏", "슬림핏", "스트레이트핏", "부츠컷", "조거핏", "테이퍼드핏", "하이웨스트"]},
    "원피스": {"fits": ["A라인", "H라인", "플레어", "머메이드", "슬림핏", "루즈핏", "랩핏", "셔츠핏"]},
    "니트/카디건": {"fits": ["루즈핏", "슬림핏", "오버핏", "크롭핏", "레귤러핏"]},
    "스커트": {"fits": ["A라인", "H라인", "플레어", "머메이드", "타이트핏", "랩핏", "플리츠"]},
    "트레이닝": {"fits": ["루즈핏", "오버핏", "조거핏", "세미슬림"]},
    "투피스/세트": {"fits": ["셋업핏", "루즈핏", "슬림핏", "크롭셋업", "트레이닝핏"]}
}

# 스타일별 타겟 핏 데이터
STYLE_FIT_MAP = {
    "캐주얼": ["레귤러핏", "스트레이트핏", "세미슬림"],
    "스트리트": ["오버핏", "루즈핏", "박시핏", "와이드핏"],
    "소피스티케이티드": ["슬림핏", "레귤러핏", "H라인"],
    "페미닌": ["슬림핏", "A라인", "랩핏", "플레어"],
    "매니시": ["레귤러핏", "루즈핏", "스트레이트핏"],
    "스포티": ["조거핏", "루즈핏", "트레이닝핏"],
    "모던/미니멀": ["레귤러핏", "슬림핏", "스트레이트핏"],
    "로맨틱": ["A라인", "플레어", "크롭핏"],
    "힙스터/펑크": ["오버핏", "타이트핏", "크롭핏", "와이드핏"],
    "레트로": ["부츠컷", "테이퍼드핏", "롱라인"]
}

questions = [
    {
        "question": "Q1. [첫인상/무드] 새로운 모임에 나가는 날! 거울 앞의 나는 어떤 분위기일까?",
        "A": {"label": "깔끔하고 단정하게! ✨", "desc": "은근히 지적이면서도 세련된 인상을 주고 싶어", "scores": ["소피스티케이티드", "모던/미니멀", "페미닌", "매니시"]},
        "B": {"label": "친근하거나 힙하게! ✌️", "desc": "개성 있고 다가가기 편안한 인상을 주고 싶어", "scores": ["캐주얼", "로맨틱", "스트리트", "스포티", "힙스터/펑크", "레트로"]}
    },
    {
        "question": "Q2. [온라인 쇼핑 사이즈 고민] 쇼핑몰에서 옷을 구경하는데, 내 사이즈가 애매하게 걸쳐 있다. 이럴 때 나의 평소 주문 습관은?",
        "A": {"label": "핏이 무너지면 안 되지! 📏", "desc": "내 체형에 딱 맞는 정사이즈를 고른다.", "scores": ["타이트/노멀 핏"]},
        "B": {"label": "작은 것보단 큰 게 낫지! 👕", "desc": "고민할 바엔 그냥 한 사이즈 크게 사서 넉넉하게 입는다.", "scores": ["루즈/오버 핏"]}
    },
    {
        "question": "Q3. [핏 Fit] 밥 먹고 배가 살짝 부른 상태다! 지금 내 옷의 핏(Fit)은?",
        "A": {"label": "그래도 핏은 포기 못 해! 👗", "desc": "내 예쁜 라인을 딱 잡아주는 텐션 있는 옷", "scores": ["페미닌", "소피스티케이티드", "힙스터/펑크", "로맨틱", "타이트/노멀 핏"]},
        "B": {"label": "아 배불러~ 완전 편해! ☁️", "desc": "몸을 쪼이지 않고 넉넉하게 툭 떨어지는 오버핏", "scores": ["캐주얼", "스트리트", "스포티", "매니시", "레트로", "루즈/오버 핏"]}
    },
    {
        "question": "Q4. [디테일 Detail] 마음에 쏙 드는 온라인 쇼핑몰 발견! 내 장바구니에 담긴 옷들은?",
        "A": {"label": "돌려 입기 최고! 🤍", "desc": "로고나 패턴 없이 심플하고 색감이 깔끔한 기본템들", "scores": ["모던/미니멀", "캐주얼", "매니시", "소피스티케이티드"]},
        "B": {"label": "이건 사야 해! 💖", "desc": "흔하지 않은 디자인, 톡톡 튀는 컬러나 유니크한 포인트템들", "scores": ["힙스터/펑크", "레트로", "스트리트", "로맨틱"]}
    },
    {
        "question": "Q5. [활동성 TPO] 날씨 좋은 주말! 내가 가장 행복함을 느끼는 외출 코스는?",
        "A": {"label": "조용한 힐링 📸", "desc": "예쁜 카페에서 조용히 커피 마시거나, 핫플에서 예쁜 사진 남기기", "scores": ["로맨틱", "페미닌", "소피스티케이티드", "모던/미니멀", "레트로"]},
        "B": {"label": "활동적인 하루 🏃‍♀️", "desc": "방탈출, 한강 피크닉, 보드게임 등 활동적으로 뽈뽈거리며 돌아다니기", "scores": ["스포티", "캐주얼", "스트리트", "힙스터/펑크", "매니시"]}
    },
    {
        "question": "Q6. [온도/감성] 나를 한 장의 영화 포스터로 표현한다면?",
        "A": {"label": "차가운 시크 🌃", "desc": "흑백 필름이나 쿨톤 필터가 씌워진, 차갑고 시크한 도심 누아르", "scores": ["매니시", "모던/미니멀", "소피스티케이티드", "스트리트"]},
        "B": {"label": "따뜻한 감성 🎞️", "desc": "따뜻한 햇살 필터가 가득한, 몽글몽글하고 빈티지한 감성 로맨스", "scores": ["로맨틱", "레트로", "페미닌", "캐주얼"]}
    }
]

color_options = [
    {"id": "봄 라이트", "season": "봄", "stripe": "stripe-spring", "desc": "밝고 연한 파스텔. 산뜻한 이미지.", "colors": ["#FFD9B3", "#FFC3A0", "#FFEAD5"]},
    {"id": "봄 브라이트", "season": "봄", "stripe": "stripe-spring", "desc": "선명하고 생기 있는 비비드한 톤.", "colors": ["#FF9F43", "#FFD32A", "#FF6B6B"]},
    {"id": "봄 웜", "season": "봄", "stripe": "stripe-spring", "desc": "따뜻한 복숭아 베이스. 건강한 피부톤.", "colors": ["#F4A261", "#E76F51", "#FFBA93"]},
    {"id": "여름 라이트", "season": "여름", "stripe": "stripe-summer", "desc": "연하고 차가운 파스텔. 청순한 이미지.", "colors": ["#B5D5F7", "#D9C4F0", "#C8E6F5"]},
    {"id": "여름 쿨", "season": "여름", "stripe": "stripe-summer", "desc": "밝고 선명한 쿨 계열. 생동감 있는 쿨톤.", "colors": ["#A1C4FD", "#B2A4D4", "#F7CAC9"]},
    {"id": "여름 뮤트", "season": "여름", "stripe": "stripe-summer", "desc": "차분하고 오묘한 회색빛 쿨 계열.", "colors": ["#9BB5CC", "#B0A4C8", "#C4B3C9"]},
    {"id": "가을 뮤트", "season": "가을", "stripe": "stripe-autumn", "desc": "채도 낮은 카키와 올리브. 내추럴 스타일.", "colors": ["#8D8B4E", "#6B7C41", "#9C8B5E"]},
    {"id": "가을 딥", "season": "가을", "stripe": "stripe-autumn", "desc": "깊고 진한 버건디와 브라운. 성숙한 이미지.", "colors": ["#8B3A3A", "#5C3317", "#7B4F2E"]},
    {"id": "가을 웜", "season": "가을", "stripe": "stripe-autumn", "desc": "클래식하고 따뜻한 어스톤 분위기.", "colors": ["#C67B2A", "#D4956A", "#E8B07A"]},
    {"id": "겨울 브라이트", "season": "겨울", "stripe": "stripe-winter", "desc": "선명하고 청량한 아이시 컬러. 강렬한 인상.", "colors": ["#00CEC9", "#6C5CE7", "#E84393"]},
    {"id": "겨울 딥", "season": "겨울", "stripe": "stripe-winter", "desc": "짙은 네이비와 블랙. 카리스마 스타일.", "colors": ["#2C2C6C", "#6D1F4E", "#1A1A3A"]},
    {"id": "겨울 쿨", "season": "겨울", "stripe": "stripe-winter", "desc": "차가운 핑크와 라일락. 모던한 쿨톤.", "colors": ["#1034A6", "#FF00FF", "#FFFFFF"]}
]

color_guide_data = {
    "봄 라이트": {"musinsa": ["화이트", "아이보리", "라이트핑크", "피치", "코럴", "옐로우"], "zigzag": ["화이트", "아이보리", "라이트핑크", "피치", "코럴", "옐로우"]},
    "봄 브라이트": {"musinsa": ["핑크", "오렌지", "레드", "민트", "그린", "옐로우"], "zigzag": ["핑크", "오렌지", "레드", "민트", "그린", "옐로우"]},
    "봄 웜": {"musinsa": ["아이보리", "베이지", "오렌지", "머스타드", "샌드"], "zigzag": ["아이보리", "베이지", "브라운", "오렌지", "코럴"]},
    "여름 라이트": {"musinsa": ["화이트", "라이트핑크", "스카이블루", "라벤더"], "zigzag": ["화이트", "라이트핑크", "라이트블루", "퍼플"]},
    "여름 쿨": {"musinsa": ["화이트", "블루", "네이비", "실버"], "zigzag": ["화이트", "블루", "네이비", "실버"]},
    "여름 뮤트": {"musinsa": ["그레이", "라이트그레이", "다크그레이", "블루"], "zigzag": ["그레이", "챠콜", "로즈", "모브", "블루"]},
    "가을 뮤트": {"musinsa": ["베이지", "다크베이지", "카키", "오트밀"], "zigzag": ["베이지", "카키", "민트", "브라운"]},
    "가을 딥": {"musinsa": ["다크브라운", "딥레드", "버건디", "진청"], "zigzag": ["브라운", "버건디", "챠콜"]},
    "가을 웜": {"musinsa": ["카멜", "머스타드", "다크오렌지", "브라운"], "zigzag": ["오렌지", "브라운", "카키", "골드"]},
    "겨울 브라이트": {"musinsa": ["블랙", "화이트", "레드", "블루", "퍼플"], "zigzag": ["블랙", "화이트", "레드", "블루", "퍼플"]},
    "겨울 딥": {"musinsa": ["블랙", "다크네이비", "다크그린", "버건디"], "zigzag": ["블랙", "네이비", "버건디", "챠콜"]},
    "겨울 쿨": {"musinsa": ["화이트", "네이비", "실버", "데님"], "zigzag": ["화이트", "네이비", "실버"]},
    "모르겠어요": {"musinsa": ["블랙", "화이트", "그레이", "베이지"], "zigzag": ["블랙", "화이트", "그레이", "베이지"]}
}

# ── Custom CSS ──────────────────────────────────────────
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Cormorant+Garamond:wght@600;700&display=swap');
        [data-testid="stAppViewContainer"] { background-color: #0b0b0e; font-family: 'Noto Sans KR', sans-serif; color: #efefef; }
        [data-testid="stHeader"] { background: rgba(11,11,14,0.88); backdrop-filter: blur(16px); }
        .main::before {
            content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
            opacity: 0.4;
        }
        :root { --gold: #c9a96e; --gold-soft: rgba(201,169,110,0.12); --card: #1a1a24; --border: rgba(255,255,255,0.08); }
        h1, h2, h3 { color: #efefef !important; }
        .section-title { font-size: 1.6rem; font-weight: 900; margin-bottom: 0.35rem; }
        .section-num { font-size: 0.7rem; font-weight: 700; color: var(--gold); letter-spacing: 0.15em; text-transform: uppercase; }
        .logo-name { font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; color: var(--gold); font-weight: 700; }
        .custom-card { padding: 1.5rem; border-radius: 14px; border: 1.5px solid var(--border); background: var(--card); transition: all 0.25s ease; position: relative; overflow: hidden; }
        .selected-card { border-color: var(--gold) !important; background: var(--gold-soft) !important; box-shadow: 0 0 0 1px var(--gold); }
        .cc-swatch { width: 18px; height: 18px; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.12); margin-right: 4px; display: inline-block; }
        .stripe { position: absolute; top: 0; left: 0; right: 0; height: 4px; }
        .stripe-spring { background: linear-gradient(90deg,#ffd580,#f4a261,#e76f51); }
        .stripe-summer { background: linear-gradient(90deg,#c9b8f4,#90bfff,#f2a7c3); }
        .stripe-autumn { background: linear-gradient(90deg,#c67b2a,#8b5e3c,#6b7c41); }
        .stripe-winter { background: linear-gradient(90deg,#8ec5fc,#6d1f4e,#2c2c6c); }
        .stripe-unknown { background: linear-gradient(90deg,#555,#888,#bbb); }
        .summary-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; background: rgba(11,11,14,0.94); backdrop-filter: blur(16px); border-top: 1px solid var(--border); padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .s-pill { padding: 0.25rem 0.7rem; border-radius: 999px; background: rgba(255,255,255,0.05); color: #888; font-size: 0.72rem; font-weight: 600; border: 1px solid var(--border); margin-right: 0.5rem; }
        .s-pill.filled { background: var(--gold-soft); color: var(--gold); border-color: rgba(201,169,110,0.3); }
        div.stButton > button { border-radius: 999px !important; background: var(--card) !important; border: 1.5px solid var(--border) !important; color: #efefef !important; }
        div.stButton > button:hover { border-color: var(--gold) !important; color: var(--gold) !important; }
        div.stButton > button[kind="primary"] { background: var(--gold) !important; color: #0b0b0e !important; border: none !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ── Session State ─────────────────────────────────────────
for key in ['gender', 'personal_color', 'analysis_result']:
    if key not in st.session_state: st.session_state[key] = None
if 'quiz_step' not in st.session_state: st.session_state.quiz_step = 0
if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers = []
if 'final_clothing' not in st.session_state: st.session_state.final_clothing = "상의"
if 'top_1_style' not in st.session_state: st.session_state.top_1_style = None
# 미리보기 결과 유지용 세션
if 'm_previews' not in st.session_state: st.session_state.m_previews = None
if 'z_previews' not in st.session_state: st.session_state.z_previews = None
# 퍼스널 컬러 진단용 세션
if 'pc_diagnosis_active' not in st.session_state: st.session_state.pc_diagnosis_active = False
if 'pc_quiz_step' not in st.session_state: st.session_state.pc_quiz_step = 1
if 'pc_warm_cool' not in st.session_state: st.session_state.pc_warm_cool = []

# ── Sidebar ──
with st.sidebar:
    st.title("👗 Mapsi-TI Settings")
    if os.getenv("OPENAI_API_KEY"): st.success("🔒 AI 엔진 연결됨")
    else: st.error("⚠️ OPENAI_API_KEY 누락")
    if st.button("🔄 테스트 초기화", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ── Header ──
st.markdown("""
    <div style="margin-bottom: 2rem; padding-top: 1rem;">
        <span class="logo-name">Mapsi-TI</span>
        <p style="font-size: 0.7rem; color: #888; margin-top: -5px; letter-spacing: 0.05em;">AI PERSONAL STYLE CURATION</p>
    </div>
""", unsafe_allow_html=True)

# ── Main Flow ─────────────────────────────────────────────
if st.session_state.analysis_result is None:
    # 1. Gender & Age
    st.markdown('<div class="section-num">Section 01</div><h2 class="section-title">기본 정보</h2>', unsafe_allow_html=True)
    cg1, cg2 = st.columns(2)
    with cg1:
        if st.button(f"👔 남성 {' (선택됨)' if st.session_state.gender=='남성' else ''}", use_container_width=True):
            st.session_state.gender = "남성"; st.rerun()
    with cg2:
        if st.button(f"👗 여성 {' (선택됨)' if st.session_state.gender=='여성' else ''}", use_container_width=True):
            st.session_state.gender = "여성"; st.rerun()

    # 2. Personal Color
    st.markdown('<div style="height:40px;"></div><div class="section-num">Section 02</div><h2 class="section-title">퍼스널 컬러</h2>', unsafe_allow_html=True)
    c_cols = st.columns(3)
    for idx, c in enumerate(color_options):
        with c_cols[idx % 3]:
            is_sel = st.session_state.personal_color == c['id']
            # 컬러 스와치 HTML 생성
            swatches_html = "".join([f'<span class="cc-swatch" style="background:{color};"></span>' for color in c['colors']])
            st.markdown(f"""
                <div class="custom-card {"selected-card" if is_sel else ""}" style="height:140px; margin-bottom:10px;">
                    <div class="stripe {c["stripe"]}"></div>
                    <div style="font-size:0.9rem; font-weight:700;">{c["id"]}</div>
                    <div style="margin-top: 5px; margin-bottom: 5px;">{swatches_html}</div>
                    <div style="font-size:0.7rem; color:#bbb;">{c["desc"]}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"{'취소' if is_sel else '선택'}: {c['id']}", key=f"pc_{idx}", use_container_width=True):
                if is_sel:
                    st.session_state.personal_color = None
                else:
                    st.session_state.personal_color = c['id']
                st.rerun()
    
    if st.session_state.personal_color is None and not st.session_state.pc_diagnosis_active:
        if st.button("모르겠어요 (내 컬러 찾아보기 🔍)", use_container_width=True):
            st.session_state.pc_diagnosis_active = True; st.rerun()

    # --- 퍼스널 컬러 간이 진단 퀴즈 레이어 ---
    if st.session_state.pc_diagnosis_active and st.session_state.personal_color is None:
        st.markdown('<div style="background:var(--card); padding:2rem; border-radius:20px; border:1px solid var(--gold);">', unsafe_allow_html=True)
        
        if st.session_state.pc_quiz_step == 1:
            st.markdown("### 1단계: 내 피부는 어떤 바탕색일까?\n**Q1. 손목 안쪽을 봤을 때, 혈관이 어떤 색으로 보이나요?**")
            c1, c2 = st.columns(2)
            if c1.button("초록색이나 올리브색 (웜)", use_container_width=True): 
                st.session_state.pc_warm_cool.append("W"); st.session_state.pc_quiz_step = 2; st.rerun()
            if c2.button("파란색이나 보라색 (쿨)", use_container_width=True): 
                st.session_state.pc_warm_cool.append("C"); st.session_state.pc_quiz_step = 2; st.rerun()
        
        elif st.session_state.pc_quiz_step == 2:
            st.markdown("### 1단계: 내 피부는 어떤 바탕색일까?\n**Q2. 햇볕 아래에서 오랫동안 놀고 나면 피부가 어떻게 되나요?**")
            c1, c2 = st.columns(2)
            if c1.button("어둡게 타는 편 (웜)", use_container_width=True): 
                st.session_state.pc_warm_cool.append("W"); st.session_state.pc_quiz_step = 3; st.rerun()
            if c2.button("빨갛게 익는 편 (쿨)", use_container_width=True): 
                st.session_state.pc_warm_cool.append("C"); st.session_state.pc_quiz_step = 3; st.rerun()
        
        elif st.session_state.pc_quiz_step == 3:
            # 컬러 데이터 매핑용 헬퍼
            c_map = {c['id']: c['colors'] for c in color_options}
            
            # 웜/쿨 답변 존재 여부 확인
            has_warm = "W" in st.session_state.pc_warm_cool
            has_cool = "C" in st.session_state.pc_warm_cool
            
            st.markdown("### 2단계: 나에게 어울리는 진짜 색깔 찾기\n1단계 결과를 바탕으로 어울리는 느낌을 골라보세요.")

            def render_pc_option(res_color, desc):
                colors = c_map.get(res_color, ["#888", "#888", "#888"])
                swatches_html = "".join([f'<span class="cc-swatch" style="background:{c}; width:14px; height:14px; margin-right:4px;"></span>' for c in colors])
                st.markdown(f'<div style="margin-top:10px; margin-bottom:5px;">{swatches_html} <b>{res_color}</b></div>', unsafe_allow_html=True)
                if st.button(desc, key=f"pc_btn_{res_color}", use_container_width=True):
                    st.session_state.personal_color = res_color
                    st.session_state.pc_diagnosis_active = False
                    st.rerun()

            # 웜톤 질문 노출
            if has_warm:
                st.markdown("#### [웜(Warm) 느낌이 있다면?]")
                warm_opts = [
                    ("봄 라이트", "노란색 개나리처럼 밝고 화사한 색"),
                    ("봄 브라이트", "새콤달콤한 귤처럼 쨍하고 생생한 색"),
                    ("가을 뮤트", "부드러운 모래나 나무처럼 차분하고 편안한 색"),
                    ("가을 딥", "진한 초콜릿이나 단풍잎처럼 깊고 어두운 색")
                ]
                for res_color, desc in warm_opts:
                    render_pc_option(res_color, desc)

            # 쿨톤 질문 노출
            if has_cool:
                if has_warm: st.markdown("---") # 구분선
                st.markdown("#### [쿨(Cool) 느낌이 있다면?]")
                cool_opts = [
                    ("여름 라이트", "시원한 딸기 우유처럼 맑고 연한 색"),
                    ("여름 뮤트", "구름 낀 하늘처럼 은은하고 회색빛이 섞인 색"),
                    ("겨울 브라이트", "형광펜처럼 눈에 확 띄고 아주 진한 색"),
                    ("겨울 딥", "캄캄한 밤하늘처럼 아주 어둡고 묵직한 색")
                ]
                for res_color, desc in cool_opts:
                    render_pc_option(res_color, desc)
        
        if st.button("↩️ 진단 취소", type="secondary"):
            st.session_state.pc_diagnosis_active = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Quiz Trigger
    if st.session_state.gender and st.session_state.personal_color:
        st.markdown('<div style="height:60px;"></div><h2 class="section-title">취향 퀴즈</h2>', unsafe_allow_html=True)
        if st.session_state.quiz_step < len(questions):
            q = questions[st.session_state.quiz_step]
            st.markdown(f"### {q['question']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div class="custom-card" style="height:120px; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:1.1rem; font-weight:700; color:var(--gold);">{q['A']['label']}</div>
                        <div style="font-size:0.85rem; color:#bbb; margin-top:5px;">{q['A']['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("선택 A", key=f"qa_{st.session_state.quiz_step}", use_container_width=True):
                    st.session_state.quiz_answers.extend(q['A']['scores'])
                    st.session_state.quiz_step += 1
                    st.rerun()
            with c2:
                st.markdown(f"""
                    <div class="custom-card" style="height:120px; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:1.1rem; font-weight:700; color:var(--gold);">{q['B']['label']}</div>
                        <div style="font-size:0.85rem; color:#bbb; margin-top:5px;">{q['B']['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("선택 B", key=f"qb_{st.session_state.quiz_step}", use_container_width=True):
                    st.session_state.quiz_answers.extend(q['B']['scores'])
                    st.session_state.quiz_step += 1
                    st.rerun()
        else:
            if st.button("분석 결과 확인 ✨", type="primary", use_container_width=True):
                with st.spinner("스타일 분석 중..."):
                    # 점수 계산
                    from collections import Counter
                    counts = Counter(st.session_state.quiz_answers)
                    
                    # 핏 점수 분리
                    fit_types = ["타이트/노멀 핏", "루즈/오버 핏"]
                    style_counts = {k: v for k, v in counts.items() if k not in fit_types}
                    fit_counts = {k: v for k, v in counts.items() if k in fit_types}
                    
                    # Top 3 스타일 선정
                    sorted_styles = sorted(style_counts.items(), key=lambda item: item[1], reverse=True)
                    top_styles = [s for s, c in sorted_styles[:3]]
                    st.session_state.top_1_style = top_styles[0] if top_styles else "캐주얼"
                    
                    # 선호 핏 선정
                    preferred_fit = max(fit_counts.items(), key=lambda item: item[1])[0] if fit_counts else "노멀 핏"
                    
                    final_quiz_summary = {
                        "top_styles": top_styles,
                        "preferred_fit": preferred_fit
                    }
                    
                    # 현재 퍼스널 컬러에 맞는 무신사 및 지그재그 컬러 리스트 추출
                    guide = color_guide_data.get(st.session_state.personal_color, color_guide_data["모르겠어요"])
                    m_colors = guide.get("musinsa", [])
                    z_colors = guide.get("zigzag", [])
                    
                    res = analyze_fashion_style(None, st.session_state.gender, st.session_state.personal_color, final_quiz_summary, m_colors, z_colors)
                    st.session_state.analysis_result = res
                    st.balloons()
                    st.rerun()

else:
    # --- 결과 페이지 최상단 강제 고정 스크립트 ---
    top_anchor = st.empty()
    top_anchor.markdown('<div id="result-top"></div>', unsafe_allow_html=True)
    st.components.v1.html(
        """
        <script>
            var mainContainer = window.parent.document.querySelector('section.main');
            if (mainContainer) {
                mainContainer.scrollTo({ top: 0, behavior: 'instant' });
            }
            // 대체 방법: 요소 기준 스크롤
            var topElement = window.parent.document.getElementById('result-top');
            if (topElement) {
                topElement.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        </script>
        """,
        height=0
    )
    
    # Results UI
    res = st.session_state.analysis_result
    if "error" in res:
        st.error(res["error"])
        if st.button("다시 시도"): st.session_state.analysis_result = None; st.rerun()
    else:
        st.markdown(f'<div style="padding:2rem; border-radius:20px; border:1px solid var(--gold); text-align:center; margin-bottom:2rem;"><h1 style="color:var(--gold)!important;">"{res["persona_name"]}"</h1><p>{res["persona_description"]}</p></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="custom-card"><h4>💡 스타일 팁</h4><p style="font-size:0.9rem;">{res["styling_tip"]}</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="custom-card" style="background:var(--gold-soft);"><h4>🎨 포인트 컬러</h4><p style="font-size:0.9rem; white-space: pre-wrap;">{res["point_color"]}</p></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:40px;"></div><h3 style="margin-bottom:1rem;">🛒 쇼핑 큐레이션</h3>', unsafe_allow_html=True)
        
        # 성별에 따른 카테고리 필터링 (남성일 때 원피스, 스커트 제외)
        cat_labels = ["상의", "팬츠", "아우터", "니트/카디건"]
        if st.session_state.gender == "여성":
            cat_labels += ["원피스", "스커트"]
            
        cloth_cols = st.columns(len(cat_labels))
        for i, item in enumerate(cat_labels):
            if cloth_cols[i].button(item, type="primary" if item == st.session_state.final_clothing else "secondary", use_container_width=True, key=f"cat_btn_{item}"):
                st.session_state.final_clothing = item
                # 카테고리 변경 시 미리보기 초기화
                st.session_state.m_previews = None
                st.session_state.z_previews = None
                st.rerun()
        
        guide = color_guide_data.get(st.session_state.personal_color, color_guide_data["모르겠어요"])
        selected_clothing = st.session_state.final_clothing
        
        # 지능형 핏 추천 로직
        top_style = st.session_state.top_1_style
        target_fits = STYLE_FIT_MAP.get(top_style, [])
        possible_fits = ZIGZAG_MASTER_MAP.get(selected_clothing, {"fits": ["기본핏"]})["fits"]
        valid_fits = [f for f in possible_fits if any(tf in f for tf in target_fits)]
        fit_options = valid_fits if valid_fits else possible_fits

        # --- [1] 핏/컬러 통합 설정 영역 ---
        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
        
        # 성별에 따른 레이아웃 분기 (남성일 경우 중앙에 하나만 배치)
        if st.session_state.gender == "여성":
            set_c1, set_c2 = st.columns(2)
            with set_c1:
                st.markdown('<div style="text-align: center;"><h5>👔 무신사 검색 설정</h5></div>', unsafe_allow_html=True)
                m_set_fit, m_set_clr = st.columns(2)
                sel_m_fit = m_set_fit.selectbox("핏", fit_options, key=f"m_sel_fit_{selected_clothing}")
                sel_m_clr = m_set_clr.selectbox("컬러", guide['musinsa'], key=f"m_sel_clr_{selected_clothing}")
                m_query = f"{sel_m_fit} {sel_m_clr} {st.session_state.gender} {selected_clothing}".strip()
            with set_c2:
                st.markdown('<div style="text-align: center;"><h5>👗 지그재그 검색 설정</h5></div>', unsafe_allow_html=True)
                z_set_fit, z_set_clr = st.columns(2)
                sel_z_fit = z_set_fit.selectbox("핏", fit_options, key=f"z_sel_fit_{selected_clothing}")
                sel_z_clr = z_set_clr.selectbox("컬러", guide['zigzag'], key=f"z_sel_clr_{selected_clothing}")
                z_query = f"{sel_z_fit} {sel_z_clr} {st.session_state.gender} {selected_clothing}".strip()
        else:
            # 남성일 경우 중앙 정렬 레이아웃 적용
            _, mid_c, _ = st.columns([1, 2, 1])
            with mid_c:
                st.markdown('<div style="text-align: center;"><h5>👔 무신사 검색 설정</h5></div>', unsafe_allow_html=True)
                m_set_fit, m_set_clr = st.columns(2)
                sel_m_fit = m_set_fit.selectbox("핏", fit_options, key=f"m_sel_fit_{selected_clothing}")
                sel_m_clr = m_set_clr.selectbox("컬러", guide['musinsa'], key=f"m_sel_clr_{selected_clothing}")
                m_query = f"{sel_m_fit} {sel_m_clr} {st.session_state.gender} {selected_clothing}".strip()
                z_query = None

        # --- [2] 통합 실시간 미리보기 버튼 ---
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        if st.button(f"⚡ 현재 선택한 조건으로 인기 상품 미리보기", key="unified_preview_btn", use_container_width=True):
            with st.spinner("상품 정보를 실시간으로 수집 중입니다..."):
                m_gender = 'M' if st.session_state.gender == '남성' else 'F'
                st.session_state.m_previews = get_musinsa_previews(m_query, gender=m_gender, top_n=5)
                if z_query:
                    st.session_state.z_previews = get_zigzag_previews(z_query, top_n=5)
            st.rerun()

        # --- [3] 결과 출력 영역 (성별 맞춤 레이아웃) ---
        if st.session_state.gender == "여성":
            res_main_c1, res_main_c2 = st.columns(2)
            
            # 여성: 무신사 (왼쪽)
            with res_main_c1:
                if st.session_state.m_previews:
                    st.markdown(f'<div style="text-align: center; margin-top: 1rem;"><h4>🛍️ 무신사 Pick: {m_query}</h4></div>', unsafe_allow_html=True)
                    for idx, item in enumerate(st.session_state.m_previews):
                        st.markdown(f"""
                            <a href="{item.get('link', '#')}" target="_blank" style="text-decoration:none; color:inherit;">
                                <div class="custom-card" style="padding:1rem; margin-bottom:10px; display:flex; align-items:center; cursor:pointer;">
                                    <img src="{item['img']}" style="width:80px; height:100px; border-radius:6px; object-fit: cover; margin-right:15px;">
                                    <div style="flex:1; text-align:left;">
                                        <div style="font-weight:700; color:var(--gold); font-size:0.7rem;">{item['mall']}</div>
                                        <div style="font-size:0.85rem; margin:2px 0; height:40px; overflow:hidden;">{item['title']}</div>
                                        <div style="font-weight:900; font-size:1rem;">{item['price']}원</div>
                                    </div>
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                    m_url = f"https://www.musinsa.com/search/goods?keyword={urllib.parse.quote_plus(m_query)}&gf=F"
                    st.link_button(f"무신사 전체 결과 보기", m_url, use_container_width=True)

            # 여성: 지그재그 (오른쪽)
            with res_main_c2:
                if st.session_state.z_previews:
                    st.markdown(f'<div style="text-align: center; margin-top: 1rem;"><h4>🛍️ 지그재그 Pick: {z_query}</h4></div>', unsafe_allow_html=True)
                    for idx, item in enumerate(st.session_state.z_previews):
                        st.markdown(f"""
                            <a href="{item.get('link', '#')}" target="_blank" style="text-decoration:none; color:inherit;">
                                <div class="custom-card" style="padding:1rem; margin-bottom:10px; display:flex; align-items:center; cursor:pointer;">
                                    <img src="{item['img']}" style="width:80px; height:100px; border-radius:8px; object-fit: cover; margin-right:15px;">
                                    <div style="flex:1; text-align:left;">
                                        <div style="font-weight:700; color:var(--gold); font-size:0.7rem;">{item['mall']}</div>
                                        <div style="font-size:0.85rem; margin:2px 0; height:40px; overflow:hidden;">{item['title']}</div>
                                        <div style="font-weight:900; font-size:1rem;">{item['price']}</div>
                                    </div>
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                    z_url = f"https://zigzag.kr/search?keyword={urllib.parse.quote_plus(z_query)}"
                    st.link_button(f"지그재그 전체 결과 보기", z_url, use_container_width=True)
        else:
            # 남성: 무신사만 중앙에 크게 배치
            if st.session_state.m_previews:
                _, mid_res, _ = st.columns([1, 2, 1])
                with mid_res:
                    st.markdown(f'<div style="text-align: center; margin-top: 1rem;"><h4>🛍️ 무신사 Pick: {m_query}</h4></div>', unsafe_allow_html=True)
                    for idx, item in enumerate(st.session_state.m_previews):
                        st.markdown(f"""
                            <a href="{item.get('link', '#')}" target="_blank" style="text-decoration:none; color:inherit;">
                                <div class="custom-card" style="padding:1rem; margin-bottom:10px; display:flex; align-items:center; cursor:pointer;">
                                    <img src="{item['img']}" style="width:80px; height:100px; border-radius:6px; object-fit: cover; margin-right:15px;">
                                    <div style="flex:1; text-align:left;">
                                        <div style="font-weight:700; color:var(--gold); font-size:0.7rem;">{item['mall']}</div>
                                        <div style="font-size:0.85rem; margin:2px 0; height:40px; overflow:hidden;">{item['title']}</div>
                                        <div style="font-weight:900; font-size:1rem;">{item['price']}원</div>
                                    </div>
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                    m_url = f"https://www.musinsa.com/search/goods?keyword={urllib.parse.quote_plus(m_query)}&gf=M"
                    st.link_button(f"무신사 전체 결과 보기", m_url, use_container_width=True)

        st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
        if st.button("🔄 처음부터 다시 하기", key="reset_analysis_final_btn", use_container_width=True, type="primary"):
            # 미리보기 데이터까지 모두 초기화
            st.session_state.analysis_result = None
            st.session_state.quiz_step = 0
            st.session_state.quiz_answers = []
            st.session_state.m_previews = None
            st.session_state.z_previews = None
            st.rerun()

# ── Summary Bar ──
st.markdown(f"""
    <div class="summary-bar">
        <div style="display:flex;">
            <div class="s-pill {'filled' if st.session_state.gender else ''}">{st.session_state.gender or '성별'}</div>
            <div class="s-pill {'filled' if st.session_state.personal_color else ''}">{st.session_state.personal_color or '컬러'}</div>
        </div>
        <div style="color:#555; font-size:0.7rem; font-weight:700;">MAPSI-TI v1.1</div>
    </div>
    <div style="height:100px;"></div>
""", unsafe_allow_html=True)
