"""
채팅 API 라우터
쇼핑 챗봇과의 대화 관련 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/chat",
    tags=["chat", "챗봇"],
    responses={404: {"description": "Not found"}}
)


# 요청/응답 모델 정의
class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    message: str
    user_id: Optional[str] = None


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


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """
    채팅 메시지 전송
    사용자의 메시지를 받아 챗봇 응답을 반환
    """
    if not chat_message.message.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")
    
    # 메시지 ID 생성
    message_id = str(uuid.uuid4())
    current_time = datetime.now()
    
    # 더미 응답 생성 (실제로는 LangGraph Agent 호출)
    user_msg = chat_message.message.lower()
    
    if "최저가" in user_msg or "가격" in user_msg:
        bot_response = f"'{chat_message.message}'에 대한 최저가를 검색하고 있습니다. 잠시만 기다려주세요!"
    elif "안녕" in user_msg or "hello" in user_msg:
        bot_response = "안녕하세요! 쇼핑 최저가 검색 도우미입니다. 어떤 상품의 최저가를 찾아드릴까요?"
    else:
        bot_response = f"'{chat_message.message}'에 대해 도움을 드리겠습니다. 구체적인 상품명을 알려주시면 최저가를 찾아드릴게요!"
    
    # 히스토리에 저장
    history_item = ChatHistoryItem(
        message_id=message_id,
        user_message=chat_message.message,
        bot_response=bot_response,
        timestamp=current_time
    )
    chat_history_store.append(history_item)
    
    return ChatResponse(
        response=bot_response,
        message_id=message_id,
        timestamp=current_time
    )


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