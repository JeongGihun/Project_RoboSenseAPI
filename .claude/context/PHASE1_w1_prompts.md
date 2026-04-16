# PHASE 1 — W1 Claude Code 프롬프트 모음

> 작성: 2026.04
> 사용 기간: 2026.04.20 ~ 04.25 (W1 1주)
> 배치 위치: `.claude/context/PHASE1_w1_prompts.md`
> 상위 문서: `CLAUDE.md`, `.claude/context/PHASE1.md`

---

## 사용법

### 사전 준비 (04.19 일요일)

1. 레포 루트에 `CLAUDE.md` 배치
2. `.claude/tasks/todo.md`, `.claude/tasks/lessons.md` 배치 (빈 템플릿)
3. `.claude/context/PHASE1.md`, `.claude/context/PHASE1_w1_prompts.md` 배치
4. Git 브랜치 준비: `integration` 브랜치 생성 (main과 동일한 상태)
5. Claude Code 실행 (`claude` 커맨드)

### 매일 진행 절차

1. **그날 feature 브랜치 체크아웃**
   - 예: `git checkout -b feat/w1-tests`
2. **Claude Code에 그날 프롬프트 전달**
3. **Plan Mode 검토** → 승인 → Execute
4. **9단계 사이클** 완료 (CLAUDE.md 참조)
5. **feature 브랜치에 커밋** → `integration` 브랜치로 PR & 머지
6. **다음 날 새 feature 브랜치 체크아웃**

**main 브랜치 직접 머지 금지**. 토요일 D6 끝나고 1회 통합 배포.

### 공통 주의

- 매 프롬프트는 **Plan Mode 요청**으로 끝남. Execute는 Plan 검토 후 별도 승인
- 의사결정 지점(해시 방식, 로거 구현 등)은 **Plan 단계에서 논의**
- Claude Code가 사용자 의도 재해석할 위험 있음 → Plan 꼼꼼히 검토
- 코드 생성 후 **반드시 `pytest` 실행**

---

## D1 (월, 04.20) — 테스트 코드 기초

**브랜치**: `feat/w1-tests`

```
프로젝트 맥락 확인을 위해 아래 순서로 파일 읽어:
1. CLAUDE.md (상시 규칙)
2. .claude/tasks/lessons.md (이전 실수 기록)
3. .claude/context/PHASE1.md (Phase 1 전체 맥락)
4. README.md, ARCHITECTURE_v1.0.md (프로젝트 구조)

그리고 app/ 폴더 훑어봐.

오늘은 W1-D1: 테스트 코드 기초 작업이야.
.claude/context/PHASE1_w1_prompts.md의 D1 섹션 기준으로 진행.

이 작업은 TDD 엄격 대상이 아니야 (테스트 코드 자체를 만드는 작업이니까).
하지만 테스트 설계 자체는 다음 원칙 따라:
- AAA 패턴 (Arrange, Act, Assert)
- 테스트 간 독립성 (DB 상태 격리)
- 한 테스트 = 한 시나리오

오늘 목표:
- conftest.py 작성: SQLite 인메모리 DB fixture + AsyncClient fixture
- test_sensors.py: POST/GET 정상/에러 케이스 기본 (확장은 내일)
- pytest, pytest-asyncio, httpx 를 requirements-dev.txt에 추가 (dev 분리)

제약:
- 기존 app/ 코드 수정 금지
- 기존 docker-compose 환경 영향 금지
- 테스트 실행이 일관되게 재현 가능해야 함 (flaky 금지)

성공 기준 (CLAUDE.md 사이클 6~9단계 기준):
- QA: pytest -v 전체 통과
- 각 테스트가 독립적으로 돌아감
- 커밋: feat/w1-tests 브랜치에 커밋

Plan Mode로 먼저 보여줘:
- 어떤 파일 만들지 (경로)
- 패키지 목록
- 테스트 케이스 분할 방식
- SQLite 인메모리 전환 방법
- .claude/tasks/todo.md에 기록할 plan 내용

Plan 검토 후 Execute.
```

---

## D2 (화, 04.21) — 테스트 확장 + 커버리지 70%

**브랜치**: `feat/w1-tests` (D1에서 이어서)

```
어제 D1에서 테스트 기초 세팅 완료. 
.claude/tasks/lessons.md 먼저 읽고 (새로 추가된 것 있으면) 반영해서 진행.

오늘은 W1-D2: 테스트 확장 + 커버리지 70% 작업.

오늘 목표:
- test_sensors.py 확장: 페이지네이션(Cursor), 필터링(robot_id, sensor_type), 에러 케이스
- test_robots.py 생성: 등록/조회/개별 조회/404
- test_stats.py 생성: Redis 캐시 동작, 캐시 무효화
- pytest-cov 설정 → app/ 커버리지 70% 이상
- conftest.py 공통 fixture로 중복 제거

제약:
- 기존 라우트 코드 건드리지 마
- 테스트 실행 시간 15초 이내
- 에러 응답 포맷 일관성 검증 (404, 422, 500)
- flaky 테스트 금지 (datetime.now() 등 주의)

성공 기준:
- pytest --cov 에서 app/ 70%+
- 전체 통과
- fixture 중복 제거 완료
- feat/w1-tests 브랜치에 커밋 → integration으로 PR & 머지

Plan Mode로 먼저 보여줘:
- 추가할 테스트 케이스 리스트 (파일별)
- 커버리지 70% 확보 전략 (어떤 부분 먼저)
- flaky 위험 지점 식별
- .claude/tasks/todo.md에 기록할 plan

Plan 검토 후 Execute.

작업 완료 후 .claude/tasks/lessons.md에 기록할 학습 있으면 제안.
```

---

## D3 (수, 04.22) — API Key 인증

**브랜치**: `feat/w1-api-key`

```
.claude/tasks/lessons.md 먼저 읽어.

오늘은 W1-D3: API Key 인증 (X-API-Key 헤더 방식) 작업.

**이 작업은 TDD 엄격 대상**. 
- RED: 실패하는 인증 테스트 먼저 작성
- GREEN: 최소 구현
- REFACTOR: 구조 개선

JWT 아닌 API Key 선택 이유: 로봇↔서버 시스템 간 통신이라 사람 로그인 없음. 
면접에서 "왜 JWT 안 썼어요?" 답변 예정 → 코드도 그 방향에 맞게.

오늘 목표 (TDD 순서):

### RED (실패 테스트 먼저)
- test_auth.py: 유효키 → 200, 무효키 → 401, 키 없음 → 401, 폐기키 → 401
- test_admin_api_keys.py: 관리자 키 발급/조회 테스트

### GREEN (테스트 통과 최소 구현)
- app/models/db_models.py: ApiKey 모델 (key_hash, robot_id FK, created_at, revoked)
- app/auth.py: X-API-Key 검증 함수 (FastAPI Depends)
- 해시 방식: bcrypt vs SHA-256+salt 중 Plan 단계에서 선택
- 기존 엔드포인트에 Depends(verify_api_key) 적용
- POST /admin/api-keys: 발급 시 평문 키 1회만 반환, DB엔 해시
- ADMIN_KEY 환경변수 기반 관리자 엔드포인트 보호

### REFACTOR
- 해시 로직 util 분리
- 예외 메시지 일관성

제약:
- 기존 테스트 전부 통과 (API Key fixture 필요시 추가)
- 평문 키 DB 저장 금지
- 평문 키 로그 남기기 금지
- /health, /metrics는 인증 제외 (D4에서 만듦, 미리 고려)

성공 기준:
- RED → GREEN → REFACTOR 순서 준수 (커밋 메시지로 구분)
- Swagger UI Authorize로 동작 확인
- pytest 전체 통과, 커버리지 70% 유지
- feat/w1-api-key 브랜치 → integration PR

Plan Mode로 먼저 보여줘:
- TDD 순서별 작업 단계
- 해시 방식 선택 + 이유 (bcrypt vs SHA-256+salt)
- 관리자 엔드포인트 보호 방식
- 기존 테스트에 fixture 추가 방법
- .claude/tasks/todo.md 기록

Plan 검토 후 Execute.
```

---

## D4 (목, 04.23) — 구조화 로깅 + /health + /metrics

**브랜치**: `feat/w1-logging`

```
.claude/tasks/lessons.md 먼저 읽어.

오늘은 W1-D4: 구조화 로깅 + /health + /metrics 작업.

**TDD 적용 영역 구분**:
- ✅ 엄격: /health, /metrics 엔드포인트 로직
- ⚠️ 예외: 로깅 포맷 자체 (수동 검증). 단, 로깅 호출이 일어나는지 여부는 테스트 가능

오늘 목표:

### RED (엄격 영역)
- test_health.py: /health 200 + 구조 확인, DB 다운 시 503
- test_metrics.py: /metrics 200 + 기본 필드 존재 확인

### GREEN
- app/logging.py: JSON 포맷 로거 (timestamp, level, request_id, path, method, status, duration_ms, message)
- request_id 미들웨어 (UUID 생성 + request.state에 저장)
- GET /health: DB + Redis 연결 확인 → {"status": "ok", "db": "ok", "redis": "ok"} (실패 시 503)
- GET /metrics: 기본 메트릭 JSON (요청 수, 응답 시간 p50/p95/p99)

### REFACTOR
- 로거 초기화 util 분리
- 미들웨어 로직 정리

제약:
- 기존 stdout print 전부 logger로 교체
- /health, /metrics는 API Key 인증 제외
- Prometheus 연동 금지 (범위 초과). 기본 JSON만.
- 로그 내용 assert하는 기존 테스트가 있으면 최소 수정

성공 기준:
- 로그가 JSON 한 줄 (jq 파싱 가능)
- /health, /metrics 정상 응답
- request_id 로그에 전파됨
- pytest 전체 통과
- feat/w1-logging → integration PR

Plan Mode로 먼저 보여줘:
- 로거 구현 (python logging vs structlog 선택 + 이유)
- request_id 전파 방식 (contextvars vs request.state)
- /metrics 저장소 (메모리 권장, 이유)
- p50/p95/p99 계산 방식 (전체 기록 vs 슬라이딩 윈도우)
- .claude/tasks/todo.md 기록

Plan 검토 후 Execute.
```

---

## D5 (금, 04.24) — CI/CD + EC2 자동 배포 파이프라인 구축

**브랜치**: `feat/w1-ci-cd`

```
.claude/tasks/lessons.md 먼저 읽어.

오늘은 W1-D5: CI/CD + EC2 자동 배포 파이프라인 구축 작업.

**이 작업은 TDD 예외 영역** (인프라 설정). 
단, 가능한 부분은 검증 포함 (workflow syntax 체크, dry-run 등).

**중요**: 파이프라인 구축만 오늘 완료. 
**실제 main 머지 → EC2 배포는 W1 종료 후 토요일/일요일 1회만**.
이유: W1 중간 작업들이 불완전한 상태에서 배포되면 안 됨.

상황:
- EC2 프리티어 사용 중
- SSH 접근 가능
- Docker, docker-compose EC2 설치 여부 불확실 → Plan에서 확인 체크리스트 필요

오늘 목표:
- .github/workflows/ci.yml: PR 시 pytest + ruff (PostgreSQL + Redis 서비스 컨테이너 포함)
- .github/workflows/deploy.yml: main 머지 시
  1. Docker 이미지 빌드
  2. GHCR 푸시
  3. EC2 SSH → docker-compose pull && up -d
  4. 배포 후 /health 헬스체크
  5. 실패 시 이전 이미지 태그로 롤백
- GitHub Secrets 등록 체크리스트 (EC2_HOST, EC2_SSH_KEY, GHCR_TOKEN, ADMIN_KEY 등)
- README에 CI/CD 배지 마크다운 추가

제약:
- 시크릿 하드코딩 절대 금지
- feat/w1-ci-cd 브랜치에서 작업. main에 직접 머지 금지
- EC2 세팅 막히면 **CI만 먼저 완성, 배포는 수동 스크립트로 폴백**. 억지로 하루에 끝내려고 망치지 말 것

성공 기준 (최소):
- CI 파이프라인 동작 (PR 생성 시 테스트 실행)
- 수동 배포 스크립트 + 문서화

성공 기준 (목표):
- 위 + deploy.yml 완성 (실제 트리거는 W1 종료 후)

Plan Mode로 먼저 보여줘:
- CI workflow 전체 구성 (서비스 컨테이너 포함)
- Deploy workflow 단계
- EC2 사전 체크리스트 (docker 설치, 보안 그룹, SSH 키 권한, known_hosts)
- 롤백 전략 구체안
- **폴백 시나리오**: EC2 세팅 실패 시 어디서 멈추고 수동으로 가는지
- .claude/tasks/todo.md 기록

Plan 검토 후 Execute.

막히는 지점 생기면 즉시 "수동 폴백 제안" 해줘.
```

---

## D6 (토, 04.25) — OpenAPI + 예외 핸들러 (기반만)

**브랜치**: `feat/w1-openapi`

```
.claude/tasks/lessons.md 먼저 읽어.

오늘은 W1-D6: OpenAPI + 커스텀 예외 핸들러 기반 작업.

**이 작업은 TDD 엄격 대상** (예외 핸들러 로직).
단, 엔드포인트 문서화 (response_model 추가 등)는 TDD 불필요.

**중요**: 기반만 오늘. 전체 엔드포인트 문서화는 W2~W6에 내가 직접 이어서.

오늘 목표:

### RED
- test_exceptions.py: 커스텀 예외 발생 시 통일 포맷 검증
  - SensorTypeInvalidError → 400 + error_code="SENSOR_TYPE_INVALID"
  - RobotNotFoundError → 404 + error_code="ROBOT_NOT_FOUND"
  - ApiKey 관련은 이미 D3에서 일부 있음

### GREEN
- app/exceptions.py: 커스텀 예외 클래스
  * BaseAPIException (공통 부모)
  * SensorTypeInvalidError
  * ApiKeyMissingError
  * ApiKeyInvalidError
  * RobotNotFoundError
- 글로벌 예외 핸들러 (app/main.py 또는 app/handlers.py):
  ```
  {
    "error_code": "SENSOR_TYPE_INVALID",
    "message": "지원하지 않는 센서 타입입니다",
    "detail": {"sensor_type": "xyz"},
    "timestamp": "2026-04-20T10:30:00Z"
  }
  ```
- 핵심 3개 엔드포인트에 response_model, status_code, summary 우선 적용
  (POST /api/sensors, GET /api/robots, POST /admin/api-keys)
- 기존 HTTPException 사용처 중 위 3개 연관된 곳만 커스텀 예외로 교체

### REFACTOR
- 에러 코드 네이밍 일관성 확인
- 예외 클래스 계층 정리

제약:
- 모든 엔드포인트 문서화는 오늘 안 함. 기반만.
- 에러 코드 명명: SCREAMING_SNAKE_CASE (예: API_KEY_MISSING)
- 기존 테스트 전부 통과 (에러 포맷 바뀐 3곳은 맞춰 업데이트)

성공 기준:
- 커스텀 예외 → 통일 포맷 응답
- Swagger UI에 핵심 3개 엔드포인트 에러 스펙 표시
- pytest 전체 통과
- feat/w1-openapi → integration PR
- **REMAINING_WORK.md** 파일 생성: W2~W6 이어할 작업 목록 (모든 엔드포인트에 response_model, 에러 코드 목록 완성, 예외 핸들러 전체 적용)

Plan Mode로 먼저 보여줘:
- 예외 클래스 상속 구조
- 글로벌 핸들러 등록 방식
- 오늘 교체할 핵심 3곳 선정 + 이유
- REMAINING_WORK.md 구조
- .claude/tasks/todo.md 기록

Plan 검토 후 Execute.

**오늘 끝나면 W1 스프린트 종료**. 마지막에 W1 전체 요약 제공:
- 각 일자별 완료 여부
- 남은 이슈
- W2 코드리뷰 시 우선 볼 부분
- lessons.md에 누적된 학습 (참조용)
```

---

## W1 종료 후 체크리스트 (토 저녁 ~ 일, 04.25~04.26)

### 배포 전 확인
- [ ] 모든 feature 브랜치 작업 `integration` 브랜치로 머지 완료
- [ ] `integration` 브랜치에서 pytest 전체 통과
- [ ] 커버리지 70%+ 유지
- [ ] `REMAINING_WORK.md` 작성 확인
- [ ] `.claude/tasks/lessons.md` 내용 한번 훑어봄

### 배포 (1회 통합)
- [ ] `integration` → `main` 최종 PR 생성
- [ ] PR CI (pytest + ruff) 통과 확인
- [ ] `main` 머지 → `deploy.yml` 트리거 확인
- [ ] EC2 배포 완료 확인 (GitHub Actions 로그)

### 배포 검증
- [ ] EC2 `/health` 200 응답 (curl 또는 브라우저)
- [ ] Swagger UI (`/docs`) 접속 가능
- [ ] 핵심 API 하나 curl로 호출 성공 (API Key 사용)
- [ ] 실패 시 이전 이미지 태그로 롤백 스크립트 실행

### W2 준비
- [ ] Claude Code가 만든 파일 목록 정리 (리뷰 대상)
- [ ] W2 월요일 첫 리뷰 파일 선정
- [ ] PHASE1.md 4-2 "코드리뷰 방법" 다시 읽기
