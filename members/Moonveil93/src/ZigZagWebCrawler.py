# 지그재그 인기순 TOP 5 상품 크롤링 코드
import time
from urllib.parse import urlparse, parse_qs 
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def crawl_zigzag_store(url, category):
    print(f"\n[{category}] 인기순 첫 화면 상위 5개 데이터 수집을 준비 중입니다...")
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    
    driver = uc.Chrome(options=options, version_main=146)
    
    print("페이지 접속 중...")
    driver.get(url)
    
    # 💡 첫 화면의 상품 이미지와 데이터가 온전히 뜰 때까지 조금 넉넉히 기다립니다.
    time.sleep(6) 

    # 💡 [핵심 수정] 스크롤을 내리는 코드를 아예 삭제했습니다! 
    # 접속하자마자 보이는 맨 위쪽 상품부터 바로 긁어오기 시작합니다.
    print("스크롤 없이 맨 위 데이터 추출을 시작합니다.")
    products = driver.find_elements(By.CSS_SELECTOR, ".product-card") 
    
    scraped_data = []
    if not products:
        print("❗ 주의: 상품을 찾을 수 없습니다. 클래스명을 다시 확인하세요.")
        
    for product in products:
        # 정확히 5개가 모이면 즉시 종료!
        if len(scraped_data) == 5:
            break
            
        try:
            mall_name = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomr8").text
            title = product.find_element(By.CSS_SELECTOR, ".zds4_1kdomrc").text
            price = product.find_element(By.CSS_SELECTOR, ".zds4_1jsf80i3").text
            
            img_element = product.find_element(By.CSS_SELECTOR, ".product-card-thumbnail img")
            img_url = img_element.get_attribute("src")
            
            scraped_data.append({
                "category": category, 
                "mall_name": mall_name, 
                "title": title, 
                "price": price,
                "img_url": img_url 
            })
        except Exception as e:
            continue

    print("브라우저를 종료합니다.")
    driver.quit()

    return scraped_data

# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    # URL에 '&order=SCORE_DESC'(인기순)이 잘 붙어있습니다!
    TARGET_URL = "https://zigzag.kr/search?keyword=%EB%A0%88%EB%93%9C%20%EC%83%81%EC%9D%98%20%ED%95%98%EC%9D%98&order=SCORE_DESC" 
    
    parsed_url = urlparse(TARGET_URL)
    query_dict = parse_qs(parsed_url.query)
    
    if 'keyword' in query_dict:
        TARGET_CATEGORY = query_dict['keyword'][0] 
    else:
        TARGET_CATEGORY = "알 수 없음" 
        
    results = crawl_zigzag_store(TARGET_URL, TARGET_CATEGORY)
    
    print("\n==================================")
    print(f" 🔥 [{TARGET_CATEGORY}] 첫 화면 인기순 TOP 5 🔥")
    print("==================================")

    for idx, item in enumerate(results, 1): 
        print(f"{idx}위. [{item['mall_name']}] {item['title']} - {item['price']}원")
        print(f"    🔗 이미지 링크: {item['img_url']}\n")
