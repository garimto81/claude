# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 6.0.0 | **Context**: Windows, PowerShell, Root: `D:\AI\archive-analyzer`

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `D:\AI\archive-analyzer\...` |
| **충돌** | 지침 충돌 시 → **사용자에게 질문** (임의 판단 금지) |

---

## 프로젝트 구조

4개의 독립적인 컴포넌트로 구성된 모노레포:

```
D:\AI\archive-analyzer\
├── src/agents/          # AI 워크플로우 에이전트 (Python)
├── archive-analyzer/    # OTT 미디어 아카이브 분석 도구 (Python)
├── backend/             # FastAPI 비디오 처리 서버 (Python)
└── frontend/            # React 프론트엔드 (TypeScript)
```

**데이터 흐름**:
```
NAS(SMB) → archive-analyzer → pokervod.db ← backend → frontend
                                   ↑
                            MeiliSearch (검색)
```

---

## 빌드 & 테스트

### Python (archive-analyzer)

```powershell
cd D:\AI\archive-analyzer\archive-analyzer
pip install -e ".[dev,media]"                # 설치
pytest tests/test_scanner.py -v              # 단일 테스트
pytest tests/ -v -m unit                     # 마커별 테스트
ruff check src/ && black --check src/        # 린트
```

### Backend (FastAPI)

```powershell
cd D:\AI\archive-analyzer\backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001    # 서버 실행
pytest tests/ -v                             # 테스트
```

### Frontend (React/Vite)

```powershell
cd D:\AI\archive-analyzer\frontend
npm install
npm run dev                                  # 개발 서버 (port 8003)
npm test                                     # Vitest 단위 테스트
npm run test:e2e                             # Playwright E2E
npm run lint                                 # ESLint
```

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| main 브랜치 수정 금지 | **차단** | `git checkout -b feat/issue-N-desc` |
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |

---

## 작업 방법

```
사용자 요청 → /work "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/work` → 이슈 → 브랜치 → TDD → PR |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 (브랜치 불필요) |
| 질문 | 직접 응답 |

---

## 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/work "내용"` | 전체 워크플로우 |
| `/issue fix #N` | 이슈 해결 |
| `/commit` | 커밋 |
| `/tdd` | TDD 워크플로우 |
| `/check` | 린트 + 테스트 |
| `/parallel dev` | 병렬 개발 |

전체: `.claude/commands/`

---

## 안전 규칙

### Crash Prevention (필수)

```powershell
# ❌ 금지 (120초 초과 → 크래시)
pytest tests/ -v --cov                # 대규모 테스트
npm install && npm run build          # 체인 명령

# ✅ 권장
pytest tests/test_a.py -v             # 개별 실행
# 또는 run_in_background: true
```

### 보호 대상

- `pokervod.db` 스키마 변경 금지 (`qwen_hand_analysis` 소유)
- 경로: `D:/AI/claude01/shared-data/pokervod.db`

---

## 문제 해결

```
문제 → WHY(원인) → WHERE(영향 범위) → HOW(해결) → 수정
```

**즉시 수정 금지.** 원인 파악 → 유사 패턴 검색 → 구조적 해결.

---

## 참조

| 문서 | 용도 |
|------|------|
| `archive-analyzer/CLAUDE.md` | 아카이브 분석기 상세 |
| `docs/WORKFLOW_REFERENCE.md` | 상세 워크플로우 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 목록 |
| `.claude/commands/` | 커맨드 상세 |
