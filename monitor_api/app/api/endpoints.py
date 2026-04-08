from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import TextAnalysisRequest, TextAnalysisResponse, BulkAnalysisResponse
from app.services.analyzer import inference_service
from app.services.scraper import scraper_service
import asyncio

router = APIRouter()

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_content(request: TextAnalysisRequest):
    """
    들어온 텍스트를 분석하여 스팸, 도배, 주제 이탈 여부를 반환합니다.
    """
    try:
        response = await inference_service.analyze_text(
            text=request.content,
            post_id=request.post_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.get("/analyze/dcinside/{gallery_id}", response_model=BulkAnalysisResponse)
async def analyze_dcinside_gallery(
    gallery_id: str = Path(..., description="DC인사이드 갤러리 ID (예: programming)")
):
    """
    특정 갤러리의 최근 실시간 글 약 20개를 가져와 AI 모델을 통해 유해성을 일괄 판단합니다.
    """
    try:
        # 1. 갤러리 최신 글 스크래핑
        posts = await scraper_service.get_recent_posts(gallery_id, limit=20)
        
        if not posts:
            raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다. (갤러리 ID 오류 또는 접근 차단)")

        # 2. AI 추론 작업 병렬 실행
        tasks = [
            inference_service.analyze_text(text=post["content"], post_id=post["post_id"])
            for post in posts
        ]
        results = await asyncio.gather(*tasks)

        return BulkAnalysisResponse(
            gallery_id=gallery_id,
            analyzed_count=len(results),
            results=list(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping/Inference error: {str(e)}")

