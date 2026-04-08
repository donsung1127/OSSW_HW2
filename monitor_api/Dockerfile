# 빌드 스테이지
FROM python:3.11-slim AS builder

WORKDIR /app

# 파이썬 캐시 생성을 방지하고 버퍼 없이 출력하도록 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 빌드에 필요한 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 (의존성 캐시 활용)
COPY requirements.txt .

# 머신러닝 의존성(PyTorch)은 CPU 버전으로 최적화 설치하여 이미지 크기 대폭 감소
# 다른 패키지들도 함께 설치
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

# ---------------------------------------------------- #
# 실행 스테이지
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 보안을 위해 non-root 사용자 생성
RUN addgroup --system appgroup && adduser --system --group appuser

# 빌드 스테이지에서 생성된 wheel 파일들을 복사하여 다시 설치 (컴파일 흔적 방지)
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# 소스코드 복사
COPY ./app ./app

# 소유권 변경
RUN chown -R appuser:appgroup /app

# Non-root 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
