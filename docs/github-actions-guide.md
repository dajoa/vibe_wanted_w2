# GitHub Actions 사용 가이드

이 프로젝트는 GitHub Actions를 사용하여 CI/CD 파이프라인과 자동화된 프로젝트 관리를 제공합니다.

## 🔧 설정된 GitHub Actions

### 1. CI (Continuous Integration)
**파일**: `.github/workflows/ci.yml`

**트리거**: 
- `main` 브랜치에 push
- `main` 브랜치로의 Pull Request

**기능**:
- Python 3.11 환경에서 테스트 실행
- 백엔드 및 프론트엔드 테스트 병렬 실행
- 코드 커버리지 측정 및 Codecov 업로드
- 코드 품질 검사 (flake8, black, mypy)

### 2. PR Management
**파일**: `.github/workflows/pr-management.yml`

**트리거**: 
- Pull Request 생성, 업데이트, 리뷰

**기능**:
- **자동 댓글**: PR 생성 시 체크리스트 댓글 추가
- **자동 할당**: PR 생성자에게 자동 할당
- **자동 라벨링**: 파일 변경사항과 제목 기반 라벨 자동 추가
- **자동 코드 리뷰**: 기본적인 코드 리뷰 댓글 추가

### 3. Issue Management  
**파일**: `.github/workflows/issue-management.yml`

**트리거**:
- 이슈 생성, 수정, 닫기
- 이슈 댓글 생성

**기능**:
- **자동 댓글**: 이슈 생성 시 안내 댓글 추가
- **자동 할당**: 이슈 타입별 담당자 자동 할당
- **자동 라벨링**: 키워드 기반 라벨 자동 추가
- **상태 업데이트**: 이슈 완료 시 댓글 추가

## 🏷️ 자동 라벨링 시스템

### 이슈 타입 라벨
- `bug`: 버그 신고
- `enhancement`: 기능 개선 및 새 기능
- `documentation`: 문서 관련
- `question`: 질문
- `tests`: 테스트 관련

### 컴포넌트 라벨
- `backend`: 백엔드 관련
- `frontend`: 프론트엔드 관련
- `agent`: Agent 관련
- `api`: API 관련
- `ci/cd`: CI/CD 관련

### 우선순위 라벨
- `priority/high`: 높은 우선순위
- `priority/medium`: 보통 우선순위
- `priority/low`: 낮은 우선순위

### 크기 라벨 (PR용)
- `size/S`: 작은 크기 (< 50 lines)
- `size/M`: 중간 크기 (50-200 lines)
- `size/L`: 큰 크기 (200-500 lines)
- `size/XL`: 매우 큰 크기 (> 500 lines)

## 📝 이슈 및 PR 템플릿

### 이슈 템플릿
1. **버그 신고** (`.github/ISSUE_TEMPLATE/bug_report.yml`)
2. **기능 요청** (`.github/ISSUE_TEMPLATE/feature_request.yml`)

### PR 템플릿
- **PR 템플릿** (`.github/PULL_REQUEST_TEMPLATE.md`)

## 🔨 사용법

### 새로운 기능 개발
1. 새 브랜치 생성: `feature/TASK-XXX-설명`
2. 코드 작성 및 테스트
3. PR 생성 → 자동으로 체크리스트 댓글 추가
4. 자동 라벨링 및 할당
5. CI 테스트 통과 후 리뷰
6. 병합

### 버그 수정
1. 이슈 생성 (버그 신고 템플릿 사용)
2. 새 브랜치 생성: `bugfix/ISSUE-XXX-설명`
3. 수정 및 테스트
4. PR 생성 및 리뷰
5. 병합 후 이슈 닫기

### 문서 업데이트
1. 새 브랜치 생성: `docs/설명`
2. 문서 수정
3. PR 생성 → 자동으로 `documentation` 라벨 추가
4. 리뷰 및 병합

## 🎯 자동화 규칙

### PR 자동 할당
- PR 생성자에게 자동 할당
- 파일 변경사항 기반 라벨 추가
- 제목 키워드 기반 라벨 추가

### 이슈 자동 할당
- 버그: 해당 모듈 담당자 (설정 필요)
- 기능: 프로젝트 리더 (설정 필요)
- 문서: 문서 담당자 (설정 필요)

*주의: 실제 사용을 위해서는 GitHub Actions 파일에서 실제 GitHub 사용자명으로 변경해야 합니다.*

### 자동 코드 리뷰
- 파일 크기가 큰 경우 경고
- 새 파일에 대한 테스트 코드 확인
- Python 코드 품질 검사

## 🚀 CI/CD 파이프라인

### 테스트 단계
1. 의존성 설치 (캐시 사용)
2. 백엔드 테스트 실행
3. 프론트엔드 테스트 실행
4. 코드 커버리지 측정
5. 코드 품질 검사

### 품질 검사 도구
- **flake8**: 코드 스타일 검사
- **black**: 코드 포맷팅 검사
- **mypy**: 타입 검사
- **pytest**: 테스트 실행 및 커버리지

## 📊 메트릭스 및 모니터링

### 커버리지 리포팅
- Codecov를 통한 커버리지 추적
- PR에서 커버리지 변화 확인

### 자동 알림
- CI 실패 시 GitHub 알림
- PR 상태 변경 시 알림
- 이슈 할당 시 알림

## 🔧 추가 설정

### 라벨 동기화
라벨을 일괄 생성하려면 GitHub CLI를 사용하거나, 수동으로 `.github/labels.yml` 파일의 라벨들을 GitHub 리포지토리에 추가해야 합니다.

### 담당자 설정
실제 사용을 위해서는 다음 파일들에서 사용자명을 수정해야 합니다:
- `.github/workflows/issue-management.yml`
- `.github/workflows/pr-management.yml`

### 브랜치 보호 규칙
`main` 브랜치에 다음 보호 규칙을 설정하는 것을 권장합니다:
- PR 리뷰 필수
- CI 통과 필수
- 최신 상태 유지 필수

## 🤝 기여 가이드

1. 이슈 생성 시 적절한 템플릿 사용
2. 브랜치명 규칙 준수
3. PR 템플릿의 체크리스트 완료
4. 테스트 코드 작성 및 TDD 프로세스 준수
5. 코드 리뷰 가이드라인 준수

---

더 자세한 정보는 [GitHub Actions 공식 문서](https://docs.github.com/en/actions)를 참조하세요. 