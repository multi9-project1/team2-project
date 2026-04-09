# 맵시TI 정적 프론트엔드 (HTML / CSS / JS)

이 폴더는 FastAPI 백엔드와 연결되는 정적 프론트엔드입니다.

이번 수정본에서는 UI에서 `API 상태`, `백엔드 gallery-demo`, `TOP 추천 카드` 영역을 제거하고, 분석 결과와 쇼핑 큐레이션 중심으로 정리했습니다.

## 파일 구성

- `index.html` - 화면 마크업 엔트리
- `css/style.css` - 목업 기반 스타일
- `js/constants.js` - 설문 문항, 페르소나, 카테고리, API 기본값
- `js/api.js` - 백엔드 호출 래퍼
- `js/app.js` - 화면 흐름 / 상태 / 결과 렌더링
- `assets/images/README.md` - 필요한 이미지 파일명 목록
- `assets/fonts/README.md` - 필요한 폰트 파일명 목록

## 설문 흐름

성별 -> 퍼스널컬러 -> 스타일 -> 핏

퍼스널컬러 단계에서는
- `알아! 바로 선택할래` 선택 시 12가지 퍼스널컬러를 직접 선택
- `모르겠어 ... 진단해줘` 선택 시에만 Q1~Q3 진단과 웜/쿨 후속 선택 진행

즉, `몰라요` 흐름일 때만 추가 진단이 열리며, 중복 설문이 나오지 않습니다.

## 백엔드 연결 엔드포인트

- `POST /profile`
- `POST /recommendations`
- `POST /crawl/musinsa`
- `POST /crawl/zigzag`

기본 API 주소는 `js/constants.js`에서 수정할 수 있습니다.

```js
export const API_BASE_URL = 'http://127.0.0.1:8000';
export const API_PREFIX = '';
```

백엔드에서 `/api` prefix를 쓴다면 `API_PREFIX = 'api'`로 바꾸면 됩니다.

## 실행 방법

정적 파일이므로 아무 서버에서나 바로 띄울 수 있습니다.
예시:

```bash
cd mapsiti-static-frontend
python3 -m http.server 5500
```

브라우저에서 `http://127.0.0.1:5500` 접속

## 폰트

폰트 파일은 보안/배포상 포함하지 않았습니다.
아래 파일명을 `assets/fonts` 폴더에 직접 넣어주세요.

- `MonaS12TextKR.woff2`
- `MonaS12-Bold.woff2`
- `Mona12ColorEmoji.woff2`

## 이미지

아래 파일명을 `assets/images` 폴더에 넣으면 목업과 동일한 흐름으로 바로 연결됩니다.

- 성별 선택
  - `male_select.png`
  - `female_select.png`
- 페르소나
  - `casual_m.png`, `casual_w.png`
  - `feminine_m.png`, `feminine_w.png`
  - `hipster_punk_m.png`, `hipster_punk_w.png`
  - `mannish_m.png`, `mannish_w.png`
  - `modern_minimal_m.png`, `modern_minimal_w.png`
  - `retro_m.png`, `retro_w.png`
  - `romantic_m.png`, `romantic_w.png`
  - `sophisticated_m.png`, `sophisticated_w.png`
  - `sporty_m.png`, `sporty_w.png`
  - `street_m.png`, `street_w.png`

파일이 아직 없어도 화면은 fallback 카드로 깨지지 않게 처리되어 있습니다.
