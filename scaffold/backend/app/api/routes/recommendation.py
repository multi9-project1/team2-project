from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict
from app.schemas.recommendation import RecommendationQueryRequest, ProfileAnalysisRequest
from app.services.recommendation_service import (
    generate_dataset_recommendation_response,
    create_profile_response_payload
)
from app.logic.survey_parser import create_survey_profile

router = APIRouter()

@router.post("/profile")
def analyze_profile(request: ProfileAnalysisRequest) -> Dict[str, Any]:
    try:
        user_profile = create_survey_profile(request.survey.model_dump()).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    response = create_profile_response_payload(user_profile)
    response["meta"] = {
        "includes_dataset_recommendations": False,
        "recommended_usage": "service-fast-path",
    }
    return response

@router.post("/recommendations")
def get_recommendation_summary_text(request: RecommendationQueryRequest) -> Dict[str, Any]:
    try:
        result = generate_dataset_recommendation_response(request, "http://127.0.0.1:8000/")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    return {"text": result["preference_analysis"]["text"]}