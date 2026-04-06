폴더 구조

project-root/
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/
│   │   │   ├── dataset.ts
│   │   │   └── recommendations.ts
│   │   ├── assets/
│   │   │   └── images/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Loading.tsx
│   │   │   ├── survey/
│   │   │   │   ├── SurveyForm.tsx
│   │   │   │   └── QuestionCard.tsx
│   │   │   └── recommendation/
│   │   │       ├── ProductCard.tsx
│   │   │       ├── GalleryGrid.tsx
│   │   │       └── ResultSummary.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── SurveyPage.tsx
│   │   │   ├── ResultPage.tsx
│   │   │   └── GalleryPage.tsx
│   │   ├── hooks/
│   │   │   ├── useSurvey.ts
│   │   │   └── useRecommendations.ts
│   │   ├── store/
│   │   │   └── surveyStore.ts
│   │   ├── types/
│   │   │   ├── survey.ts
│   │   │   ├── recommendation.ts
│   │   │   └── product.ts
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── routes.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       ├── dataset.py
│   │   │       └── recommendations.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── schemas/
│   │   │   ├── common.py
│   │   │   ├── dataset.py
│   │   │   ├── survey.py
│   │   │   └── recommendation.py
│   │   ├── services/
│   │   │   ├── dataset_service.py
│   │   │   └── recommendation_service.py
│   │   ├── logic/
│   │   │   ├── fashion_config.py
│   │   │   ├── survey_parser.py
│   │   │   ├── item_feature_builder.py
│   │   │   └── recommender.py
│   │   ├── crawlers/
│   │   │   ├── base.py
│   │   │   ├── musinsa_crawler.py
│   │   │   └── zigzag_crawler.py
│   │   ├── utils/
│   │   │   ├── zip_handler.py
│   │   │   ├── json_loader.py
│   │   │   └── file_manager.py
│   │   ├── data/
│   │   │   ├── raw/
│   │   │   ├── prepared/
│   │   │   ├── processed/
│   │   │   └── cache/
│   │   └── tests/
│   │       ├── test_dataset_api.py
│   │       ├── test_recommendation_api.py
│   │       ├── test_recommender.py
│   │       └── test_crawlers.py
│   ├── requirements.txt
│   └── .env.example
│
├── infra/
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   └── frontend.Dockerfile
│   ├── nginx/
│   │   └── default.conf
│   └── docker-compose.yml
│
├── scripts/
│   ├── run_backend.sh
│   ├── run_frontend.sh
│   └── crawl_once.py
│
├── docs/
│   ├── architecture.md
│   └── api_spec.md
│
├── .gitignore
├── README.md
└── .env
