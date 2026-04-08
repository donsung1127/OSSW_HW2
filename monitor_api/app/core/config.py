from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Community Monitor API"
    API_V1_STR: str = "/api/v1"
    
    # ML 모델 설정 (예: HuggingFace 모델명 또는 로컬 경로)
    MODEL_NAME_OR_PATH: str = "smilegate-ai/kor_unsmile"
    
    # 모델 추론 임계값 (예: 스팸 판별 기준치)
    SPAM_THRESHOLD: float = 0.8
    TOXIC_THRESHOLD: float = 0.75

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
