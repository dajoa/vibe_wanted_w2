"""
Streamlit 챗봇 애플리케이션 테스트
"""
import pytest
from streamlit.testing.v1 import AppTest


class TestStreamlitChatApp:
    """Streamlit 챗봇 앱 테스트 클래스"""
    
    def test_app_initialization(self):
        """앱이 정상적으로 초기화되는지 테스트"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # 앱이 정상적으로 실행되는지 확인
        assert not at.exception
        
    def test_app_title_display(self):
        """앱 타이틀이 정상적으로 표시되는지 테스트"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # 타이틀이 존재하는지 확인
        assert len(at.title) > 0
        assert "상품 검색 챗봇" in at.title[0].value
        
    def test_chat_interface_exists(self):
        """채팅 인터페이스가 존재하는지 테스트"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # 채팅 입력 위젯이 존재하는지 확인
        assert len(at.chat_input) > 0
        
    def test_session_state_initialization(self):
        """세션 상태가 정상적으로 초기화되는지 테스트"""
        at = AppTest.from_file("app.py")
        at.run()
        
        # 메시지 히스토리가 초기화되었는지 확인
        assert "messages" in at.session_state
        assert isinstance(at.session_state["messages"], list)
        assert len(at.session_state["messages"]) == 0 