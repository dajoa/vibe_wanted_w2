import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import uuid
import json


class TestChatAPIMemory:
    """Chat API 멀티턴 메모리 기능 테스트"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트 생성"""
        from app.main import app
        return TestClient(app)
    
    def test_chat_api_with_session_support(self, client):
        """Chat API가 세션 지원을 하는지 테스트"""
        # 세션 ID와 사용자 ID를 포함한 요청
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        request_data = {
            "query": "iPhone 15에 대해 알려주세요",
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.return_value = "iPhone 15에 대한 정보입니다."
            mock_get_agent.return_value = mock_agent
            
            response = client.post("/api/chat", json=request_data)
            
            assert response.status_code == 200
            result = response.json()
            assert "response" in result
            assert result["response"] is not None
            
            # Agent가 올바른 매개변수로 호출되었는지 확인
            mock_agent.search_products_with_memory.assert_called_once_with(
                query="iPhone 15에 대해 알려주세요",
                thread_id=thread_id,
                user_id=user_id
            )
    
    def test_chat_api_multiturn_conversation(self, client):
        """Chat API 멀티턴 대화 테스트"""
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 첫 번째 대화
        request1 = {
            "query": "iPhone 15 가격이 어떻게 되나요?",
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        # 두 번째 대화 (같은 세션)
        request2 = {
            "query": "Galaxy S24와 비교해주세요",
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.side_effect = [
                "iPhone 15는 약 120만원입니다.",
                "이전에 문의하신 iPhone 15와 비교하면 Galaxy S24는..."
            ]
            mock_get_agent.return_value = mock_agent
            
            # 첫 번째 요청
            response1 = client.post("/api/chat", json=request1)
            assert response1.status_code == 200
            
            # 두 번째 요청
            response2 = client.post("/api/chat", json=request2)
            assert response2.status_code == 200
            
            # 두 번째 응답에서 컨텍스트가 유지되는지 확인
            result2 = response2.json()
            assert "iPhone 15" in result2["response"] or "이전" in result2["response"]
    
    def test_chat_api_without_session_ids(self, client):
        """세션 ID 없이 Chat API 호출 테스트 (기본값 사용)"""
        request_data = {
            "query": "iPhone 15에 대해 알려주세요"
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.return_value = "iPhone 15에 대한 정보입니다."
            mock_get_agent.return_value = mock_agent
            
            response = client.post("/api/chat", json=request_data)
            
            assert response.status_code == 200
            result = response.json()
            assert "response" in result
            
            # Agent가 기본값으로 호출되었는지 확인
            mock_agent.search_products_with_memory.assert_called_once()
            call_args = mock_agent.search_products_with_memory.call_args
            assert call_args[1]["query"] == "iPhone 15에 대해 알려주세요"
            assert call_args[1]["thread_id"] is not None
            assert call_args[1]["user_id"] is not None
    
    def test_chat_api_session_isolation(self, client):
        """서로 다른 세션 간 격리 테스트"""
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())
        thread1_id = str(uuid.uuid4())
        thread2_id = str(uuid.uuid4())
        
        # 사용자 1의 요청
        request1 = {
            "query": "iPhone 15 좋아해요",
            "thread_id": thread1_id,
            "user_id": user1_id
        }
        
        # 사용자 2의 요청
        request2 = {
            "query": "Galaxy S24 어떤가요?",
            "thread_id": thread2_id,
            "user_id": user2_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.side_effect = [
                "iPhone 15에 대한 정보를 저장했습니다.",
                "Galaxy S24에 대한 정보입니다."
            ]
            mock_get_agent.return_value = mock_agent
            
            # 두 요청 모두 처리
            response1 = client.post("/api/chat", json=request1)
            response2 = client.post("/api/chat", json=request2)
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # 각각 다른 세션 ID로 호출되었는지 확인
            calls = mock_agent.search_products_with_memory.call_args_list
            assert len(calls) == 2
            assert calls[0][1]["user_id"] == user1_id
            assert calls[1][1]["user_id"] == user2_id
            assert calls[0][1]["thread_id"] == thread1_id
            assert calls[1][1]["thread_id"] == thread2_id
    
    def test_chat_api_streaming_support(self, client):
        """Chat API 스트리밍 지원 테스트"""
        request_data = {
            "query": "iPhone 15에 대해 알려주세요",
            "stream": True,
            "thread_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4())
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.return_value = "iPhone 15에 대한 정보입니다."
            mock_get_agent.return_value = mock_agent
            
            response = client.post("/api/chat/stream", json=request_data)
            
            # 스트리밍 응답인지 확인
            assert response.status_code == 200
            assert response.headers.get("content-type") == "text/plain; charset=utf-8" 