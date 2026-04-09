# System Architecture (시스템 아키텍처)

**문서 작성자:** 조은별
**최종 수정일:** 2026년 4월 6일

---

## 1. 시스템 개요 (System Overview)

본 시스템은 사용자의 설문 응답을 분석하여 개인화된 패션 상품을 추천하는 웹 서비스입니다. 전체 아키텍처는 관심사 분리(Separation of Concerns) 원칙에 따라 크게 4개의 계층(Layer)으로 설계되었습니다. 

1. **Client Layer:** 경량화된 프론트엔드 환경
2. **API Layer:** FastAPI 기반의 백엔드 인터페이스
3. **Python Logic Module:** 데이터 분석 및 추천 알고리즘 핵심 로직
4. **Crawler Layer:** 외부 쇼핑몰 데이터 동적 수집

---

## 2. 계층별 상세 설계 (Layer Details)

### 2.1. Client Layer (Frontend)
순수 HTML, CSS, JavaScript로 구성되어 별도의 빌드 과정 없이 가볍고 빠르게 동작합니다.
* **주요 역할:** * 사용자로부터 설문 데이터 입력 접수
  * 백엔드 API와의 비동기 통신 (JSON 포맷)
  * 추천된 Top 5 아이템 및 데이터셋 기반 Top 6 갤러리 이미지 시각화

### 2.2. API Layer (FastAPI Backend)
프론트엔드와 내부 파이썬 로직을 연결하는 중간 서버 역할을 수행합니다.
* **`/dataset-recommendations/gallery`**: 데이터셋 추천 이미지 Top 6를 반환하여 갤러리 화면 렌더링을 지원합니다.
* **`/dataset/prepare`**: 추천에 필요한 원본 이미지 및 데이터 Zip 파일의 압축을 해제하고 파싱을 준비합니다.
* **`/recommendations`**: 클라이언트로부터 설문 데이터(JSON)를 수신하고, 내부 분석 및 추천 로직을 트리거한 뒤 최종 결과를 반환합니다.

### 2.3. Python Logic Module (Core Recommendation)
시스템의 핵심 비즈니스 로직을 담당하며, 사용자 데이터를 분석하고 모델을 통해 최적의 결과를 도출합니다.
* **`survey_parser.py`**: 설문 기반 사용자 프로필을 빌드하고 크롤링에 필요한 핵심 키워드를 도출합니다.
* **`fashion_config.py`**: 설문 키워드와 실제 쇼핑몰 검색용 키워드 간의 맵핑 가이드를 제공합니다.
* **`item_feature_builder.py`**: 크롤러가 수집한 JSON 파일을 파싱하여 전체 아이템의 특징(Feature) 벡터를 생성합니다.
* **`recommender.py`**: 도출된 사용자 프로필과 생성된 아이템 특징 벡터를 기반으로 Scikit-learn의 K-Means 알고리즘을 활용해 점수 계산 및 필터링을 수행하여 최종 Top 5를 추출합니다.

### 2.4. Crawler Layer (Data Collection)
동적 웹 페이지 크롤링을 통해 실시간에 가까운 패션 트렌드 및 상품 데이터를 수집합니다.
* **도구:** Selenium, Undetected-Chromedriver (봇 탐지 우회)
* **대상 플랫폼:** * 무신사 (키워드/품목 기반 검색)
  * 지그재그 (키워드/품목 기반 검색)

---

## 3. 데이터 흐름 (Data Flow)

시스템 내 주요 데이터 흐름은 다음과 같이 진행됩니다.

1. **[초기 설정]** Client가 API Layer의 `/dataset/prepare`를 호출하면, Python Logic이 Zip 파일을 해제하고 `fashion_config.py`를 참조하여 기본 설정을 준비합니다.
2. **[갤러리 요청]** Client가 갤러리 화면 렌더링을 위해 API Layer(`/dataset-recommendations/gallery`)로 요청을 보내면, 시스템이 사전에 준비된 추천 이미지 Top 6를 반환합니다.
3. **[설문 제출]** 사용자가 프론트엔드에서 설문을 완료하면, Client Layer가 설문 데이터(JSON)를 `/recommendations` 엔드포인트로 전송합니다.
4. **[분석 및 크롤링 트리거]** API Layer는 응답 분석을 위해 `survey_parser.py`로 데이터를 넘기고, 파서는 사용자 프로필과 쇼핑 키워드를 도출하여 Crawler Layer(무신사, 지그재그)로 전달합니다.
5. **[특징 추출]** Crawler Layer가 수집한 상품 데이터를 반환하면, `item_feature_builder.py`가 이를 받아 각 상품의 특징 벡터(데이터셋)를 구성합니다.
6. **[추천 실행]** `recommender.py`는 `survey_parser`로부터 전달받은 사용자 프로필 점수와 `item_feature_builder`가 구성한 상품 특징 벡터를 매칭(K-Means 등 활용)하여 점수를 계산하고 최종 Top 5 아이템을 추출합니다.
7. **[결과 반환]** 추출된 최종 아이템 리스트가 API Layer를 거쳐 Client Layer로 전달되어 화면에 출력됩니다.

---

## 4. 기술 스택 (Technology Stack)

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python 3.x, FastAPI, Pydantic, Uvicorn
* **AI/ML:** Scikit-learn (K-Means Clustering), Pandas, NumPy
* **Crawling:** Selenium, Undetected-Chromedriver