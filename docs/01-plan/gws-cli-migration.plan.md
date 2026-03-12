# gws CLI Migration Plan

## 배경
Google Workspace CLI (gws) v0.9.x 출시. MCP 서버는 아직 미포함 (향후 버전 예정). CLI subprocess 방식으로 통합. 기존 Python API 의존을 2-Tier Hybrid (CLI > Python) 으로 전환.

## 구현 범위

### 변경 파일 목록

| # | 파일 | 변경 유형 | 설명 |
|---|------|----------|------|
| 1 | `.claude/skills/gmail/SKILL.md` | MODIFY | 2-Tier 전환 (CLI 우선) |
| 2 | `.claude/skills/calendar/SKILL.md` | MODIFY | Anti-Patterns 정리 |
| 3 | `.claude/skills/drive/SKILL.md` | MODIFY | gws CLI 전환 |
| 4 | `.claude/skills/google-workspace/SKILL.md` | MODIFY | Docs/Sheets gws 전환 |
| 5 | `lib/gmail/client.py` | MODIFY | gws 하이브리드 백엔드 추가 |
| 6 | `.claude/skills/google-workspace/REFERENCE.md` | MODIFY | gws CLI 예시 추가 |
| 7 | `.claude/skills/gmail/references/gmail-workflows.md` | MODIFY | gws 명령 추가 |

### 영향 범위
- 스킬 4개 (직접 수정)
- 라이브러리 1개 (lib/gmail/client.py)
- Reference 문서 2개

## 구현 순서

### Step 1: gws CLI 설치 + 인증 (인프라)
- [ ] `npm install -g @googleworkspace/cli`
- [ ] `gws auth login` (기존 Google 계정)
- [ ] `gws gmail users messages list --params '{"userId":"me","maxResults":1}'` 테스트
- [ ] `gws calendar events list --params '{"calendarId":"primary","maxResults":1}'` 테스트

### Step 2: gws CLI 동작 검증
- [x] gws v0.11.1 MCP 미지원 확인 (Unknown service 'mcp')
- [x] CLI subprocess 방식으로 전환 결정
- [x] 4개 서비스 (Gmail, Calendar, Drive, Docs) CLI 명령 동작 확인

### Step 3: Gmail 스킬 전환
- [ ] `.claude/skills/gmail/SKILL.md` 수정
  - 2-Tier 백엔드 선택 로직 추가 (CLI > Python)
  - gws CLI 명령 추가: `gws gmail users messages list`
  - Anti-Patterns 업데이트
- [ ] `lib/gmail/client.py` gws 하이브리드 적용
  - Calendar의 `shutil.which("gws")` 패턴 참조
  - `_call_gws()` 메서드 추가
  - 각 API 메서드에 gws 우선 분기 추가

### Step 4: Calendar 스킬 보강
- [ ] `.claude/skills/calendar/SKILL.md` 수정
  - Anti-Patterns 정리 (MCP 관련 항목 제거)
  - 2-Tier 구조 명시

### Step 5: Drive 스킬 전환
- [ ] `.claude/skills/drive/SKILL.md` 수정
  - gws CLI 명령 추가: `gws drive files list`, `gws drive files get`
  - 2-Tier 백엔드 선택 로직 추가 (CLI > Python)
  - Drive Guardian은 Python 유지 명시

### Step 6: Google Workspace 스킬 전환
- [ ] `.claude/skills/google-workspace/SKILL.md` 수정
  - Sheets/Docs 읽기를 gws CLI로 전환
  - Docs converter는 Python 유지 명시
  - gws CLI 명령 예시 추가
- [ ] `.claude/skills/google-workspace/REFERENCE.md` 수정
  - gws CLI 코드 예시 추가

### Step 7: 통합 검증
- [ ] 4개 스킬 키워드 트리거 테스트
- [ ] gws 미설치 환경 시뮬레이션 (PATH 임시 제거) → Python fallback 동작 확인

## 위험 요소

| 위험 | 확률 | 영향 | 완화 |
|------|:----:|:----:|------|
| gws 설치 실패 (npm/Windows) | 중 | 중 | PowerShell installer 대체 |
| gws auth 실패 (OAuth) | 저 | 고 | 기존 desktop_credentials.json으로 수동 설정 |
| gws 파괴적 변경 (v1.0) | 고 | 중 | Python fallback 유지, gws 버전 pin |

## 아키텍처 결정

### 2-Tier Hybrid 근거
1. **CLI 우선**: gws v0.11.1 기준 MCP 미지원 — CLI subprocess 방식으로 통합
2. **Python 유지**: gws 미설치 fallback + 복잡 로직 (converter, guardian)

> (향후) Tier 0: MCP — gws 차기 버전에서 MCP 서버 포함 시 우선 전환 검토

### 전환하지 않는 것
- `lib/google_docs/converter.py`: Markdown→Google Docs 변환은 Batch API 호출 수십 건 필요. gws CLI 1:1 대체 불가.
- `lib/google_docs/drive_guardian.py`: AI 맥락 분석 기반 거버넌스는 Python 로직 필수.
- `lib/google_docs/table_renderer.py`: 네이티브 테이블 렌더링은 Docs API batchUpdate 전용.

## 커밋 전략

| 순서 | 커밋 메시지 | 포함 파일 |
|:----:|------------|----------|
| 1 | `feat(gmail): gws 2-Tier Hybrid 전환` | SKILL.md, client.py, gmail-workflows.md |
| 2 | `feat(calendar): gws CLI 전환 (Anti-Patterns 정리)` | SKILL.md |
| 3 | `feat(drive): gws CLI 전환` | SKILL.md |
| 4 | `feat(gws): Docs/Sheets gws CLI 전환` | SKILL.md, REFERENCE.md |

## Changelog

| 날짜 | 버전 | 변경 내용 | 변경 유형 | 결정 근거 |
|------|------|-----------|----------|----------|
| 2026-03-12 | v1.0 | 최초 작성 | - | gws CLI v0.9.x 출시 대응 |
| 2026-03-12 | v1.1 | 3-Tier→2-Tier 전환 (gws v0.11.1 MCP 미지원) | TECH | gws MCP 서버 미포함 확인 |
