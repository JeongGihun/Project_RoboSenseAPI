# /plan — 1~3단계 (Plan + Task화 + TDD RED)

아래 순서대로 파일을 읽어:
1. CLAUDE.md
2. .claude/tasks/lessons.md
3. .claude/context/PHASE1.md
4. .claude/context/PHASE1_w1_prompts.md
5. .claude/tasks/todo.md

$ARGUMENTS 가 있으면 해당 작업 범위로 진행.
$ARGUMENTS 가 없으면 "어떤 작업을 진행할지 알려줘 (예: 전체, 테스트+인증, D3만)" 라고 물어봐.

## 1단계: Plan 작성
- Plan Mode로 진입
- 지정된 범위의 구현 계획 수립
- 기존 app/ 코드 구조 파악 (Explore 에이전트 활용)
- lessons.md에 관련 교훈 있으면 반드시 반영
- Plan 작성 후 사용자 승인 대기

## 2단계: Task화
- 승인된 Plan을 .claude/tasks/todo.md에 기록
- 포맷은 todo.md 상단의 템플릿 따라서

## 3단계: 테스트 작성 (TDD RED)
- TDD 엄격 대상이면: 실패하는 테스트 먼저 작성
- TDD 예외 영역이면: 이 단계 건너뛰고 "TDD 예외 영역이라 RED 단계 스킵" 알림
- 테스트 작성 후 pytest 실행해서 실제 RED(실패) 확인
- RED 확인되면 사용자에게 "/write 로 구현 진행하세요" 안내

## 에러 처리
- Plan이 lessons.md 교훈과 충돌하면 경고 후 재설계
- 테스트 파일 문법 에러 시 자동 수정 후 재실행
- 서브에이전트로 코드베이스 탐색 → 결과 검토 → 문제 있으면 재탐색
