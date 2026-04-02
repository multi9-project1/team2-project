# FastAPI 기반 패션 추천 로직

설문 응답을 받아 퍼스널컬러, 대표 스타일, 보조 스타일, 핏 선호를 계산하고 AI-Hub 라벨 구조와 유사한 아이템 특성에 대해 top-N 추천 결과를 반환하는 프로토타입입니다.

## 파일 구성

- `survey_parser.py`: 설문 응답 정규화와 사용자 프로필 계산
- `item_feature_builder.py`: `sample_data` 또는 zip의 JSON 라벨 파싱
- `recommender.py`: 스타일/핏/컬러 점수 계산과 랭킹
- `main.py`: FastAPI 엔드포인트
- `run_demo.py`: 샘플 설문 2개 실행

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

## API 예시

### 1. 서비스용 빠른 결과

```bash
curl -X POST http://127.0.0.1:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "survey": {
      "gender": "여성",
      "personal_color": "winter_deep",
      "Qstyle_1": "A",
      "Qstyle_2": "B",
      "Qstyle_3": "B",
      "Qstyle_4": "A",
      "Qstyle_5": "B",
      "Qstyle_6": "A"
    }
  }'
```

이 응답은 `user_profile`, `deeplink_context`만 빠르게 반환합니다.

### 2. 데이터셋 유사 이미지 갤러리

```bash
curl -X POST http://127.0.0.1:8000/dataset-recommendations/gallery \
  -H "Content-Type: application/json" \
  -d '{
    "survey": {
      "gender": "여성",
      "personal_color": "winter_deep",
      "Qstyle_1": "A",
      "Qstyle_2": "B",
      "Qstyle_3": "B",
      "Qstyle_4": "A",
      "Qstyle_5": "B",
      "Qstyle_6": "A"
    },
    "top_n": 5,
    "allow_mock_data": false,
    "prefer_extracted_dataset": true,
    "dataset_dir": "/Users/igyueun/Documents/New project/sample_data"
  }'
```

이 응답은 top 5 이미지를 한 번에 볼 수 있는 HTML 갤러리입니다.

## 데이터셋 연결

- `dataset_dir`: 이미 압축 해제된 라벨 루트 폴더
- `zip_path` + `extract_dir`: zip을 압축 해제하면서 로드
- 실제 데이터셋이 없으면 mock 아이템으로 fallback
- 현재 기본 경로는 `/Users/igyueun/Documents/New project/sample_data`
- 추천 결과의 `image_url`로 브라우저에서 샘플 이미지 직접 확인 가능

## 데모 실행

```bash
python3 run_demo.py
```
