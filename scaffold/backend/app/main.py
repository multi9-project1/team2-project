from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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
    from app.logic.survey_parser import collect_style_search_keywords, create_survey_profile

app = FastAPI(title="Fashion Recommendation API", version="0.1.0")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
    ],
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


def resolve_default_dataset_csv_path() -> Path:
    for candidate_path in DEFAULT_DATASET_CSV_CANDIDATES:
        if candidate_path.exists():
            return candidate_path
    return DEFAULT_DATASET_CSV_CANDIDATES[0]


class SurveyInputModel(BaseModel):
    gender: Optional[str] = "U"
    personal_color: Optional[str] = "unknown"
    Q1: Optional[str] = None
    Q2: Optional[str] = None
    Q3: Optional[str] = None
    Qwarm: Optional[str] = None
    Qcool: Optional[str] = None
    Qstyle_1: Optional[str] = None
    Qstyle_2: Optional[str] = None
    Qstyle_3: Optional[str] = None
    Qstyle_4: Optional[str] = None
    Qstyle_5: Optional[str] = None
    Qstyle_6: Optional[str] = None
    Qstyle_7: Optional[str] = None
    Qstyle_8: Optional[str] = None
    Qstyle_9: Optional[str] = None


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
    return {
        "user_profile": user_profile,
        "deeplink_context": create_deeplink_context(user_profile),
    }


def format_preference_analysis_text(top_match: Dict[str, Any]) -> str:
    matched_era = str(top_match.get("era", "unknown"))
    matched_style_group = resolve_dataset_style_group_label(str(top_match.get("style", "unknown")))
    similarity_percent = int(top_match.get("similarity_percent", 0))
    return f"알고리즘 분석 결과, 당신의 취향은 **[{matched_era}년대]**의 **[{matched_style_group}]**과 {similarity_percent}% 일치합니다"


def resolve_dataset_style_label(style_code: str) -> str:
    korean_label = DATASET_STYLE_LABELS.get(style_code.lower())
    if not korean_label:
        return "기타 스타일"
    return korean_label


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
    if not image_path or not dataset_dir:
        return None

    dataset_root = Path(dataset_dir).resolve()
    if not dataset_root.is_dir():
        return None
    candidate = Path(image_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / image_path).resolve()

    try:
        relative_path = candidate.relative_to(dataset_root)
    except ValueError:
        return None

    return f"/sample-files/{relative_path.as_posix()}"


def attach_recommendation_image_urls(
    recommendations: List[Dict[str, Any]],
    dataset_dir: Optional[str],
    base_url: str,
) -> List[Dict[str, Any]]:
    for item in recommendations:
        relative_url = build_static_image_url(str(item.get("image_path", "")), dataset_dir)
        item["image_url"] = relative_url
        item["image_full_url"] = f"{base_url.rstrip('/')}{relative_url}" if relative_url else None
    return recommendations


def generate_dataset_recommendation_response(
    request: RecommendationQueryRequest,
    base_url: str,
) -> Dict[str, Any]:
    user_profile = create_survey_profile(request.survey.model_dump()).to_dict()
    zip_path, extract_dir, dataset_dir = resolve_dataset_input_paths(request)

    if request.prefer_extracted_dataset and zip_path and extract_dir:
        extracted_path = ensure_dataset_archive_extracted(zip_path, extract_dir)
        dataset_dir = str(extracted_path)

    dataset_items = load_dataset_item_records(
        zip_path=zip_path,
        extract_dir=extract_dir,
        dataset_dir=dataset_dir,
        allow_mock=request.allow_mock_data,
    )
    gender_filtered_items = filter_items_by_user_gender(dataset_items, user_profile["gender"])
    image_ready_items = filter_image_available_items(gender_filtered_items)
    candidate_items = image_ready_items or gender_filtered_items or dataset_items
    top_similarity_matches = collect_top_similarity_matches(user_profile, gender_filtered_items or dataset_items, top_k=20)
    inferred_style_profile = derive_style_profile_from_similarity_matches(top_similarity_matches)
    if inferred_style_profile.get("primary_style_code"):
        primary_style_code = inferred_style_profile["primary_style_code"]
        secondary_style_codes = inferred_style_profile["secondary_style_codes"]
        user_profile["primary_style"] = primary_style_code
        user_profile["secondary_styles"] = secondary_style_codes
        user_profile["style_display"] = {primary_style_code: STYLE_LABELS.get(primary_style_code, primary_style_code)}
        user_profile["style_search_keywords"] = collect_style_search_keywords(primary_style_code, secondary_style_codes)

    top_match = find_highest_similarity_item_match(user_profile, gender_filtered_items or dataset_items)
    recommendations = attach_recommendation_image_urls(
        rank_recommendation_candidates(user_profile, candidate_items, top_n=request.top_n),
        dataset_dir,
        base_url,
    )

    response = create_profile_response_payload(user_profile)
    response["recommendation_results"] = recommendations
    response["preference_analysis"] = {
        "era": top_match["era"],
        "style": inferred_style_profile["primary_group"],
        "similarity_percent": top_match["similarity_percent"],
        "text": f"알고리즘 분석 결과, 당신의 취향은 **[{top_match['era']}년대]**의 **[{inferred_style_profile['primary_group']}]**과 {top_match['similarity_percent']}% 일치합니다",
    }
    response["meta"] = {
        "includes_dataset_recommendations": True,
        "item_count": len(dataset_items),
        "gender_filtered_item_count": len(gender_filtered_items),
        "image_ready_item_count": len(image_ready_items),
        "mock_data_used": _is_mock_recommendation_source(dataset_items),
        "resolved_zip_path": zip_path,
        "resolved_dataset_dir": dataset_dir or extract_dir,
        "sample_files_base_url": "/sample-files" if dataset_dir else None,
        "recommended_usage": "analysis-or-demo",
        "tpo_scoring_enabled": True,
    }
    return response


def render_recommendation_gallery_html(result: Dict[str, Any]) -> str:
    user_profile = result["user_profile"]
    cards: List[str] = []
    for index, item in enumerate(result.get("recommendation_results", []), start=1):
        image_tag = (
            f'<img src="{item["image_full_url"]}" alt="top {index}" loading="lazy" />'
            if item.get("image_full_url")
            else '<div class="empty">이미지를 찾지 못했습니다</div>'
        )
        reason_html = "".join(f"<li>{reason}</li>" for reason in item.get("reasons", []))
        cards.append(
            f"""
            <article class="card">
              <div class="rank">TOP {index}</div>
              <div class="media">{image_tag}</div>
              <div class="body">
                <h2>{item.get("item_id", "-")}</h2>
                <p class="meta">gender: {item.get("gender", "-")} | era: {item.get("era", "-")} | style: {resolve_dataset_style_group_label(str(item.get("style", "-")))}</p>
                <p class="score">score: {item.get("score", "-")}</p>
                <ul>{reason_html}</ul>
              </div>
            </article>
            """
        )

    color_keywords = ", ".join(result["deeplink_context"].get("color_search_keywords", []))
    style_keywords = ", ".join(result["deeplink_context"].get("style_search_keywords", []))
    return f"""
    <!doctype html>
    <html lang="ko">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Top 5 Similar Images</title>
        <style>
          :root {{
            --bg: #f6f1e8;
            --card: #fffaf4;
            --ink: #2e241b;
            --muted: #7b6a59;
            --line: #dfd0bf;
            --accent: #9c5f3c;
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: "Helvetica Neue", Arial, sans-serif;
            color: var(--ink);
            background:
              radial-gradient(circle at top left, #fff7ef 0, transparent 35%),
              linear-gradient(135deg, #efe3d1, var(--bg));
          }}
          .wrap {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 20px 56px;
          }}
          .hero {{
            margin-bottom: 24px;
            padding: 24px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255,255,255,0.72);
            backdrop-filter: blur(10px);
          }}
          h1 {{ margin: 0 0 10px; font-size: 32px; }}
          .summary {{ color: var(--muted); line-height: 1.6; }}
          .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
          }}
          .card {{
            border: 1px solid var(--line);
            border-radius: 22px;
            overflow: hidden;
            background: var(--card);
            box-shadow: 0 14px 40px rgba(86, 57, 30, 0.08);
          }}
          .rank {{
            padding: 12px 16px;
            font-weight: 700;
            color: white;
            background: linear-gradient(90deg, #8f4f2c, var(--accent));
          }}
          .media {{
            aspect-ratio: 4 / 5;
            background: #eadfce;
          }}
          .media img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
          }}
          .empty {{
            width: 100%;
            height: 100%;
            display: grid;
            place-items: center;
            color: var(--muted);
            padding: 24px;
            text-align: center;
          }}
          .body {{ padding: 16px; }}
          .body h2 {{ margin: 0 0 8px; font-size: 18px; }}
          .meta, .score {{ margin: 0 0 10px; color: var(--muted); }}
          ul {{ margin: 0; padding-left: 18px; line-height: 1.5; }}
        </style>
      </head>
      <body>
        <main class="wrap">
          <section class="hero">
            <h1>유사 이미지 Top {len(result.get("recommendation_results", []))}</h1>
            <p class="summary">
              성별: {user_profile.get("gender")} |
              퍼스널 컬러: {user_profile.get("personal_color_display")} |
              대표 스타일: {user_profile.get("primary_style")} |
              컬러 키워드: {color_keywords} |
              스타일 키워드: {style_keywords} |
              분석 문장: {result.get("preference_analysis", {}).get("text", "")}
            </p>
          </section>
          <section class="grid">
            {''.join(cards)}
          </section>
        </main>
      </body>
    </html>
    """


def render_gallery_demo_page_html() -> str:
    return """
    <!doctype html>
    <html lang="ko">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Gallery Demo</title>
        <style>
          body {
            margin: 0;
            font-family: "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #f7efe5, #efe1d0);
            color: #2f241b;
          }
          .wrap {
            max-width: 840px;
            margin: 40px auto;
            padding: 24px;
          }
          .panel {
            background: rgba(255,255,255,0.82);
            border: 1px solid #dbcab7;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 14px 40px rgba(86, 57, 30, 0.08);
          }
          h1 {
            margin-top: 0;
            font-size: 30px;
          }
          p {
            color: #6f5c49;
            line-height: 1.6;
          }
          form {
            display: grid;
            gap: 14px;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
          }
          label {
            display: grid;
            gap: 6px;
            font-size: 14px;
            font-weight: 600;
          }
          input, select {
            width: 100%;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid #cfbda8;
            background: #fffaf5;
            font-size: 14px;
          }
          button {
            border: 0;
            border-radius: 999px;
            padding: 14px 20px;
            background: linear-gradient(90deg, #8f4f2c, #b06a40);
            color: white;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
          }
          .hint {
            font-size: 13px;
            color: #7b6755;
          }
        </style>
      </head>
      <body>
        <main class="wrap">
          <section class="panel">
            <h1>Top 5 이미지 보기</h1>
            <p>아래 값을 넣고 버튼을 누르면 새 탭에서 실제 추천 이미지 5장이 바로 뜹니다.</p>
            <form id="gallery-form">
              <div class="grid">
                <label>성별
                  <select name="gender">
                    <option value="여성" selected>여성</option>
                    <option value="남성">남성</option>
                  </select>
                </label>
                <label>퍼스널 컬러
                  <select name="personal_color">
                    <option value="winter_deep" selected>winter_deep</option>
                    <option value="winter_cool">winter_cool</option>
                    <option value="winter_bright">winter_bright</option>
                    <option value="summer_light">summer_light</option>
                    <option value="summer_muted">summer_muted</option>
                    <option value="spring_light">spring_light</option>
                    <option value="spring_bright">spring_bright</option>
                    <option value="autumn_deep">autumn_deep</option>
                    <option value="autumn_muted">autumn_muted</option>
                  </select>
                </label>
                <label>Qstyle_1
                  <select name="Qstyle_1"><option value="A" selected>A</option><option value="B">B</option></select>
                </label>
                <label>Qstyle_2
                  <select name="Qstyle_2"><option value="A" selected>A</option><option value="B">B</option></select>
                </label>
                <label>Qstyle_3
                  <select name="Qstyle_3"><option value="A">A</option><option value="B" selected>B</option></select>
                </label>
                <label>Qstyle_4
                  <select name="Qstyle_4"><option value="A">A</option><option value="B" selected>B</option></select>
                </label>
                <label>Qstyle_5
                  <select name="Qstyle_5"><option value="A" selected>A</option><option value="B">B</option></select>
                </label>
                <label>Qstyle_6
                  <select name="Qstyle_6"><option value="A" selected>A</option><option value="B">B</option></select>
                </label>
                <label>Qstyle_7
                  <select name="Qstyle_7"><option value="A">A</option><option value="B" selected>B</option></select>
                </label>
                <label>Qstyle_8
                  <select name="Qstyle_8"><option value="A">A</option><option value="B" selected>B</option></select>
                </label>
                <label>Qstyle_9
                  <select name="Qstyle_9">
                    <option value="A" selected>A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                  </select>
                </label>
              </div>
              <input type="hidden" name="top_n" value="5" />
              <input type="hidden" name="allow_mock_data" value="false" />
              <input type="hidden" name="prefer_extracted_dataset" value="true" />
              <input type="hidden" name="dataset_dir" value="{resolve_default_dataset_csv_path()}" />
              <button type="submit">갤러리 열기</button>
              <div class="hint">새 탭에서 실제 이미지 5장을 렌더링합니다.</div>
            </form>
          </section>
        </main>
        <script>
          const form = document.getElementById("gallery-form");
          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const popup = window.open("", "_blank");
            if (!popup) {
              alert("브라우저가 새 창 열기를 차단했습니다. 팝업 차단을 해제한 뒤 다시 시도해주세요.");
              return;
            }
            popup.document.open();
            popup.document.write("<p style='font-family:Arial,sans-serif;padding:24px'>갤러리를 불러오는 중입니다...</p>");
            popup.document.close();
            const formData = new FormData(form);
            const payload = {
              survey: {
                gender: formData.get("gender"),
                personal_color: formData.get("personal_color"),
                Qstyle_1: formData.get("Qstyle_1"),
                Qstyle_2: formData.get("Qstyle_2"),
                Qstyle_3: formData.get("Qstyle_3"),
                Qstyle_4: formData.get("Qstyle_4"),
                Qstyle_5: formData.get("Qstyle_5"),
                Qstyle_6: formData.get("Qstyle_6"),
                Qstyle_7: formData.get("Qstyle_7"),
                Qstyle_8: formData.get("Qstyle_8"),
                Qstyle_9: formData.get("Qstyle_9")
              },
              top_n: Number(formData.get("top_n")),
              allow_mock_data: formData.get("allow_mock_data") === "true",
              prefer_extracted_dataset: formData.get("prefer_extracted_dataset") === "true",
              dataset_dir: formData.get("dataset_dir")
            };

            const response = await fetch("/dataset-recommendations/gallery", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });

            const html = await response.text();
            if (!response.ok) {
              popup.document.open();
              popup.document.write("<pre style='font-family:monospace;padding:24px'>" + html.replace(/</g, "&lt;") + "</pre>");
              popup.document.close();
              return;
            }
            popup.document.open();
            popup.document.write(html);
            popup.document.close();
          });
        </script>
      </body>
    </html>
    """


def render_home_page_html() -> str:
    return """
    <!doctype html>
    <html lang="ko">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Fashion Recommendation API</title>
        <style>
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            font-family: "Helvetica Neue", Arial, sans-serif;
            background:
              radial-gradient(circle at top left, #fff8ee 0, transparent 30%),
              linear-gradient(135deg, #efe1cf, #f6efe6);
            color: #2f241b;
          }
          .panel {
            width: min(760px, calc(100vw - 32px));
            background: rgba(255,255,255,0.82);
            border: 1px solid #dbcab7;
            border-radius: 28px;
            padding: 32px;
            box-shadow: 0 18px 50px rgba(86, 57, 30, 0.1);
          }
          h1 {
            margin: 0 0 12px;
            font-size: 34px;
          }
          p {
            margin: 0 0 24px;
            line-height: 1.7;
            color: #6f5c49;
          }
          .actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
          }
          a {
            display: block;
            text-decoration: none;
            text-align: center;
            padding: 16px 18px;
            border-radius: 999px;
            font-weight: 700;
          }
          .primary {
            color: white;
            background: linear-gradient(90deg, #8f4f2c, #b06a40);
          }
          .secondary {
            color: #5b4734;
            background: #fff8ef;
            border: 1px solid #d9c6b1;
          }
        </style>
      </head>
      <body>
        <main class="panel">
          <h1>패션 취향 추천 홈</h1>
          <p>빠른 텍스트 결과는 API 문서에서 확인하고, 유사 이미지 검증은 갤러리 화면에서 바로 볼 수 있습니다.</p>
          <div class="actions">
            <a class="primary" href="/gallery-demo">갤러리 보기</a>
            <a class="secondary" href="/docs">API 문서</a>
            <a class="secondary" href="/health">상태 확인</a>
          </div>
        </main>
      </body>
    </html>
    """


@app.post("/dataset/prepare")
def prepare_dataset_directory(
    zip_path: Optional[str] = None,
    extract_dir: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_zip_path = zip_path or (str(DEFAULT_SAMPLE_ZIP) if DEFAULT_SAMPLE_ZIP.exists() else None)
    resolved_extract_dir = extract_dir or str(LEGACY_SAMPLE_DATASET_DIR)

    if not resolved_zip_path:
        raise HTTPException(status_code=404, detail="Sample.zip not found")

    try:
        extracted_path = ensure_dataset_archive_extracted(resolved_zip_path, resolved_extract_dir)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    json_count = sum(1 for _ in extracted_path.rglob("*.json"))
    image_count = sum(1 for _ in extracted_path.rglob("*.jpg"))
    return {
        "status": "ready",
        "zip_path": resolved_zip_path,
        "dataset_dir": str(extracted_path),
        "json_count": json_count,
        "image_count": image_count,
        "sample_files_base_url": "/sample-files",
    }


@app.get("/health")
def get_health_status() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def render_home_page() -> HTMLResponse:
    return HTMLResponse(content=render_home_page_html())


@app.post("/profile")
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


@app.post("/dataset-recommendations/gallery", response_class=HTMLResponse)
def render_dataset_recommendation_gallery(request: RecommendationQueryRequest, http_request: Request) -> HTMLResponse:
    try:
        result = generate_dataset_recommendation_response(request, str(http_request.base_url))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    return HTMLResponse(content=render_recommendation_gallery_html(result))


@app.get("/gallery-demo", response_class=HTMLResponse)
def render_gallery_demo_page() -> HTMLResponse:
    return HTMLResponse(content=render_gallery_demo_page_html())


@app.post("/recommendations")
def get_recommendation_summary_text(request: RecommendationQueryRequest) -> Dict[str, Any]:
    try:
        result = generate_dataset_recommendation_response(request, "http://127.0.0.1:8000/")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    return {
        "text": result["preference_analysis"]["text"],
        "recommendations": result.get("recommendation_results", []),
        "user_profile": result.get("user_profile", {}),
        "preference_analysis": result.get("preference_analysis", {}),
    }



import json
import traceback

@app.post("/crawl/musinsa")
def crawl_musinsa_products(request: CrawlQueryRequest) -> Dict[str, Any]:
    import json
    import traceback

    request_payload = request.model_dump()
    print("\n" + "=" * 80)
    print("[/crawl/musinsa] REQUEST PAYLOAD")
    print(json.dumps(request_payload, ensure_ascii=False, indent=2))
    print("=" * 80)

    try:
        from app.crawlers.musinsa_crl import recommend_outfit_from_survey

        crawl_result = recommend_outfit_from_survey(
            request.survey.model_dump(),
            category_name=request.category_name,
            selected_color=request.selected_color,
            dataset_dir=request.dataset_dir,
            allow_mock=request.allow_mock_data,
            top_n=request.top_n,
        )

        print("\n" + "-" * 80)
        print("[/crawl/musinsa] RESULT SUMMARY")
        print(f"platform: {crawl_result.get('platform')}")
        print(f"category: {crawl_result.get('category')}")
        print(f"selected_color: {crawl_result.get('selected_color')}")
        print(f"search_keyword: {crawl_result.get('search_keyword')}")
        print(f"url: {crawl_result.get('url')}")
        print(f"items_count: {len(crawl_result.get('items', []))}")
        print("-" * 80)

        return crawl_result

    except FileNotFoundError as exc:
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ValueError as exc:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": type(exc).__name__,
                "message": str(exc),
                "request_payload": request_payload,
            },
        ) from exc


@app.post("/crawl/zigzag")
def crawl_zigzag_products(request: CrawlQueryRequest) -> Dict[str, Any]:
    try:
        try:
            from app.crawlers.zigzag_crl import get_zigzag_recommendations_from_survey
        except ImportError:
            from crawler.zigzag_crl import get_zigzag_recommendations_from_survey

        crawl_result = get_zigzag_recommendations_from_survey(
            request.survey.model_dump(),
            request.category_name,
            selected_color=request.selected_color,
            dataset_dir=request.dataset_dir,
            allow_mock=request.allow_mock_data,
            top_n=request.top_n,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"unexpected error: {exc}") from exc

    return crawl_result


def _is_mock_recommendation_source(items: List[Dict[str, Any]]) -> bool:
    return bool(items) and all(str(item.get("item_id", "")).startswith("mock_") for item in items)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
