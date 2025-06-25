import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from app.config import config


class ProductSearchAgent:
    """상품 검색을 위한 LangGraph React Agent"""
    
    def __init__(self):
        """Agent 초기화"""
        # LangSmith 설정
        config.configure_langsmith()
        
        # DuckDuckGo 검색 도구 초기화 (항상 사용 가능)
        self.search_tool = DuckDuckGoSearchRun()
        
        # Google API 키 환경 변수 설정 (명시적으로)
        self.llm = None
        self.agent = None
        self.use_agent = False
        
        if config.GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
            # 추가 환경 변수들도 설정
            os.environ["GOOGLE_GENAI_API_KEY"] = config.GOOGLE_API_KEY
            os.environ["GEMINI_API_KEY"] = config.GOOGLE_API_KEY
            
            try:
                # Gemini 모델 초기화
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=config.GOOGLE_API_KEY,
                    temperature=0.1
                )
                
                # 시스템 프롬프트 설정
                system_prompt = """
                당신은 상품 가격 비교 전문 AI 어시스턴트입니다.
                사용자가 요청한 상품에 대해 웹 검색을 통해 최저가 가격 정보를 제공합니다.
                
                검색 결과를 바탕으로 다음과 같은 정보를 포함하여 응답해주세요:
                - 상품명과 브랜드
                - 주요 특징 및 사양
                - 가격 정보 (가능한 경우)
                - 구매 가능한 온라인 쇼핑몰
                - 사용자 리뷰나 평점 (있는 경우)
                
                항상 한국어로 응답하며, 정확하고 유용한 정보를 제공하세요.
                """
                
                # React Agent 생성
                self.agent = create_react_agent(
                    model=self.llm,
                    tools=[self.search_tool],
                    prompt=system_prompt
                )
                self.use_agent = True
                
            except Exception as e:
                print(f"Agent 초기화 실패: {e}")
                # Agent 없이 직접 검색만 사용
                self.use_agent = False
    
    def search_products(self, query: str) -> str:
        """
        상품 검색 실행
        
        Args:
            query: 검색할 상품명 또는 키워드
            
        Returns:
            검색 결과를 포함한 응답 문자열
        """
        if not query.strip():
            return "검색할 상품명을 입력해주세요."
        
        # Agent를 사용할 수 있는 경우
        if self.use_agent and self.agent:
            try:
                # Agent 실행
                result = self.agent.invoke({
                    "messages": [{"role": "user", "content": f"다음 상품에 대해 검색해주세요: {query}"}]
                })
                
                # 마지막 메시지 (AI 응답) 반환
                if result and "messages" in result:
                    return result["messages"][-1].content
                else:
                    return "검색 결과를 가져올 수 없습니다."
                    
            except Exception as e:
                print(f"Agent 검색 실패: {e}")
                # Agent 실패 시 직접 검색으로 폴백
                return self._direct_search(query)
        else:
            # Agent를 사용할 수 없는 경우 직접 검색
            return self._direct_search(query)
    
    def _direct_search(self, query: str) -> str:
        """DuckDuckGo 직접 검색"""
        try:
            # DuckDuckGo 직접 검색
            search_results = self.search_tool.run(f"{query} 상품 가격 리뷰 구매")
            
            # 결과 포맷팅
            formatted_result = f"""🔍 '{query}' 상품 검색 결과

{search_results}

📝 추천사항:
• 여러 쇼핑몰에서 가격을 비교해보세요
• 사용자 리뷰와 평점을 확인하세요  
• 배송비와 반품 정책을 확인하세요
• 정품 인증과 A/S 정보를 확인하세요

※ 구체적인 가격과 재고는 각 쇼핑몰에서 직접 확인해주세요."""
            
            return formatted_result
            
        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {str(e)}" 