#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
Shopping Chat Agent 백엔드 서버
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("🚀 Shopping Chat Agent API Server 시작...")
    print(f"📖 API 문서: http://{settings.fastapi_host}:{settings.fastapi_port}/docs")
    print(f"🔍 ReDoc: http://{settings.fastapi_host}:{settings.fastapi_port}/redoc")
    
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True,
        log_level="info"
    ) 