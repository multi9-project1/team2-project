from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.survey import SurveyInputModel

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