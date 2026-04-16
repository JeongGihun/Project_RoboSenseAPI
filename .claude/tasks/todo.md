# TODO

> Plan Mode 결과가 저장되는 곳.
> 매 작업 시작 시 여기 기록하고 사용자 승인 후 Execute 진행.

---

## 포맷

```markdown
## YYYY-MM-DD (W?-D?) — 작업 제목

### Goal
작업 목표 한 문단

### Steps
- [ ] 1단계: ...
- [ ] 2단계: ...
- [ ] 3단계: ...

### Test Cases (TDD RED 대상)
- [ ] 테스트 1: ...
- [ ] 테스트 2: ...

### Success Criteria
- [ ] pytest 전체 통과
- [ ] 커버리지 유지 (70%+)
- [ ] 로컬 /health 스모크 테스트 통과
- [ ] (작업별 추가 기준)

### Notes
- 의사결정 지점
- 선택 근거
- 참조한 lessons.md 항목
```

---

## 누적 기록

## 2026-04-16 (W1 전체) — D1~D6 전체 보강

### Goal
RoboSenseAPI에 테스트/인증/로깅/CI-CD/OpenAPI/예외핸들러 6개 보강 한번에 구현

### Steps
- [ ] D1-D2: 테스트 인프라 (conftest.py + test_sensors/robots/stats + 커버리지 70%)
- [ ] D3: API Key 인증 (auth.py + admin_routes + Depends 적용)
- [ ] D4: 구조화 로깅 + /health + /metrics
- [ ] D5: CI/CD 파이프라인 (ci.yml + deploy.yml)
- [ ] D6: 커스텀 예외 핸들러 + OpenAPI 기반

### Test Cases (TDD RED 대상)
- [ ] test_sensors: POST 정상/에러, GET 목록/개별/404, 페이지네이션, 필터링
- [ ] test_robots: POST/GET/PUT 정상/에러/404
- [ ] test_stats: 기본/커스텀 시간, 캐시
- [ ] test_auth: 키 없음/무효/유효/폐기 → 401/200
- [ ] test_admin: 발급/목록/폐기
- [ ] test_health: 정상/DB다운/Redis다운
- [ ] test_metrics: 필수필드/요청반영
- [ ] test_exceptions: 통일 포맷 검증

### Success Criteria
- [ ] pytest 전체 통과
- [ ] 커버리지 70%+
- [ ] ruff 린트 통과
- [ ] Docker 빌드 + /health 200
- [ ] API Key 인증 동작 (유효→200, 무효→401)

### Notes
- sensor_cpp C++ 모듈은 conftest.py에서 sys.modules mock
- SQLite in-memory + fakeredis 사용
- SHA-256+salt 해시 (bcrypt 불필요)
- lessons.md 비어있음 (첫 작업)
