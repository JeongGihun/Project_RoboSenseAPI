# /execute 커맨드

## 역할
RoboSenseAPI 코드 구현 전문 모드.
.claude/tasks/todo.md에서 현재 작업 확인 후 10단계 사이클 실행.

## 사전 읽기
1. CLAUDE.md (상시 규칙)
2. .claude/tasks/lessons.md (과거 실수 방지)
3. .claude/tasks/todo.md (현재 작업)
4. .claude/context/PHASE1.md (전체 맥락, 필요 시)

## 10단계 사이클
1. Plan 작성 (Plan Mode)
2. Task화 (todo.md 기록)
3. 테스트 작성 (TDD RED)
4. 구현 (TDD GREEN)
5. 리팩토링 (TDD REFACTOR)
6. QA (pytest 전체 실행)
7. 학습 기록 (lessons.md)
8. 커밋 (feature 브랜치)
9. 로컬 검증 (Docker + /health)
10. integration 머지 (PR + CI 확인)

## 에러 처리
- 실패 시 자동 원인 분석 → 수정 → 재실행
- 3회 연속 실패 시 사용자에게 보고
- 서브에이전트로 탐색, 메인 에이전트가 검토

## 규칙
- AI 티 안 나게 (CLAUDE.md 섹션 8)
- MCP/skill 변경 금지
- 이 레포 외부 파일 수정 금지
- masterplan 참조 필요 시 .claude/context/ 내 복사본만 사용
