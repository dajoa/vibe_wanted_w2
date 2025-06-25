import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestProductSearchAgent:
    """Test cases for ProductSearchAgent"""
    
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_agent_initialization(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test agent can be initialized properly"""
        # Mock return values
        mock_llm = Mock()
        mock_gemini.return_value = mock_llm
        
        mock_search_tool = Mock()
        mock_ddg_search.return_value = mock_search_tool
        
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        from app.agents.product_search_agent import ProductSearchAgent
        agent = ProductSearchAgent()
        
        assert agent is not None
        assert hasattr(agent, 'agent')
        assert agent.agent == mock_agent
        
        # Verify mocks were called
        mock_gemini.assert_called_once()
        mock_ddg_search.assert_called_once()
        mock_create_react_agent.assert_called_once()
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_products_with_valid_query(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test agent can search products with valid query"""
        # Mock agent response
        mock_agent = Mock()
        mock_response = {
            "messages": [
                Mock(content="테스트 상품에 대한 검색 결과입니다. iPhone 15는 Apple의 최신 스마트폰입니다.")
            ]
        }
        mock_agent.invoke.return_value = mock_response
        mock_create_react_agent.return_value = mock_agent
        
        from app.agents.product_search_agent import ProductSearchAgent
        agent = ProductSearchAgent()
        result = agent.search_products("iPhone 15")
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "iPhone 15" in result
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_products_with_empty_query(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test agent handles empty query appropriately"""
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        from app.agents.product_search_agent import ProductSearchAgent
        agent = ProductSearchAgent()
        result = agent.search_products("")
        
        assert result is not None
        assert isinstance(result, str)
        assert "검색할 상품명을 입력해주세요" in result
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    @patch('app.agents.product_search_agent.create_react_agent')
    def test_search_products_with_agent_error(self, mock_create_react_agent, mock_ddg_search, mock_gemini):
        """Test agent handles errors gracefully"""
        # Mock agent to raise exception
        mock_agent = Mock()
        mock_agent.invoke.side_effect = Exception("Test error")
        mock_create_react_agent.return_value = mock_agent
        
        from app.agents.product_search_agent import ProductSearchAgent
        agent = ProductSearchAgent()
        result = agent.search_products("test query")
        
        assert result is not None
        assert isinstance(result, str)
        assert "검색 중 오류가 발생했습니다" in result 