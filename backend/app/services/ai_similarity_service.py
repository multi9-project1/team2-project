import base64
import requests
import re
import concurrent.futures
from typing import List, Dict, Any, Optional
import math

# AI 서버 설정
AI_API_BASE_URL = "http://ailon.iptime.org:53000"
PREDICT_ENDPOINT = f"{AI_API_BASE_URL}/predict"

# 스타일 매핑
STYLE_MAP = {
    "캐주얼": "casual fashion",
    "스트리트": "streetwear fashion",
    "오피스/소피스티케이티드": "office wear fashion",
    "페미닌": "feminine fashion",
    "매니시": "mannish fashion",
    "스포티": "sporty fashion",
    "모던/미니멀": "modern minimal fashion",
    "로맨틱": "romantic fashion",
    "힙스터/펑크": "hipster fashion",
    "레트로/빈티지": "retro fashion"
}

def get_ai_similarity_score(image_url: str, target_style_ko: str) -> float:
    """단일 이미지 분석 (순수 점수 반환)"""
    try:
        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if response.status_code != 200: return 0.0
        
        image_b64 = base64.b64encode(response.content).decode("utf-8")
        target_label = STYLE_MAP.get(target_style_ko, "casual fashion")
        
        api_res = requests.post(PREDICT_ENDPOINT, json={
            "image_b64": image_b64,
            "candidate_labels": list(STYLE_MAP.values())
        }, timeout=10)
        
        if api_res.status_code == 200:
            raw_score = api_res.json().get("scores", {}).get(target_label, 0.0)
            return round(float(raw_score), 4)
    except Exception:
        pass
    return 0.0

def apply_ai_scoring_to_items_parallel(items: List[Dict[str, Any]], target_style_ko: str) -> List[Dict[str, Any]]:
    """여러 상품을 병렬(Thread)로 분석하여 속도 최적화"""
    if not items: return items
    
    # 최대 20개까지만 분석 (속도와 품질의 타협점)
    target_items = items[:20]
    print(f"    🧠 AI가 {len(target_items)}개 상품을 병렬 분석 중...")

    def process_item(item):
        img_url = item.get("img_url") or item.get("image_url")
        if img_url:
            score = get_ai_similarity_score(img_url, target_style_ko)
            item["ai_score"] = score
            item["ai_score_percent"] = int(score * 100)
        else:
            item["ai_score"] = 0.0
            item["ai_score_percent"] = 0
        return item

    # 쓰레드 풀을 사용하여 병렬 요청 (AI 서버 성능에 따라 조절 가능)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(process_item, target_items))

    # AI 점수 순으로 재정렬
    target_items.sort(key=lambda x: x.get("ai_score", 0.0), reverse=True)
    return target_items
