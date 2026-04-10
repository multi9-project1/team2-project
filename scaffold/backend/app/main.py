from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

try:
    from app.logic.fashion_config import DATASET_STYLE_GROUP_LABELS, DATASET_STYLE_LABELS, STYLE_LABELS, TPO_OPTION_TO_DEEPLINK_KEYWORD
    from app.logic.item_feature_builder import ensure_dataset_archive_extracted, load_dataset_item_records
    from app.logic.recommender import (
        collect_top_similarity_matches,
        derive_style_profile_from_similarity_matches,
        filter_image_available_items,
        filter_items_by_user_gender,
        find_highest_similarity_item_match,
        rank_recommendation_candidates,
    )
    from app.logic.survey_parser import collect_style_search_keywords, create_survey_profile
except ImportError:
    from fashion_config import DATASET_STYLE_GROUP_LABELS, DATASET_STYLE_LABELS, STYLE_LABELS, TPO_OPTION_TO_DEEPLINK_KEYWORD
    from item_feature_builder import ensure_dataset_archive_extracted, load_dataset_item_records
    from recommender import (
        collect_top_similarity_matches,
        derive_style_profile_from_similarity_matches,
        filter_image_available_items,
        filter_items_by_user_gender,
        find_highest_similarity_item_match,
        rank_recommendation_candidates,
    )
    from survey_parser import collect_style_search_keywords, create_survey_profile

app = FastAPI(title="Fashion Recommendation API", version="0.1.0")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET_CSV_CANDIDATES = [
    PROJECT_ROOT / "fashion_data.csv",
    PROJECT_ROOT / "logic" / "fashion_data.csv",
]
DEFAULT_SAMPLE_ZIP = PROJECT_ROOT / "Sample.zip"
LEGACY_SAMPLE_DATASET_DIR = PROJECT_ROOT / "sample_data"
app.mount("/sample-files", StaticFiles(directory=str(LEGACY_SAMPLE_DATASET_DIR), check_dir=False), name="sample-files")
FRONTEND_DIR = (PROJECT_ROOT.parent.parent / "frontend").resolve()
INDEX_HTML_PATH = FRONTEND_DIR / "index.html"
SURVEY_HTML_PATH = FRONTEND_DIR / "survey.html"
RESULT_HTML_PATH = FRONTEND_DIR / "result.html"

class SurveyInputModel(BaseModel):
    model_config = ConfigDict(extra='allow') # 정해지지 않은 필드도 모두 허용
    gender: Optional[str] = "W"
    personal_color: Optional[str] = "unknown"
    Qstyle_1: Optional[str] = "A"
    Qstyle_2: Optional[str] = "A"
    Qstyle_3: Optional[str] = "A"
    Qstyle_4: Optional[str] = "A"
    Qstyle_5: Optional[str] = "A"
    Qstyle_6: Optional[str] = "A"
    Qstyle_7: Optional[str] = "A"
    Qstyle_8: Optional[str] = "A"
    Qstyle_9: Optional[str] = "A"

# ... (기타 모델 및 함수들 유지) ...
class RecommendationQueryRequest(BaseModel):
    survey: SurveyInputModel
    top_n: int = Field(default=5, ge=1, le=20)
    zip_path: Optional[str] = None
    extract_dir: Optional[str] = None
    dataset_dir: Optional[str] = None
    allow_mock_data: bool = True
    prefer_extracted_dataset: bool = True

class ProfileAnalysisRequest(BaseModel):
    survey: SurveyInputModel

class CrawlQueryRequest(BaseModel):
    survey: SurveyInputModel
    category_name: str = "상의"
    selected_color: Optional[str] = None
    dataset_dir: Optional[str] = None
    allow_mock_data: bool = True
    top_n: int = Field(default=3, ge=1, le=10)

def create_deeplink_context(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "gender": user_profile["gender"],
        "personal_color_code": user_profile["personal_color"],
        "personal_color_display": user_profile["personal_color_display"],
        "representative_colors": user_profile["representative_colors"],
        "color_search_keywords": user_profile["color_search_keywords"],
        "primary_style_code": user_profile["primary_style"],
        "primary_style_display": user_profile["style_display"].get(user_profile["primary_style"], user_profile["primary_style"]),
        "secondary_style_codes": user_profile["secondary_styles"],
        "style_search_keywords": user_profile["style_search_keywords"],
        "fit_preference": user_profile["fit_preference"],
        "tpo_keyword": TPO_OPTION_TO_DEEPLINK_KEYWORD.get(user_profile.get("tpo_preference", ""), ""),
        "musinsa_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
        "zigzag_search_keywords": user_profile["color_search_keywords"] + user_profile["style_search_keywords"],
    }

def create_profile_response_payload(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    # 스타일 ID를 한글 라벨로 변환하여 프론트엔드가 PERSONAS 객체에서 정확히 찾을 수 있게 함
    style_id = user_profile.get("primary_style")
    if style_id in STYLE_LABELS:
        user_profile["primary_style"] = STYLE_LABELS[style_id]
    
    return {
        "user_profile": user_profile,
        "deeplink_context": create_deeplink_context(user_profile),
    }

def resolve_default_dataset_csv_path() -> Path:
    for candidate_path in DEFAULT_DATASET_CSV_CANDIDATES:
        if candidate_path.exists():
            return candidate_path
    return DEFAULT_DATASET_CSV_CANDIDATES[0]

def resolve_dataset_style_group_label(style_code: str) -> str:
    return DATASET_STYLE_GROUP_LABELS.get(style_code.lower(), "기타 스타일")

def resolve_dataset_input_paths(request: RecommendationQueryRequest) -> tuple[Optional[str], Optional[str], Optional[str]]:
    zip_path = request.zip_path
    extract_dir = request.extract_dir
    dataset_dir = request.dataset_dir
    default_dataset_csv_path = resolve_default_dataset_csv_path()
    if not dataset_dir and default_dataset_csv_path.exists():
        dataset_dir = str(default_dataset_csv_path)
    if not zip_path and DEFAULT_SAMPLE_ZIP.exists():
        zip_path = str(DEFAULT_SAMPLE_ZIP)
    if not extract_dir and zip_path:
        extract_dir = str(LEGACY_SAMPLE_DATASET_DIR)
    return zip_path, extract_dir, dataset_dir

def build_static_image_url(image_path: str, dataset_dir: Optional[str]) -> Optional[str]:
    if not image_path or not dataset_dir: return None
    dataset_root = Path(dataset_dir).resolve()
    if not dataset_root.is_dir(): return None
    candidate = Path(image_path)
    if not candidate.is_absolute():
        abs_candidate = (PROJECT_ROOT / image_path).resolve()
        if abs_candidate.exists(): candidate = abs_candidate
        else:
            filename = candidate.name
            found_files = list(dataset_root.rglob(filename))
            if found_files: candidate = found_files[0]
            else: return None
    try: relative_path = candidate.relative_to(dataset_root)
    except ValueError: return None
    return f"/sample-files/{relative_path.as_posix()}"

def attach_recommendation_image_urls(recommendations: List[Dict[str, Any]], dataset_dir: Optional[str], base_url: str) -> List[Dict[str, Any]]:
    for item in recommendations:
        relative_url = build_static_image_url(str(item.get("image_path", "")), dataset_dir)
        item["image_url"] = relative_url
        item["image_full_url"] = f"{base_url.rstrip('/')}{relative_url}" if relative_url else None
    return recommendations

def generate_dataset_recommendation_response(request: RecommendationQueryRequest, base_url: str) -> Dict[str, Any]:
    user_profile = create_survey_profile(request.survey.model_dump()).to_dict()
    zip_path, extract_dir, dataset_dir = resolve_dataset_input_paths(request)
    if request.prefer_extracted_dataset and zip_path and extract_dir:
        extracted_path = ensure_dataset_archive_extracted(zip_path, extract_dir)
        dataset_dir = str(extracted_path)
    dataset_items = load_dataset_item_records(zip_path=zip_path, extract_dir=extract_dir, dataset_dir=dataset_dir, allow_mock=request.allow_mock_data)
    gender_filtered_items = filter_items_by_user_gender(dataset_items, user_profile["gender"])
    image_ready_items = filter_image_available_items(gender_filtered_items)
    candidate_items = image_ready_items or gender_filtered_items or dataset_items
    top_similarity_matches = collect_top_similarity_matches(user_profile, gender_filtered_items or dataset_items, top_k=20)
    inferred_style_profile = derive_style_profile_from_similarity_matches(top_similarity_matches)
    if inferred_style_profile.get("primary_style_code"):
        ps = inferred_style_profile["primary_style_code"]
        ss = inferred_style_profile["secondary_style_codes"]
        user_profile["primary_style"] = ps
        user_profile["secondary_styles"] = ss
        user_profile["style_display"] = {ps: STYLE_LABELS.get(ps, ps)}
        user_profile["style_search_keywords"] = collect_style_search_keywords(ps, ss)
    top_match = find_highest_similarity_item_match(user_profile, gender_filtered_items or dataset_items)
    recommendations = attach_recommendation_image_urls(rank_recommendation_candidates(user_profile, candidate_items, top_n=request.top_n), dataset_dir, base_url)
    response = create_profile_response_payload(user_profile)
    response["recommendation_results"] = recommendations
    response["preference_analysis"] = {
        "era": top_match["era"], "style": inferred_style_profile["primary_group"], "similarity_percent": top_match["similarity_percent"],
        "text": f"알고리즘 분석 결과, 당신의 취향은 **[{top_match['era']}년대]**의 **[{inferred_style_profile['primary_group']}]**과 {top_match['similarity_percent']}% 일치합니다",
    }
    return response

@app.get("/health")
def get_health_status() -> Dict[str, str]: return {"status": "ok"}


@app.get("/", include_in_schema=False)
def serve_index_page() -> FileResponse:
    return FileResponse(INDEX_HTML_PATH)


@app.get("/survey", include_in_schema=False)
def serve_survey_page() -> FileResponse:
    return FileResponse(SURVEY_HTML_PATH)


@app.get("/result", include_in_schema=False)
def serve_result_page() -> FileResponse:
    return FileResponse(RESULT_HTML_PATH)

@app.post("/profile")
def analyze_profile(request: ProfileAnalysisRequest) -> Dict[str, Any]:
    try:
        user_profile = create_survey_profile(request.survey.model_dump()).to_dict()
        return create_profile_response_payload(user_profile)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/recommendations")
def get_recommendation_summary_text(request: RecommendationQueryRequest) -> Dict[str, Any]:
    try:
        result = generate_dataset_recommendation_response(request, "http://127.0.0.1:8000/")
        return {
            "text": result["preference_analysis"]["text"],
            "recommendations": result.get("recommendation_results", []),
            "user_profile": result.get("user_profile", {}),
            "preference_analysis": result.get("preference_analysis", {}),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/crawl/musinsa")
def crawl_musinsa_products(request: CrawlQueryRequest) -> Dict[str, Any]:
    from app.crawlers.musinsa_crl import recommend_outfit_from_survey
    from app.services.ai_similarity_service import apply_ai_scoring_to_items_parallel
    
    # 1. 1차 후보군 수집 (넉넉하게 20개)
    crawl_result = recommend_outfit_from_survey(request.survey.model_dump(), request.category_name, selected_color=request.selected_color, top_n=20)
    
    # 2. 실시간 AI 스타일 유사도 정밀 분석 (병렬 처리)
    if crawl_result.get("items"):
        style_ko = crawl_result.get("profile", {}).get("mapsiti", "캐주얼")
        # 20개를 분석하여 점수순 정렬
        scored_items = apply_ai_scoring_to_items_parallel(crawl_result["items"], style_ko)
        # 최종적으로 상위 N개(요청된 top_n)만 반환
        crawl_result["items"] = scored_items[:request.top_n]
        
    return crawl_result

@app.post("/crawl/zigzag")
def crawl_zigzag_products(request: CrawlQueryRequest) -> Dict[str, Any]:
    from app.crawlers.zigzag_crl import get_zigzag_recommendations_from_survey
    from app.services.ai_similarity_service import apply_ai_scoring_to_items_parallel
    
    # 1. 1차 후보군 수집 (넉넉하게 20개)
    crawl_result = get_zigzag_recommendations_from_survey(request.survey.model_dump(), request.category_name, selected_color=request.selected_color, top_n=20)
    
    # 2. 실시간 AI 스타일 유사도 정밀 분석 (병렬 처리)
    if crawl_result.get("items"):
        style_ko = crawl_result.get("profile", {}).get("inferred_style_profile", {}).get("primary_group", "캐주얼")
        # 20개를 분석하여 점수순 정렬
        scored_items = apply_ai_scoring_to_items_parallel(crawl_result["items"], style_ko)
        # 최종적으로 상위 N개(요청된 top_n)만 반환
        crawl_result["items"] = scored_items[:request.top_n]
        
    return crawl_result

# 프론트엔드 정적 파일 서빙
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    # 경로를 못 찾을 경우를 대비해 디버깅용 메시지 출력
    print(f"Warning: FRONTEND_DIR not found at {FRONTEND_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

