import logging
from transformers import pipeline
from app.models.schemas import TextAnalysisResponse, LabelScore
from app.core.config import settings

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self):
        try:
            logger.info(f"[{settings.PROJECT_NAME}] Loading ML Model: {settings.MODEL_NAME_OR_PATH}...")
            # 한국어 혐오 표현/스팸 분류로 많이 쓰이는 smilegate-ai/kor_unsmile 활용
            self.classifier = pipeline(
                "text-classification", 
                model=settings.MODEL_NAME_OR_PATH,
                top_k=None
            )
            print("ML Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.classifier = None

    async def analyze_text(self, text: str, post_id: str) -> TextAnalysisResponse:
        if not self.classifier:
            raise RuntimeError("ML Pipeline is not initialized")

        # 허깅페이스 모델 추론 (로컬 CPU/GPU 활용)
        predictions = self.classifier(text)[0]
        
        scores = []
        is_safe = True
        action = "none"
        
        # 모델의 출력 결과 분석
        # kor_unsmile 모델은 'clean', '욕설', '악플/혐오' 등 다중 라벨에 대한 확률을 반환합니다.
        for pred in predictions:
            label = pred['label']
            score = pred['score']
            scores.append(LabelScore(label=label, score=score))
            
            # clean 라벨이 아닌 유해 라벨들의 점수가 임계값을 넘는지 확인
            if label != 'clean':
                if score > settings.TOXIC_THRESHOLD:
                    is_safe = False
                    action = "block" # 차단
                elif score > (settings.TOXIC_THRESHOLD - 0.2) and action == "none":
                    is_safe = False
                    action = "flag" # 검토 필요
                    
        # 'clean' 점수가 다른 모든 위험 모델 점수보다 압도적으로 높다면 안전으로 간주
        clean_score = next((s.score for s in scores if s.label == 'clean'), 0.0)
        if clean_score > 0.8:
            is_safe = True
            action = "none"

        return TextAnalysisResponse(
            post_id=post_id,
            content=text,
            is_safe=is_safe,
            action_required=action,
            details=scores
        )


# 싱글톤으로 사용하여 모델이 매번 새로 로드되지 않도록 합니다.
inference_service = InferenceService()
