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

        # 2. 블랙리스트 필터링 및 AI 추론 작업 준비
        from app.core.config import settings
        
        results = []
        inference_tasks = []
        
        for post in posts:
            author = post.get("author", "익명")
            if author in settings.BLACKLIST_NICKNAMES:
                # 블랙리스트에 포함된 경우 AI 모델 없이 즉시 차단 판정
                results.append(TextAnalysisResponse(
                    post_id=post["post_id"],
                    content=post["content"],
                    author=author,
                    is_safe=False,
                    action_required="block",
                    details=[LabelScore(label="blacklist", score=1.0)]
                ))
            else:
                # 일반 유저는 AI 추론 예약
                inference_tasks.append(
                    (author, inference_service.analyze_text(text=post["content"], post_id=post["post_id"]))
                )

        if inference_tasks:
            # AI 추론 작업 병렬 실행
            authors = [t[0] for t in inference_tasks]
            tasks = [t[1] for t in inference_tasks]
            inference_results = await asyncio.gather(*tasks)
            
            # 작성자 정보 매칭하여 최종 결과에 추가
            for author, res in zip(authors, inference_results):
                res.author = author
                results.append(res)

        return BulkAnalysisResponse(
            gallery_id=gallery_id,
            analyzed_count=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping/Inference error: {str(e)}")

