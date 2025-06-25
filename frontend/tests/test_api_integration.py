"""
FastAPI 백엔드 연동 테스트
"""
import pytest
from unittest.mock import Mock, patch
from api_client import APIClient


class TestAPIIntegration:
    """API 연동 테스트 클래스"""
    
    def test_api_client_initialization(self):
        """API 클라이언트가 정상적으로 초기화되는지 테스트"""
        client = APIClient()
        assert client is not None
        assert hasattr(client, 'base_url')
        assert client.base_url == "http://localhost:8000"
    
    @patch('requests.post')
    def test_search_products_success(self, mock_post):
        """상품 검색 API 호출 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "iPhone 15에 대한 검색 결과입니다...",
            "query": "iPhone 15"
        }
        mock_post.return_value = mock_response
        
        # API 클라이언트 테스트
        client = APIClient()
        result = client.search_products("iPhone 15")
        
        assert result is not None
        assert "iPhone 15에 대한 검색 결과" in result
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_search_products_error_handling(self, mock_post):
        """상품 검색 API 에러 처리 테스트"""
        # Mock 에러 응답 설정
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")
        mock_post.return_value = mock_response
        
        # API 클라이언트 테스트
        client = APIClient()
        result = client.search_products("테스트")
        
        assert "오류가 발생했습니다" in result
    
    def test_api_client_url_configuration(self):
        """API 클라이언트 URL 설정 테스트"""
        client = APIClient("http://custom:9000")
        assert client.base_url == "http://custom:9000" 