import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

def universal_scraper():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options, version_main=146)
    
    print("\n[지그재그 역추적 크롤링]")
    try:
        driver.get("https://zigzag.kr/search?keyword=원피스")
        time.sleep(5)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(1)
            
        soup = BeautifulSoup(driver.page_source, "html.parser")
        images = soup.find_all("img")
        count = 0
        for img in images:
            src = img.get("src") or img.get("data-src") or ""
            if not src or "data:" in src or "icon" in src.lower() or "logo" in src.lower(): 
                continue
                
            # 사진 부모를 타고 올라가며 텍스트 찾기
            parent = img.parent
            text = ""
            for _ in range(5):
                text = parent.get_text(separator=" | ", strip=True)
                # 텍스트가 존재하고, 가격 정보(숫자)가 포함되어 있으면 정답 박스
                if len(text) > 10 and any(c.isdigit() for c in text):
                    break
                parent = parent.parent
                if not parent: break
                
            if len(text) > 10 and any(c.isdigit() for c in text):
                print(f"  [발견] {text}\n  [사진] {src}\n")
                count += 1
            if count >= 3: break
    except Exception as e:
        print(e)

    print("\n[무신사 역추적 크롤링]")
    try:
        driver.get("https://www.musinsa.com/categories/item/001?gf=W&sortCode=SALE_ONE_WEEK_COUNT")
        time.sleep(5)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(1)
            
        soup = BeautifulSoup(driver.page_source, "html.parser")
        images = soup.find_all("img")
        count = 0
        for img in images:
            src = img.get("data-original") or img.get("src") or ""
            if not src or "data:" in src or "thumb" not in src: 
                continue
                
            parent = img.parent
            text = ""
            for _ in range(5):
                text = parent.get_text(separator=" | ", strip=True)
                if len(text) > 10 and any(c.isdigit() for c in text):
                    break
                parent = parent.parent
                if not parent: break
                
            if len(text) > 10 and any(c.isdigit() for c in text):
                print(f"  [발견] {text}\n  [사진] {src}\n")
                count += 1
            if count >= 3: break
    except Exception as e:
        print(e)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    universal_scraper()
