# 맵시TI : Fashion Recommendation Service

사용자 설문 응답을 기반으로 스타일/핏/TPO 결과를 분석하고, 이에 맞는 상품을 추천한 뒤 무신사/지그재그 딥링크를 생성해 제공하는 추천 서비스입니다.

---

## 1. 프로젝트 개요

본 프로젝트는 프론트엔드에서 사용자의 설문 응답을 수집하고, Python 백엔드 서버가 이를 분석하여 다음 결과를 반환하는 구조로 설계되었습니다.

- 설문 점수 계산
- 스타일 / 핏 / TPO 결과 생성
- 결과에 맞는 상품 추천
- 무신사 / 지그재그 딥링크 생성

프론트엔드는 최종 결과 JSON을 받아 사용자에게 시각적으로 렌더링합니다.

---

## 2. 시스템 흐름

1. 사용자가 프론트엔드에서 설문 응답을 제출합니다.
2. 프론트엔드는 설문 응답 데이터를 Python 서버로 전송합니다.
3. Python 서버는 다음 작업을 수행합니다.
   - 설문 점수 계산
   - 스타일 / 핏 / TPO 결과 생성
   - 결과 기반 추천 상품 추출
   - 무신사 / 지그재그 딥링크 생성
4. 프론트엔드는 결과 JSON을 받아 결과 화면을 렌더링합니다.

---

## 3. 기술 스택

### Frontend
- React
- TypeScript
- Vite

### Backend
- FastAPI
- Pydantic
- Uvicorn

### Recommendation / Analysis
- Python
- Scikit-learn
- K-Means

### Crawling
- Selenium
- Undetected-Chromedriver

---

## 4. 폴더 구조

```bash
project-root/
├── frontend/
│   ├── public/
│   └── src/
│       ├── api/
│       │   └── recommendationApi.ts
│       ├── components/
│       │   ├── survey/
│       │   │   ├── SurveyForm.tsx
│       │   │   └── QuestionCard.tsx
│       │   └── result/
│       │       ├── ResultSummary.tsx
│       │       ├── ProductCard.tsx
│       │       └── ProductList.tsx
│       ├── pages/
│       │   ├── HomePage.tsx
│       │   ├── SurveyPage.tsx
│       │   └── ResultPage.tsx
│       ├── types/
│       │   ├── survey.ts
│       │   └── recommendation.ts
│       ├── hooks/
│       │   └── useRecommendation.ts
│       ├── utils/
│       │   └── format.ts
│       ├── App.tsx
│       └── main.tsx
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       └── recommendation.py
│   │   ├── schemas/
│   │   │   ├── survey.py
│   │   │   └── recommendation.py
│   │   ├── services/
│   │   │   ├── survey_service.py
│   │   │   ├── scoring_service.py
│   │   │   ├── persona_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── deeplink_service.py
│   │   ├── logic/
│   │   │   ├── fashion_config.py
│   │   │   ├── survey_parser.py
│   │   │   ├── item_feature_builder.py
│   │   │   └── recommender.py
│   │   ├── crawlers/
│   │   │   ├── musinsa_crawler.py
│   │   │   └── zigzag_crawler.py
│   │   ├── models/
│   │   │   └── kmeans_model.pkl
│   │   ├── data/
│   │   │   ├── raw/
│   │   │   ├── processed/
│   │   │   └── cache/
│   │   ├── utils/
│   │   │   ├── logger.py
│   │   │   └── helpers.py
│   │   └── tests/
│   │       ├── test_api.py
│   │       ├── test_scoring.py
│   │       └── test_recommendation.py
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   └── architecture.md
│
├── .gitignore
├── docker-compose.yml
└── README.md
