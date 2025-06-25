# 온라인 쇼핑 최저가 검색 챗봇 Agent

온라인 쇼핑 시 특정 상품의 최저가를 자동으로 검색하고 비교하여 리스트업해주는 챗봇형 Agent 프로젝트입니다.

## 프로젝트 개요

사용자가 상품명을 입력하면 여러 쇼핑몰의 가격을 자동으로 비교하여 최적의 구매 선택을 도와주는 AI 어시스턴트입니다.

### 주요 기능

- 🔍 **자동 상품 검색**: Agent가 웹 검색을 통해 상품 정보 수집
- 💰 **가격 비교**: 여러 쇼핑몰의 가격을 자동으로 비교
- 💬 **챗봇 인터페이스**: 자연스러운 대화형 UI
- ⚡ **실시간 응답**: 스트리밍 방식으로 즉시 결과 제공

## 기술 스택

### Backend
- **FastAPI**: 웹 프레임워크
- **uvicorn**: ASGI 서버  
- **LangGraph**: Agent 프레임워크
- **LangChain**: 도구 및 LLM 연동

### Frontend  
- **Streamlit**: 웹 인터페이스
- **streamlit-chat**: 챗봇 UI 컴포넌트

### AI/LLM
- **Gemini-2.5-flash**: 대화형 AI 모델
- **DuckDuckGo Search**: 웹 검색 도구

## 프로젝트 구조

```
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── api/      # API 라우터
│   │   ├── services/ # 비즈니스 로직
│   │   └── agents/   # LangGraph Agent
│   └── tests/        # 백엔드 테스트
├── frontend/         # Streamlit 프론트엔드
└── docs/            # 문서
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일에서 API 키 설정
LANGSMITH_API_KEY=your_api_key_here
```

### 3. 백엔드 실행

```bash
cd backend
uvicorn app.main:app --reload --host localhost --port 8000
```

### 4. 프론트엔드 실행

```bash
cd frontend  
streamlit run app.py --server.port 8501
```

## 개발 도구

### 테스트 실행

```bash
# 프로젝트 구조 테스트
python test_project_structure.py

# Python 환경 테스트  
python test_python_environment.py

# 의존성 테스트
python test_dependencies.py

# 설정 파일 테스트
python test_config_files.py
```

### 코드 포맷팅

```bash
pip install -r requirements-dev.txt
black .
flake8 .
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다 