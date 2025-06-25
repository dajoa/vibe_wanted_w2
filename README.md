# Vibe Wanted W2 - 상품 검색 챗봇

상품 검색을 위한 AI 챗봇 시스템입니다.

## 🚀 PR 테스트 추가

이 라인은 GitHub Actions PR 자동화 기능을 테스트하기 위해 추가되었습니다.

## 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 프레임워크
- **Python 3.11**: 최신 Python 버전 사용

### 프론트엔드
- **Streamlit**: 빠른 웹 앱 개발

### AI Agent
- **LangGraph**: Agent 워크플로우 관리
- **Gemini**: Google의 최신 LLM 모델

## 프로젝트 구조

```
vibe_wanted_w2/
├── backend/          # FastAPI 백엔드
├── frontend/         # Streamlit 프론트엔드
├── docs/            # 문서
├── .github/         # GitHub Actions 워크플로우
└── tests/           # 테스트 코드
```

## 개발 가이드

### 환경 설정

1. **가상환경 생성**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **의존성 설치**
```bash
# 백엔드 의존성
cd backend
pip install -r requirements.txt

# 프론트엔드 의존성
cd ../frontend
pip install -r requirements.txt

# 개발 도구
pip install -r requirements-dev.txt
```

### 실행 방법

1. **백엔드 서버 실행**
```bash
cd backend
python run_server.py
```

2. **프론트엔드 실행**
```bash
cd frontend
streamlit run app.py
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 백엔드 테스트
cd backend && pytest tests/

# 프론트엔드 테스트
cd frontend && pytest tests/
```

## GitHub Actions

이 프로젝트는 다음 자동화 워크플로우를 제공합니다:

- **CI/CD**: 자동 테스트 및 코드 품질 검사
- **PR 관리**: 자동 라벨링, 할당, 댓글
- **이슈 관리**: 자동 분류 및 담당자 할당

자세한 내용은 [GitHub Actions 가이드](docs/github-actions-guide.md)를 참조하세요.

## 개발 원칙

- **TDD**: 테스트 주도 개발
- **SOLID**: 객체지향 설계 원칙
- **Clean Architecture**: 깨끗한 아키텍처

## 기여 방법

1. 이슈 생성 (버그 신고 또는 기능 요청)
2. 브랜치 생성: `feature/TASK-XXX-설명`
3. 코드 작성 및 테스트
4. PR 생성
5. 코드 리뷰 후 병합

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**🔗 GitHub 저장소**: https://github.com/dajoa/vibe_wanted_w2 