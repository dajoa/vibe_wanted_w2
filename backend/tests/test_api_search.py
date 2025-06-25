import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os


class TestSearchAPI:
    """Test cases for search API endpoint"""
    
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_endpoint_exists(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test search endpoint exists and returns proper response"""
        # Mock agent response
        mock_agent = Mock()
        mock_response = {
            "messages": [
                Mock(content="테스트 상품 검색 결과")
            ]
        }
        mock_agent.invoke.return_value = mock_response
        mock_create_react_agent.return_value = mock_agent
        
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/api/search", json={"query": "테스트"})
        assert response.status_code in [200, 422]  # 422 if validation fails
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_with_valid_query(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test search with valid product query"""
        mock_agent = Mock()
        mock_response = {
            "messages": [
                Mock(content="iPhone 15 검색 결과입니다.")
            ]
        }
        mock_agent.invoke.return_value = mock_response
        mock_create_react_agent.return_value = mock_agent
        
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/api/search", json={"query": "iPhone 15"})
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert isinstance(data["result"], str)
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_with_empty_query(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test search with empty query"""
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/api/search", json={"query": ""})
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        
    def test_search_without_query(self):
        """Test search without query parameter"""
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/api/search", json={})
        assert response.status_code == 422  # Validation error
        
    def test_search_invalid_json(self):
        """Test search with invalid JSON"""
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/api/search", data="invalid json")
        assert response.status_code == 422 