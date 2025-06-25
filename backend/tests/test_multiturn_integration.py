import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import uuid
import time


class TestMultiturnIntegration:
    """멀티턴 메모리 시스템 통합 테스트"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트 생성"""
        from app.main import app
        return TestClient(app)
    
    def test_complete_multiturn_conversation_flow(self, client):
        """완전한 멀티턴 대화 플로우 테스트"""
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 대화 시나리오
        conversations = [
            {
                "query": "iPhone 15에 대해 알려주세요",
                "expected_response": "iPhone 15에 대한 정보입니다."
            },
            {
                "query": "가격은 얼마인가요?",
                "expected_response": "이전에 문의하신 iPhone 15의 가격은 약 120만원입니다."
            },
            {
                "query": "Galaxy S24와 비교해주세요",
                "expected_response": "iPhone 15와 Galaxy S24를 비교하면..."
            },
            {
                "query": "어떤 걸 추천하시나요?",
                "expected_response": "사용자의 이전 대화를 고려하여 iPhone 15를 추천합니다."
            }
        ]
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            # 각 대화에 대한 응답 설정
            mock_agent.search_products_with_memory.side_effect = [
                conv["expected_response"] for conv in conversations
            ]
            mock_get_agent.return_value = mock_agent
            
            responses = []
            
            # 순차적으로 대화 진행
            for i, conv in enumerate(conversations):
                request_data = {
                    "query": conv["query"],
                    "thread_id": thread_id,
                    "user_id": user_id
                }
                
                response = client.post("/api/chat", json=request_data)
                assert response.status_code == 200
                
                result = response.json()
                assert "response" in result
                assert result["response"] == conv["expected_response"]
                responses.append(result)
                
                # 잠시 대기 (실제 대화 간격 시뮬레이션)
                time.sleep(0.1)
            
            # 모든 호출이 같은 세션 정보로 이루어졌는지 확인
            calls = mock_agent.search_products_with_memory.call_args_list
            assert len(calls) == len(conversations)
            
            for call in calls:
                assert call[1]["thread_id"] == thread_id
                assert call[1]["user_id"] == user_id
    
    def test_memory_persistence_across_sessions(self, client):
        """세션 간 메모리 지속성 테스트"""
        user_id = str(uuid.uuid4())
        
        # 첫 번째 세션
        thread_id_1 = str(uuid.uuid4())
        request1 = {
            "query": "iPhone 15 좋아해요. 기억해주세요.",
            "thread_id": thread_id_1,
            "user_id": user_id
        }
        
        # 두 번째 세션 (다른 thread_id, 같은 user_id)
        thread_id_2 = str(uuid.uuid4())
        request2 = {
            "query": "제가 좋아하는 제품이 뭐였죠?",
            "thread_id": thread_id_2,
            "user_id": user_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.side_effect = [
                "iPhone 15 선호도를 기억했습니다.",
                "이전에 iPhone 15를 좋아한다고 하셨네요."
            ]
            mock_get_agent.return_value = mock_agent
            
            # 첫 번째 세션
            response1 = client.post("/api/chat", json=request1)
            assert response1.status_code == 200
            
            # 두 번째 세션
            response2 = client.post("/api/chat", json=request2)
            assert response2.status_code == 200
            
            # 두 번째 응답에서 첫 번째 세션의 정보를 기억하는지 확인
            result2 = response2.json()
            assert "iPhone 15" in result2["response"]
    
    def test_user_isolation_in_multiturn(self, client):
        """멀티턴에서 사용자 격리 테스트"""
        # 사용자 A
        user_a_id = str(uuid.uuid4())
        thread_a_id = str(uuid.uuid4())
        
        # 사용자 B
        user_b_id = str(uuid.uuid4())
        thread_b_id = str(uuid.uuid4())
        
        # 사용자 A의 대화
        request_a1 = {
            "query": "iPhone 15 관심있어요",
            "thread_id": thread_a_id,
            "user_id": user_a_id
        }
        
        request_a2 = {
            "query": "제가 관심있는 제품이 뭐였죠?",
            "thread_id": thread_a_id,
            "user_id": user_a_id
        }
        
        # 사용자 B의 대화
        request_b1 = {
            "query": "Galaxy S24 좋아해요",
            "thread_id": thread_b_id,
            "user_id": user_b_id
        }
        
        request_b2 = {
            "query": "제가 좋아하는 제품이 뭐였죠?",
            "thread_id": thread_b_id,
            "user_id": user_b_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.side_effect = [
                "iPhone 15에 대한 관심을 기록했습니다.",      # A1
                "Galaxy S24 선호도를 기록했습니다.",         # B1
                "사용자 A는 iPhone 15에 관심을 보였습니다.",  # A2
                "사용자 B는 Galaxy S24를 좋아한다고 했습니다." # B2
            ]
            mock_get_agent.return_value = mock_agent
            
            # 사용자 A의 첫 번째 대화
            response_a1 = client.post("/api/chat", json=request_a1)
            assert response_a1.status_code == 200
            
            # 사용자 B의 첫 번째 대화
            response_b1 = client.post("/api/chat", json=request_b1)
            assert response_b1.status_code == 200
            
            # 사용자 A의 두 번째 대화
            response_a2 = client.post("/api/chat", json=request_a2)
            assert response_a2.status_code == 200
            result_a2 = response_a2.json()
            assert "iPhone 15" in result_a2["response"]
            
            # 사용자 B의 두 번째 대화
            response_b2 = client.post("/api/chat", json=request_b2)
            assert response_b2.status_code == 200
            result_b2 = response_b2.json()
            assert "Galaxy S24" in result_b2["response"]
            
            # 각 사용자가 자신의 정보만 기억하는지 확인
            calls = mock_agent.search_products_with_memory.call_args_list
            assert len(calls) == 4
            
            # 사용자별 호출 확인
            user_a_calls = [call for call in calls if call[1]["user_id"] == user_a_id]
            user_b_calls = [call for call in calls if call[1]["user_id"] == user_b_id]
            
            assert len(user_a_calls) == 2
            assert len(user_b_calls) == 2
    
    def test_streaming_multiturn_conversation(self, client):
        """스트리밍 멀티턴 대화 테스트"""
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 스트리밍 요청
        request_data = {
            "query": "iPhone 15에 대한 자세한 정보를 스트리밍으로 알려주세요",
            "thread_id": thread_id,
            "user_id": user_id,
            "stream": True
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.return_value = "iPhone 15는 애플의 최신 스마트폰입니다"
            mock_get_agent.return_value = mock_agent
            
            response = client.post("/api/chat/stream", json=request_data)
            
            assert response.status_code == 200
            assert response.headers.get("content-type") == "text/plain; charset=utf-8"
            
            # 스트리밍 응답 내용 확인
            content = response.text
            assert len(content) > 0
            assert "iPhone" in content
    
    def test_error_handling_in_multiturn(self, client):
        """멀티턴 대화에서 오류 처리 테스트"""
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        request_data = {
            "query": "iPhone 15에 대해 알려주세요",
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            # Agent에서 예외 발생 시뮬레이션
            mock_agent.search_products_with_memory.side_effect = Exception("검색 서비스 오류")
            mock_get_agent.return_value = mock_agent
            
            response = client.post("/api/chat", json=request_data)
            
            # 500 오류가 발생해야 함
            assert response.status_code == 500
            result = response.json()
            assert "검색 중 오류가 발생했습니다" in result["detail"]
    
    def test_concurrent_multiturn_conversations(self, client):
        """동시 멀티턴 대화 테스트"""
        # 여러 사용자의 동시 대화 시뮬레이션
        users = [
            {"user_id": str(uuid.uuid4()), "thread_id": str(uuid.uuid4())},
            {"user_id": str(uuid.uuid4()), "thread_id": str(uuid.uuid4())},
            {"user_id": str(uuid.uuid4()), "thread_id": str(uuid.uuid4())}
        ]
        
        with patch('app.api.chat.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.search_products_with_memory.side_effect = [
                f"사용자 {i+1}의 요청을 처리했습니다." for i in range(len(users))
            ]
            mock_get_agent.return_value = mock_agent
            
            responses = []
            
            # 동시에 여러 요청 전송
            for i, user in enumerate(users):
                request_data = {
                    "query": f"사용자 {i+1}의 상품 검색 요청",
                    "thread_id": user["thread_id"],
                    "user_id": user["user_id"]
                }
                
                response = client.post("/api/chat", json=request_data)
                assert response.status_code == 200
                responses.append(response.json())
            
            # 모든 응답이 올바르게 처리되었는지 확인
            assert len(responses) == len(users)
            for i, response in enumerate(responses):
                assert f"사용자 {i+1}" in response["response"] 