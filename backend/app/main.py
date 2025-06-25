"""
FastAPI 메인 애플리케이션
온라인 쇼핑 최저가 검색 챗봇 Agent 백엔드 서버
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.config import settings
from app.api.chat import router as chat_router
from app.api.search import router as search_router

# 환경 변수 로드
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    print("🚀 Shopping Chat Agent API Server started!")
    print(f"📖 API Documentation: http://localhost:8000/docs")
    yield
    # 종료 시 실행
    print("🛑 Shopping Chat Agent API Server stopped!")


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="Shopping Chat Agent",
    description="온라인 쇼핑 시 특정 상품의 최저가를 자동으로 검색하고 비교하여 리스트업해주는 챗봇형 Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용 - 운영에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(chat_router)
app.include_router(search_router)


@app.get("/")
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return {
        "message": "Shopping Chat Agent API Server",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트 - 서버 상태 모니터링"""
    return {
        "status": "healthy",
        "service": "Shopping Chat Agent",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/info")
async def api_info():
    """API 정보 엔드포인트 - 서버 정보 제공"""
    return {
        "name": "Shopping Chat Agent API",
        "version": "1.0.0",
        "description": "최저가 검색 챗봇 Agent API",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "info": "/info",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# 기존 on_event는 lifespan으로 대체됨


if __name__ == "__main__":
    import uvicorn
    
    # 환경 변수에서 설정 읽기
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    
    # 서버 실행
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 