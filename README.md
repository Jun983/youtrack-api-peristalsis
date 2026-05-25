# youtrack-api-peristalsis

YouTrack REST API를 사용하는 Python 자동화 스크립트 모음입니다.

## 프로젝트 구조

```
youtrack-api-peristalsis/
├── src/youtrack_peristalsis/   # 공용 라이브러리 (클라이언트, 설정, 모델)
├── scripts/                    # 실행용 스크립트 (CLI)
├── tests/                      # 단위·통합 테스트
├── pyproject.toml
└── .env.example
```

## 시작하기

```bash
cd youtrack-api-peristalsis
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# .env 에 YOUTRACK_BASE_URL, YOUTRACK_TOKEN, YOUTRACK_ARTICLE_PREFIX 등 설정
```

## 기술 자료 (Knowledge Base) 동기화

YouTrack **기술 자료**는 REST API의 [Articles](https://www.jetbrains.com/help/youtrack/devportal/resource-api-articles.html) 리소스로 다룹니다.

### 1. 문서 조회 → 로컬 md 저장 (pull)

`.env`에 `YOUTRACK_ARTICLE_PREFIX=XAC`를 설정하면 문서 번호만 넘겨도 됩니다.

```bash
python scripts/pull_article.py 13
# → API 조회 ID: XAC-13, 저장: {YOUTRACK_DOCS_DIR}/XAC-13.md

python scripts/pull_article.py XAC-13
python scripts/pull_article.py 13 -o ./docs/custom-name.md
```

### 2. 로컬 md → 기술 자료 작성 (push, 생성만)

```bash
python scripts/push_article.py ./docs/new-article.md
python scripts/push_article.py ./docs/new-article.md -p NP --parent NP-A-7
```

md 파일은 YAML frontmatter + 본문 형식입니다:

```markdown
---
summary: 문서 제목
project: NP
parent_article: NP-A-7
---

## 본문

마크다운 내용...
```

`summary`는 필수입니다. `project` / `parent_article`은 생략 시 `.env`의 `YOUTRACK_PROJECT`, `YOUTRACK_PARENT_ARTICLE`을 사용합니다.

pull로 받은 파일에는 `id_readable`, `article_id` 등이 frontmatter에 포함되며, push는 **새 문서 생성**만 지원합니다 (수정·삭제 미구현).

## 개발

```bash
ruff check .
pytest
```
