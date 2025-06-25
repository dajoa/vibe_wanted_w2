# 🛒 상품 검색 챗봇 - 프론트엔드

Streamlit 기반의 상품 검색 챗봇 인터페이스

## 🚀 기능

- **직관적인 채팅 인터페이스**: 사용자 친화적인 대화형 UI
- **실시간 상품 검색**: FastAPI 백엔드와 연동하여 실시간 검색
- **에러 처리**: 네트워크 오류 및 서버 에러에 대한 적절한 처리
- **상태 모니터링**: 사이드바에서 백엔드 서버 상태 확인 가능

## 🛠 기술 스택

- **Streamlit**: 웹 애플리케이션 프레임워크
- **Requests**: HTTP 클라이언트 라이브러리
- **Pytest**: 테스트 프레임워크

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
streamlit run app.py
```

### 3. 테스트 실행
```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 테스트 파일 실행
pytest tests/test_app.py -v
pytest tests/test_api_integration.py -v
```

## 🏗 프로젝트 구조

```
frontend/
├── app.py                    # 메인 Streamlit 애플리케이션
├── api_client.py            # FastAPI 백엔드 연동 클라이언트
├── requirements.txt         # 패키지 의존성
├── README.md               # 프로젝트 문서
└── tests/                  # 테스트 파일
    ├── test_app.py         # 앱 기능 테스트
    └── test_api_integration.py  # API 연동 테스트
```

## 💻 사용법

1. **백엔드 서버 실행**: FastAPI 백엔드 서버가 `http://localhost:8000`에서 실행 중인지 확인
2. **프론트엔드 실행**: `streamlit run app.py` 명령으로 앱 실행
3. **상품 검색**: 채팅 입력창에 원하는 상품명 입력
4. **결과 확인**: AI가 검색한 상품 정보 확인

## 🔧 개발

### TDD (Test-Driven Development)
이 프로젝트는 TDD 방식으로 개발되었습니다:

1. **테스트 코드 작성**
2. **기능 구현**
3. **테스트 실행 및 수정**
4. **반복**

### 코드 품질
- **Clean Architecture**: 계층별 역할 분리
- **SOLID 원칙**: 객체지향 설계 원칙 준수
- **간단한 구조**: 불필요한 복잡성 제거

## 🌐 API 연동

백엔드 API 엔드포인트:
- `POST /api/search`: 상품 검색
- `GET /health`: 서버 상태 확인 