from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="실시간 커뮤니티 모니터링 및 필터링을 위한 MLOps Inference API",
        version="1.0.0",
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 라우터 등록
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 정적 파일 서빙 설정 (UI)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    @app.get("/health")
    def health_check():
        """로드밸런서(L4/L7) 및 쿠버네티스의 Readiness/Liveness Probe를 위한 엔드포인트"""
        return {"status": "ok", "model_loaded": True}

    return app

app = create_app()
