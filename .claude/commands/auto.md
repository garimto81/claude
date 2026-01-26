---
name: auto
alias_of: "work --loop"
version: 9.0.0
description: /work --loop의 단축 명령 (자율 반복 모드)
deprecated: false
---

# /auto - 자율 반복 모드

> **`/work --loop`의 단축 명령입니다.**

## 매핑

| /auto 명령 | 실행되는 명령 |
|-----------|--------------|
| `/auto` | `/work --loop` |
| `/auto "지시"` | `/work --loop "지시"` |
| `/auto status` | `/work --loop status` |
| `/auto stop` | `/work --loop stop` |
| `/auto redirect "방향"` | `/work --loop redirect "방향"` |
| `/auto --max N` | `/work --loop --max N` |
| `/auto --debate "주제"` | 3AI 토론 즉시 실행 |
| `/auto --gdocs` | 현재 프로젝트 PRD → Google Docs 변환 |
| `/auto --gdocs "파일"` | 특정 파일 → Google Docs 변환 |
| `/auto --gdocs --sync` | Google Docs ↔ 로컬 동기화 (check) |
| `/auto --gdocs --sync pull` | Google Docs → 로컬 동기화 |
| `/auto --gdocs --sync push` | 로컬 → Google Docs 동기화 |
| `/auto --research "키워드"` | `/research` 스킬 호출 |
| `/auto --research web "키워드"` | 오픈소스/솔루션 웹 검색 |

## 특수 기능

| 명령 | 동작 |
|------|------|
| `/auto --mockup "이름"` | `/mockup` 스킬 직접 호출 |
| `/auto --mockup --bnw "이름"` | B&W T&M 와이어프레임 (흑백 + 플레이스홀더) |
| `/auto --debate "주제"` | Ultimate Debate 3AI 토론 |
| `/auto --gdocs` | 현재 프로젝트 PRD 자동 탐색 → Google Docs 변환 |
| `/auto --gdocs "파일"` | 지정 파일 → Google Docs 변환 |
| `/auto --gdocs --sync` | Google Docs ↔ 로컬 동기화 상태 확인 |
| `/auto --gdocs --sync pull` | Google Docs → 로컬 Markdown 동기화 |
| `/auto --gdocs --sync push` | 로컬 Markdown → Google Docs 동기화 |
| `/auto --research "키워드"` | 코드베이스 분석 (기본값) |
| `/auto --research web "키워드"` | 오픈소스/솔루션 웹 검색 |
| `/auto --research plan "대상"` | 구현 계획 수립 |
| `/auto --research review` | AI 기반 코드 리뷰 |

### --mockup 옵션

| 옵션 | 설명 |
|------|------|
| `--bnw` | **B**lack & White **T**ext/**M**edia wireframe 모드 |

### --mockup --bnw 설정 (Black & White T&M)

| 항목 | 값 | 설명 |
|------|-----|------|
| Style | `wireframe` | 흑백 박스 레이아웃 |
| Colors | `#000`, `#fff`, `#ccc` | 순수 흑백 + 회색 |
| Text | 플레이스홀더 | `Lorem ipsum`, `[Title]` 등 |
| Media | 플레이스홀더 | `[Logo]`, `[Image]`, `[Icon]` 등 |

> **참고**: `--bnw`는 구조 중심 빠른 목업에 최적화. 컬러/실제 콘텐츠 필요 시 기본 모드 사용

### --debate 사용법

```bash
# 3AI 토론 즉시 실행
/auto --debate "캐싱 전략 선택: Redis vs Memcached"

# 복잡한 아키텍처 결정
/auto --debate "마이크로서비스 vs 모놀리식 아키텍처"
```

> **참고**: `<!-- DECISION_REQUIRED -->` 마커 대신 `--debate` 플래그로 간단하게 토론 트리거

### --gdocs 옵션 (Google Docs 자동 변환/동기화)

| 옵션 | 설명 |
|------|------|
| `--gdocs` | 현재 프로젝트 PRD 자동 탐색 → Google Docs 변환 |
| `--gdocs "파일"` | 지정된 파일 → Google Docs 변환 |
| `--gdocs --sync` | 동기화 상태 확인 (CLAUDE.md 기준) |
| `--gdocs --sync pull` | Google Docs → 로컬 동기화 |
| `--gdocs --sync push` | 로컬 → Google Docs 동기화 |

### --gdocs 자동 처리 워크플로우 (MANDATORY)

```
/auto --gdocs
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. PRD/문서 파일 자동 탐색                                   │
│    - docs/prds/*.md                                         │
│    - tasks/prds/*.md                                        │
│    - docs/PRD-*.md                                          │
│    - docs/guides/*.md                                       │
│    - *.prd.md                                               │
│    탐색 실패 시: 사용자에게 파일 경로 질문                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 절대 경로 변환                                            │
│    상대 경로 → C:\claude\{현재프로젝트}\...                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 루트에서 변환 명령 실행 (필수!)                           │
│    cd C:\claude && python -m lib.google_docs convert "..."  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Google Docs URL 반환                                      │
│    성공: URL 출력                                            │
│    실패: 에러 메시지 + 해결 방법 안내                        │
└─────────────────────────────────────────────────────────────┘
```

**⚠️ 서브 프로젝트에서 실행 시 주의:**
- 반드시 `cd C:\claude &&` 접두사로 루트에서 실행
- 파일 경로는 항상 절대 경로로 지정
- Gemini CLI 토큰이 아닌 `C:\claude\json\token.json` 사용

### --gdocs --sync 동기화 워크플로우

```
/auto --gdocs --sync [action]
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. CLAUDE.md에서 Google Docs 매핑 정보 읽기                  │
│    - Google Docs ID                                         │
│    - 로컬 파일 경로                                         │
│    - 버전 정보                                              │
│    - 마지막 동기화 날짜                                     │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 동기화 작업 실행                                          │
│    check : 차이점만 확인 (기본값)                           │
│    pull  : Google Docs → 로컬 Markdown                      │
│    push  : 로컬 Markdown → Google Docs                      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CLAUDE.md 동기화 날짜 업데이트                            │
│    - 동기화 성공 시 자동 업데이트                           │
└─────────────────────────────────────────────────────────────┘
```

**CLAUDE.md 필수 형식:**

```markdown
## Google Docs Reference

| 문서 | Google Docs ID | 버전 | 동기화 날짜 |
|------|----------------|------|-------------|
| **문서명** | `DOC_ID_HERE` | v1.0.0 | 2026-01-26 |
```

**실행 명령 (전역 스크립트):**

```powershell
# 어디서든 실행 가능
python C:\claude\scripts\prd_sync.py check                          # 자동 감지
python C:\claude\scripts\prd_sync.py check --project wsoptv_nbatv_clone  # 프로젝트 지정
python C:\claude\scripts\prd_sync.py pull --project wsoptv_ott           # GDocs → 로컬
python C:\claude\scripts\prd_sync.py push --force                        # 확인 없이 실행
python C:\claude\scripts\prd_sync.py list                                # 프로젝트 목록
```

### --research 옵션 (통합 리서치)

| 옵션 | 설명 |
|------|------|
| `--research "키워드"` | 코드베이스 분석 (기본값) |
| `--research web "키워드"` | 오픈소스/솔루션 웹 검색 |
| `--research plan "대상"` | 구현 계획 수립 |
| `--research review` | AI 기반 코드 리뷰 |

### --research 사용법

```bash
# 코드베이스 분석
/auto --research "authentication"
/auto --research code src/api/

# 웹 검색 (오픈소스/솔루션)
/auto --research web "React state management"
/auto --research web "Python async HTTP client"

# 구현 계획
/auto --research plan 123            # 이슈 #123 구현 계획
/auto --research plan "user auth"    # 기능 구현 계획

# 코드 리뷰
/auto --research review              # staged 변경사항 리뷰
/auto --research review --branch     # 현재 브랜치 전체
```

### --research web 출력 예시

```markdown
## 웹 리서치: React state management

### 추천 라이브러리
| 라이브러리 | 별점 | 장점 | 단점 |
|-----------|------|------|------|
| Zustand | ⭐⭐⭐⭐⭐ | 간단, 가벼움 | 대규모 앱 한계 |
| Jotai | ⭐⭐⭐⭐ | 원자적 상태 | 러닝커브 |

### Make vs Buy 분석
- **Buy 권장**: 인증된 라이브러리 사용
```

## 실행 지시

**$ARGUMENTS를 분석하여 `/work --loop`로 변환 후 Skill tool 호출:**

```python
# /auto → /work --loop
Skill(skill="work", args="--loop")

# /auto "지시" → /work --loop "지시"
Skill(skill="work", args="--loop \"$ARGUMENTS\"")

# /auto status → /work --loop status
Skill(skill="work", args="--loop status")

# /auto stop → /work --loop stop
Skill(skill="work", args="--loop stop")

# /auto --mockup "이름" → /mockup "이름"
Skill(skill="mockup", args="$NAME")

# /auto --mockup --bnw "이름" → /mockup "이름" --style=wireframe --bnw
Skill(skill="mockup", args="$NAME --style=wireframe --bnw")

# /auto --debate "주제" → ultimate-debate 실행
Skill(skill="ultimate-debate", args="\"$TOPIC\"")

# /auto --gdocs → Google Docs 자동 변환 (직접 실행, 스킬 호출 아님!)
# 1. 현재 프로젝트에서 PRD 파일 탐색
#    - Glob("docs/prds/*.md"), Glob("tasks/prds/*.md"), Glob("docs/PRD-*.md")
# 2. 발견된 파일을 절대 경로로 변환
# 3. 루트에서 변환 명령 실행:
#    Bash("cd C:\claude && python -m lib.google_docs convert \"{절대경로}\"")
# 4. 결과 URL 출력

# /auto --gdocs "파일" → 지정 파일 변환
# 1. 파일 경로를 절대 경로로 변환
# 2. Bash("cd C:\claude && python -m lib.google_docs convert \"{절대경로}\"")
# 3. 결과 URL 출력

# /auto --gdocs --sync → 동기화 상태 확인 (전역 스크립트 사용)
# 1. Bash("python C:\\claude\\scripts\\prd_sync.py check")
# 2. 현재 프로젝트 자동 감지 또는 --project 옵션 사용
# 3. 결과 출력

# /auto --gdocs --sync pull → Google Docs → 로컬 동기화
# 1. Bash("python C:\\claude\\scripts\\prd_sync.py pull")
# 2. 확인 프롬프트 표시 후 실행

# /auto --gdocs --sync push → 로컬 → Google Docs 동기화
# 1. Bash("python C:\\claude\\scripts\\prd_sync.py push")
# 2. 확인 프롬프트 표시 후 실행

# /auto --gdocs --sync list → 동기화 가능한 프로젝트 목록
# 1. Bash("python C:\\claude\\scripts\\prd_sync.py list")

# /auto --research "키워드" → /research "키워드"
Skill(skill="research", args="$KEYWORD")

# /auto --research web "키워드" → /research web "키워드"
Skill(skill="research", args="web \"$KEYWORD\"")

# /auto --research plan "대상" → /research plan "대상"
Skill(skill="research", args="plan \"$TARGET\"")

# /auto --research review → /research review
Skill(skill="research", args="review")

# /auto --research review --branch → /research review --branch
Skill(skill="research", args="review --branch")
```

## 상세 문서

전체 기능은 `/work` 커맨드 참조: `.claude/commands/work.md`

---

**이 커맨드는 `/work --loop`의 alias입니다. 새 기능은 `/work`에 추가됩니다.**
