# RoboSense API

## 부제
```
High-Performance Sensor Data Processing API for Robotics
(로보틱스를 위한 고성능 센서 데이터 처리 API)
```

## 목적
```
대용량 센서 데이터를 실시간으로 처리 후, 대규모 트래픽 처리 경험을 극한까지 설정 및 최적화
```

## 개발 타임라인
- '25. 12. 13 ~ '26. 01. 03 : 프로토 타입 작성
- '26. 01. 04 : 첫 부하 테스트 진행
- '26. 01. 04 ~ : 성능 최적화

## 주요 기능
- POST /api/sensors - 센서 데이터 수집
- GET /api/sensors - 센서 데이터 조회 및 필터링
- GET /api/sensors?robot_id={id} - 특정 로봇 센서 조회
- GET /api/sensors?sensor_type={type} - 센서 타입별 조회
- POST /api/robots - 로봇 등록
- GET /api/robots - 로봇 목록 조회
- GET /api/robots/{id} - 특정 로봇 목록 조회

## 실행 방법

### 1. PostgreSQL 시작
```
docker start postgres-robosense
```

### 2. 가상환경 생성 및 활성화
```
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. 서버 실행
```
uvicorn app.main:app --reload
```

### 4. API 문서 확인
- Swagger UI: http://127.0.0.1:8000/docs

### 5. Locust 부하 테스트
- locust -f test/locustfile.py --host=http://localhost:8000

## 프로젝트 구조
```
RobosenseAPI/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── database.py             # DB 연결 및 세션 관리
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy ORM 모델
│   │   ├── sensor.py           # 센서 Pydantic 스키마
│   │   ├── robot.py            # 로봇 Pydantic 스키마
│   │   └── enums.py            # Enum 타입 정의
│   └── routes/
│       ├── sensor_routes.py    # 센서 데이터 API
│       └── robot_routes.py     # 로봇 관리 API
├── test/
│   ├── locustfile.py           # 부하 테스트 시나리오
│   └── mock_data_generator.py  # 테스트 데이터 생성
├── .venv/                      # 가상환경
├── requirements.txt
├── .env.example
└── README.md
```

## 기술 스택 / 사용 Tool
- Python (3.11)
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Docker
- Locust

## 부하 테스트 (세부 결과 : Test - Performance 참조)
- Week 10('26. 01. 04.)
```
기준 : User 50명, Spawn Rate 5명/초, Data 50,000개
결과 : TPS (16.4) / Fail (0) / Average response (3,635ms)
분석사항
1. 커넥션풀 사이즈 변경 (10,5 -> 50,50) / TPS 변동 없음
2. DB 쿼리 속도 확인 : SELECT(2.5ms), JOIN(33.9) / 문제 없음
결론
어디서 문제인지 모르겠음. 문제 파악하면서, 당장 조금이라도 줄일 수 있는 방법은 Redis로 변경해보자
```
