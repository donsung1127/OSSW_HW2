from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="실시간 커뮤니티 모니터링 및 필터링을 위한 MLOps Inference API",
        version="1.0.0",
    )

    # API 라우터 등록
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    def health_check():
        """로드밸런서(L4/L7) 및 쿠버네티스의 Readiness/Liveness Probe를 위한 엔드포인트"""
        return {"status": "ok", "model_loaded": True}

    return app

app = create_app()
