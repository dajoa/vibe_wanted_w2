"""
검색 API 라우터
상품 검색 및 최저가 비교 관련 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from app.agents.product_search_agent import ProductSearchAgent

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/api",
    tags=["search", "검색"],
    responses={404: {"description": "Not found"}}
)

# Agent 인스턴스 (싱글톤 패턴으로 사용)
agent = None


def get_agent():
    """Agent 인스턴스 가져오기 (lazy loading)"""
    global agent
    if agent is None:
        agent = ProductSearchAgent()
    return agent


# 요청/응답 모델 정의
class ProductSearchRequest(BaseModel):
    """상품 검색 요청 모델"""
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "price"  # price, rating, popularity


class ProductInfo(BaseModel):
    """상품 정보 모델"""
    product_id: str
    name: str
    price: float
    original_price: Optional[float] = None
    discount_rate: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    seller: str
    url: str
    image_url: Optional[str] = None
    shipping_info: Optional[str] = None


class SearchResult(BaseModel):
    """검색 결과 모델"""
    search_id: str
    query: str
    products: List[ProductInfo]
    total_count: int
    search_time: float
    timestamp: datetime
    status: str = "success"


class SearchSummary(BaseModel):
    """검색 요약 정보"""
    search_id: str
    query: str
    product_count: int
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    average_price: Optional[float] = None
    timestamp: datetime


class SearchRequest(BaseModel):
    """Agent 검색 요청 모델"""
    query: str


class SearchResponse(BaseModel):
    """Agent 검색 응답 모델"""
    result: str
    query: str


# 더미 데이터 저장소
search_results_store: Dict[str, SearchResult] = {}


def generate_dummy_products(query: str, count: int = 10) -> List[ProductInfo]:
    """더미 상품 데이터 생성"""
    products = []
    base_price = 100000  # 기본 가격
    
    for i in range(count):
        product_id = str(uuid.uuid4())
        price = base_price + (i * 5000) + (hash(query) % 50000)
        original_price = price + (price * 0.1)  # 10% 할인
        
        product = ProductInfo(
            product_id=product_id,
            name=f"{query} - 상품 {i+1}번",
            price=price,
            original_price=original_price,
            discount_rate=10.0,
            rating=4.0 + (i % 5) * 0.2,
            review_count=100 + (i * 50),
            seller=f"판매자{i+1}",
            url=f"https://example-shop{i+1}.com/product/{product_id}",
            image_url=f"https://example.com/images/{product_id}.jpg",
            shipping_info="무료배송" if i % 2 == 0 else "배송비 3,000원"
        )
        products.append(product)
    
    # 가격순 정렬
    products.sort(key=lambda x: x.price)
    return products


@router.post("/products", response_model=SearchResult)
async def search_products(search_request: ProductSearchRequest):
    """
    상품 검색
    주어진 검색어로 상품을 검색하고 최저가 순으로 정렬하여 반환
    """
    if not search_request.query.strip():
        raise HTTPException(status_code=400, detail="검색어가 비어있습니다")
    
    # 검색 ID 생성
    search_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # 더미 상품 데이터 생성
    products = generate_dummy_products(search_request.query, 15)
    
    # 가격 필터링
    if search_request.min_price:
        products = [p for p in products if p.price >= search_request.min_price]
    if search_request.max_price:
        products = [p for p in products if p.price <= search_request.max_price]
    
    # 정렬
    if search_request.sort_by == "rating":
        products.sort(key=lambda x: x.rating or 0, reverse=True)
    elif search_request.sort_by == "popularity":
        products.sort(key=lambda x: x.review_count or 0, reverse=True)
    # 기본값은 이미 price로 정렬됨
    
    # 검색 시간 계산
    search_time = (datetime.now() - start_time).total_seconds()
    
    # 검색 결과 생성
    result = SearchResult(
        search_id=search_id,
        query=search_request.query,
        products=products,
        total_count=len(products),
        search_time=search_time,
        timestamp=datetime.now()
    )
    
    # 결과 저장
    search_results_store[search_id] = result
    
    return result


@router.get("/results/{search_id}", response_model=SearchResult)
async def get_search_results(search_id: str):
    """
    검색 결과 조회
    저장된 검색 결과를 ID로 조회
    """
    if search_id not in search_results_store:
        raise HTTPException(status_code=404, detail="검색 결과를 찾을 수 없습니다")
    
    return search_results_store[search_id]


@router.get("/history")
async def get_search_history(limit: int = 20):
    """
    검색 히스토리 조회
    최근 검색 기록을 반환
    """
    # 검색 요약 정보만 반환
    summaries = []
    
    for search_id, result in search_results_store.items():
        prices = [p.price for p in result.products]
        
        summary = SearchSummary(
            search_id=search_id,
            query=result.query,
            product_count=len(result.products),
            lowest_price=min(prices) if prices else None,
            highest_price=max(prices) if prices else None,
            average_price=sum(prices) / len(prices) if prices else None,
            timestamp=result.timestamp
        )
        summaries.append(summary)
    
    # 최신순 정렬
    summaries.sort(key=lambda x: x.timestamp, reverse=True)
    
    return {
        "history": summaries[:limit],
        "total_count": len(summaries),
        "status": "success"
    }


@router.delete("/history")
async def clear_search_history():
    """
    검색 히스토리 삭제
    모든 검색 기록을 삭제
    """
    global search_results_store
    deleted_count = len(search_results_store)
    search_results_store.clear()
    
    return {
        "status": "success",
        "message": f"{deleted_count}개의 검색 기록이 삭제되었습니다",
        "deleted_count": deleted_count
    }


@router.get("/categories")
async def get_categories():
    """
    상품 카테고리 목록 조회
    """
    categories = [
        {"id": "electronics", "name": "전자제품", "count": 1500},
        {"id": "fashion", "name": "패션/의류", "count": 2300},
        {"id": "home", "name": "홈/리빙", "count": 800},
        {"id": "beauty", "name": "뷰티/화장품", "count": 1200},
        {"id": "sports", "name": "스포츠/레저", "count": 600},
        {"id": "books", "name": "도서/문구", "count": 900},
        {"id": "food", "name": "식품/건강", "count": 700}
    ]
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "status": "success"
    }


@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    상품 검색 API 엔드포인트
    
    Args:
        request: 검색할 상품명이 포함된 요청 객체
        
    Returns:
        SearchResponse: 검색 결과를 포함한 응답 객체
        
    Raises:
        HTTPException: Agent 실행 중 오류 발생 시
    """
    try:
        # Agent 가져오기
        search_agent = get_agent()
        
        # 상품 검색 실행
        result = search_agent.search_products(request.query)
        
        return SearchResponse(
            result=result,
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 처리 중 오류가 발생했습니다: {str(e)}"
        ) 