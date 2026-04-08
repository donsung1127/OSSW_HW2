from pydantic import BaseModel, Field
from typing import List, Optional

class TextAnalysisRequest(BaseModel):
    post_id: str = Field(..., description="게시글 또는 댓글의 고유 ID")
    content: str = Field(..., description="분석할 텍스트 내용", min_length=1)
    user_id: Optional[str] = Field(None, description="작성자 ID (도배 등 사용자 패턴 분석용)")

class LabelScore(BaseModel):
    label: str = Field(..., description="분류 라벨 (예: spam, toxic, off-topic, clean)")
    score: float = Field(..., description="모델이 예측한 확률 값")

class TextAnalysisResponse(BaseModel):
    post_id: str
    content: Optional[str] = None
    author: Optional[str] = None
    is_safe: bool = Field(..., description="승인 가능(안전한 글) 여부")
    action_required: Optional[str] = Field(None, description="필요한 조치 (예: block, flag, none)")
    details: List[LabelScore]

class BulkAnalysisResponse(BaseModel):
    gallery_id: str
    analyzed_count: int
    results: List[TextAnalysisResponse]
