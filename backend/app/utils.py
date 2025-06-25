"""
유틸리티 함수들
PR 테스트를 위해 추가된 파일입니다.
"""

def format_price(price: float) -> str:
    """가격을 포맷팅하여 반환합니다."""
    return f"￦{price:,.0f}"


def validate_search_query(query: str) -> bool:
    """검색 쿼리의 유효성을 검사합니다."""
    if not query or len(query.strip()) < 2:
        return False
    return True


def clean_product_name(name: str) -> str:
    """상품명을 정리합니다."""
    import re
    return re.sub(r'\s+', ' ', name.strip()) 