# AI Job Market Tracker

국내 AI/IT 채용공고를 수집하고 공통 형식으로 정규화해 채용시장 동향을 분석하는 개인 프로젝트입니다. 장기적으로는 축적한 데이터를 바탕으로 자연어로 채용시장에 질문할 수 있는 RAG 서비스와 React 대시보드를 만드는 것을 목표로 합니다.

## 목표

- 여러 채용 데이터 소스의 공고 수집 및 정규화
- 직무별 기술 스택, 경력, 학력, 고용형태 등 채용시장 통계 분석
- PostgreSQL과 pgvector를 활용한 데이터 저장 및 검색
- 자연어 질의응답과 React 기반 대시보드 제공

## 현재 개발 단계

현재는 **프로젝트 기반과 데이터 수집 계층을 준비하는 단계**입니다.

- 사람인 Open API용 HTTP 클라이언트 기본 구조
- 환경변수 기반 API 키 관리
- 채용 사이트 공통 `JobPosting` 데이터 모델
- 정규화 및 데이터베이스 계층을 위한 패키지 구조

아직 PostgreSQL, RAG, LangChain, Vector DB, React 애플리케이션은 구성하지 않았습니다.

## 예정 아키텍처

```text
채용 API / 크롤링
        ↓
데이터 수집
        ↓
정제 및 정규화
        ↓
PostgreSQL 저장
        ↓
기술스택 및 채용시장 통계 분석
        ↓
pgvector 기반 RAG
        ↓
자연어 질의응답
        ↓
React 기반 대시보드
```

현재 구현 범위는 위 흐름의 **데이터 수집**까지입니다.

## 프로젝트 구조

```text
.
├── src/
│   ├── config.py
│   ├── collectors/
│   │   └── saramin.py
│   ├── processing/
│   │   └── normalizer.py
│   ├── database/
│   └── models/
│       └── job_posting.py
├── data/
│   ├── raw/
│   └── processed/
└── tests/
```

## 설치 방법

Python 3.10 이상을 권장합니다.

```bash
python -m venv .venv
```

가상환경을 활성화한 뒤 의존성을 설치합니다.

```bash
python -m pip install -r requirements.txt
```

## 환경변수 설정

프로젝트 루트의 `.env.example`을 복사해 `.env`를 만들고 발급받은 사람인 API 키를 입력합니다.

```env
SARAMIN_API_KEY=your_api_key_here
```

`.env`는 Git에서 제외됩니다. 실제 API 키, 비밀번호와 같은 민감정보는 커밋하지 마세요.

사람인 API 키는 이용 신청 승인 후 발급받을 수 있습니다. 자세한 내용은 [사람인 API 공식 안내](https://oapi.saramin.co.kr/guide/info)를 참고하세요.

## 실행 방법

사람인 채용공고 한 페이지를 원본 JSON 형태로 조회합니다.

```bash
python -m src.collectors.saramin --keywords "AI 개발자" --start 0 --count 10
```

키가 설정되지 않았다면 민감정보를 노출하지 않는 명확한 설정 오류와 함께 종료됩니다. 현재 collector는 원본 JSON 응답까지만 반환하며, 공통 `JobPosting` 모델로 변환하는 로직은 API 응답 검증과 함께 후속 단계에서 구현합니다.

기본 테스트는 표준 라이브러리 `unittest`로 실행할 수 있습니다.

```bash
python -m unittest discover -s tests -v
```

## 향후 개발 계획

1. 사람인 API 연동 및 실제 응답 검증
2. 채용공고 정규화
3. PostgreSQL 저장
4. 기술스택 추출
5. 채용시장 통계 분석
6. 추가 데이터 소스 연동
7. pgvector 및 RAG
8. 자연어 질의
9. React Dashboard
