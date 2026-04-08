# FastAPI 연동 버전 메모

이 프론트는 다음 순서로 동작합니다.

1. `survey.html` 완료 시 `POST /profile` 호출
2. 이어서 `POST /recommendations` 호출
3. 응답 원문은 `sessionStorage`에 저장 후 `result.html`에서 재사용

기본 API Base URL:
- 같은 origin에서 서빙되면 `window.location.origin`
- Live Server(5500/5501)에서는 `http://localhost:8000`

현재 프론트는 백엔드 스키마 차이를 견디기 위해 `/profile`, `/recommendations` 요청 payload를 몇 가지 형태로 순차 재시도합니다.
응답 키도 `profile`, `parsed_profile`, `recommendations`, `products`, `musinsa_products` 등 여러 패턴을 우선적으로 해석합니다.
