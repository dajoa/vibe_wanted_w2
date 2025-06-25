"""
채팅 API 라우터
쇼핑 챗봇과의 대화 관련 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from app.agents.product_search_agent import ProductSearchAgent

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/chat",
    tags=["chat", "챗봇"],
    responses={404: {"description": "Not found"}}
)


# 요청/응답 모델 정의
class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    query: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    message_id: str
    timestamp: datetime
    status: str = "success"


class ChatHistoryItem(BaseModel):
    """채팅 히스토리 아이템"""
    message_id: str
    user_message: str
    bot_response: str
    timestamp: datetime


class ChatHistory(BaseModel):
    """채팅 히스토리 응답"""
    history: List[ChatHistoryItem]
    total_count: int
    status: str = "success"


# 더미 데이터 저장소 (실제로는 데이터베이스 사용)
chat_history_store = []

# ProductSearchAgent 싱글톤 인스턴스
_agent_instance = None

def get_agent():
    """ProductSearchAgent 싱글톤 인스턴스 반환"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ProductSearchAgent()
    return _agent_instance


@router.post("", response_model=ChatResponse)
async def chat_with_memory(chat_message: ChatMessage):
    """
    메모리 기능을 가진 채팅 메시지 전송
    사용자의 메시지를 받아 멀티턴 대화 지원 챗봇 응답을 반환
    """
    if not chat_message.query.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")
    
    # 메시지 ID 생성
    message_id = str(uuid.uuid4())
    current_time = datetime.now()
    
    # 세션 ID 생성 (없으면 새로 생성)
    thread_id = chat_message.thread_id or str(uuid.uuid4())
    user_id = chat_message.user_id or str(uuid.uuid4())
    
    try:
        # ProductSearchAgent를 통한 메모리 기반 검색
        agent = get_agent()
        bot_response = agent.search_products_with_memory(
            query=chat_message.query,
            thread_id=thread_id,
            user_id=user_id
        )
        
        # 히스토리에 저장
        history_item = ChatHistoryItem(
            message_id=message_id,
            user_message=chat_message.query,
            bot_response=bot_response,
            timestamp=current_time
        )
        chat_history_store.append(history_item)
        
        return ChatResponse(
            response=bot_response,
            message_id=message_id,
            timestamp=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")


@router.post("/stream")
async def chat_with_memory_stream(chat_message: ChatMessage):
    """
    스트리밍 방식의 메모리 기능을 가진 채팅
    """
    if not chat_message.query.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")
    
    # 세션 ID 생성 (없으면 새로 생성)
    thread_id = chat_message.thread_id or str(uuid.uuid4())
    user_id = chat_message.user_id or str(uuid.uuid4())
    
    def generate_response():
        try:
            # ProductSearchAgent를 통한 메모리 기반 검색
            agent = get_agent()
            response = agent.search_products_with_memory(
                query=chat_message.query,
                thread_id=thread_id,
                user_id=user_id
            )
            
            # 응답을 청크 단위로 스트리밍
            for chunk in response.split():
                yield f"{chunk} "
                
        except Exception as e:
            yield f"검색 중 오류가 발생했습니다: {str(e)}"
    
    return StreamingResponse(generate_response(), media_type="text/plain")


@router.get("/history", response_model=ChatHistory)
async def get_chat_history(limit: int = 50):
    """
    채팅 히스토리 조회
    최근 대화 내역을 반환
    """
    # 최신 순으로 정렬하여 제한된 개수만 반환
    recent_history = sorted(chat_history_store, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    return ChatHistory(
        history=recent_history,
        total_count=len(chat_history_store)
    )


@router.delete("/history/{thread_id}")
async def clear_thread_history(thread_id: str):
    """
    특정 스레드의 대화 히스토리 삭제
    """
    try:
        agent = get_agent()
        if thread_id in agent.conversation_history:
            deleted_count = len(agent.conversation_history[thread_id])
            del agent.conversation_history[thread_id]
            return {
                "status": "success",
                "message": f"스레드 {thread_id}의 {deleted_count}개 대화가 삭제되었습니다",
                "deleted_count": deleted_count,
                "thread_id": thread_id
            }
        else:
            return {
                "status": "success",
                "message": f"스레드 {thread_id}에 삭제할 대화가 없습니다",
                "deleted_count": 0,
                "thread_id": thread_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 삭제 중 오류가 발생했습니다: {str(e)}")


@router.get("/debug/{thread_id}")
async def get_thread_debug_info(thread_id: str):
    """
    특정 스레드의 디버깅 정보 조회
    """
    try:
        agent = get_agent()
        conversation_count = len(agent.conversation_history.get(thread_id, []))
        
        return {
            "thread_id": thread_id,
            "conversation_count": conversation_count,
            "has_history": thread_id in agent.conversation_history,
            "total_threads": len(agent.conversation_history),
            "conversation_history": agent.conversation_history.get(thread_id, [])[:5]  # 최대 5개만 반환
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디버깅 정보 조회 중 오류가 발생했습니다: {str(e)}")


@router.delete("/history")
async def clear_chat_history():
    """
    채팅 히스토리 삭제
    모든 대화 내역을 삭제
    """
    global chat_history_store
    deleted_count = len(chat_history_store)
    chat_history_store.clear()
    
    return {
        "status": "success",
        "message": f"{deleted_count}개의 대화 내역이 삭제되었습니다",
        "deleted_count": deleted_count
    }


@router.get("/status")
async def get_chat_status():
    """
    채팅 서비스 상태 확인
    """
    return {
        "status": "active",
        "service": "Shopping Chat Agent",
        "total_conversations": len(chat_history_store),
        "last_activity": chat_history_store[-1].timestamp if chat_history_store else None
    } 