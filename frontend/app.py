"""
상품 검색 챗봇 - Streamlit 애플리케이션 (멀티턴 메모리 지원)
"""
import streamlit as st
import uuid
from api_client import APIClient


def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="상품 검색 챗봇 (멀티턴 메모리)",
        page_icon="🛒",
        layout="wide"
    )
    
    # 앱 타이틀
    st.title("🛒 상품 검색 챗봇 (멀티턴 메모리)")
    st.markdown("이전 대화를 기억하는 AI 챗봇입니다! 원하는 상품을 검색해보세요!")
    
    # API 클라이언트 초기화
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 멀티턴 메모리를 위한 세션 ID 초기화
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    # 사이드바에 시스템 정보 표시
    with st.sidebar:
        st.header("🔧 시스템 상태")
        if st.button("서버 상태 확인"):
            with st.spinner("서버 상태 확인 중..."):
                is_healthy = st.session_state.api_client.health_check()
                if is_healthy:
                    st.success("✅ 백엔드 서버 정상 작동")
                else:
                    st.error("❌ 백엔드 서버 연결 실패")
        
        st.divider()
        st.markdown("### 🧠 멀티턴 메모리")
        st.markdown(f"**세션 ID**: `{st.session_state.thread_id[:8]}...`")
        st.markdown(f"**사용자 ID**: `{st.session_state.user_id[:8]}...`")
        st.markdown(f"**대화 수**: {len(st.session_state.messages) // 2}")
        
        # 멀티턴 테스트 버튼 추가
        if st.button("멀티턴 테스트"):
            with st.spinner("멀티턴 메모리 테스트 중..."):
                # 첫 번째 테스트
                test_response1 = st.session_state.api_client.chat_with_memory(
                    query="갤럭시 스마트폰 추천해줘",
                    thread_id=st.session_state.thread_id,
                    user_id=st.session_state.user_id
                )
                
                # 두 번째 테스트
                test_response2 = st.session_state.api_client.chat_with_memory(
                    query="그 중에서 50만원 이하인 것만 추천해줘",
                    thread_id=st.session_state.thread_id,
                    user_id=st.session_state.user_id
                )
                
                # 결과 표시
                if "갤럭시 스마트폰" in test_response2:
                    st.success("✅ 멀티턴 메모리 정상 작동!")
                else:
                    st.error("❌ 멀티턴 메모리 문제 발생")
                    st.text(f"응답: {test_response2[:100]}...")
        
        if st.button("새 대화 시작"):
            # 백엔드 대화 히스토리 삭제
            old_thread_id = st.session_state.thread_id
            clear_result = st.session_state.api_client.clear_thread_history(old_thread_id)
            
            # 새로운 세션 시작
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            
            if clear_result.get("status") == "success":
                st.success(f"새로운 대화가 시작되었습니다! (이전 대화 {clear_result.get('deleted_count', 0)}개 삭제)")
            else:
                st.success("새로운 대화가 시작되었습니다!")
            st.rerun()
        
        if st.button("대화 기록 삭제"):
            # 백엔드 대화 히스토리 삭제
            clear_result = st.session_state.api_client.clear_thread_history(st.session_state.thread_id)
            
            # 프론트엔드 메시지 삭제
            st.session_state.messages = []
            
            if clear_result.get("status") == "success":
                st.success(f"대화 기록이 삭제되었습니다! ({clear_result.get('deleted_count', 0)}개 삭제)")
            else:
                st.success("대화 기록이 삭제되었습니다!")
            st.rerun()
        
        st.divider()
        st.markdown("### 💡 사용법")
        st.markdown("""
        1. 아래 입력창에 찾고 싶은 상품을 입력하세요
        2. AI가 이전 대화를 기억하며 응답합니다
        3. 후속 질문을 통해 더 구체적인 정보를 얻어보세요
        
        **예시 대화:**
        - "갤럭시 스마트폰 추천해줘"
        - "그 중에서 가격이 저렴한 것은?"
        - "배터리 용량은 어떻게 돼?"
        """)
        
        # 디버깅 정보 표시
        if st.checkbox("디버깅 정보 표시"):
            st.markdown("### 🔍 디버깅 정보")
            st.text(f"Thread ID: {st.session_state.thread_id}")
            st.text(f"User ID: {st.session_state.user_id}")
            st.text(f"API URL: {st.session_state.api_client.base_url}")
            st.text(f"프론트엔드 메시지 수: {len(st.session_state.messages)}")
            
            # 백엔드 디버깅 정보 조회
            if st.button("백엔드 상태 확인"):
                debug_info = st.session_state.api_client.get_thread_debug_info(st.session_state.thread_id)
                if debug_info.get("status") != "error":
                    st.json(debug_info)
                else:
                    st.error(debug_info.get("message", "알 수 없는 오류"))
            
            if st.session_state.messages:
                st.text(f"마지막 메시지: {st.session_state.messages[-1]['content'][:50]}...")
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("검색하고 싶은 상품을 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성 (멀티턴 메모리 사용)
        with st.chat_message("assistant"):
            with st.spinner("AI가 이전 대화를 기억하며 응답 중..."):
                # 멀티턴 메모리 API 호출
                response = st.session_state.api_client.chat_with_memory(
                    query=prompt,
                    thread_id=st.session_state.thread_id,
                    user_id=st.session_state.user_id
                )
                st.markdown(response)
        
        # AI 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main() 