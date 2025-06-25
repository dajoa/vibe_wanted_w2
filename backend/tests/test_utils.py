"""
utils.py 모듈에 대한 테스트
"""

import pytest
from app.utils import format_price, validate_search_query, clean_product_name


class TestFormatPrice:
    """가격 포맷팅 함수 테스트"""
    
    def test_format_price_regular_number(self):
        """일반적인 숫자 포맷팅 테스트"""
        assert format_price(1000) == "￦1,000"
        assert format_price(10000) == "￦10,000"
        assert format_price(1000000) == "￦1,000,000"
    
    def test_format_price_zero(self):
        """0원 포맷팅 테스트"""
        assert format_price(0) == "￦0"
    
    def test_format_price_decimal(self):
        """소수점 포맷팅 테스트 (소수점 제거)"""
        assert format_price(1000.99) == "￦1,001"
        assert format_price(9999.5) == "￦10,000"


class TestValidateSearchQuery:
    """검색 쿼리 유효성 검사 함수 테스트"""
    
    def test_validate_search_query_valid(self):
        """유효한 검색 쿼리 테스트"""
        assert validate_search_query("iPhone") is True
        assert validate_search_query("삼성 갤럭시") is True
        assert validate_search_query("노트북") is True
    
    def test_validate_search_query_empty(self):
        """빈 문자열 테스트"""
        assert validate_search_query("") is False
        assert validate_search_query("   ") is False
    
    def test_validate_search_query_too_short(self):
        """너무 짧은 쿼리 테스트"""
        assert validate_search_query("a") is False
        assert validate_search_query(" b ") is False
    
    def test_validate_search_query_none(self):
        """None 값 테스트"""
        assert validate_search_query(None) is False


class TestCleanProductName:
    """상품명 정리 함수 테스트"""
    
    def test_clean_product_name_normal(self):
        """일반적인 상품명 정리 테스트"""
        assert clean_product_name("iPhone 15") == "iPhone 15"
        assert clean_product_name("  삼성 갤럭시  ") == "삼성 갤럭시"
    
    def test_clean_product_name_multiple_spaces(self):
        """여러 공백 정리 테스트"""
        assert clean_product_name("iPhone  15  Pro") == "iPhone 15 Pro"
        assert clean_product_name("  삼성    갤럭시    S24  ") == "삼성 갤럭시 S24"
    
    def test_clean_product_name_empty(self):
        """빈 문자열 테스트"""
        assert clean_product_name("") == ""
        assert clean_product_name("   ") == "" 