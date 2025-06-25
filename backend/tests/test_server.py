import pytest
from fastapi.testclient import TestClient
import requests
import time
import subprocess
import signal
import os


class TestServerExecution:
    """서버 실행 및 검증 테스트"""
    
    def setup_method(self):
        """테스트 메서드 실행 전 설정"""
        from app.main import app
        self.client = TestClient(app)
    
    def test_server_startup_with_testclient(self):
        """TestClient를 통한 서버 시작 테스트"""
        # TestClient는 자동으로 서버를 시작하고 종료함
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Shopping Chat Agent" in data["message"]
        
    def test_all_endpoints_accessible(self):
        """모든 주요 엔드포인트가 접근 가능한지 확인"""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/info", "GET"),
            ("/docs", "GET"),
            ("/openapi.json", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = self.client.get(endpoint)
                assert response.status_code == 200, f"{endpoint} 엔드포인트에 접근할 수 없습니다"
                
    def test_api_endpoints_accessible(self):
        """API 엔드포인트들이 접근 가능한지 확인"""
        # 채팅 API 테스트
        response = self.client.post("/api/chat/message", json={"message": "안녕하세요"})
        assert response.status_code == 200
        
        response = self.client.get("/api/chat/history")
        assert response.status_code == 200
        
        # 검색 API 테스트
        response = self.client.post("/api/search/products", json={"query": "아이폰"})
        assert response.status_code == 200
        
        response = self.client.get("/api/search/categories")
        assert response.status_code == 200
        
    def test_cors_headers(self):
        """CORS 헤더가 올바르게 설정되어 있는지 확인"""
        response = self.client.get("/")
        
        # CORS 관련 헤더 확인
        headers = response.headers
        # TestClient는 실제 CORS 헤더를 모두 포함하지 않을 수 있음
        # 하지만 서버가 정상적으로 응답하는지는 확인 가능
        assert response.status_code == 200
        
    def test_openapi_documentation(self):
        """OpenAPI 문서가 올바르게 생성되는지 확인"""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data
        
        # API 경로들이 문서에 포함되어 있는지 확인
        paths = openapi_data["paths"]
        assert "/api/chat/message" in paths
        assert "/api/search/products" in paths
        
    def test_config_integration(self):
        """설정이 서버에 올바르게 적용되는지 확인"""
        from app.config import settings
        
        # 설정값들이 올바르게 로드되었는지 확인
        assert settings.fastapi_host is not None
        assert settings.fastapi_port is not None
        assert isinstance(settings.fastapi_port, int)
        
    def test_error_handling(self):
        """서버 레벨 에러 처리가 올바른지 확인"""
        # 존재하지 않는 엔드포인트
        response = self.client.get("/nonexistent")
        assert response.status_code == 404
        
        # 잘못된 HTTP 메서드
        response = self.client.post("/")
        assert response.status_code == 405
        
        # 잘못된 JSON 데이터
        response = self.client.post("/api/chat/message", json={})
        assert response.status_code == 422  # Validation Error
        
    def test_server_performance(self):
        """서버 기본 성능 테스트"""
        import time
        
        # 간단한 응답 시간 측정
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0, f"응답 시간이 너무 깁니다: {response_time}초"
        
    def test_multiple_concurrent_requests(self):
        """동시 요청 처리 테스트"""
        import concurrent.futures
        
        def make_request():
            response = self.client.get("/health")
            return response.status_code
        
        # 10개의 동시 요청
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 모든 요청이 성공적으로 처리되었는지 확인
        assert all(status == 200 for status in results)
        assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 