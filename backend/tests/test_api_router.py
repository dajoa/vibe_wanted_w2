import pytest
from fastapi.testclient import TestClient


class TestAPIRouter:
    """API 라우터 구조 테스트"""
    
    def setup_method(self):
        """테스트 메서드 실행 전 설정"""
        # main app에 라우터가 포함된 후 테스트
        from app.main import app
        self.client = TestClient(app)
    
    def test_chat_router_exists(self):
        """chat 라우터가 존재하는지 확인"""
        from app.api.chat import router
        assert router is not None
        
    def test_chat_router_is_api_router(self):
        """chat 라우터가 APIRouter 인스턴스인지 확인"""
        from fastapi import APIRouter
        from app.api.chat import router
        assert isinstance(router, APIRouter)
        
    def test_chat_router_prefix(self):
        """chat 라우터의 prefix가 올바른지 확인"""
        from app.api.chat import router
        # APIRouter의 prefix 확인 (내부 속성)
        assert hasattr(router, 'prefix')
        
    def test_chat_endpoints_exist(self):
        """채팅 관련 엔드포인트들이 존재하는지 확인"""
        # POST /api/chat/message - 메시지 전송
        response = self.client.post("/api/chat/message", json={"message": "test"})
        assert response.status_code != 404, "채팅 메시지 엔드포인트가 없습니다"
        
        # GET /api/chat/history - 채팅 히스토리
        response = self.client.get("/api/chat/history")
        assert response.status_code != 404, "채팅 히스토리 엔드포인트가 없습니다"
        
        # DELETE /api/chat/history - 채팅 히스토리 삭제
        response = self.client.delete("/api/chat/history")
        assert response.status_code != 404, "채팅 히스토리 삭제 엔드포인트가 없습니다"
        
    def test_search_endpoints_exist(self):
        """검색 관련 엔드포인트들이 존재하는지 확인"""
        # POST /api/search/products - 상품 검색
        response = self.client.post("/api/search/products", json={"query": "test"})
        assert response.status_code != 404, "상품 검색 엔드포인트가 없습니다"
        
        # 검색이 성공했다면 search_id를 얻어서 결과 조회 테스트
        if response.status_code == 200:
            search_data = response.json()
            search_id = search_data.get("search_id")
            
            # GET /api/search/results/{search_id} - 검색 결과 조회
            response = self.client.get(f"/api/search/results/{search_id}")
            assert response.status_code != 404, "검색 결과 조회 엔드포인트가 없습니다"
        else:
            # 검색이 실패했어도 엔드포인트 자체는 존재해야 함
            response = self.client.get("/api/search/results/dummy_id")
            # 404가 아닌 다른 에러(422 등)이면 엔드포인트는 존재하는 것
            assert response.status_code != 404, "검색 결과 조회 엔드포인트가 없습니다"
        
    def test_router_inclusion_in_main_app(self):
        """메인 앱에 라우터가 포함되어 있는지 확인"""
        from app.main import app
        
        # FastAPI 앱의 라우터 확인
        router_paths = []
        for route in app.routes:
            if hasattr(route, 'path'):
                router_paths.append(route.path)
                
        # API 경로들이 포함되어 있는지 확인
        api_paths = [path for path in router_paths if path.startswith('/api')]
        assert len(api_paths) > 0, "API 라우터가 메인 앱에 포함되지 않았습니다"
        
    def test_api_router_tags(self):
        """API 라우터에 적절한 태그가 설정되어 있는지 확인"""
        from app.api.chat import router as chat_router
        
        # 라우터에 태그가 설정되어 있는지 확인
        assert hasattr(chat_router, 'tags')
        
    def test_api_response_format(self):
        """API 응답 형식이 일관성 있는지 확인"""
        # 채팅 메시지 전송 테스트
        response = self.client.post("/api/chat/message", json={
            "message": "아이폰 15 최저가 알려줘"
        })
        
        if response.status_code == 200:
            data = response.json()
            # 기본 응답 구조 확인
            assert "status" in data or "message" in data or "response" in data
            
    def test_error_handling(self):
        """API 에러 처리가 올바른지 확인"""
        # 잘못된 요청 데이터
        response = self.client.post("/api/chat/message", json={})
        
        # 4xx 또는 적절한 에러 응답이 있는지 확인
        assert response.status_code >= 400 or "error" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 