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

## 개발 기간
- '2025. 12. 13 ~ 진행중

## 주요 기능
- 센서 데이터 수집
- 센서 데이터 조회 및 필터링

## 실행 방법

### 1. 가상환경 생성 및 활성화
```
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```
pip install -r requirements.txt
```

### 3. 서버 실행
```
python -m uvicorn app.main:app --reload
```

### 4. API 문서 확인
- Swagger UI: http://127.0.0.1:8000/docs

## 프로젝트 구조
```
RobosenseAPI/
├── app/
│   ├── main.py          # FastAPI 앱
│   ├── models/
│   │   └── sensor.py    # Pydantic 스키마
│   └── routes/
│       └── sensor_routes.py  # API 엔드포인트
├── .venv/
├── requirements.txt
└── README.md
```

## 기술 스택
- Python (3.11)
- FastAPI
- Uvicorn


