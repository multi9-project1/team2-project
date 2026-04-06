from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

# ============================================================
# Configuration
# ============================================================
# Supported file formats: .csv, .parquet
# You can override this with an environment variable.
DATA_PATH = os.getenv("FASHION_DATA_PATH", "./data/fashion_items.parquet")
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "5"))

# ============================================================
# Notebook-derived constants
# ============================================================
WARM_COLOR_MAP = {
    "A": "spring_light",
    "B": "spring_bright",
    "C": "autumn_muted",
    "D": "autumn_deep",
}

COOL_COLOR_MAP = {
    "A": "summer_light",
    "B": "summer_muted",
    "C": "winter_bright",
    "D": "winter_deep",
}

VALID_PERSONAL_COLORS = set(WARM_COLOR_MAP.values()) | set(COOL_COLOR_MAP.values()) | {
    "spring_warm",
    "summer_cool",
    "autumn_warm",
    "winter_cool",
    "unknown",
}

STYLE_CATEGORIES = [
    "sophisticated",
    "modern_minimal",
    "feminine",
    "mannish",
    "casual",
    "romantic",
    "street",
    "sporty",
    "hipster_punk",
    "retro",
]

STYLE_SCORE_MAP = {
    "qstyle_1": {
        "A": ["sophisticated", "modern_minimal", "feminine", "mannish"],
        "B": ["casual", "romantic", "street", "sporty", "hipster_punk", "retro"],
    },
    "qstyle_3": {
        "A": ["feminine", "sophisticated", "hipster_punk", "romantic"],
        "B": ["casual", "street", "sporty", "mannish", "retro"],
    },
    "qstyle_4": {
        "A": ["modern_minimal", "casual", "mannish", "sophisticated"],
        "B": ["hipster_punk", "retro", "street", "romantic"],
    },
    "qstyle_5": {
        "A": ["romantic", "feminine", "sophisticated", "modern_minimal", "retro"],
        "B": ["sporty", "casual", "street", "hipster_punk", "mannish"],
    },
    "qstyle_6": {
        "A": ["mannish", "modern_minimal", "sophisticated", "street"],
        "B": ["romantic", "retro", "feminine", "casual"],
    },
}

STYLE_FEATURE_MAP = {
    "sophisticated": ["item.survey.Q4202", "item.survey.Q4204"],
    "feminine": ["item.survey.Q4214", "item.survey.Q4216"],
    "hipster_punk": ["item.survey.Q4209", "item.survey.Q4206", "item.survey.Q4207"],
    "casual": ["item.survey.Q4210", "item.survey.Q4212"],
    "modern_minimal": ["item.survey.Q4205", "item.survey.Q4208"],
    "romantic": ["item.survey.Q4213", "item.survey.Q4216"],
    "mannish": ["item.survey.Q4215", "item.survey.Q4202"],
    "street": ["item.survey.Q4207", "item.survey.Q4203"],
    "sporty": ["item.survey.Q4211", "item.survey.Q4212"],
    "retro": ["item.survey.Q4207", "item.survey.Q412"],
}

Q42_FEATURE_COLUMNS = [f"item.survey.Q42{str(i).zfill(2)}" for i in range(1, 17)]
USER_FEATURE_COLUMNS = ["item.survey.Q411", *Q42_FEATURE_COLUMNS]
REQUIRED_BASE_COLUMNS = [
    "item.gender",
    "item.style",
]

# ============================================================
# Request / Response Schemas
# ============================================================
class RecommendRequest(BaseModel):
    gender: Literal["M", "W"]
    personal_color_input: str = Field(default="unknown")
    warmcool_q1: Optional[Literal["A", "B"]] = None
    warmcool_q2: Optional[Literal["A", "B"]] = None
    warmcool_q3: Optional[Literal["A", "B"]] = None
    qwarm: Optional[Literal["A", "B", "C", "D"]] = None
    qcool: Optional[Literal["A", "B", "C", "D"]] = None
    qstyle_1: Optional[Literal["A", "B"]] = None
    qstyle_2: Optional[Literal["A", "B"]] = None
    qstyle_3: Optional[Literal["A", "B"]] = None
    qstyle_4: Optional[Literal["A", "B"]] = None
    qstyle_5: Optional[Literal["A", "B"]] = None
    qstyle_6: Optional[Literal["A", "B"]] = None
    top_k: int = Field(default=TOP_K_DEFAULT, ge=1, le=30)
    strategy: Literal["cosine", "mapped", "hybrid"] = "hybrid"
    target_style: Optional[str] = None

    @model_validator(mode="after")
    def validate_personal_color(self) -> "RecommendRequest":
        if self.personal_color_input not in VALID_PERSONAL_COLORS:
            raise ValueError(f"invalid personal_color_input: {self.personal_color_input}")
        return self


class ProfileResponse(BaseModel):
    gender: str
    personal_color: str
    personal_color_source: str
    personal_color_confidence: float
    warmcool_path: Optional[Dict[str, Any]] = None
    style_scores: Dict[str, int]
    primary_style: str
    secondary_styles: List[str]
    fit_scores: Dict[str, int]
    recommended_fit: str


class RecommendationItem(BaseModel):
    item_id: str
    mall: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    deep_link: Optional[str] = None
    web_url: Optional[str] = None
    style: Optional[str] = None
    era: Optional[str] = None
    score: float
    cosine_score: Optional[float] = None
    style_match_score: Optional[float] = None
    reason: List[str] = []


class RecommendResponse(BaseModel):
    profile: ProfileResponse
    items: List[RecommendationItem]
    meta: Dict[str, Any]


# ============================================================
# Core domain logic (refactored from notebook)
# ============================================================
@dataclass
class UserInput:
    gender: str
    personal_color_input: str
    warmcool_q1: Optional[str] = None
    warmcool_q2: Optional[str] = None
    warmcool_q3: Optional[str] = None
    qwarm: Optional[str] = None
    qcool: Optional[str] = None
    qstyle_1: Optional[str] = None
    qstyle_2: Optional[str] = None
    qstyle_3: Optional[str] = None
    qstyle_4: Optional[str] = None
    qstyle_5: Optional[str] = None
    qstyle_6: Optional[str] = None

    def __post_init__(self) -> None:
        if self.gender not in {"M", "W"}:
            raise ValueError("gender must be 'M' or 'W'")
        if self.personal_color_input not in VALID_PERSONAL_COLORS:
            raise ValueError(f"invalid personal_color_input: {self.personal_color_input}")


class RecommendationEngine:
    def __init__(self, raw_input: Dict[str, Any]) -> None:
        self.user_data = UserInput(**raw_input)

    def determine_personal_color(self) -> Dict[str, Any]:
        if self.user_data.personal_color_input != "unknown":
            return {
                "personal_color": self.user_data.personal_color_input,
                "personal_color_source": "direct",
                "personal_color_confidence": 1.0,
                "warmcool_path": None,
            }

        answers = [
            self.user_data.warmcool_q1,
            self.user_data.warmcool_q2,
            self.user_data.warmcool_q3,
        ]
        warm_count = answers.count("A")
        cool_count = answers.count("B")

        path_info = {
            "warm_count": warm_count,
            "cool_count": cool_count,
            "branch": None,
            "detail_answer": None,
        }

        if warm_count > cool_count:
            path_info["branch"] = "warm"
            detail = self.user_data.qwarm
            path_info["detail_answer"] = detail
            color = WARM_COLOR_MAP.get(detail, "unknown")
            return {
                "personal_color": color,
                "personal_color_source": "inferred",
                "personal_color_confidence": 0.9,
                "warmcool_path": path_info,
            }

        if cool_count > warm_count:
            path_info["branch"] = "cool"
            detail = self.user_data.qcool
            path_info["detail_answer"] = detail
            color = COOL_COLOR_MAP.get(detail, "unknown")
            return {
                "personal_color": color,
                "personal_color_source": "inferred",
                "personal_color_confidence": 0.9,
                "warmcool_path": path_info,
            }

        path_info["branch"] = "tie"
        return {
            "personal_color": "needs_more_info",
            "personal_color_source": "inferred",
            "personal_color_confidence": 0.3,
            "warmcool_path": path_info,
        }

    def calculate_styles_and_fit(self) -> Dict[str, Any]:
        style_scores = {style: 0 for style in STYLE_CATEGORIES}
        fit_scores = {"tight_normal": 0, "loose": 0}

        for q_key, q_map in STYLE_SCORE_MAP.items():
            answer = getattr(self.user_data, q_key)
            if answer in q_map:
                for style in q_map[answer]:
                    style_scores[style] += 1

        if self.user_data.qstyle_2 == "A":
            fit_scores["tight_normal"] += 1
        elif self.user_data.qstyle_2 == "B":
            fit_scores["loose"] += 1

        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        primary_style = sorted_styles[0][0] if sorted_styles else "casual"
        max_score = sorted_styles[0][1] if sorted_styles else 0

        secondary_styles = [
            style
            for style, score in sorted_styles[1:]
            if max_score - score <= 1 and score > 0
        ]

        if fit_scores["tight_normal"] > fit_scores["loose"]:
            recommended_fit = "tight_or_normal"
        elif fit_scores["loose"] > fit_scores["tight_normal"]:
            recommended_fit = "loose_or_overfit"
        else:
            recommended_fit = "balanced"

        return {
            "style_scores": style_scores,
            "primary_style": primary_style,
            "secondary_styles": secondary_styles,
            "fit_scores": fit_scores,
            "recommended_fit": recommended_fit,
        }

    def generate_profile(self) -> Dict[str, Any]:
        return {
            "gender": self.user_data.gender,
            **self.determine_personal_color(),
            **self.calculate_styles_and_fit(),
        }


# ============================================================
# Utility functions
# ============================================================
def ensure_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            df[col] = 0.0
    return df


def minmax_scale(matrix: np.ndarray) -> np.ndarray:
    min_vals = matrix.min(axis=0)
    max_vals = matrix.max(axis=0)
    denom = np.where((max_vals - min_vals) == 0, 1.0, max_vals - min_vals)
    return (matrix - min_vals) / denom


def cosine_similarity_single(user_vector: np.ndarray, item_matrix: np.ndarray) -> np.ndarray:
    user_norm = np.linalg.norm(user_vector)
    item_norm = np.linalg.norm(item_matrix, axis=1)
    denom = np.where((user_norm * item_norm) == 0, 1e-8, user_norm * item_norm)
    return item_matrix.dot(user_vector) / denom


def build_user_vector_from_request(req: RecommendRequest, fit_weight: float = 1.5) -> np.ndarray:
    user_vector_dict = {col: 0.0 for col in USER_FEATURE_COLUMNS}

    # Fit mapping from notebook logic
    if req.qstyle_2 == "A":
        fit_target = 0.3
    elif req.qstyle_2 == "B":
        fit_target = 0.9
    else:
        fit_target = 0.5
    user_vector_dict["item.survey.Q411"] = fit_target * fit_weight

    # Mood mapping from the earlier recommend_fashion example
    # You can expand this to match your full survey design.
    mood_answer = req.qstyle_5
    if mood_answer == "A":
        user_vector_dict["item.survey.Q4201"] = 1.0
        user_vector_dict["item.survey.Q4202"] = 1.0
    elif mood_answer == "B":
        user_vector_dict["item.survey.Q4215"] = 1.0
        user_vector_dict["item.survey.Q4216"] = 1.0

    return np.array([user_vector_dict[col] for col in USER_FEATURE_COLUMNS], dtype=float)


def normalize_mall_name(value: Any) -> Optional[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    return str(value)


# ============================================================
# Data repository
# ============================================================
class FashionRepository:
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.df: pd.DataFrame = pd.DataFrame()

    def load(self) -> None:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"dataset not found: {self.data_path}. Set FASHION_DATA_PATH to your csv/parquet file."
            )

        if self.data_path.endswith(".csv"):
            df = pd.read_csv(self.data_path)
        elif self.data_path.endswith(".parquet"):
            df = pd.read_parquet(self.data_path)
        else:
            raise ValueError("Only .csv and .parquet are supported")

        missing = [col for col in REQUIRED_BASE_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"dataset is missing required columns: {missing}")

        ensure_columns(df, USER_FEATURE_COLUMNS)

        if "item_id" not in df.columns:
            if "imgName" in df.columns:
                df["item_id"] = df["imgName"].astype(str)
            else:
                df["item_id"] = df.index.astype(str)

        self.df = df

    def filter_candidates(self, gender: str, target_style: Optional[str]) -> pd.DataFrame:
        if self.df.empty:
            raise RuntimeError("repository is not loaded")

        sub_df = self.df[self.df["item.gender"] == gender].copy()
        if target_style:
            sub_df = sub_df[
                sub_df["item.style"].astype(str).str.contains(target_style, case=False, na=False)
            ].copy()
        return sub_df


# ============================================================
# Recommender service
# ============================================================
class RecommenderService:
    def __init__(self, repo: FashionRepository) -> None:
        self.repo = repo

    def analyze_profile(self, req: RecommendRequest) -> Dict[str, Any]:
        engine = RecommendationEngine(req.model_dump(exclude={"top_k", "strategy", "target_style"}))
        return engine.generate_profile()

    def score_cosine(self, req: RecommendRequest, candidates: pd.DataFrame) -> pd.DataFrame:
        if candidates.empty:
            return candidates.assign(cosine_score=np.nan)

        work_df = ensure_columns(candidates.copy(), USER_FEATURE_COLUMNS)
        item_matrix = work_df[USER_FEATURE_COLUMNS].fillna(0).astype(float).to_numpy()
        user_vector = build_user_vector_from_request(req)

        scaled_matrix = minmax_scale(item_matrix)
        # Use item-wise min/max domain to place user vector roughly in the same space.
        # This is simpler than sklearn scaler and keeps runtime dependencies low.
        mins = item_matrix.min(axis=0)
        maxs = item_matrix.max(axis=0)
        denom = np.where((maxs - mins) == 0, 1.0, maxs - mins)
        scaled_user = (user_vector - mins) / denom

        similarities = cosine_similarity_single(scaled_user, scaled_matrix)
        work_df["cosine_score"] = similarities
        return work_df

    def score_mapped(self, primary_style: str, candidates: pd.DataFrame) -> pd.DataFrame:
        if candidates.empty:
            return candidates.assign(style_match_score=np.nan)

        target_features = STYLE_FEATURE_MAP.get(primary_style, [])
        if not target_features:
            return candidates.assign(style_match_score=np.nan)

        work_df = ensure_columns(candidates.copy(), target_features)
        feature_data = work_df[target_features].fillna(0).astype(float).to_numpy()
        scaled = minmax_scale(feature_data)
        work_df["style_match_score"] = scaled.mean(axis=1)
        return work_df

    def merge_scores(
        self,
        scored_cosine: pd.DataFrame,
        scored_mapped: pd.DataFrame,
        strategy: str,
    ) -> pd.DataFrame:
        if strategy == "cosine":
            merged = scored_cosine.copy()
            merged["final_score"] = merged["cosine_score"].fillna(0)
            return merged

        if strategy == "mapped":
            merged = scored_mapped.copy()
            merged["final_score"] = merged["style_match_score"].fillna(0)
            return merged

        merged = scored_cosine.copy()
        if "style_match_score" in scored_mapped.columns:
            merged["style_match_score"] = scored_mapped["style_match_score"]
        else:
            merged["style_match_score"] = np.nan

        merged["cosine_score"] = merged["cosine_score"].fillna(0)
        merged["style_match_score"] = merged["style_match_score"].fillna(0)
        merged["final_score"] = 0.65 * merged["cosine_score"] + 0.35 * merged["style_match_score"]
        return merged

    def build_reason(self, row: pd.Series, profile: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []
        if row.get("item.style"):
            reasons.append(f"style match: {row.get('item.style')}")
        if pd.notna(row.get("cosine_score")):
            reasons.append(f"cosine score {float(row.get('cosine_score')):.3f}")
        if pd.notna(row.get("style_match_score")):
            reasons.append(f"mapped style score {float(row.get('style_match_score')):.3f}")
        reasons.append(f"primary style: {profile['primary_style']}")
        return reasons

    def recommend(self, req: RecommendRequest) -> RecommendResponse:
        profile = self.analyze_profile(req)
        target_style = req.target_style or profile["primary_style"]
        candidates = self.repo.filter_candidates(req.gender, target_style)

        # Fallback: if style-filtered set is empty, relax to gender-only.
        if candidates.empty:
            candidates = self.repo.filter_candidates(req.gender, None)

        if candidates.empty:
            raise HTTPException(status_code=404, detail="No candidate items found for the given gender")

        scored_cosine = self.score_cosine(req, candidates)
        scored_mapped = self.score_mapped(profile["primary_style"], candidates)
        ranked = self.merge_scores(scored_cosine, scored_mapped, req.strategy)
        ranked = ranked.sort_values("final_score", ascending=False).head(req.top_k)

        items: List[RecommendationItem] = []
        for _, row in ranked.iterrows():
            items.append(
                RecommendationItem(
                    item_id=str(row.get("item_id")),
                    mall=normalize_mall_name(row.get("mall") or row.get("source") or row.get("platform")),
                    name=None if pd.isna(row.get("name")) else str(row.get("name")),
                    brand=None if pd.isna(row.get("brand")) else str(row.get("brand")),
                    image_url=None if pd.isna(row.get("image_url")) else str(row.get("image_url")),
                    deep_link=None if pd.isna(row.get("deep_link")) else str(row.get("deep_link")),
                    web_url=None if pd.isna(row.get("web_url")) else str(row.get("web_url")),
                    style=None if pd.isna(row.get("item.style")) else str(row.get("item.style")),
                    era=None if pd.isna(row.get("item.era")) else str(row.get("item.era")),
                    score=float(row.get("final_score", 0.0)),
                    cosine_score=None if pd.isna(row.get("cosine_score")) else float(row.get("cosine_score")),
                    style_match_score=None if pd.isna(row.get("style_match_score")) else float(row.get("style_match_score")),
                    reason=self.build_reason(row, profile),
                )
            )

        return RecommendResponse(
            profile=ProfileResponse(**profile),
            items=items,
            meta={
                "strategy": req.strategy,
                "top_k": req.top_k,
                "candidate_count": int(len(candidates)),
                "applied_target_style": target_style,
                "fallback_used": req.target_style is not None and len(self.repo.filter_candidates(req.gender, req.target_style)) == 0,
            },
        )


# ============================================================
# App wiring
# ============================================================
class AppState:
    repo: FashionRepository
    recommender: RecommenderService


state = AppState()


@asynccontextmanager
async def lifespan(_: FastAPI):
    state.repo = FashionRepository(DATA_PATH)
    state.repo.load()
    state.recommender = RecommenderService(state.repo)
    yield


app = FastAPI(
    title="Fashion Recommendation API",
    version="1.0.0",
    description="Survey-based fashion recommendation service for React frontend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "rows": 0 if state.repo.df.empty else int(len(state.repo.df)),
        "data_path": DATA_PATH,
    }


@app.post("/api/profile/analyze", response_model=ProfileResponse)
def analyze_profile(req: RecommendRequest) -> ProfileResponse:
    profile = state.recommender.analyze_profile(req)
    return ProfileResponse(**profile)


@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest) -> RecommendResponse:
    return state.recommender.recommend(req)


# ============================================================
# Local run
# ============================================================
# Example:
#   export FASHION_DATA_PATH=./data/fashion_items.parquet
#   uvicorn fastapi_recommendation_service:app --reload --host 0.0.0.0 --port 8000
#
# Example request body:
# {
#   "gender": "W",
#   "personal_color_input": "unknown",
#   "warmcool_q1": "B",
#   "warmcool_q2": "B",
#   "warmcool_q3": "B",
#   "qcool": "D",
#   "qstyle_1": "B",
#   "qstyle_2": "B",
#   "qstyle_3": "B",
#   "qstyle_4": "A",
#   "qstyle_5": "B",
#   "qstyle_6": "A",
#   "top_k": 5,
#   "strategy": "hybrid"
# }
