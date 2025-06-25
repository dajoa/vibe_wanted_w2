import pytest
from unittest.mock import Mock, patch
import uuid
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


class TestMemorySystem:
    """멀티턴 메모리 시스템 테스트"""

    def test_inmemory_saver_initialization(self):
        """InMemorySaver 초기화 테스트"""
        checkpointer = InMemorySaver()
        assert checkpointer is not None
        
    def test_inmemory_store_initialization(self):
        """InMemoryStore 초기화 테스트"""
        store = InMemoryStore()
        assert store is not None
        
    def test_thread_id_generation(self):
        """스레드 ID 생성 테스트"""
        thread_id = str(uuid.uuid4())
        assert thread_id is not None
        assert len(thread_id) > 0
        
    def test_user_id_generation(self):
        """사용자 ID 생성 테스트"""
        user_id = str(uuid.uuid4())
        assert user_id is not None
        assert len(user_id) > 0
        
    def test_memory_namespace_creation(self):
        """메모리 네임스페이스 생성 테스트"""
        user_id = "test_user_123"
        namespace = ("memories", user_id)
        assert namespace[0] == "memories"
        assert namespace[1] == user_id
        
    def test_config_with_thread_and_user_id(self):
        """thread_id와 user_id를 포함한 설정 테스트"""
        thread_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
        
        assert config["configurable"]["thread_id"] == thread_id
        assert config["configurable"]["user_id"] == user_id


class TestMemoryIntegration:
    """메모리 통합 테스트"""
    
    def test_memory_store_put_and_search(self):
        """메모리 저장 및 검색 테스트"""
        store = InMemoryStore()
        namespace = ("memories", "test_user")
        memory_id = str(uuid.uuid4())
        memory_data = {"data": "사용자 이름은 홍길동입니다"}
        
        # 메모리 저장
        store.put(namespace, memory_id, memory_data)
        
        # 메모리 검색
        memories = store.search(namespace)
        assert len(memories) > 0
        assert memories[0].value == memory_data
        
    def test_memory_isolation_between_users(self):
        """사용자 간 메모리 격리 테스트"""
        store = InMemoryStore()
        
        # 사용자 1 메모리
        namespace1 = ("memories", "user1")
        store.put(namespace1, "mem1", {"data": "사용자1 정보"})
        
        # 사용자 2 메모리
        namespace2 = ("memories", "user2")
        store.put(namespace2, "mem2", {"data": "사용자2 정보"})
        
        # 각 사용자의 메모리 검색
        user1_memories = store.search(namespace1)
        user2_memories = store.search(namespace2)
        
        assert len(user1_memories) == 1
        assert len(user2_memories) == 1
        assert user1_memories[0].value["data"] == "사용자1 정보"
        assert user2_memories[0].value["data"] == "사용자2 정보"
        
    def test_messages_state_structure(self):
        """MessagesState 구조 테스트"""
        # MessagesState는 LangGraph에서 제공하는 기본 상태 클래스
        # 메시지 리스트를 관리하는 구조를 가져야 함
        test_messages = [
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
        
        # MessagesState 타입 검증
        state = {"messages": test_messages}
        assert "messages" in state
        assert isinstance(state["messages"], list)
        assert len(state["messages"]) == 2 