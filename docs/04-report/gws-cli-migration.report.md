# gws CLI Migration PDCA 완료 보고서

## 개요

| 항목 | 값 |
|------|-----|
| 작업명 | Google Workspace CLI 2-Tier Hybrid 전환 |
| 복잡도 | STANDARD (3/6) |
| 시작일 | 2026-03-12 |
| 완료일 | 2026-03-12 |
| 커밋 | `b4b65ca` |

## 변경 요약

### 배경
gws CLI v0.11.1 출시. MCP 서버 미포함 (`Unknown service 'mcp'`). CLI subprocess 방식 2-Tier Hybrid로 전환.

### 아키텍처 결정
- **Tier 1 (Primary)**: gws CLI subprocess — 읽기 전용 API 호출
- **Tier 2 (Fallback)**: Python API — 쓰기 작업 + gws 미설치 환경
- **Tier 0 (Future)**: MCP — gws 차기 버전에서 MCP 서버 포함 시 전환

### 변경 파일 (10개)

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `.claude/skills/gmail/SKILL.md` | MODIFY | 2-Tier 백엔드 선택 로직 |
| `.claude/skills/calendar/SKILL.md` | MODIFY | Anti-Patterns 정리 (MCP 금지 제거) |
| `.claude/skills/drive/SKILL.md` | MODIFY | gws CLI Integration 섹션 |
| `.claude/skills/google-workspace/SKILL.md` | MODIFY | gws CLI Integration 섹션 |
| `.claude/skills/google-workspace/REFERENCE.md` | MODIFY | gws CLI 명령 예시 추가 |
| `.claude/skills/gmail/references/gmail-workflows.md` | MODIFY | gws CLI Commands 섹션 |
| `lib/gmail/client.py` | MODIFY | gws 하이브리드 백엔드 구현 |
| `lib/gmail/errors.py` | MODIFY | GwsNotFoundError, NetworkError 추가 |
| `docs/00-prd/prd-gws-cli-migration.prd.md` | CREATE | PRD 문서 |
| `docs/01-plan/gws-cli-migration.plan.md` | CREATE | Plan 문서 |

### lib/gmail/client.py 핵심 변경

```python
# gws CLI 감지 (Calendar 패턴 동일)
self._gws_available = prefer_gws and shutil.which("gws") is not None

# gws 호출 공통 메서드
def _gws_call(self, resource: str, method: str, params: dict = None) -> dict:
    cmd = ["gws"] + resource.split(".") + [method]
    # → "gmail.users.messages" → ["gws", "gmail", "users", "messages", "list"]
```

- 읽기 7개 메서드: gws 우선 분기 (`get_profile`, `list_emails`, `get_email` 등)
- 쓰기 7개 메서드: Python 전용 유지 (`send`, `reply`, `archive` 등)

## 발견된 이슈 및 수정

| # | 이슈 | 심각도 | 상태 |
|---|------|--------|------|
| 1 | `_gws_call()` resource path 단일 인자 전달 | HIGH | 수정 완료 |
| 2 | gws v0.11.1 MCP 미지원 | INFO | 2-Tier로 전환 |
| 3 | gws auth 401 invalid_client (3회) | MEDIUM | OAuth 프로젝트 재설정으로 해결 |

## 전환하지 않은 것 (의도적)

| 컴포넌트 | 이유 |
|---------|------|
| `lib/google_docs/converter.py` | Batch API 수십 건 호출, CLI 1:1 대체 불가 |
| `lib/google_docs/drive_guardian.py` | AI 맥락 분석 기반 거버넌스, Python 필수 |
| `lib/google_docs/table_renderer.py` | Docs API batchUpdate 전용 |
| Gmail send/reply | Base64 인코딩 필요, CLI 부적합 |

## 검증 결과

- Architect Gate: APPROVE (조건부 → 4개 수정 후 통과)
- 4개 스킬 SKILL.md: 2-Tier Hybrid 섹션 추가 확인
- lib/gmail/client.py: resource.split(".") 패턴 적용 확인
- Reference 문서 2개: gws CLI 명령 예시 포함 확인
