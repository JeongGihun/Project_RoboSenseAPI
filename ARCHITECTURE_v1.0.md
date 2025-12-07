# 프로젝트 3 : RoboSense API

## 부제 : High-Performance Sensor Data Processing API for Robotics
             (로보틱스를 위한 고성능 센서 데이터 처리 API)

## 시나리오 : 물류 창고에서 자율주행 로봇 여러 대가 물건을 운반하면서 실시간으로 센서 데이터를 API 서버로 전송. 서버는 이를 처리하여 로봇의 위치 추적, 장애물 감지, 경로 최적화 등을 지원.

## 핵심 기술
- 대용량 센서 데이터 실시간 처리
- Python + C++ 효율적 통합
- 낮은 응답 지연 시간

## 목표
- TPS 15,000 달성
- 성능 최적화
- 응답 지연 시간 100ms 이내 처리 목표
- 에러율 1% 미만
- 동시 접속 : 1000+

## 시스템 아키텍쳐 다이어그램
![시스템 아키텍쳐 다이어그램](images/photo.png)
* FAST API 인스턴스 5개인 이유 -> 현재 로컬이 CPU 코어가 6개, 1개는 메인 시스템 운영용
* 다만 인스턴스 갯수를 개발 중 : 5개 -> 정상 배포 확인 시 : 2개 -> 프로젝트 완료 직전 : 5개로 변경
* Redis 캐싱 : 로봇별 최근 10초간 데이터, 시간대별 통계
  (로봇 상태 : TTL 10초시 효과 50ms -> 5ms 예상, 통계 데이터 : TTL 1분시 효과 500ms->5ms)
  (패턴 : Cache-Aside, 조회 시 캐시 확인 -> 없으면 DB -> 캐시 저장)

## 핵심 기능 정의
- (MVP) 센서 데이터 수집 - POST /api/sensors
- (MVP) 로봇 상태 모니터링 - GET /api/robots/{id}
- (MVP) 데이터 집계 및 통계 - GET /api/stats
- (후순위) 실시간 데이터 필터링 - GET /api/sensors/filtered
- (후순위) 좌표 변환 처리 - POST /api/transform
* 데이터 흐름의 전체 사이클 판단을 위해 MVP 선정

## 추가 엔드포인트
- 로봇 등록 - POST /api/robots
- 전체 로봇 목록 - GET /api/robots
- 특정 로봇 센서 데이터 조회 - GET /api/sensors?robot_id=1

### 센서 데이터 수집
- 요청
```
{
  "robot_id": 1,
  "timestamp": "2024-12-06T10:30:00",
  "sensors": [
    {
      "sensor_type": "IMU",
      "data": {"acceleration": {"x": 1.2, "y": -0.5, "z": 9.8}}
    },
    {
      "sensor_type": "GPS",
      "data": null  // null 허용 (신호 끊김 등)
    },
    {
      "sensor_type": "LiDAR",
      "data": {"distance": 3.5, "angle": 45}
    }
  ]
}
```
- 응답
```
{
  "status": "success",
  "inserted_count": 3,
  "robot_id": 1
}
```
- 필수 : robot_id, timestamp, sensor_type
- 선택 : data (null) 허용

### 로봇 상태 모니터링
- 응답
```
{
  "robot_id": 1,
  "name": "Robot-A",
  "model": "Warehouse-Bot-v2",
  "status": "active",
  "last_seen": "2024-12-06T10:30:05",
  "recent_sensors": [
    {
      "sensor_type": "IMU",
      "timestamp": "2024-12-06T10:30:05",
      "data": {"acceleration": {"x": 1.2, "y": -0.5, "z": 9.8}}
    },
    {
      "sensor_type": "GPS",
      "timestamp": "2024-12-06T10:30:04",
      "data": null  // null도 보여줌 (센서 문제 표시)
    },
    // ... 최근 10초간 데이터
  ]
}
```
* Redis 캐시 확인 후, 없으면 PostgreSQL조회 -> Redis 저장 방식 채택 (속도 최적화)

### 데이터 집계 및 통계
- 전체 / 응답
```
{
  "timestamp": "2024-12-06T16:00:00",
  "hourly_averages": { ... },
  "null_rates": { ... },
  "robot_summary": { ... }
}
```
- 시간대별 센서 평균값 / 응답
```
"hourly_averages": {
  "2024-12-06T14:00:00": {
    "IMU": {
      "acceleration": {"x": 1.15, "y": -0.48, "z": 9.81}
    },
    "LiDAR": {
      "distance": 3.2
    }
  },
  "2024-12-06T15:00:00": { ... }
}
```
- 센서 타입별 null 비율 / 응답
```
"null_rates": {
  "IMU": 0.02,      // 2%
  "GPS": 0.15,      // 15% (실내에서 끊김)
  "LiDAR": 0.01     // 1%
}
```
- 전체 로봇 현재 상태 요약 / 응답
```
"robot_summary": {
  "total_robots": 12,
  "active": 10,
  "inactive": 2,
  "status_details": [
    {"robot_id": 3, "status": "inactive", "last_seen": "2024-12-06T09:00:00"},
    {"robot_id": 7, "status": "inactive", "last_seen": "2024-12-06T10:15:00"}
  ]
}
```
* 마찬가지로 통계 계산은 DB에서 GROUP BY같은 연산은 느림
* 따라서 호출 후 Redis 확인 -> 없으면 PostgreSQL에서 통계 계산 -> Redis 저장

## DB 스키마 설계

### 로봇 상태 모니터링 -> robots 테이블
```
CREATE TABLE robots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    status status_enum DEFAULT 'active',
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TYPE status_enum AS ENUM ('active', 'inactive', 'maintenance');
```

### 센서 데이터 수집 -> sensor_data 테이블
```
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    robot_id INTEGER REFERENCES robots(id) ON DELETE CASCADE,
    sensor_type sensor_type_enum NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TYPE sensor_type_enum AS ENUM('IMU', 'GPS', 'LiDAR');
```
* JSONB 사용 이유 : 저장 속도가 느린 대신, 조회속도가 빠름. 데이터 구조 다양시 사용
* 해당 위치에서는 센서 데이터의 종류가 달라 데이터 구조가 다양해 JSONB 사용

### 데이터 전처리 결과 -> processed_data 테이블
```
CREATE TABLE processed_data(
    id SERIAL PRIMARY KEY,
    sensor_data_id INTEGER REFERENCES sensor_data(id) ON DELETE CASCADE,
    process_type process_type_enum NOT NULL,
    processed_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TYPE process_type_enum AS ENUM('filtering', 'transform', 'both');
```
* 왜 stats 테이블이 아닌, processed_data 테이블을 만드는가?
* 목적이 processed_data를 모아 나중에 통계화한 stats 테이블을 만들기 위함
* 즉, stats 테이블은 결과이며, 어차피 redis로 처리 예정

### robots 테이블 인덱스
```
CREATE INDEX idx_status ON robots(status);
```
* 로봇 상태별 인덱스 필요하다 판단

### sensor_data 테이블 인덱스
```
CREATE INDEX idx_robot_timestamp ON sensor_data(robot_id, timestamp);
CREATE INDEX idx_sensor_type ON sensor_data(sensor_type);
```
* 로봇의 시간별 데이터가 필요해 복합 인덱스 생성
* 복합 인덱스 생성 시 컬럼 순서 중요 -> 내용은 같으나 결과 순서가 다름
* 즉, 더 자주 검색하는 컬럼을 앞으로
* 센서 타입별 집계 빠름

### processed_data 테이블 인덱스
```
CREATE INDEX idx_sensor_data_id ON processed_data(sensor_data_id);
CREATE INDEX idx_process_type ON processed_data(process_type);
```
* id는 기본, type별 결과는 유지보수시 필요하다 판단

### 기타 알아야 할 사항
```
PostgreSQL에서는 인덱스명을 사용하지 않음. MySQL에서는 사용
인덱스를 많이 생성하면 조회, JOIN문 속도 향상. 다만 INSERT / UPDATE / DELETE 성능 저하, 디스크 사용량 증가
```

## API 엔드 포인트 설계
### 센서 데이터 관리
- POST /api/sensors - 센서 데이터 수집 (배열 지원, null 허용)
* 에러 사유를 알아야해서 null 허용
- GET /api/sensors - 센서 데이터 조회 (robot_id, sensor_type, 시간 범위, 페이징)
* 페이지 번호 방식. cursor은 구현 난이도가 높고, offset방식은 데이터 처리가 느림
### 로봇 관리
- POST /api/robots - 로봇 등록 (이름 중복 체크)
* 초기 상태 확인 필요해서 status 요청해서 받기, 이름 중복 시 에러. 이름이 unique값이 되도록 의도
- GET /api/robots - 로봇 목록 조회 (상태 필터)
* 인덱스 만들거라 상태별 필터 사용에 동의
- GET /api/robots/{id} - 특정 로봇 상태 + 최근 10초 센서 데이터
* 특정 로봇들의 상태를 확인 필요

### 통계
- GET /api/stats - 시간대별 평균, null 비율, 로봇 상태 요약 (시간 범위 지정 가능)
* 시간대별로 확인하는 것이 유동적이여야 함.
### 데이터 처리
- GET /api/sensors/filtered - 필터링된 데이터 조회 (필터 타입, robot_id)
* 이상치 확인이 필요해 필터 타입 지정 필요, 페이징도 필요 없다 판단
- POST /api/transform - 좌표 변환 처리 (sensor_data_id 참조)
* 원본 센서 데이터 활용. JOIN활용하면 되고, 데이터 직접 넣다가 오류 발생 우려

### 공통 응답 형식
- 성공시
```
{
  "status": "success",
  "data": {...}
}
```

- 실패시
```
{
  "status": "error",
  "message": "Error description"
}
```

### 주요 상태 코드
- 200: 성공
- 201: 생성됨
- 400: 잘못된 요청
- 404: 찾을 수 없음
- 409: 중복
- 500: 서버 에러

## 기타
```
<문제>
인스턴스 5개로는 tps 15,000달성 불가
데이터 수를 줄이면 tps가 올라가긴 하지만 , 드라마틱하게 증가하지는 않음
- 센서 3개 -> 1개 : TPS 250 -> 333 (예상)
- 응답 데이터 10초 -> 3초 : 830 -> 1200 (예상)
<해결 방안>
- AWS 배포 시 t2.micro -> t3.small(인스턴스 25개) 사용
- 인스턴스 사용 갯수는 유동적이고, 초단위 사용이 가능해 최종 배포시에만 사용
- 6시간 기준 30~50$
- 방법은 AWS Console or Docker Compose 사용
```

## 기술 스택 (예상)
### 백엔드
- FastAPI : 비동기 처리(동시 요청 처리), 타입 힌트 지원, 대중적
- Uvicorn : FastAPI를 실행시켜주는 ASGI 서버
- Pydantic : 데이터 검증 라이브러리 
- Python 3.11 : 안정성 위해 하향

### DB
- PostgreSQL 16 : 센서 데이터 구조 유연, 안정성, 대중적
   * InfluxDB : 시간대별 집계가 빠르지만, 학습 곡선 낮음
- asyncpg : PostgreSQL 비동기 드라이버 (성능 최적화)

### 캐싱
- Redis 7 : 속도, 범용성, TTL 지원
- redis.asyncio : Redis 비동기 드라이버

### 성능 최적화
- C++ 17 : 표준, 회사에서 C++ 사용
- pybind11 : 통합 안정성
- NumPy : 배열 연산 라이브러리
- CMake : C++ 프로젝트 빌드 도구

### 인프라
- Docker & Docker Compose : 환경 일관성, 배포 편리, 대중적
- Nginx : 안정성, 성능, 대중적
- AWS EC2 (t2.micro → t3.small) : 실제 TPS 테스트 가능

### 테스트 & 모니터링
- Locust : 확장성, 대중적
- pytest-asyncio : 비동기 테스트 표준
- cProfile / py-spy : Python 성능 프로파일링 / 실시간 성능 모니터링

### 배포 & CI / CD
- GitHub Actions (필요 시) : 수동 배포 자동화
- 환경 변수 관리 (.env) : 보안
