# 맵시TI : Fashion Recommendation Service
demo: https://mapssiti.onrender.com/

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998B?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.23+-494A4F?logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-CLIP-FFD21E)](https://huggingface.co/docs/transformers/model_doc/clip)
[![BentoML](https://img.shields.io/badge/BentoML-FF4C11?logo=bentoml&logoColor=white)](https://www.bentoml.com/)
[![Vector Similarity](https://img.shields.io/badge/Cosine--Similarity-Logic-blue)](#)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12+-black)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![Requests](https://img.shields.io/badge/Requests-2.31+-0052CC)](https://requests.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-v2-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)


사용자의 설문 응답을 바탕으로 개인의 취향과 스타일 성향을 분석하고, 이에 맞는 패션 아이템을 추천하는 웹 서비스입니다.  
프론트엔드에서 수집한 설문 데이터를 FastAPI 백엔드로 전달하면, 백엔드에서 점수화 및 사용자 유형 분류를 수행한 뒤 추천 알고리즘을 통해 크롤링된 쇼핑몰 상품 중 가장 적합한 아이템을 반환합니다.

---

## 1. 프로젝트 소개

맵시TI는 사용자의 설문 응답을 바탕으로 스타일 취향을 해석하고, 그 결과를 실제 쇼핑몰 상품 추천으로 연결하는 패션 추천 웹 서비스입니다.  
단순히 인기 상품을 나열하는 것이 아니라, **사용자의 취향을 설명 가능한 형태로 분석한 뒤 그 근거와 함께 추천 결과를 보여주는 경험**을 목표로 설계했습니다.

이 프로젝트에서 해결하고자 한 핵심 문제는 다음과 같았습니다.

1. 사용자는 자신의 취향을 막연하게 느끼지만, 검색창에서는 이를 구체적인 키워드로 표현하기 어렵다.
2. 설문 기반 규칙 추천만으로는 실제 상품 이미지가 주는 분위기와 감성까지 충분히 반영하기 어렵다.
3. 추천 근거가 모델 파일 내부에만 있으면, 데이터 흐름과 추천 로직을 포트폴리오에서 설명하기 어렵다.

이를 해결하기 위해 맵시TI는 다음 세 축으로 추천 구조를 구성했습니다.

- **설문 기반 1차 분석**: 사용자의 성별, 퍼스널컬러, 핏, 스타일 선호, TPO 응답을 구조화해 취향 프로필과 설명형 결과를 생성
- **AI-HUB 데이터 기반 2차 유사도 분석**: `fashion_data.csv`를 기준 데이터셋으로 사용해 연도감, 스타일, 핏, 컬러, 설문 특징값을 비교하고 유사도 기반 추천 수행
- **CLIP 기반 3차 고도화**: 상품 이미지와 스타일 텍스트를 동일 임베딩 공간에서 비교해, 실제 상품 분위기까지 반영하도록 추천 결과를 재정렬

특히 기존의 `kmeans_model.pkl` 대신, **AI-HUB의 "연도별 패션 선호도 파악 및 추천" 데이터를 기반으로 K-Means 군집화와 코사인 유사도 계산에 활용할 수 있도록 정제한 `fashion_data.csv`를 프로젝트 내부에 포함**했습니다. 이를 통해 추천 로직의 입력 데이터와 기준을 코드와 함께 직접 관리할 수 있게 했고, 포트폴리오 관점에서도 추천 과정의 근거를 더 투명하게 설명할 수 있도록 구성했습니다.

즉, 이 프로젝트는 **설명 가능한 설문 기반 추천**, **AI-HUB 기반 데이터 유사도 추천**, **딥러닝 기반 멀티모달 재랭킹**을 결합한 패션 추천 프로젝트입니다.

---

## 2. 프로젝트 목적

맵시TI의 핵심 목적은 아래와 같습니다.

- 사용자의 패션 취향을 설문 데이터로 구조화하고 해석 가능한 프로필로 변환
- 결과를 단순 추천 목록이 아니라 **분석 요약 + 스타일 설명 + 상품 추천** 흐름으로 제공
- 무신사, 지그재그 등 실제 쇼핑몰 상품 데이터를 활용해 현실적인 추천 결과 제공
- AI-HUB 패션 데이터와 코사인 유사도 기반 추천을 통해 설문 결과를 실제 스타일 데이터와 연결
- CLIP 멀티모달 모델을 활용해 텍스트 기반 취향과 이미지 기반 상품 특성을 함께 비교
- 사용자가 “왜 이런 추천을 받았는지” 납득할 수 있는 설명형 UI/UX 구현

포트폴리오 관점에서 맵시TI는 단순 CRUD 서비스가 아니라,
**추천 로직 설계 → 데이터 전처리 및 유사도 설계 → 외부 데이터 수집 → 멀티모달 AI 연동 → 결과 시각화까지 연결한 서비스형 프로젝트**라는 점에 의미가 있습니다.

---

## 3. 핵심 기능

### 3.1 설문 기반 사용자 프로필 생성
- 성별, 퍼스널컬러, 스타일 선호, TPO, 핏 성향 등의 설문 응답 수집
- 설문 응답을 추천 엔진이 사용할 수 있는 구조화 데이터로 변환
- 사용자 프로필과 쇼핑몰 검색용 키워드를 함께 생성

### 3.2 AI-HUB 기반 유사도 추천 데이터 활용
- AI-HUB의 **연도별 패션 선호도 파악 및 추천 데이터**를 기반으로 추천용 CSV 데이터셋 구성
- `fashion_data.csv`에 연도, 스타일, 성별, 설문 응답 특징값(Q3, Q411~Q4216) 등을 정리
- 해당 CSV를 기준으로 사용자 프로필과 데이터셋 아이템 간의 유사도를 계산해 취향에 가까운 스타일 분포를 도출
- 기존 `kmeans_model.pkl` 대신 CSV 자산을 직접 포함해 데이터 흐름과 추천 기준을 코드 레벨에서 추적 가능하도록 구성

### 3.3 취향 분석 및 설명형 결과 생성
- 설문 응답과 데이터셋 유사도 결과를 바탕으로 스타일 성향과 분위기를 해석
- 시대감성, 대표 스타일, 퍼스널컬러, 핏 정보 등을 분석 요약 카드로 시각화
- 결과 화면에서 사용자가 자신의 취향을 쉽게 이해할 수 있도록 설명형 UI 제공

### 3.4 패션 상품 크롤링 자동화
- 무신사와 지그재그 상품 정보를 실시간 수집
- 상품명, 이미지, 가격, 링크, 카테고리 등을 추천 후보군으로 확보
- 사용자 프로필 기반 검색 키워드를 조합해 후보 탐색 정확도 향상

### 3.5 CLIP 기반 멀티모달 추천 고도화
- AI-HUB 패션 이미지 및 스타일 텍스트 데이터를 활용해 Hugging Face CLIP 모델 파인 튜닝
- 파인 튜닝된 모델로 크롤링한 상품 이미지를 벡터화
- 사용자 페르소나 텍스트와 상품 이미지 벡터를 같은 특징 공간에서 비교
- 코사인 유사도를 기반으로 후보 상품을 재정렬해 더 정교한 추천 결과 제공

### 3.6 결과 화면 UX 개선
- 분석 결과를 먼저 보여주고, 사용자가 버튼을 눌렀을 때만 추천 상품을 로드하도록 흐름 제어
- 설명 → 분석 요약 → 스타일 팁 → 포인트 컬러 → 상품 추천 순으로 정보 구조를 배치해 사용자 이해도 향상
- 단순 추천 결과가 아니라 “분석된 취향을 바탕으로 이어지는 쇼핑 경험”을 구현

---

## 4. 기술 스택

### Frontend
- **HTML5**
- **CSS3**
- **Vanilla JavaScript**

### Backend
- **Python 3**
- **FastAPI**
- **Pydantic**
- **Uvicorn**

### Recommendation / Data Modeling
- **K-Means Clustering**
- **Cosine Similarity**
- **AI-HUB 연도별 패션 선호도 파악 및 추천 데이터 기반 `fashion_data.csv` 구성**
- **설문 응답 특징값 기반 스타일/핏/컬러 매칭 로직**

### Recommendation / AI
- **Hugging Face CLIP**
- **Multimodal Embedding**
- **AI-HUB 패션 이미지/스타일 데이터 기반 파인 튜닝**

### Data Collection
- **requests**
- **BeautifulSoup4**
- **Selenium**
- **undetected-chromedriver**

### Serving / Runtime
- **BentoML 기반 CLIP 추론 서버**
- **Docker / Docker Compose**

---

## 5. 시스템 구성 및 추천 흐름

### 5.1 전체 흐름
1. 사용자가 설문을 작성한다.
2. 프론트엔드가 `/profile` API로 설문 데이터를 전달한다.
3. 백엔드가 사용자 프로필과 스타일 검색 문맥을 생성한다.
4. `/recommendations` API가 `fashion_data.csv`를 기반으로 유사한 데이터셋 아이템을 찾고, 취향 분석 결과와 설명 텍스트를 반환한다.
5. 사용자가 맞춤 상품 추천 버튼을 클릭하면 `/crawl/musinsa`, `/crawl/zigzag`가 호출된다.
6. 각 크롤러가 쇼핑몰에서 후보 상품을 수집한다.
7. CLIP 추론 서버가 후보 이미지에 대해 스타일 유사도를 계산한다.
8. 백엔드가 AI 점수 기준으로 후보를 재정렬한 뒤 상위 상품을 사용자에게 보여준다.

### 5.2 왜 `fashion_data.csv`를 사용했는가
초기에는 사용자 군집화 모델 파일(`kmeans_model.pkl`) 중심으로 추천 근거를 관리했지만, 포트폴리오와 유지보수 관점에서는 **추천 기준이 어떤 데이터에 의해 형성되는지 직접 드러나는 구조**가 더 적합하다고 판단했습니다.

그래서 AI-HUB의 **연도별 패션 선호도 파악 및 추천 데이터**를 기반으로,
- 연도(era)
- 스타일(style)
- 성별(gender)
- 설문 특징값(Q3, Q411~Q4216)

을 정리한 `fashion_data.csv`를 프로젝트 내부에 포함했습니다.

이 CSV는 **K-Means 기반 스타일 군집화와 코사인 유사도 계산에 활용할 수 있도록 정제된 추천 기준 데이터**로 사용되며, 기존 피클 파일을 대체하는 역할을 합니다. 덕분에 추천 로직의 입력 데이터와 특징값을 코드/버전 관리 체계 안에서 함께 추적할 수 있게 되었습니다.

### 5.3 AI-HUB 기반 추천 방식
설문 기반 추천은 아래 순서로 동작합니다.

#### 1) 프로필 생성 단계
- 사용자의 설문 응답을 바탕으로 성별, 핏, 퍼스널컬러, 대표 스타일, 보조 스타일을 추출
- 스타일 키워드와 쇼핑몰 검색용 문맥을 함께 생성

#### 2) 데이터셋 매칭 단계
- `fashion_data.csv`에서 사용자와 유사한 패션 샘플을 탐색
- 스타일 특징 벡터와 TPO 응답 벡터를 조합해 코사인 유사도 계산
- 유사한 샘플들의 분포를 기반으로 대표 시대감성과 스타일 프로필을 도출

#### 3) 추천 랭킹 단계
- 데이터셋과의 유사도 결과를 바탕으로 대표 스타일을 보정
- 핏, 컬러, 스타일 요소를 결합한 가중치 점수로 추천 후보를 정렬
- 분석 요약 카드와 함께 설명 가능한 결과를 반환

### 5.4 왜 CLIP을 도입했는가
초기 설계는 설문 기반 규칙 추천과 데이터셋 유사도 분석에 강점이 있었지만, 실제 상품 이미지의 분위기와 사용자가 기대하는 감성적 스타일을 충분히 반영하기에는 한계가 있었습니다.

이를 보완하기 위해 **이미지와 텍스트를 같은 임베딩 공간에서 비교할 수 있는 CLIP 모델**을 도입했습니다. 특히 AI-HUB 패션 이미지와 스타일 설명 데이터로 CLIP을 파인 튜닝함으로써, 범용 모델이 아니라 **패션 도메인에 특화된 추천 엔진**으로 활용할 수 있도록 설계했습니다.

### 5.5 CLIP 기반 고도화 방식
멀티모달 추천은 아래 순서로 동작합니다.

#### 1) 학습 단계
- AI-HUB의 패션 이미지 + 스타일 텍스트 데이터를 활용해 CLIP 모델 파인 튜닝
- 패션 스타일 분류와 분위기 매칭에 유리하도록 도메인 적응 수행

#### 2) 후보 분석 단계
- 무신사, 지그재그에서 수집한 상품 이미지를 파인 튜닝된 CLIP 이미지 인코더에 입력
- 각 상품 이미지를 특징 벡터로 변환
- 추천 후보군에 대해 실시간 점수 계산 방식으로 적용

#### 3) 추론 단계
- 사용자 설문 결과를 바탕으로 페르소나 텍스트 또는 대표 스타일 라벨 생성
- 동일한 CLIP 계열 인코더 기준에서 텍스트-이미지 유사도 계산
- 코사인 유사도 기반으로 상품을 재정렬하여 최종 추천에 반영

### 5.6 왜 텍스트와 이미지 모두 동일한 파인 튜닝 모델을 써야 하는가
멀티모달 추천에서 중요한 점은 텍스트 벡터와 이미지 벡터가 **같은 잠재 공간(latent space)** 에 존재해야 한다는 것입니다.

- 텍스트만 파인 튜닝된 인코더를 사용하고
- 이미지는 기존 범용 인코더를 사용하면

비교 기준이 달라져 유사도 계산의 품질이 떨어질 수 있습니다.

따라서 본 프로젝트는 파인 튜닝된 CLIP을 추천 시스템의 핵심 엔진으로 보고,
**사용자 취향 텍스트와 상품 이미지 양쪽 모두를 동일 기준으로 해석하는 구조**를 지향했습니다.

---

## 6. CLIP 추론 서버 연동

백엔드의 `backend/app/services/ai_similarity_service.py`는 별도의 CLIP 추론 서버에 상품 이미지를 전달해 스타일 점수를 받아옵니다. 현재 구현은 다음 흐름을 따릅니다.

- 상품 이미지 URL 다운로드
- 이미지를 base64로 인코딩
- `/predict` 엔드포인트에 후보 스타일 라벨과 함께 전달
- 응답으로 받은 스타일별 점수 중 목표 스타일 점수를 `ai_score`로 사용
- 여러 상품을 병렬 처리한 뒤 AI 점수 기준으로 재정렬

추론 서버는 운영 환경에서 별도 서빙되며, 헬스 체크와 상태 확인, 추론 요청을 분리한 API 구조로 관리할 수 있도록 설계했습니다.

---

## 7. 프로젝트 구조

```text
scaffold/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI 진입점 및 핵심 API 정의
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── routes/recommendation.py
│   │   ├── crawlers/
│   │   │   ├── musinsa_crl.py          # 무신사 크롤러
│   │   │   ├── zigzag_crl.py           # 지그재그 크롤러
│   │   │   └── recommendation_search_profile.py
│   │   ├── logic/
│   │   │   ├── fashion_config.py       # 스타일/색상/핏 매핑 설정
│   │   │   ├── fashion_data.csv        # AI-HUB 연도별 패션 선호도 파악 및 추천 데이터 기반 추천 데이터셋 
│   │   │   ├── item_feature_builder.py # 데이터셋/상품 특징 로딩 및 파싱
│   │   │   ├── recommender.py          # 유사도 계산 및 추천 랭킹
│   │   │   └── survey_parser.py        # 설문 응답 파싱
│   │   ├── schemas/
│   │   │   ├── recommendation.py
│   │   │   └── survey.py
│   │   ├── services/
│   │   │   ├── ai_similarity_service.py # CLIP 추론 서버 연동
│   │   │   └── recommendation_service.py
│   │   └── utils/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── index.html
│   ├── survey.html
│   ├── result.html
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── survey.js
│   │   ├── result.js
│   │   └── utils.js
│   └── assets/images/
├── docs/
│   ├── architecture.md
│   └── screenshots/
├── docker-compose.yml
└── README.md
```

---

## 8. 배포 방법

이 프로젝트는 현재 `FastAPI`가 `frontend` 정적 파일까지 함께 서빙하도록 구성되어 있으므로, 배포 시에는 **단일 Docker 서비스**로 올리는 방식이 가장 간단합니다.

### 로컬에서 배포용 실행 확인

프로젝트 루트에서 아래 명령으로 실행할 수 있습니다.

```bash
docker compose up --build
```

실행 후 접속 주소:

- 메인 화면: `http://localhost:8001`
- 헬스체크: `http://localhost:8001/health`

### 클라우드 배포

루트 `Dockerfile` 기준으로 아래와 같은 Docker 지원 플랫폼에 바로 배포할 수 있습니다.

- Render
- Railway
- Fly.io
- EC2 + Docker

배포 설정 핵심값:

- Build Context: 프로젝트 루트
- Dockerfile Path: `Dockerfile`
- Port: `8000`

로컬 Docker Compose 실행은 기존 개발 서버와 충돌을 피하기 위해 호스트 `8001` 포트를 사용하도록 설정되어 있습니다.

일부 플랫폼은 `PORT` 환경변수를 자동 주입하는데, 현재 실행 명령은 이를 반영하도록 되어 있습니다.

#### Render 기준

- 서비스 타입: `Web Service`
- Runtime: `Docker`
- Dockerfile Path: `./Dockerfile`
- Docker Context: `.`
- Health Check Path: `/health`

저장소 루트에 `render.yaml`도 추가되어 있어서, Render Blueprint 방식으로 연결해도 동일하게 배포할 수 있습니다.

### 참고

- 현재 추천 데이터셋(`Sample.zip`, `sample_data`)이 없으면 API는 mock 데이터 기반으로 동작할 수 있습니다.
- 실제 추천 이미지까지 함께 배포하려면 데이터셋 파일을 `backend/` 아래에 포함하거나, 외부 스토리지 경로를 연결해야 합니다.

## 9. 스크린샷

![mapssi 시연](https://github.com/user-attachments/assets/8e3051ea-9fe4-4ef0-82e9-a3b08a429a0a)


### 9.1 결과 화면 - 분석 요약 카드
사용자의 스타일 분석 결과를 시대감성, 대표 스타일, 성별, 퍼스널컬러, 핏 정보와 함께 요약해 주는 UI입니다.

<img width="596" height="851" alt="스크린샷 2026-04-09 131327" src="https://github.com/user-attachments/assets/72dad37a-ab8f-4053-9347-806898097dcd" />

### 9.2 결과 화면 - 스타일 설명 / 스타일 팁 / 포인트 컬러
추천 결과를 단순 상품 카드로 끝내지 않고, 스타일 설명과 코디 팁까지 함께 제공해 사용자가 결과를 더 잘 이해할 수 있도록 구성했습니다.

<img width="567" height="729" alt="스크린샷 2026-04-09 131335" src="https://github.com/user-attachments/assets/9964ddc9-9cd3-4d0b-9f99-40f8a3a64cb2" />

### 9.3 CLIP 연동 기반 실시간 상품 분석 로그
크롤러가 수집한 상품 후보를 대상으로 CLIP 추론 서버가 병렬 유사도 분석을 수행하는 과정입니다.

<img width="742" height="235" alt="image" src="https://github.com/user-attachments/assets/35293756-e1fb-471c-9d43-2a3e6ea998e8" />

---

## 10. 개발 과정에서 겪은 이슈와 해결 과정

### 이슈 1. 추천 근거를 모델 파일보다 데이터 중심으로 관리할 필요가 있었다
초기에는 `kmeans_model.pkl`처럼 직렬화된 모델 파일 중심으로 추천 구조를 설명하려고 했지만, 이 방식은 포트폴리오와 협업 관점에서 **어떤 데이터가 추천 근거가 되는지 한눈에 드러나지 않는 문제**가 있었습니다.

#### 해결
- AI-HUB의 **연도별 패션 선호도 파악 및 추천 데이터**를 기반으로 추천용 CSV를 별도로 구성
- `fashion_data.csv`에 연도, 스타일, 성별, 설문 특징값을 정리해 프로젝트 내부 자산으로 포함
- K-Means와 코사인 유사도 기반 추천 흐름을 데이터셋 중심으로 설명 가능하도록 구조 전환

#### 결과
피클 파일에 의존하지 않고도 추천 기준 데이터를 코드와 함께 직접 관리할 수 있게 되었고, 추천 로직의 입력과 근거를 README와 코드에서 더 투명하게 설명할 수 있었습니다.

### 이슈 2. 설문 기반 추천만으로는 이미지 분위기 반영이 어려웠다
초기 버전은 설문 응답을 구조화해 스타일 설명을 만드는 데에는 강점이 있었지만, 실제 서비스 관점에서는 “속성은 맞는데 분위기가 다른 상품”이 추천되는 문제가 있었습니다.

#### 해결
- 이미지와 텍스트를 함께 다루는 멀티모달 모델 도입 필요성을 확인
- Hugging Face CLIP 모델을 AI-HUB 패션 데이터로 파인 튜닝
- 사용자의 스타일 텍스트와 상품 이미지 유사도를 함께 반영하는 방향으로 추천 구조 확장

#### 결과
설문 기반 추천의 해석 가능성을 유지하면서도, 실제 상품 이미지의 무드와 스타일 감성을 더 잘 반영하는 추천 구조로 발전시킬 수 있었습니다.

### 이슈 3. 텍스트와 이미지의 비교 기준을 일치시켜야 했다
멀티모달 추천에서 텍스트 벡터와 이미지 벡터가 서로 다른 기준으로 생성되면 유사도 계산 자체가 불안정해집니다.

#### 해결
- 텍스트와 이미지 모두 동일한 CLIP 계열 모델 기준으로 비교하도록 설계
- 사용자 페르소나 텍스트와 상품 이미지가 같은 특징 공간에서 비교되도록 구조화

#### 결과
추천 점수 해석의 일관성이 높아졌고, 왜 특정 상품이 선택되었는지 설명하기 쉬워졌습니다.

### 이슈 4. 크롤링 결과의 품질 편차가 컸다
쇼핑몰 크롤링 특성상 같은 카테고리라도 실제 스타일이 섞여 들어오는 문제가 있었습니다. 단순 키워드 검색만으로는 후보군 정제가 충분하지 않았습니다.

#### 해결
- 1차로 넉넉하게 후보군을 수집
- 2차로 CLIP 추론 서버를 통해 병렬 스타일 분석 수행
- `ai_score` 기준으로 후보를 다시 정렬해 상위 상품만 노출

#### 결과
초기 검색 결과의 노이즈를 줄이고, 사용자 기대 스타일과 더 가까운 상품이 상단에 배치되도록 개선했습니다.

### 이슈 5. 추론 서버를 애플리케이션 서버와 분리해야 했다
CLIP 추론은 일반 API 처리보다 무겁고, 모델 로딩 상태나 GPU 사용 가능 여부를 별도로 점검할 필요가 있었습니다.

#### 해결
- 추론 기능을 별도 API 서버로 분리
- 상태 확인과 운영성을 위해 헬스 체크, 상태 조회, 추론 엔드포인트를 분리해 관리
- 백엔드 서비스는 추론 서버를 호출하는 방식으로 결합도를 낮춤

#### 결과
웹 서비스 로직과 AI 추론 로직을 분리해 유지보수성과 운영 안정성을 확보했습니다.

### 이슈 6. 결과 화면에서 사용자 경험 흐름을 조정해야 했다
초기에는 결과 화면 진입 직후 더미 상품이 먼저 노출되어, 사용자가 “분석 결과를 본 뒤 상품을 본다”는 흐름보다 “상품부터 보는 느낌”을 더 강하게 받았습니다.

#### 해결
- 결과 화면 진입 시에는 분석 요약과 스타일 설명을 먼저 노출
- 사용자가 버튼을 눌렀을 때만 맞춤 상품을 불러오도록 렌더링 순서를 조정

#### 결과
서비스 경험이 더 자연스러워졌고, 추천의 근거를 먼저 이해한 뒤 상품을 확인하는 구조로 개선되었습니다.

---

## 11. 배운 점

이 프로젝트를 통해 단순히 추천 결과를 반환하는 것보다,
**왜 이 추천이 나왔는지 설명할 수 있는가** 와 **사용자가 실제로 납득할 수 있는 결과인가** 가 서비스 품질에 더 중요하다는 점을 배웠습니다.

특히 다음과 같은 경험을 얻을 수 있었습니다.

- 설문 데이터를 서비스 로직이 활용할 수 있는 형태로 모델링하는 경험
- AI-HUB 기반 추천 데이터셋을 서비스 코드 안에서 관리하는 경험
- K-Means와 코사인 유사도 기반 추천 흐름을 설명 가능한 형태로 정리한 경험
- 규칙 기반 추천과 멀티모달 재랭킹을 조합하는 경험
- 크롤링 데이터의 품질 문제를 후처리와 재정렬로 개선하는 경험
- CLIP 멀티모달 모델을 추천 서비스에 연결해 서비스형 구조로 확장하는 경험
- 프론트엔드 UI/UX까지 포함해 분석 결과를 설명 가능한 형태로 전달하는 경험

---

## 12. 한 줄 요약

**맵시TI는 설문 기반 취향 분석, AI-HUB 기반 데이터 유사도 추천, CLIP 멀티모달 재랭킹을 결합해 사용자 취향 텍스트와 실제 상품 이미지를 함께 반영하는 개인화 패션 추천 경험을 구현한 프로젝트입니다.**
