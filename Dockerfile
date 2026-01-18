# 베이스 이미지 (c++ 컴파일 필요해서 3.11)
FROM python:3.11

# 작업 폴더 설정
WORKDIR /app

# 패키지 업데이트 및 C++빌더 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/list/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 포트 노출
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]