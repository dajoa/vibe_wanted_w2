"""
애플리케이션 설정 관리
환경 변수를 통한 설정 로드 및 검증
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # FastAPI 서버 설정
    fastapi_host: str = Field(default="localhost", description="FastAPI 서버 호스트")
    fastapi_port: int = Field(default=8000, ge=1, le=65535, description="FastAPI 서버 포트")
    
    # Streamlit 프론트엔드 설정
    streamlit_port: int = Field(default=8501, ge=1, le=65535, description="Streamlit 포트")
    
    # LangSmith 모니터링 설정
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API 키")
    
    # API 키들
    google_api_key: Optional[str] = Field(default=None, description="Google API 키")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API 키")
    langsmith_project: Optional[str] = Field(default="langgraph-agent", description="LangSmith 프로젝트명")
    
    # 환경 설정
    environment: str = Field(default="development", description="실행 환경 (development/production)")
    debug: bool = Field(default=True, description="디버그 모드")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
        
    def is_production(self) -> bool:
        """운영 환경인지 확인"""
        return self.environment.lower() == "production"
        
    def is_development(self) -> bool:
        """개발 환경인지 확인"""
        return self.environment.lower() == "development"


class Config:
    """Agent 관련 설정"""
    
    def __init__(self, settings: Settings = None):
        if settings is None:
            settings = Settings()
        self.GOOGLE_API_KEY = settings.google_api_key or ""
        self.LANGSMITH_API_KEY = settings.langsmith_api_key or ""
        self.LANGSMITH_PROJECT = settings.langsmith_project or "langgraph-agent"
        
    def configure_langsmith(self):
        """LangSmith 추적 설정"""
        if self.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT


# 전역 설정 인스턴스
settings = Settings()
config = Config(settings)


def get_settings() -> Settings:
    """설정 인스턴스 반환 (의존성 주입용)"""
    return settings 