"""
상품 검색 챗봇 - Streamlit 애플리케이션
"""
import streamlit as st
from api_client import APIClient


def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="상품 검색 챗봇",
        page_icon="🛒",
        layout="wide"
    )
    
    # 앱 타이틀
    st.title("🛒 상품 검색 챗봇")
    st.markdown("원하는 상품을 검색해보세요!")
    
    # API 클라이언트 초기화
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 사이드바에 서버 상태 표시
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
        st.markdown("### 💡 사용법")
        st.markdown("""
        1. 아래 입력창에 찾고 싶은 상품을 입력하세요
        2. AI가 웹에서 상품 정보를 검색합니다
        3. 검색 결과를 확인해보세요
        """)
    
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
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("상품 검색 중..."):
                # API 호출
                response = st.session_state.api_client.search_products(prompt)
                st.markdown(response)
        
        # AI 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main() 