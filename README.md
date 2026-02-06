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
- '26. 01. 04 : 첫 부하 테스트 진행 [TPS : 26]
- '26. 01. 04 ~ '26. 01. 11 : Redis 도입, 페이징네이션 도입(Cursor)
- '26. 01. 11 ~ '26. 01. 18 : Docker Compose 작성, 2번째 부하 테스트 [TPS : 489]
   * FastAPI 5개 + Nginx + Docker

## 주요 기능
- POST /api/sensors - 센서 데이터 수집
- GET /api/sensors - 센서 데이터 조회 및 필터링
- GET /api/sensors?robot_id={id} - 특정 로봇 센서 조회
- GET /api/sensors?sensor_type={type} - 센서 타입별 조회
- POST /api/robots - 로봇 등록
- GET /api/robots - 로봇 목록 조회
- GET /api/robots/{id} - 특정 로봇 목록 조회
- GET /api/stats - 최근 1시간 통계 조회

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
```
Swagger UI: http://127.0.0.1:80/docs
```

### 5. Locust 부하 테스트
```
locust -f test/locustfile.py --host=http://localhost:8000
```

### 6. Docker 도입 이후
```
docker-compose up -d --build (생성)
docker-compose down (삭제)
docker-compose ps (상태 조회)
locust -f locustfile.py --host=http://localhost (Locust)
```

## 프로젝트 구조
```
RobosenseAPI/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── database.py             # DB 연결 및 세션 관리
│   ├── redis_client.py         # Redis 클라이언트
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py        # SQLAlchemy ORM 모델
│   │   └── enums.py            # Enum 타입 정의
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── sensor.py           # 센서 Pydantic 스키마
│   │   └── robot.py            # 로봇 Pydantic 스키마
│   └── routes/
│       ├── __init__.py
│       ├── sensor_routes.py    # 센서 데이터 API
│       └── robot_routes.py     # 로봇 관리 API
├── scripts/
│   └── quick_mock.py           # Mock 데이터 생성
├── .venv/                      # 가상환경 (gitignore)
├── Dockerfile                  # FastAPI 이미지 빌드
├── docker-compose.yml          # 전체 시스템 구성
├── nginx.conf                  # Nginx 로드 밸런서 설정
├── .dockerignore
├── locustfile.py               # 부하 테스트 시나리오
├── requirements.txt
├── .env                        # 환경 변수 (gitignore)
├── .env.docker                 # Docker용 환경 변수 (gitignore)
├── .gitignore
└── README.md
```
## 시스템 아키텍처
```
Client / Locust
    ↓
Nginx (Port 80) - Load Balancer
    ↓ (round-robin)
    ├─ FastAPI-1 (8000)
    ├─ FastAPI-2 (8000)
    ├─ FastAPI-3 (8000)
    ├─ FastAPI-4 (8000)
    └─ FastAPI-5 (8000)
         ↓
    PostgreSQL (5432) - Persistent Storage
    Redis (6379) - Cache Layer
```

**컨테이너 구성:**
- Nginx: 1개 (로드 밸런서)
- FastAPI: 5개 (애플리케이션 서버)
- PostgreSQL: 1개 (데이터베이스)
- Redis: 1개 (캐시)

## 기술 스택 / 사용 Tool
- Python (3.11)
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Docker
- Locust
- Redis (7.1.0)

## 부하 테스트
- Week 10 ('26. 01. 04.)
```
기준 : User 50명, Spawn Rate 5명/초, Data 50,000개
결과 : TPS (26) / Fail (0%) / Average response (3,635ms)

< 분석사항 >
1. 평균 응답도 늦지만, 특정 타입 / 로봇에 대한 센서 조회가 터무니 없이 늦음
2. 커넥션풀 사이즈 변경 (10,5 -> 50,50) / TPS 변동 없음
3. DB 쿼리 속도 확인 : SELECT(2.5ms), JOIN(33.9) / 문제 없음

< 결론 >
어디서 문제인지 모르겠음. 문제 파악하면서, 당장 조금이라도 줄일 수 있는 방법은 Redis로 변경해보자
```

- Week 12 ('26. 01. 18.)
```
기준 : User 100명, Spawn Rate 10명/초, Data 300개 (데이터 재생성)
변경점 : 페이징네이션, Redis, Docker 도입
결과 : TPS (489) / Fail (0%) / Average response (174ms)

< 분석사항 >
1. TPS가 최대 800까지 상승. 긍정적임
2. 다만 stats에서 1분 단위로 캐시무효화 전략을 할 때마다 TPS가 급격히 낮아짐
3. DB가 늘어남에 따라 속도가 점점 낮아짐

< 결론 >
1. 캐시 워밍업 필요
2. 쿼리 최적화, 커넥션 풀 사이즈 재조정
```


## 회고
- 10주차 : FastAPI 사용해서 프로그램 만들 때까지, 처음 보는 것들이 너무 많아 힘들다고 생각했는데 산 넘어 산인 것 같다. TPS를 측정하고 분석하니 어디서부터 손을 대야할 지도 모르겠다. 하지만 좌절하지는 않았다. 분명 내가 모르는 어느 지점에서 문제가 생긴 것이고 찾으면 되니. 매주 쉬는 날 없이 개발을 공부하다보니 지친 날도 있지만 그보단 고양감이 올라온다. 다음주에도 깨닫음을 얻을 수 있길.

- 12주차 : 11주차도 했지만, 중간에 페이징네이션 도입이 필요하다는 것을 느껴 같이 하다보니 생략됨. 우선 내가 CS 지식으로만 알던 것을 도입하다보니 왜 필요하고, 코드 작성도 중요하지만 이를 어떻게 해결할 것인지도 굉장히 중요하다는 것을 깨닫은 2주였다. 그러다 보니 회사에서는 어떻게 도입을 했고 왜 그랬는지 자연스럽게 관심이 간다. 물론 워낙 방대하고, 당장 있는 Task가 있어 전부 알 순 없지만 시간이 가용할 때마다 조사해봐야겠다는 생각이 들었다.




