# Security

RoboSenseAPI의 보안 정책과 구현 내역을 정리한 문서.

## 인증 / 인가

| 대상 | 방식 | 헤더 | 저장 |
|------|------|------|------|
| 일반 API | API Key | `X-API-Key` | SHA-256 + per-key salt |
| 관리자 API | Admin Key | `X-Admin-Key` | 환경변수 (`ADMIN_KEY`) |

- API Key는 `secrets.token_urlsafe(32)` 로 발급. 평문은 DB에 저장하지 않음.
- 관리자 엔드포인트(`/admin/api-keys`, `DELETE /api/reset`)는 별도 키로만 접근.

## 적용된 보안 조치

### 네트워크 격리
- PostgreSQL 포트(5432)는 컨테이너 외부로 노출하지 않음 (`expose` 만 사용)
- `pg_hba.conf`는 Docker 내부망(`samenet`)과 로컬호스트만 허용. `0.0.0.0/0` 거부

### CORS
- `ALLOWED_ORIGINS` 환경변수 기반 화이트리스트
- 와일드카드(`*`) 사용 안 함
- `allow_credentials=False` (기본값 유지)

### 캐시 무결성
- stats 캐시 재생성 시 `SETNX` 락 사용해 중복 갱신 방지 (thundering herd 대응)

### 입력 검증
- 모든 POST/PUT body는 Pydantic 모델로 스키마 강제
- `GET /api/sensors`의 `limit` 파라미터는 `ge=1, le=1000` 제약

### 에러 응답
- 라우트 내부의 예외는 글로벌 핸들러에서 `"서버 내부 오류"` 고정 메시지로 변환
- 내부 예외 메시지(`str(e)`, 스택트레이스, SQL 문법 등) 클라이언트 노출 금지
- 원본 예외는 `logger.error`로만 기록 (request_id 포함)

### 시크릿 관리
- `.env` 는 `.gitignore` 처리. 레포에 커밋된 이력 없음
- 운영 배포 시 `ADMIN_KEY`, `POSTGRES_PASSWORD`는 EC2 환경변수로 별도 주입 (아래 체크리스트 참조)

### EC2 접근 정책
- **HTTP (80)**: `0.0.0.0/0` 허용 (랜딩페이지 공개 + API는 API Key로 보호)
- **SSH (22)**: `0.0.0.0/0` 허용
  - 이유: GitHub Actions 러너 IP가 매 실행마다 달라서 화이트리스트 운영 불가
  - 완화: `PasswordAuthentication no` 로 비밀번호 로그인 차단, `.pem` 키 파일로만 접근
  - 트레이드오프 인지: 운영급이면 AWS Systems Manager Session Manager 또는 self-hosted runner로 전환 권장
- **PostgreSQL (5432) / Redis (6379)**: 인바운드 차단. Docker 내부망으로만 접근

## 배포 전 체크리스트

배포 파이프라인(`.github/workflows/deploy.yml`) 실행 전 아래 항목 확인.

- [ ] EC2의 `.env`에 운영용 `ADMIN_KEY` 설정됨 (`secrets.token_urlsafe(32)` 권장)
- [ ] EC2의 `.env`에 운영용 `POSTGRES_PASSWORD` 설정됨 (테스트용 `postgres` 금지)
- [ ] EC2의 `.env`에 운영 도메인 기반 `ALLOWED_ORIGINS` 설정됨
- [ ] EC2 보안그룹: 인바운드 80/443만 열림 (5432, 6379 차단 확인)
- [ ] GitHub Secrets: `GHCR_TOKEN`, `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY` 설정됨
- [ ] 배포 후 `curl -f http://<도메인>/health` 로 상태 확인
- [ ] 배포 후 `/api/robots` 에 invalid API Key로 접근 시 401 응답 확인

## 취약점 제보

보안 이슈 발견 시 아래 이메일로 직접 제보.

- solux3501@gmail.com

공개 이슈 트래커(GitHub Issues)에는 보안 관련 상세 내용을 올리지 말 것.

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-04-18 | API Key 인증, Admin Key 분리, CORS 화이트리스트, SETNX 락 도입 |
| 2026-04-19 | DB 포트 외부 공개 차단, `pg_hba` 0.0.0.0/0 제거, 에러 메시지 마스킹, `limit` 상한 추가, EC2 접근 정책 명시 |
