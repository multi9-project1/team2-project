***

# MAPSITI 시스템 아키텍처 명세서 (Architecture)

## 1. 시스템 개요 (System Overview)
MAPSITI(패션 스타일 페르소나 기반 추천 시스템)는 사용자의 설문 응답을 기반으로 패션 취향을 분석하고, 머신러닝(K-Means) 모델과 코사인 유사도 알고리즘을 활용하여 최적의 패션 아이템을 큐레이션 하는 지능형 웹 서비스입니다. 

본 시스템은 클라이언트 측 렌더링(Vanilla JS)과 RESTful API(FastAPI) 기반의 백엔드로 완전히 분리된 아키텍처를 채택하여 확장성과 유지보수성을 극대화했습니다.

---

## 2. 전체 디렉토리 구조 (Directory Structure)

```text
project-root/                              
├── frontend/                              # 사용자 웹 프론트엔드
├── backend/                               # FastAPI 기반 API 서버 및 추천 엔진
├── docs/                                  # 프로젝트 문서
├── .gitignore                             
├── README.md                              
└── docker-compose.yml                     # 컨테이너화 및 통합 배포 설정
```

---

## 3. 프론트엔드 아키텍처 (Frontend Architecture)
프론트엔드는 가벼운 Vanilla JavaScript와 HTML/CSS로 구성되어 있으며, 컴포넌트 단위로 파일을 분리하여 상태 관리와 비동기 통신을 처리합니다.

* **View (HTML/CSS):**
    * `index.html`: 서비스 진입점 및 랜딩 페이지.
    * `survey.html`: 사용자 취향(컬러, 핏, 스타일) 수집을 위한 인터랙티브 설문 폼.
    * `result.html`: 분석된 페르소나 및 추천 상품 리스트 시각화 페이지.
    * `css/style.css`: 테마 컬러, 반응형 레이아웃 등 전역 스타일 정의.
* **Controller & Logic (JavaScript):**
    * `js/api.js`: Fetch API를 활용한 백엔드(FastAPI) 비동기 통신 및 에러 핸들링 로직.
    * `js/survey.js`: 설문 문항 순차 진행, 진행률(Progress) UI 제어 및 사용자 응답 데이터 임시 저장.
    * `js/result.js`: 추천 결과 데이터 렌더링 및 UI 연출(로딩 애니메이션 등).
    * `js/utils.js`: 상태 유지(Session/Local Storage) 및 공통 유틸리티 함수.

---

## 4. 백엔드 아키텍처 (Backend Architecture)
백엔드는 Python FastAPI 프레임워크를 기반으로 하며, 데이터 검증, 비즈니스 로직, 추천 알고리즘, 외부 데이터 수집이 계층적으로 분리되어 있습니다.

### 4.1. 계층별 모듈 역할 (Layered Modules)
* **진입점 및 라우팅 (`app/main.py`, `app/api/`)**
    * `main.py`: FastAPI 애플리케이션 초기화 및 미들웨어(CORS 등) 설정.
    * `api/router.py`: 전체 도메인 라우터 통합.
    * `api/routes/recommendation.py`: 추천 서비스와 관련된 HTTP 요청/응답 엔드포인트 관리.
* **데이터 검증 (`app/schemas/`)**
    * `survey.py`, `recommendation.py`: Pydantic을 활용하여 클라이언트로부터 들어오는 JSON 페이로드의 타입 및 필수 값 검증.
* **비즈니스 서비스 (`app/services/`)**
    * `scoring_service.py`: 설문 응답을 기반으로 항목별 점수 수치화.
    * `persona_service.py`: 수치화된 데이터를 모델에 통과시켜 사용자 유형 분류.
    * `recommendation_service.py`: 추천 엔진과 데이터베이스/크롤러를 오케스트레이션하여 최종 응답 생성.
* **핵심 추천 로직 (`app/logic/`)**
    * `fashion_config.py`: 퍼스널 컬러, 플랫폼별 검색어 등 시스템 전반의 상수 및 매핑 규칙 관리.
    * `survey_parser.py`: 설문 원시 데이터를 알고리즘이 이해할 수 있는 프로필 객체로 변환.
    * `item_feature_builder.py`: 추천 대상 아이템들의 특징(Feature) 벡터 생성.
    * `recommender.py`: 코사인 유사도(Cosine Similarity) 등을 이용한 아이템 간 매칭 및 추천 점수 계산.
    * **`fashion_data.csv`**: 시스템 구동 및 로컬 테스트의 기준점이 되는 원천 패션 데이터셋.
* **외부 연동 및 AI 모델 (`app/crawlers/`, `app/models/`)**
    * `musinsa_crawler.py` & `zigzag_crawler.py`: 쇼핑 플랫폼 실시간 상품 데이터 수집기 (Selenium/BS4).
    * `kmeans_model.pkl`: 사전 학습된 K-Means 클러스터링 기반 페르소나 분류 모델 파일.

---

## 5. 데이터 흐름 (Data Flow)

1.  **Request (Client -> API):** 사용자가 프론트엔드(`survey.js`)에서 설문을 완료하면 `api.js`가 백엔드 `recommendation.py` 라우터로 POST 요청 전송.
2.  **Validation (Schemas):** Pydantic 스키마(`survey.py`)를 통해 입력 데이터 무결성 검증.
3.  **Processing (Services & Logic):** * `scoring_service.py`와 `survey_parser.py`를 통해 데이터를 정제.
    * `persona_service.py`가 `kmeans_model.pkl`을 호출하여 사용자 페르소나 도출.
4.  **Recommendation Generation:** * 실시간 크롤링(`crawlers/`) 또는 정적 데이터(`fashion_data.csv`) 획득.
    * `item_feature_builder.py` 및 `recommender.py`가 유사도를 계산하여 최적의 아이템 선별.
5.  **Response (API -> Client):** 최종 추천 리스트와 페르소나 정보를 JSON 형태로 반환하여 프론트엔드(`result.js`)에 렌더링.