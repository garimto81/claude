# OMC BKIT Vercel BP 워크플로우 전면 재검토 계획

**Created**: 2026-02-16
**Complexity**: 5/5 (HEAVY)
**Branch**: feat/drive-project-restructure

---

## 배경

3개 분석 에이전트(OMC, BKIT, Skills)의 병렬 탐색 결과, 현재 워크플로우 시스템에 다음 문제가 확인됨:
- 세션 토큰: 상시 ~4,275t + BKIT ~2,500t = **6,775t** (목표 5,000t 대비 35% 초과)
- BKIT 11개 에이전트 중 실사용 4개, 22개 스킬 중 대부분 미사용
- OMC 위임 규칙이 비현실적 (1줄 수정도 에이전트 강제)
- 스킬 53개 중 7개 deprecated stub 미삭제, 과대 스킬 존재
- 도구 호출당 최대 10개 hook 실행

## 사용자 선택

| 영역 | 결정 |
|------|------|
| BKIT | 선택적 축소 (미사용 7개 제거, 핵심 4개 유지) |
| OMC | 실용적 임계값 도입 (10줄 이하 직접 허용) |
| 커맨드/스킬 | 적극 정리 (53→~40개) |
| 에이전트 모델 | claude-expert opus→sonnet |

---

## 구현 범위

### WI-1: OMC 글로벌 CLAUDE.md 개선 (~/.claude/CLAUDE.md)

**변경 내용:**
1. 위임 매트릭스 수정: "Single-line code change → NEVER" → "10줄 이하 단순 수정 → 직접 허용"
2. 키워드 트리거 정리: 일상 단어("fast", "search", "efficient") 제거, 명시적 키워드만 유지
3. ecomode 키워드 축소: "efficient", "save-tokens", "budget" 제거 (너무 일상적)
4. RULE 3 완화: "NEVER do code changes directly" → "Delegate code changes >10 lines"

**영향 파일:** `~/.claude/CLAUDE.md` (1개)

### WI-2: Deprecated 스킬 삭제 (10개 디렉토리)

**삭제 대상:**
1. `auto-workflow/` → auto로 통합됨
2. `auto-executor/` → auto로 통합됨
3. `cross-ai-verifier/` → verify로 통합됨
4. `issue-resolution/` → issue fix로 통합됨
5. `tdd-workflow/` → tdd로 통합됨
6. `daily-sync/` → daily로 통합됨
7. `work/` → auto로 통합됨 (v19.0 stub)
8. `debugging-workflow/` → debug 스킬과 완전 중복
9. `parallel-agent-orchestration/` → parallel + agent-teamworks와 중복
10. `journey-sharing/` → 사용 이력 없음

**결과:** 53 → 43개

**영향:** `08-skill-routing.md`의 deprecated 테이블은 이미 리다이렉트 정보 포함하므로 스킬 디렉토리만 삭제해도 안전

### WI-3: 과대 스킬 REFERENCE.md 분리 (2개)

**대상:**
1. `drive/` SKILL.md 21.4KB → SKILL.md (~4KB) + REFERENCE.md (~17KB)
2. `supabase-integration/` SKILL.md 16.1KB → SKILL.md (~4KB) + REFERENCE.md (~12KB)

**패턴:** /auto 스킬과 동일 (SKILL.md = 핵심 + REFERENCE.md = 상세)

### WI-4: 에이전트 모델 최적화 (1개)

**변경:**
- `claude-expert.md`: model: opus → model: sonnet

**참고:** 나머지 9개는 이미 sonnet/haiku로 최적화됨 (분석 보고서의 "전부 opus" 정보 오류)

### WI-5: State/Hook 정리

**즉시 정리:**
1. `docs/.pdca-status.json`: history 배열 정리 (350줄 → 최근 10개만 유지)
2. `.omc/ultrawork-state.json`: original_prompt 필드 제거 (22KB → ~1KB)
3. `.omc/state/unified-session.json`: 삭제 (2주 이상 stale)
4. `docs/.pdca-status.json` activeFeatures: phase "do" + matchRate 100인 항목 completed 처리

**Hook 개선:**
5. `session_init.py`: 디버그 로깅 최소화 (향후 세션에서)

### WI-6: BKIT 선택적 축소

**가능한 조치 (plugin cache 수정 불가 제약):**
1. `/auto` SKILL.md에서 BKIT 에이전트 참조를 핵심 4개로 명시적 한정
2. `docs/.pdca-status.json`에서 BKIT 불필요 데이터 정리
3. `.bkit-memory.json` 설정 조정 (가능 시)

**유지 대상:** gap-detector, pdca-iterator, code-analyzer, report-generator

---

## 위험 요소

| 위험 | 대응 |
|------|------|
| deprecated 스킬 삭제 후 외부 참조 | skill-causality-graph.md 확인 - 7개 필수 참조에 해당 없음 |
| OMC 임계값 도입 시 품질 저하 | 10줄 기준 + 설정 파일은 항상 직접 허용 유지 |
| drive/supabase 분리 시 기능 손실 | SKILL.md에 REFERENCE.md 참조 지시문 포함 |
| BKIT plugin 업데이트 시 설정 초기화 | 로컬 hook에서 처리 (기존 교훈 적용) |

---

## 실행 순서

1. WI-1 (OMC CLAUDE.md) — 단독 파일, 충돌 없음
2. WI-4 (에이전트 모델) — 단독 파일, 충돌 없음
3. WI-2 (deprecated 삭제) — 디렉토리 삭제, 인과관계 확인 후
4. WI-3 (스킬 분리) — 파일 읽기+분리, 순차
5. WI-5 (State 정리) — JSON 수정
6. WI-6 (BKIT 축소) — 의존성 있음, 마지막
