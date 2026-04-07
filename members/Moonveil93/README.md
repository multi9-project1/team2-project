# 개인 프로젝트: Moonveil93

> 이 디렉토리는 **Moonveil93** 의 개인 작업 공간입니다.

## 프로젝트 설명

1. 👗 지그재그(ZigZag) 맞춤형 패션 스타일 큐레이션 크롤러

사용자의 패션 취향(10가지 스타일)과 원하는 의류 종류(상의, 하의, 아우터 등)를 입력받아, 지그재그(ZigZag) 플랫폼에서 맞춤형 코디 아이템을 자동으로 찾아주는 웹 크롤링 프로젝트입니다.

💡 주요 기능
- **10가지 패션 스타일 맵핑**: 캐주얼, 스트릿, 오피스룩, 페미닌, 미니멀, 로맨틱 등 10가지 주요 스타일별 핵심 키워드와 추천 핏(Fit) 자동 조합
- **카테고리 기반 필터링**: 사용자가 선택한 타겟 카테고리(예: "상의", "하의", "전체")에 맞춰 세부 아이템(셔츠, 슬랙스, 스커트 등)을 선별하여 맞춤 검색
- **동적 키워드 생성**: [스타일 키워드] + [핏] + [세부 카테고리] 형태의 검색어를 동적으로 생성하여 검색 정확도 극대화
- **인기 상품 추출**: 검색 결과 중 인기순(SCORE_DESC) 상위 상품의 쇼핑몰 이름, 상품명, 가격, 이미지 링크 데이터 수집
- **안티 크롤링 우회**: undetected_chromedriver를 활용하여 봇 탐지를 우회하고 안정적인 백그라운드 데이터 수집 지원

📸 실행 결과 미리보기
src/ 디렉토리에 포함된 image (1).png ~ image (4).png 파일에서 터미널 기반의 크롤링 실행 결과와 스타일별 추천 코디 세트 내역을 확인할 수 있습니다.


2. Mapsi-ti 프로젝트를 진행함에 있어 우선적으로 시각화 하여 테스트 하는 Demo Project 입니다.

    1. **데이터 효율성 저하**: 방대한 이미지 데이터 전처리에 필요한 리소스와 시간의 비효율성.
    2. **최신 트렌드 반영의 한계**: 고정된 데이터셋은 빠르게 변하는 패션 트렌드를 즉각적으로 반영하기 어려움.
    3. **인프라 비용 문제**: 대규모 데이터를 서빙하기 위한 서버 유지 비용 발생.

**💡 Solution: Pivot to 'Light Version'**
우리는 고정된 데이터셋을 과감히 폐기하고, **'LLM(Google Gemini 1.5 Flash)의 방대한 사전 학습 패션 지식'**과 **'실시간 커머스 검색 엔진'**을 직접 연결하는 아키텍처로 전면 수정했습니다.

*   **결과**: 
    - 개발 속도 극대화 및 서버 유지 비용 **0원** 달성.
    - 사용자에게 **항상 최신 유행하는 실시간 상품**을 추천할 수 있는 동적 큐레이션 시스템 구축.
    - 모델 학습 없이도 정교한 스타일 페르소나 네이밍과 코디 팁 제공.

📸 실행 결과 미리보기
src/Mapsi-TI-Demo/test-screenshot/ 디렉토리에 포함된 .PNG 파일에서 데모버전 실행 결과를 확인할 수 있습니다.


3. 👗 Fashion-CLIP: 패션 특화 이미지-텍스트 파인튜닝

이 프로젝트는 일반적인 CLIP 모델을 약 3만 장의 한국 패션 데이터셋으로 파인튜닝하여, 스타일 페르소나를 정교하게 구분하는 **'패션 전문 AI 브레인'**을 구축하는 것을 목표로 합니다.

👗 **Fashion-CLIP: 패션 특화 이미지-텍스트 파인튜닝**
전 세계의 다양한 이미지를 학습한 기존 CLIP 모델에 한국 패션 스타일의 고유한 특징(스타일, 핏, 색감 등)을 추가로 학습시켜 분류 및 검색 성능을 극대화했습니다.

💡 **주요 기능 및 특징**
- **3만 건의 데이터셋 최적화**: 30,650장의 이미지와 각 이미지에 매칭되는 상세 영문 캡션(clip_training_data.csv)을 활용했습니다.
- **패션 전용 캡셔닝**: JSON 데이터를 CLIP이 선호하는 "A photo of a [era] [gender] [style]..." 형태의 자연어 문장으로 자동 변환하여 학습 효율을 높였습니다.
- **배치 분석 시스템**: 학습된 모델을 활용해 특정 폴더 내의 모든 이미지를 일괄 분석하고, 10가지 스타일별 유사도(Similarity Score)를 CSV 파일로 자동 도출합니다.
- **주로 사용된 10가지 스타일**: casual, streetwear, office wear, feminine, mannish, sporty, modern minimal, romantic, hipster, retro

⚙️ **기술적 최적화 (Hardware Specific)**
RTX 2080 및 9700K 환경에서 최적의 성능을 내기 위해 다음과 같은 기술을 적용했습니다.
- **Mixed Precision (AMP)**: `torch.cuda.amp`를 적용하여 8GB의 VRAM 환경에서도 메모리 부족 없이 안정적으로 학습 속도를 1.5배 가속했습니다.
- **멀티 프로세싱 데이터 로딩**: 9700K의 코어 성능을 활용하기 위해 `num_workers=4` 및 `pin_memory=True` 설정을 적용하여 데이터 병목 현상을 해결했습니다.
- **Windows 환경 안정화**: `KMP_DUPLICATE_LIB_OK` 설정을 통해 윈도우 라이브러리 충돌을 방지하고 학습 안정성을 확보했습니다.

📊 **학습 사양 및 결과**
- **GPU**: NVIDIA GeForce RTX 2080 (8GB VRAM)
- **CPU**: Intel Core i7-9700K (4.8GHz Overclocked)
- **RAM**: 32GB
- **Learning Rate**: 5e-6 (AdamW Optimizer)
- **Batch Size**: 8
- **성능**: 10가지 스타일 페르소나(캐주얼, 스트릿, 모던, 페미닌 등)에 대해 높은 신뢰도의 유사도 점수를 도출하며, 패션 이미지 분류 및 큐레이션 엔진으로 활용 가능합니다.

## 디렉토리 구조

```
members/Moonveil93/
├── .copilot-instructions.md   ← Agent 지시 파일 (수정 가능)
├── DEVLOG.md                  ← 변경사항 기록
├── environment.yml            ← conda 환경 파일
├── requirements.txt           ← pip 패키지 목록
├── README.md                  ← 이 파일
└── src/
    ├── ZigZagWebCrawler.py                ← 지그재그 웹 크롤링 코드
    ├── image (1).png                      ← 크롤링 결과 이미지 (1)
    ├── image (2).png                      ← 크롤링 결과 이미지 (2) 
    ├── image (3).png                      ← 크롤링 결과 이미지 (3)
    ├── image (4).png                      ← 크롤링 결과 이미지 (4)
=======
    ├── CLIP/                              ← Fashion-CLIP 파인튜닝 프로젝트
    │   ├── model_train.py          # CLIP 모델 파인튜닝 메인 로직 (RTX 2080 최적화)
    │   ├── model_test.py # 폴더 내 이미지 일괄 스타일 분석 및 CSV 저장 코드
    │   ├── label_turn.ipynb           # 파인튜닝 학습 과정 및 분석용 노트북
    │   ├── clip_training_data.csv         # 이미지-캡션 매핑 마스터 데이터 (30,650건)
    │   ├── style_analysis_results.csv     # 스타일 분석 결과 샘플 파일
    │   └── fine_tuned_clip_fashion/       # 파인튜닝이 완료된 모델 가중치 및 설정 파일
    └── MapseeTI-Demo/
>>>>>>> 4b77ed06 (CLIP model fine tuning)
        ├── app.py              # Streamlit UI 및 세션 상태 관리 메인 로직
        ├── logic.py            # LangChain 기반 LLM 분석 및 데이터 파싱 로직
        ├── requirements.txt    # 프로젝트 의존성 라이브러리
        ├── project_context.md  # 프로젝트 컨텍스트 설명
        ├── README.md           # 프로젝트 문서
        └── test-screenshot/
            └── ... (스크린샷 파일들)
```

## 실행 방법

### 1. ZigZag Web Crawler
```bash
# 환경 활성화
conda activate Moonveil93-env
# 실행
python src/ZigZagWebCrawler.py
```

### 2. MapseeTI Demo (Streamlit)
```bash
=======
# 필수 라이브러리 설치
pip install -r src/MapseeTI-Demo/requirements.txt
# API Key 설정 (환경변수 또는 .env)
# OPENAI_API_KEY=your_openai_api_key_here
# 앱 실행
streamlit run src/MapseeTI-Demo/app.py
>>>>>>> 4b77ed06 (CLIP model fine tuning)
```

### 3. Fashion-CLIP Fine-tuning
1. **필수 라이브러리 설치**
   ```bash
   pip install torch torchvision transformers pandas pillow tqdm
   ```
2. **파인튜닝 학습 시작**
   ```bash
   python src/CLIP/model_train.py
   ```
3. **폴더 내 이미지 일괄 분석 (테스트)**
   ```bash
   python src/CLIP/model_test.py
   ```

## 변경 이력

[DEVLOG.md](DEVLOG.md) 참조
