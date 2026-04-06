from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.services.recommendation_service import DEFAULT_DATASET_DIR

app = FastAPI(title="Fashion Recommendation API", version="0.1.0")

# 정적 파일 서빙 (갤러리나 샘플 이미지 제공 시 필요)
app.mount("/sample-files", StaticFiles(directory=str(DEFAULT_DATASET_DIR), check_dir=False), name="sample-files")

# 통합 라우터 등록
app.include_router(api_router)

@app.get("/health")
def get_health_status() -> dict[str, str]:
    return {"status": "ok"}