# CLAUDE.md

> 프로젝트: RoboSenseAPI
> 역할: Claude Code가 이 레포에서 작업할 때 반드시 따를 **상시 규칙**
> 유효 기간: 프로젝트 존속 동안

---

## 1. 프로젝트 소개

- 로봇/센서 데이터 처리 API
- 기술 스택: Python 3.11 + FastAPI + PostgreSQL + Redis + Docker + Nginx
- 도메인: IoT/로봇. 사람 로그인 개념 없음 → **API Key 기반 인증** (JWT 아님)
- 성능 기록: TPS 26 → 489 (Redis + Cursor 페이지네이션 + Docker 5 replica)

---

## 2. 매 작업 사이클 (필수 9단계)

모든 작업은 아래 순서를 **반드시** 거친다.

| 단계 | 내용 | 산출물 |
|------|------|--------|
| 1 | **Plan 작성** (Plan Mode로 계획 수립) | Plan 승인 |
| 2 | **Task화** (.claude/tasks/todo.md에 기록) | todo 항목 |
| 3 | **테스트 작성** (TDD RED: 실패하는 테스트 먼저) | 실패하는 테스트 |
| 4 | **구현** (TDD GREEN: 테스트 통과하는 최소 코드) | 동작 코드 |
| 5 | **리팩토링** (TDD REFACTOR: 구조 개선) | 정리된 코드 |
| 6 | **QA** (pytest 전체 실행, 기존 테스트 안 깨짐 확인) | 전체 통과 |
| 7 | **커밋** (feature 브랜치에 커밋) | 커밋 |
| 8 | **로컬 검증** (Docker 재빌드 + /health 스모크 테스트) | 동작 확인 |
| 9 | **integration 머지** (feat/* → integration PR & 머지, CI 통과 확인) | CI green |
| 10 | **학습 기록** (lessons.md 갱신, 있으면) | lesson 추가 |

**배포 흐름**: 매일 feat/* → integration 머지 시 CI(pytest + ruff)로 검증. integration → main 머지 시 deploy.yml이 자동으로 EC2 배포 트리거. 각 일자 작업 중 main 직접 머지 금지.

---

## 3. TDD 규칙

### 엄격 적용 영역
- 비즈니스 로직 (라우트, 서비스 함수)
- 모델/스키마 검증
- 커스텀 예외 및 예외 핸들러
- 인증/권한 로직

### TDD 예외 영역 (테스트 없이 구현 허용)
- 인프라 설정 (`Dockerfile`, `docker-compose.yml`, `nginx.conf`)
- CI/CD 파이프라인 (`.github/workflows/`)
- 로깅 포맷 자체 (단, 로깅 호출은 테스트 가능하면 테스트)

### TDD 순서 (엄격 영역)
```
1. RED     — 실패하는 테스트 1개 작성
2. GREEN   — 테스트 통과하는 최소 코드 작성
3. REFACTOR — 중복 제거, 구조 개선
```

각 단계에서 **테스트 먼저 돌려 실제 RED 확인** → GREEN 확인 → REFACTOR 후에도 GREEN 유지.

---

## 4. 브랜치 전략 (W1 기간 필수)

```
main              ← 배포 트리거. W1 동안 직접 머지 금지
  ↑
  (W1 토요일에 1회 통합 PR)
  ↑
feat/w1-tests     ← D1, D2 테스트 작업
feat/w1-api-key   ← D3 인증 작업
feat/w1-logging   ← D4 로깅 작업
feat/w1-ci-cd     ← D5 CI/CD 작업
feat/w1-openapi   ← D6 OpenAPI 작업
```

- 각 일자 작업은 **해당 feature 브랜치**에서 진행
- PR은 feature → `develop` (또는 `integration`) 브랜치로 누적
- **토요일 D6 완료 후** → `integration` → `main` 최종 PR → 자동 배포

이유: 각 일자마다 main에 머지하면 D5 이후 매 머지마다 배포 트리거됨. W1 중엔 **불완전 상태 배포 방지**가 우선.

---

## 5. Harness (학습 누적)

### 원칙
- **모든 작업 시작 전** `.claude/tasks/lessons.md` 먼저 읽기
- 사용자의 negative feedback 감지 시 **자동으로** lessons.md에 추가 제안
  - 예: "아니", "다시 해", "왜 이렇게 했어", "이건 틀렸어", "그게 아니라", "방향이 다르다" 등
- 작업 중 잘못 판단했다가 수정한 것도 자기 주도적으로 기록

### lessons.md 포맷
```markdown
## YYYY-MM-DD | 주제 (한 줄)
- **잘못 생각한 것**: 어떤 판단이 틀렸는지
- **올바른 방향**: 어떻게 해야 했는지
- **반복 방지 규칙**: 앞으로 이 상황에서 적용할 규칙
```

### 기록 트리거
1. 사용자 negative feedback → 즉시 초안 작성, 사용자 승인받고 저장
2. Plan Mode에서 이전 lesson과 충돌하는 결정 발견 → 경고 후 재설계
3. 작업 완료 후 되돌아보기 → 학습 있으면 제안

---

## 6. 코딩 컨벤션

- PEP 8 준수
- **타입 힌트 필수** (모든 함수 시그니처)
- docstring: 함수 목적 + 주요 파라미터 + 반환값
- 에러: 커스텀 예외 사용 (`HTTPException` 직접 사용 최소화)
- 로깅: `print()` 금지, `logger` 사용
- async 일관성: 라우트는 `async def` 유지, ORM은 async 세션

---

## 7. 금지 사항

- 기존 동작하는 API 스펙 변경 (요청/응답 구조)
- 평문 비밀번호/API Key를 DB에 저장
- 시크릿 하드코딩 (환경변수 사용)
- 테스트 없이 구현만 추가 (TDD 예외 영역 제외)
- Prometheus 등 범위 외 인프라 추가
- MCP 서버, 외부 스킬 설치 (사용자 명시 허가 없이 금지)
- **W1 중 main 브랜치 직접 머지**

---

## 8. AI 생성 티 안 나게 하는 규칙

이 프로젝트의 코드는 **면접/코드리뷰에서 "1년차 개발자가 직접 짠 코드"** 처럼 보여야 함.

### 금지
- **과도한 주석**: `# Get user from database` 같은 자명한 주석 달지 말 것
- **불필요한 추상화**: YAGNI. 당장 필요 없는 추상 클래스, 팩토리 패턴 금지
- **범위 초과 작업**: 요청 외 리팩토링 금지
- **과도하게 방어적인 코드**: 불필요한 try-except, 과도한 null 체크

### 권장
- **간결한 함수** (20줄 이내 권장)
- **일관된 네이밍**: snake_case for Python (혼용 금지)
- **커밋 메시지**: 한글 OK, 간결하게 ("api-key 인증 추가", "stats 캐시 테스트 추가")

---

## 9. 파일 참조 맵

| 목적 | 경로 |
|------|------|
| Phase 1 전체 맥락 | `.claude/context/PHASE1.md` |
| W1 일자별 프롬프트 | `.claude/context/PHASE1_w1_prompts.md` |
| Plan 저장 | `.claude/tasks/todo.md` |
| 학습 누적 | `.claude/tasks/lessons.md` |

작업 시작 시 이 순서로 참조:
1. `CLAUDE.md` (이 파일)
2. `lessons.md` (과거 실수 방지)
3. `PHASE1.md` (전체 맥락)
4. `PHASE1_w1_prompts.md` → 오늘 일자 섹션
5. `todo.md`에 Plan 기록
