# RoboSense API

## 부제
```
High-Performance Sensor Data Processing API for Robotics
(로보틱스를 위한 고성능 센서 데이터 처리 API)
```

## 목적
```
대용량 센서 데이터를 실시간으로 처리 후, 대규모 트래픽 처리 경험을 극한까지 설정 및 최적화
Python과 C++ 병합
```

## 개발 타임라인
- '25. 12. 13 ~ '26. 01. 03 : 프로토 타입 작성
- '26. 01. 04 : 첫 부하 테스트 진행 [TPS : 26]
- '26. 01. 04 ~ '26. 01. 11 : Redis 도입, 페이징네이션 도입(Cursor)
- '26. 01. 11 ~ '26. 01. 18 : Docker Compose 작성, 2번째 부하 테스트 [TPS : 489]
   * FastAPI 5개 + Nginx + Docker
- '26. 01. 18 ~ '26. 01. 25 : 복합 인덱스 추가, N+1문제 해결, 최적화 여부 확인 [TPS : 653]
- '26. 01. 25 ~ '26. 02. 01 : 쿼리 최적화, 캐시워밍, Bulk insert 도입, 배치 간격 최적화 [TPS : 1,001]
- '26. 02. 01 ~ '26. 02. 08 : C++ 모듈 도입 (센서 데이터, stats) [TPS : 1,001]
- '26. 02. 09 ~ '26. 02. 17 : C++ 모듈 도입 (filtered), C++과 Python 연산 속도 비교

## 주요 기능
- POST /api/sensors - 센서 데이터 수집
- GET /api/sensors - 센서 데이터 조회 및 필터링
- GET /api/sensors?robot_id={id} - 특정 로봇 센서 조회
- GET /api/sensors?sensor_type={type} - 센서 타입별 조회
- POST /api/robots - 로봇 등록
- GET /api/robots - 로봇 목록 조회
- GET /api/robots/{id} - 특정 로봇 목록 조회
- GET /api/stats - 최근 1시간 통계 조회
- GET /api/sensors/filtered?robot_id={id}&sensor_type={type}&field={field}&window_size=5 - 최근 5초간 이동평균 조회

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
docker-compose logs -f fastapi-1 (특정 서비스)
locust -f test/locustfile.py --host=http://localhost (Locust)
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
│   │   ├── sensor.py           # 센서 Pydantic 스키마
│   │   ├── robot.py            # 로봇 Pydantic 스키마
│   │   └── enum.py             # Enum 타입 정의
│   └── routes/
│       ├── __init__.py
│       ├── sensor_routes.py    # 센서 데이터 API
│       ├── robot_routes.py     # 로봇 관리 API
│       └── stats_routes.py     # 통계 API
├── cpp_modules/                # C++ 모듈
│   └── sensor_cpp/
│       ├── sensor.cpp          # C++ 직렬화 & 필터링 & 통계 계산
│       ├── sensor.h            # 헤더 파일
│       ├── setup.py            # pybind11 빌드 설정
│       └── test/
│           ├── test_sensor_cpp.py      # pytest 단위 테스트
│           └── test_bindings.py        # Catch2 테스트 (참고용)
├── scripts/
│   ├── quick_mock.py           # Mock 데이터 생성
│   └── db_test.py              # DB 쿼리 테스트
├── tests/
│   └── locustfile.py           # 부하 테스트 시나리오
├── .venv/                      # 가상환경 (gitignore)
├── Dockerfile                  # FastAPI 이미지 빌드
├── docker-compose.yml          # 전체 시스템 구성
├── nginx.conf                  # Nginx 로드 밸런서 설정
├── .dockerignore
├── requirements.txt            # Python 의존성
├── .env                        # 환경 변수 (gitignore)
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
- C++ (17)
- FastAPI
- Uvicorn
- PostgreSQL (16)
- SQLAlchemy
- Docker
- Locust
- Redis (7.1.0)
- Py-spy
- Pybind11 (Python-C++ 바인딩)
- Pytest

## 부하 테스트
- Week 10 ('26. 01. 04.)
```
기준 : User 50명, Spawn Rate 5명/초, Data 50,000개
결과 : TPS (26) / Fail (0%)

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
결과 : TPS (489) / Fail (0%)

< 분석사항 >
1. TPS가 최대 800까지 상승. 긍정적임
2. 다만 stats에서 1분 단위로 캐시무효화 전략을 할 때마다 TPS가 급격히 낮아짐
3. DB가 늘어남에 따라 속도가 점점 낮아짐

< 결론 >
1. 캐시 워밍업 필요
2. 쿼리 최적화, 커넥션 풀 사이즈 재조정
```

- Week 15 ('26. 02. 08.)
```
기준 : User 500명, Spawn Rate 50명/초, Data 재생성
변경점 : C++ 모듈 도입
결과 : TPS (1,001) / Fail (0%)

< 분석사항 >
1. TPS가 최대 1,001까지 상승. 긍정적임
2. C++ 모듈을 넣었지만, 임팩트 있는 효과는 보지 못함. 그러나 이런 기능이 있고 구현 했다는 것에 의의
3. Py-spy 분석 결과 : PostgreSQL이 98% 병목 (CPU 600%)
4. 배치 간격 최적화 : 1.0s -> 0.3s
5. C++ 도입 간 CMake와 Setup 방식이 있음. 나는 Setup으로 사용함

< 결론 >
1. 모든 엔드포인트가 전부 400~500ms가 소요. 
2. DB 커밋이 주요 병목 (평균 ~70ms → 0.3s 배치로 ~21ms 개선)
3. C++ 효과는 미미(2~3%)하지만 학습 가치 있음
4. 추가 최적화: Nginx keepalive, asyncpg COPY, 워커 병렬화 검토 필요
```

- Week 16 ('26. 02. 17.)
```
기준 : User 100명, Spawn Rate 10명/초, Data 재생성
변경점 : C++ 모듈 도입. 최적화는 하지 않아, 단순 C++과 Python의 속도 차이 비교
C++ 결과 : 720 ~ 880ms / Fail (0%)
Python 결과 : 940 ~ 1100ms / Fail (0%)

< 분석사항 >
1. 우선 filtered 엔드포인트 최적화를 하지 않은 상태인 것을 감안
2. C++과 Python의 경우 전체 20%의 속도 차이를 보임

< 결론 >
1. 해당 엔드포인트 최적화 필요. (측정 시간도 1분 측정 기준이지만, 현실을 기준으로 5초로 변경 필요)
2. 이동평균 계산만으로도 20% 차이라면, 응용 시 굉장한 속도 차이를 보일 것으로 판단
3. 해당 엔드포인트만 계산 시 더 많은 차이를 보일 것으로 예상됨
```


## 회고
- 10주차 : FastAPI 사용해서 프로그램 만들 때까지, 처음 보는 것들이 너무 많아 힘들다고 생각했는데 산 넘어 산인 것 같다. TPS를 측정하고 분석하니 어디서부터 손을 대야할 지도 모르겠다. 하지만 좌절하지는 않았다. 분명 내가 모르는 어느 지점에서 문제가 생긴 것이고 찾으면 되니. 매주 쉬는 날 없이 개발을 공부하다보니 지친 날도 있지만 그보단 고양감이 올라온다. 다음주에도 깨닫음을 얻을 수 있길.

- 12주차 : 11주차도 했지만, 중간에 페이징네이션 도입이 필요하다는 것을 느껴 같이 하다보니 생략됨. 우선 내가 CS 지식으로만 알던 것을 도입하다보니 왜 필요하고, 코드 작성도 중요하지만 이를 어떻게 해결할 것인지도 굉장히 중요하다는 것을 깨닫은 2주였다. 그러다 보니 회사에서는 어떻게 도입을 했고 왜 그랬는지 자연스럽게 관심이 간다. 물론 워낙 방대하고, 당장 있는 Task가 있어 전부 알 순 없지만 시간이 가용할 때마다 조사해봐야겠다는 생각이 들었다.

- 15주차 : 드디어 하고 싶던 C++ 모듈과 Python을 결합해보았다. Python자체가 중요한 부분은 c++로 연산처리하기에 효과적인 TPS의 상승은 없었지만, 굉장히 만족한다. 다만 갈수록 내가 알지 못하는 것, 어떤 부분을 병목 상태인지 해결할 것인지 모르겠다. 더 세부적으로 알아보고 극한으로 올릴 방법에 대해 공부해볼 필요가 있을 듯.

- 16주차 : C++과 연동하면서 갑자기 어려운 지점들이 나와 쉽지 않았다. 다행히 설날이 겹쳐 많은 시간을 투자했더니, 어느 정도 이해가 되는 부분이 많았다. 놀란 부분은 내가 이론적으로 알고 있던 속도 차이가 실제로 일어났을때다. 전체적으로 29%에다 User도 100으로 설정했으니 C++의 장점을 분명히 알 수 있었다. 물론 Python의 연산에서 중요한 부분은 C++로 실행하지만, 세밀한 옵션에 차이를 두면 좋다는 것도 깨닫았다.





