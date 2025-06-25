"""
FastAPI 백엔드와 통신하는 API 클라이언트
"""
import requests
import streamlit as st
from typing import Optional


class APIClient:
    """FastAPI 백엔드 API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        API 클라이언트 초기화
        
        Args:
            base_url: 백엔드 서버 URL
        """
        self.base_url = base_url
        self.timeout = 30  # 30초 타임아웃
    
    def search_products(self, query: str) -> str:
        """
        상품 검색 API 호출
        
        Args:
            query: 검색할 상품명
            
        Returns:
            str: 검색 결과 또는 에러 메시지
        """
        try:
            # API 요청 데이터 준비
            data = {"query": query}
            
            # POST 요청 보내기
            response = requests.post(
                f"{self.base_url}/api/search",
                json=data,
                timeout=self.timeout
            )
            
            # 응답 상태 확인
            response.raise_for_status()
            
            # JSON 응답 파싱
            result = response.json()
            return result.get("result", "검색 결과를 가져올 수 없습니다.")
            
        except requests.exceptions.ConnectionError:
            return "❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."
            
        except requests.exceptions.Timeout:
            return "⏰ 요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
            
        except requests.exceptions.HTTPError as e:
            return f"❌ HTTP 오류가 발생했습니다: {e}"
            
        except Exception as e:
            return f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}"
    
    def health_check(self) -> bool:
        """
        백엔드 서버 상태 확인
        
        Returns:
            bool: 서버가 정상 작동하면 True
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False 