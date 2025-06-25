import os
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from app.config import config


class ProductSearchAgent:
    """상품 검색을 위한 LangGraph React Agent"""
    
    def __init__(self):
        """Agent 초기화"""
        # LangSmith 설정
        config.configure_langsmith()
        
        # 메모리 시스템 초기화
        self.checkpointer = InMemorySaver()
        self.store = InMemoryStore()
        
        # 대화 히스토리 저장소 (thread_id별로 관리)
        self.conversation_history = {}
        
        # DuckDuckGo 검색 도구 초기화 (항상 사용 가능)
        self.search_tool = DuckDuckGoSearchRun()
        
        # Google API 키 환경 변수 설정 (명시적으로)
        self.llm = None
        self.agent = None
        self.graph = None
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
                
                # StateGraph 기반 메모리 Agent 생성
                self._create_memory_agent()
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
        
        # Graph를 사용할 수 있는 경우
        if self.use_agent and self.graph:
            try:
                # StateGraph 실행 (기본 세션으로)
                config = {
                    "configurable": {
                        "thread_id": str(uuid.uuid4()),
                        "user_id": "default_user"
                    }
                }
                
                result = None
                for chunk in self.graph.stream(
                    {"messages": [{"role": "user", "content": query}]},
                    config,
                    stream_mode="values"
                ):
                    result = chunk
                
                # 마지막 메시지 (AI 응답) 반환
                if result and "messages" in result:
                    return result["messages"][-1].content
                else:
                    return "검색 결과를 가져올 수 없습니다."
                    
            except Exception as e:
                print(f"Graph 검색 실패: {e}")
                # 실패 시 직접 검색으로 폴백
                return self._direct_search(query)
        else:
            # Graph를 사용할 수 없는 경우 직접 검색
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
    
    def _create_memory_agent(self):
        """메모리 기능을 가진 StateGraph Agent 생성"""
        def call_model(
            state: MessagesState,
            config: RunnableConfig,
            *,
            store: BaseStore,
        ):
            # 사용자 ID와 스레드 ID 추출
            user_id = config.get("configurable", {}).get("user_id", "default_user")
            thread_id = config.get("configurable", {}).get("thread_id", "default_thread")
            namespace = ("memories", user_id)
            
            # 현재 메시지
            current_message = state["messages"][-1]
            
            # 기존 메모리 검색 (사용자별 관심사)
            memories = store.search(namespace, query=str(current_message.content))
            memory_context = self.build_memory_context([m.value for m in memories])
            
            # 이전 대화 히스토리 컨텍스트 생성
            conversation_history = ""
            if len(state["messages"]) > 1:
                conversation_history = "\n## 이전 대화 내용:\n"
                for i, msg in enumerate(state["messages"][:-1]):  # 현재 메시지 제외
                    role = "사용자" if msg.type == "human" else "AI"
                    conversation_history += f"{i+1}. {role}: {msg.content}\n"
            
            # 시스템 프롬프트에 메모리와 대화 히스토리 포함
            system_prompt = f"""당신은 상품 가격 비교 전문 AI 어시스턴트입니다.
사용자가 요청한 상품에 대해 웹 검색을 통해 최저가 가격 정보를 제공합니다.

{memory_context}

{conversation_history}

검색 결과를 바탕으로 다음과 같은 정보를 포함하여 응답해주세요:
- 상품명과 브랜드
- 주요 특징 및 사양
- 가격 정보 (가능한 경우)
- 구매 가능한 온라인 쇼핑몰
- 사용자 리뷰나 평점 (있는 경우)

**중요**: 이전 대화 내용을 참고하여 연관된 질문에 대해서는 맥락을 고려한 답변을 제공하세요.
예를 들어, 이전에 특정 제품을 추천했다면 후속 질문에서 그 제품들을 기준으로 답변하세요.

항상 한국어로 응답하며, 정확하고 유용한 정보를 제공하세요."""

            # 웹 검색 수행
            search_query = f"{current_message.content} 상품 가격 리뷰 구매"
            search_results = self.search_tool.run(search_query)
            
            # LLM 응답 생성
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 검색 결과를 바탕으로 '{current_message.content}'에 대해 답변해주세요:\n\n{search_results}"}
            ]
            
            response = self.llm.invoke(messages)
            
            # 모든 대화를 메모리에 저장 (관심사 추출)
            memory_data = {
                "data": f"사용자 질문: {current_message.content}",
                "timestamp": str(uuid.uuid4()),
                "thread_id": thread_id
            }
            store.put(namespace, str(uuid.uuid4()), memory_data)
            
            # 상품 관련 키워드가 있으면 추가 메모리 저장
            product_keywords = ["스마트폰", "노트북", "태블릿", "이어폰", "헤드폰", "카메라", "TV", "모니터"]
            for keyword in product_keywords:
                if keyword in current_message.content:
                    product_memory = {
                        "data": f"사용자가 {keyword}에 관심을 보임",
                        "product_type": keyword,
                        "thread_id": thread_id
                    }
                    store.put(namespace, str(uuid.uuid4()), product_memory)
                    break
            
            return {"messages": [response]}
        
        # StateGraph 생성
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_edge(START, "call_model")
        
        # 메모리 시스템과 함께 컴파일 (checkpointer로 대화 히스토리 저장)
        self.graph = builder.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )
    
    def add_to_conversation_history(self, thread_id: str, user_message: str, ai_response: str):
        """대화 히스토리에 메시지 추가"""
        if thread_id not in self.conversation_history:
            self.conversation_history[thread_id] = []
        
        self.conversation_history[thread_id].append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": str(uuid.uuid4())
        })
    
    def get_conversation_history(self, thread_id: str) -> str:
        """대화 히스토리를 문자열로 반환"""
        if thread_id not in self.conversation_history or not self.conversation_history[thread_id]:
            return ""
        
        history_text = "\n## 이전 대화 내용:\n"
        for i, conv in enumerate(self.conversation_history[thread_id]):
            history_text += f"{i+1}. 사용자: {conv['user']}\n"
            history_text += f"{i+1}. AI: {conv['ai']}\n\n"
        
        return history_text
    
    def search_products_with_memory(self, query: str, thread_id: str = None, user_id: str = None) -> str:
        """
        메모리 기능을 포함한 상품 검색
        
        Args:
            query: 검색할 상품명 또는 키워드
            thread_id: 대화 세션 ID
            user_id: 사용자 ID
            
        Returns:
            검색 결과를 포함한 응답 문자열
        """
        if not query.strip():
            return "검색할 상품명을 입력해주세요."
        
        # 기본값 설정
        if not thread_id:
            thread_id = str(uuid.uuid4())
        if not user_id:
            user_id = "default_user"
        
        # 이전 대화 히스토리 가져오기
        conversation_history = self.get_conversation_history(thread_id)
        
        # 사용자별 메모리 검색
        namespace = ("memories", user_id)
        memories = self.store.search(namespace, query=query)
        memory_context = self.build_memory_context([m.value for m in memories])
        
        # 웹 검색 수행
        search_query = f"{query} 상품 가격 리뷰 구매"
        search_results = self.search_tool.run(search_query)
        
        # 시스템 프롬프트 구성
        system_prompt = f"""당신은 상품 가격 비교 전문 AI 어시스턴트입니다.
사용자가 요청한 상품에 대해 웹 검색을 통해 최저가 가격 정보를 제공합니다.

{memory_context}

{conversation_history}

**중요**: 이전 대화 내용을 반드시 참고하여 연관된 질문에 대해서는 맥락을 고려한 답변을 제공하세요.
예를 들어, 이전에 "갤럭시 스마트폰"을 추천했다면, "그 중에서 50만원 이하인 것"이라는 후속 질문에서는 
갤럭시 스마트폰 중에서 50만원 이하인 모델들을 추천해야 합니다.

검색 결과를 바탕으로 다음과 같은 정보를 포함하여 응답해주세요:
- 상품명과 브랜드
- 주요 특징 및 사양
- 가격 정보 (가능한 경우)
- 구매 가능한 온라인 쇼핑몰
- 사용자 리뷰나 평점 (있는 경우)

항상 한국어로 응답하며, 정확하고 유용한 정보를 제공하세요."""

        try:
            # LLM을 사용할 수 있는 경우
            if self.use_agent and self.llm:
                # 사용자 메시지에 맥락 정보 포함
                user_message = f"현재 질문: '{query}'\n\n"
                
                # 이전 대화가 있다면 맥락 힌트 추가
                if conversation_history:
                    user_message += "**중요**: 위의 이전 대화 내용을 참고하여, 현재 질문이 이전 대화와 연관된 후속 질문인지 판단하고 맥락을 고려해서 답변해주세요.\n\n"
                
                user_message += f"다음 검색 결과를 바탕으로 답변해주세요:\n\n{search_results}"
                
                # LLM 응답 생성
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
                
                response = self.llm.invoke(messages)
                ai_response = response.content
                
                # 대화 히스토리에 추가
                self.add_to_conversation_history(thread_id, query, ai_response)
                
                # 사용자 메모리에 저장
                memory_data = {
                    "data": f"사용자 질문: {query}",
                    "thread_id": thread_id
                }
                self.store.put(namespace, str(uuid.uuid4()), memory_data)
                
                # 상품 관련 키워드가 있으면 추가 메모리 저장
                product_keywords = ["스마트폰", "갤럭시", "아이폰", "노트북", "태블릿", "이어폰", "헤드폰", "카메라", "TV", "모니터"]
                for keyword in product_keywords:
                    if keyword in query:
                        product_memory = {
                            "data": f"사용자가 {keyword}에 관심을 보임",
                            "product_type": keyword,
                            "thread_id": thread_id
                        }
                        self.store.put(namespace, str(uuid.uuid4()), product_memory)
                        break
                
                return ai_response
                
            else:
                # LLM을 사용할 수 없는 경우 기본 검색
                result = self._direct_search(query)
                self.add_to_conversation_history(thread_id, query, result)
                return result
                
        except Exception as e:
            print(f"메모리 검색 실패: {e}")
            # 실패 시 기본 검색으로 폴백
            result = self._direct_search(query)
            self.add_to_conversation_history(thread_id, query, result)
            return result
    
    def store_user_memory(self, user_id: str, memory_key: str, memory_data: dict):
        """사용자 메모리 저장"""
        namespace = ("memories", user_id)
        memory_id = str(uuid.uuid4())
        self.store.put(namespace, memory_id, memory_data)
    
    def get_user_memories(self, user_id: str) -> list:
        """사용자 메모리 조회"""
        namespace = ("memories", user_id)
        memories = self.store.search(namespace)
        return [memory.value for memory in memories]
    
    def build_memory_context(self, memories: list) -> str:
        """메모리 정보를 컨텍스트 문자열로 변환"""
        if not memories:
            return ""
        
        context_parts = ["## 사용자 정보 및 이전 대화 내용:"]
        for memory in memories:
            if isinstance(memory, dict) and "data" in memory:
                context_parts.append(f"- {memory['data']}")
        
        return "\n".join(context_parts) if len(context_parts) > 1 else ""