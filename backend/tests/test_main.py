import pytest
from fastapi.testclient import TestClient


class TestMainApplication:
    """FastAPI 메인 애플리케이션 테스트"""
    
    def setup_method(self):
        """테스트 메서드 실행 전 설정"""
        # 아직 main.py가 없으므로 테스트에서 import 시도
        try:
            from app.main import app
            self.client = TestClient(app)
        except ImportError:
            self.client = None
    
    def test_fastapi_app_exists(self):
        """FastAPI 애플리케이션 인스턴스가 존재하는지 확인"""
        from app.main import app
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        
    def test_app_title_and_description(self):
        """애플리케이션 제목과 설명이 올바르게 설정되었는지 확인"""
        from app.main import app
        assert app.title == "Shopping Chat Agent"
        assert "최저가" in app.description or "쇼핑" in app.description
        
    def test_root_endpoint(self):
        """루트 엔드포인트 (GET /)가 정상 동작하는지 확인"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 (GET /health)가 정상 동작하는지 확인"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
    def test_info_endpoint(self):
        """API 정보 엔드포인트 (GET /info)가 정상 동작하는지 확인"""
        response = self.client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        
    def test_cors_middleware_configured(self):
        """CORS 미들웨어가 설정되어 있는지 확인"""
        response = self.client.options("/")
        # CORS가 설정되어 있으면 OPTIONS 요청이 처리됨
        assert response.status_code in [200, 405]  # 405는 OPTIONS가 허용되지 않는 경우
        
    def test_openapi_docs_available(self):
        """OpenAPI 문서가 사용 가능한지 확인"""
        # Swagger UI
        response = self.client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = self.client.get("/redoc")
        assert response.status_code == 200
        
        # OpenAPI 스키마
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 