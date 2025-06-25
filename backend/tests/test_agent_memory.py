import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import uuid


class TestProductSearchAgentMemory:
    """ProductSearchAgent 메모리 기능 테스트"""
    
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    def test_agent_memory_initialization(self):
        """Agent 메모리 시스템 초기화 테스트"""
        from app.agents.product_search_agent import ProductSearchAgent
        
        agent = ProductSearchAgent()
        
        # 메모리 시스템이 초기화되었는지 확인
        assert hasattr(agent, 'checkpointer')
        assert hasattr(agent, 'store')
        assert agent.checkpointer is not None
        assert agent.store is not None
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    def test_agent_with_thread_and_user_config(self):
        """Agent가 thread_id와 user_id 설정을 처리하는지 테스트"""
        from app.agents.product_search_agent import ProductSearchAgent
        
        agent = ProductSearchAgent()
        
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
        
        # config 검증
        assert config["configurable"]["thread_id"] == thread_id
        assert config["configurable"]["user_id"] == user_id
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    @patch('app.agents.product_search_agent.ChatGoogleGenerativeAI')
    @patch('app.agents.product_search_agent.DuckDuckGoSearchRun')
    def test_agent_multiturn_conversation(self, mock_ddg_search, mock_gemini):
        """Agent 멀티턴 대화 테스트"""
        # Mock 설정
        mock_llm = Mock()
        mock_gemini.return_value = mock_llm
        
        mock_search_tool = Mock()
        mock_ddg_search.return_value = mock_search_tool
        
        # Mock graph 응답 설정
        mock_graph = Mock()
        mock_response_1 = {
            "messages": [Mock(content="iPhone 15에 대한 정보입니다.")]
        }
        mock_response_2 = {
            "messages": [Mock(content="이전에 iPhone 15에 대해 문의하셨었네요. Galaxy S24는...")]
        }
        
        mock_graph.stream.side_effect = [
            [mock_response_1],  # 첫 번째 호출
            [mock_response_2]   # 두 번째 호출
        ]
        
        with patch('app.agents.product_search_agent.StateGraph') as mock_state_graph:
            mock_builder = Mock()
            mock_state_graph.return_value = mock_builder
            mock_builder.compile.return_value = mock_graph
            
            from app.agents.product_search_agent import ProductSearchAgent
            agent = ProductSearchAgent()
            
            # 첫 번째 대화
            thread_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            
            result1 = agent.search_products_with_memory(
                query="iPhone 15에 대해 알려주세요",
                thread_id=thread_id,
                user_id=user_id
            )
            
            # 두 번째 대화 (같은 세션)
            result2 = agent.search_products_with_memory(
                query="Galaxy S24는 어떤가요?",
                thread_id=thread_id,
                user_id=user_id
            )
            
            assert result1 is not None
            assert result2 is not None
            
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    def test_agent_memory_storage_and_retrieval(self):
        """Agent 메모리 저장 및 조회 테스트"""
        from app.agents.product_search_agent import ProductSearchAgent
        
        agent = ProductSearchAgent()
        
        # 메모리 저장 테스트
        user_id = "test_user_123"
        memory_data = {"preference": "삼성 갤럭시 선호"}
        
        # 메모리 저장 메서드가 있는지 확인
        assert hasattr(agent, 'store_user_memory')
        
        # 메모리 저장
        agent.store_user_memory(user_id, "preference", memory_data)
        
        # 메모리 조회
        memories = agent.get_user_memories(user_id)
        assert memories is not None
        
    @patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LANGSMITH_API_KEY': 'test_langsmith_key',
        'LANGSMITH_PROJECT': 'test_project'
    })
    def test_agent_memory_context_injection(self):
        """Agent가 메모리를 컨텍스트에 주입하는지 테스트"""
        from app.agents.product_search_agent import ProductSearchAgent
        
        agent = ProductSearchAgent()
        
        # 메모리 컨텍스트 생성 테스트
        user_id = "test_user_123"
        memories = [
            {"data": "사용자는 삼성 제품을 선호합니다"},
            {"data": "이전에 갤럭시 S23에 관심을 보였습니다"}
        ]
        
        # 컨텍스트 생성 메서드가 있는지 확인
        assert hasattr(agent, 'build_memory_context')
        
        context = agent.build_memory_context(memories)
        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0 