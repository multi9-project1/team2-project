# 👗 맵시TI (Mapsi-TI) : Demo Version
> **나의 색(Personal Color)과 마음(Fashion MBTI)이 만나는 지점, AI 맞춤형 스타일 페르소나 큐레이션 서비스**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?logo=googlegemini&logoColor=white)

---

## 🌟 Project Overview
**맵시TI**는 사용자의 **퍼스널 컬러**와 무의식적인 **패션 취향(Fashion MBTI)**을 결합하여 최적의 '인생 스타일 페르소나'를 찾아주는 AI 큐레이션 서비스입니다. 단순한 추천을 넘어, 분석된 페르소나에 기반한 실시간 커머스 딥링크를 제공하여 탐색에서 구매까지의 여정을 혁신합니다.

---

##

본 프로젝트는 Mapsi-ti 프로젝트를 진행함에 있어 우선적으로 시각화 하여 테스트 하는 Demo Project 입니다.

1. **데이터 효율성 저하**: 방대한 이미지 데이터 전처리에 필요한 리소스와 시간의 비효율성.
2. **최신 트렌드 반영의 한계**: 고정된 데이터셋은 빠르게 변하는 패션 트렌드를 즉각적으로 반영하기 어려움.
3. **인프라 비용 문제**: 대규모 데이터를 서빙하기 위한 서버 유지 비용 발생.

**💡 Solution: Pivot to 'Light Version'**
우리는 고정된 데이터셋을 과감히 폐기하고, **'LLM(Google Gemini 1.5 Flash)의 방대한 사전 학습 패션 지식'**과 **'실시간 커머스 검색 엔진'**을 직접 연결하는 아키텍처로 전면 수정했습니다.

*   **결과**: 
    - 개발 속도 극대화 및 서버 유지 비용 **0원** 달성.
    - 사용자에게 **항상 최신 유행하는 실시간 상품**을 추천할 수 있는 동적 큐레이션 시스템 구축.
    - 모델 학습 없이도 정교한 스타일 페르소나 네이밍과 코디 팁 제공.

---

## ✨ Key Features
- **🎨 퍼스널 컬러 선택**: 사계절 12톤 기반의 정밀한 컬러 타입 입력.
- **📸 패션 취향 이미지 퀴즈**: 14장의 대표 이미지를 활용한 7문항 A/B 테스트를 통해 사용자의 잠재적 스타일 선호도 파악.
- **🤖 AI 페르소나 생성**: LangChain을 활용하여 "여름 쿨톤의 도시적 미니멀리스트✨"와 같은 위트 있는 네이밍 및 3줄 핵심 코디 팁 제공.
- **🚀 실시간 커머스 딥링크**: LLM이 추출한 스타일 키워드를 기반으로 **무신사(Musinsa)** 및 **지그재그(Zigzag)** 검색 결과로 즉시 연결.
- **📢 결과 공유 및 바이럴**: SNS(인스타그램, 트위터) 최적화 포맷으로 분석 결과 복사 기능 제공.

---

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Frontend**: Streamlit
- **AI/LLM**: LangChain, gpt-4o-mini
- **Environment**: python-dotenv, Pydantic (Structured Output)

---

## 📂 Directory Structure
```
Mapsi-TI-Demo/
├── test-screenshot/
├── app.py              # Streamlit UI 및 세션 상태 관리 메인 로직
├── logic.py            # LangChain 기반 LLM 분석 및 데이터 파싱 로직
├── requirements.txt    # 프로젝트 의존성 라이브러리
├── project_context.md  # 프로젝트 컨텍스트 설명
├── README.md           # 프로젝트 문서
└── test-screenshot/
    ├── 첫화면.PNG              # 페이지 첫 화면 스크린샷
    ├── 퍼스널컬러 (1).PNG       # 퍼스널컬러 선택 페이지 스크린샷
    ├── 퍼스널컬러 (2).PNG       # 퍼스널컬러 진단 페이지 스크린샷 (1)
    ├── 퍼스널컬러 (3).PNG       # 퍼스널컬러 진단 페이지 스크린샷 (2)
    ├── 퍼스널컬러 (4).PNG       # 퍼스널컬러 진단 페이지 스크린샷 (3)
    ├── 맵시TI퀴즈 (1).PNG      # 맵시TI 퀴즈 페이지 스크린샷 (1)
    ├── 맵시TI퀴즈 (2).PNG
    ├── 분석결과.PNG            # 퍼스널 컬러 & 맵시TI 퀴즈 분석 결과 페이지 스크린샷
    ├── 쇼핑 큐레이션 (0).PNG    # 쇼핑 큐레이션 페이지 스크린샷
    ├── 쇼핑 큐레이션 (1).PNG    # 쇼핑 큐레이션 페이지 키워드 선택 스크린샷 (1)
    ├── 쇼핑 큐레이션 (2).PNG    # 쇼핑 큐레이션 페이지 키워드 선택 스크린샷 (2)
    └── 상품 미리보기.PNG          # 상품 미리보기 페이지 스크린샷
```

---

## 🚀 Getting Started
### 1. 환경 설정 및 설치
```bash
# 레포지토리 클론
git clone https://github.com/your-username/Mapsi-TI.git
cd Mapsi-TI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 2. API Key 설정
`.env` 파일을 생성하거나 환경 변수에 직접 설정할 수 있습니다.
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 앱 실행
```bash
streamlit run app.py
```

---

## 👤 Contact
- **Developer**: 김명균 (Myeonggyun Kim)
- **Project Link**: [https://github.com/your-username/Mapsi-TI](https://github.com/your-username/Mapsi-TI)

---

## 📜 Work Log (프로젝트 작업 기록)

### 📅 2026-03-27
- **LLM 엔진 전환 기획**: OpenAI 기반 아키텍처에서 Google Gemini 전환 계획 수립.
- **의존성 업데이트**: `langchain-google-genai` 패키지 추가.
- **분석 로직 설계**: `JsonOutputParser` 대신 `with_structured_output` (Pydantic) 기반 구조화된 출력 방식 도입.

### 📅 2026-03-30
- **기본 정보 확장**: 성별 외 **연령대(10대~60대)** 선택 기능 추가 및 AI 프롬프트 연동.
- **페르소나 서사 고도화**: 단순 스타일 명칭에서 벗어나 감성적이고 서사적인 페르소나 설명(2~3문장) 생성 로직 구현.
- **12분류 퍼스널 컬러 최적화**: 사계절 12톤별 **Best/Worst 컬러 매칭 가이드**를 AI 프롬프트에 내재화하여 추천 정확도 향상.
- **쇼핑 큐레이션 강화**:
    - 분석 결과 출력 후 **의복 종류 및 추천 색상**을 선택하여 실시간 쇼핑 검색어를 생성하도록 UI 개선.
    - **무신사/지그재그** 검색 파라미터 최적화 (성별 필터, 인기순 정렬 적용).
- **UI/UX 개선**: 결과 페이지 텍스트 가시성(검은색) 및 섹션별 디자인 통일감(Border-left 등) 부여.
- **버튼 중복 및 ID 충돌 해결**: `StreamlitDuplicateElementId` 오류 수정 및 분석 버튼 로직 통합.

### 📅 2026-03-31
- **프리미엄 UI/UX 전면 개편**: `mapsi-ti-step1.html` 디자인을 완벽 이식하여 다크 & 골드 테마의 고급스러운 인터페이스 구축.
- **'모르겠어요' 분석 로직 추가**: 퍼스널 컬러 진단 전 사용자를 위한 무채색 및 베스트셀러 기반 큐레이션 기능 통합.
- **전체 코드 리팩토링 및 경량화**:
    - **TPO 섹션 제거**: 사용자 경험 간소화를 위해 불필요한 '상황' 선택 단계를 삭제하고 분석 로직을 핵심 데이터 위주로 재설계.
    - **Clean Code 구현**: `app.py`와 `logic.py` 내의 미사용 변수, 중복 로직, 예전 기능의 잔재를 모두 제거하여 가독성과 유지보수성 극대화.
- **버그 수정**: 퍼스널 컬러 명칭과 쇼핑 큐레이션 데이터 간의 불일치('여름 브라이트' 등) 해결.
- **OpenAI 엔진 안정화**: Pydantic 기반의 구조화된 데이터 추출 방식을 통해 분석 신뢰도 및 속도 최종 개선.

### 📅 2026-04-01 (최종 고도화 및 엔진 최적화 완료)
- **취향 퀴즈 대개편**: 6문항의 심층 분석 퀴즈 도입 및 스타일별 Top 3 점수 산출 로직 구현.
- **실시간 쇼핑 통합 미리보기**: 무신사와 지그재그 인기 상품을 원클릭으로 동시 수집하는 통합 엔진 구축.
- **크롤링 안정화 및 봇 우회**: 강력한 헤드리스 모드와 정밀 셀렉터 적용으로 무신사/지그재그 데이터 수집 성공률 극대화.
- **성별 맞춤형 UI 레이아웃**: 남성용 중앙 집중형 뷰 및 여성용 좌우 비교 뷰를 도입하고 성별에 따른 카테고리 필터링 적용.
- **클릭 가능 커머스 딥링크**: 모든 상품 카드에 실시간 상세 페이지 링크를 연결하여 구매 동선 완성.
- **사용자 경험(UX) 혁신**: 결과 페이지 자동 상단 스크롤, 세션 기반 데이터 유지, 퍼스널 컬러 정밀 자가 진단 스텝 추가.
- **언어 및 성능 정교화**: AI 텍스트 표준 외래어 준수 가이드 적용 및 세션 관리 로직 개선을 통한 ID 충돌 해결.

---
*Developed as a part of Personal Project focusing on Lightweight AI Architecture.*
