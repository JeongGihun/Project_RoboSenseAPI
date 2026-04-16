# Lessons Learned

> 작업 중 잘못 판단했거나 사용자가 수정 지시한 것을 기록하는 파일.
> **매 작업 시작 전 반드시 이 파일을 먼저 읽기.**

---

## 기록 포맷

```markdown
## YYYY-MM-DD | 주제 (한 줄 요약)
- **잘못 생각한 것**: 어떤 판단이 틀렸는지
- **올바른 방향**: 어떻게 해야 했는지
- **반복 방지 규칙**: 앞으로 이 상황에서 적용할 규칙
```

---

## 기록 트리거

1. 사용자 negative feedback 감지 ("아니", "다시", "왜 이렇게", "틀렸어" 등)
   → 즉시 초안 작성 → 사용자 승인 → 저장
2. Plan Mode에서 이전 lesson과 충돌하는 결정 발견
   → 경고 후 재설계
3. 작업 완료 후 자체 회고 → 학습 포인트 있으면 제안

---

## 누적 기록

## 2026-04-16 | fakeredis 호환 문제 → 직접 mock 권장
- **잘못 생각한 것**: fakeredis[aioredis]가 redis 7.1.0과 호환될 거라 가정
- **올바른 방향**: FakeReader.at_eof 에러 발생. 간단한 FakeRedis 클래스를 직접 작성하는 게 안정적
- **반복 방지 규칙**: 외부 mock 라이브러리 도입 전 버전 호환성 확인. 안 되면 직접 mock 작성

## 2026-04-16 | get_redis()는 Depends 아님 → dependency_overrides 불가
- **잘못 생각한 것**: get_redis()를 FastAPI dependency_overrides로 교체 시도
- **올바른 방향**: get_redis()는 직접 호출 함수. 모듈 변수(redis_module.redis_client)를 직접 교체해야 함
- **반복 방지 규칙**: Depends()로 주입되는 것만 dependency_overrides 사용 가능. 직접 호출은 모듈 패치

## 2026-04-16 | 커스텀 예외가 try-except에 잡히는 문제
- **잘못 생각한 것**: RobotNotFoundError raise 후 자동으로 글로벌 핸들러까지 전파될 거라 가정
- **올바른 방향**: 기존 코드의 `except Exception as e`가 커스텀 예외도 잡아버림. `except (HTTPException, RobotNotFoundError): raise` 추가 필요
- **반복 방지 규칙**: 기존 try-except 블록에 커스텀 예외 추가 시 re-raise 패턴 확인

## 2026-04-16 | AI 티 안 나게 + MCP/skill 변경 금지
- **잘못 생각한 것**: 작업 흐름에만 집중하고 코드 스타일/환경 변경 주의를 놓침
- **올바른 방향**: 코드는 1년차 개발자가 직접 짠 것처럼. MCP 서버/skill은 건드리지 않기
- **반복 방지 규칙**: 
  1. CLAUDE.md 섹션 8 (AI 생성 티 안 나게) 매 구현 전 재확인
  2. MCP 서버, skill 설정은 절대 변경 금지. 꼭 추가해야 하는 것만 사용자 허가 후 허용
