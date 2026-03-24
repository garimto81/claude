# Audit 트렌드 권장 액션 실행 계획

## 배경 (Background)

- 2026-03-23 `/audit` 통합 점검 트렌드 분석에서 5건 갭 발견
- 워크플로우 성숙도 향상을 위한 자동화/최적화 개선 항목
- 소스: `C:\claude\.claude\research\audit-trend-2026-03-23.md`

## 구현 범위 (Scope)

- 포함: Hook 조건 분기, MCP 프로파일링, Persistent Memory 확대, eco 자동 선택, TDD Red 자동 생성
- 제외: Hook 신규 추가, 에이전트 구조 변경, SKILL.md Phase 재설계

---

## 액션 1: Hook 조건 분기 (높음)

### 현황 분석

4개 핵심 Hook이 Phase 구분 없이 모든 상황에서 실행된다.

| Hook | 이벤트 | 현재 동작 | 문제 |
|------|--------|----------|------|
| `post_edit_check.js` | PostToolUse(Edit/Write) | 매번 린트+테스트 | Phase 0(INIT)에서 불필요한 지연 |
| `session_init.py` | SessionStart | 전체 정리 루틴 실행 | Phase 무관하게 항상 실행 (이건 정상) |
| `branch_guard.py` | PreToolUse(Edit/Write) | main 브랜치 차단 | Phase 무관하게 항상 필요 (변경 불요) |
| `tool_validator.py` | PreToolUse | taskkill 차단 | Phase 무관하게 항상 필요 (변경 불요) |

실질적 개선 대상은 `post_edit_check.js` 1개이다.

### 목표

- `post_edit_check.js`에 Phase 인식 로직 추가
- Phase 0(INIT), Phase 1(PLAN) 중 린트/테스트 실행 스킵

### 구현 방안

1. `/auto` Phase 진행 시 `CURRENT_PHASE` 환경변수 설정 (SKILL.md InitContract 확장)
2. `post_edit_check.js` main() 함수 진입부에 Phase 체크 추가:
   - `CURRENT_PHASE`가 `0` 또는 `1`이면 린트/테스트 스킵, Mermaid 자동수정만 실행
   - `CURRENT_PHASE`가 `2` 이상이거나 미설정이면 기존 동작 유지

### 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\hooks\post_edit_check.js` | Phase 체크 로직 추가 (약 10줄) |
| `C:\claude\.claude\skills\auto\SKILL.md` | InitContract에 CURRENT_PHASE 환경변수 설정 명시 |

### 리스크

- **Phase 환경변수 미전파**: `/auto` 외 직접 실행 시 `CURRENT_PHASE` 미설정 → 기본 동작(전체 실행)으로 Fallback하므로 안전
- **린트 누락**: Phase 1에서 `.py` 파일 편집 시 린트가 안 돌아 오류 누적 가능 → Phase 2(BUILD) 진입 시 전체 린트 1회 실행으로 완화

### Acceptance Criteria

- [ ] `CURRENT_PHASE=0` 시 `post_edit_check.js`가 린트/테스트를 스킵하고 Mermaid 자동수정만 실행
- [ ] `CURRENT_PHASE` 미설정 시 기존 동작 100% 유지 (하위 호환)

---

## 액션 2: MCP 프로파일링 (중간)

### 현황 분석

MCP 서버 호출 횟수, 응답 시간, 토큰 비용을 추적하는 메커니즘이 없다. slow MCP 서버가 전체 워크플로우를 지연시켜도 감지 불가.

### 목표

- MCP 호출별 응답 시간 로깅
- 세션 종료 시 MCP 사용 리포트 출력
- slow server 자동 경고 (응답 > 5초)

### 구현 방안

1. `PostToolUse` Hook에서 MCP 도구 호출 감지 (tool_name 패턴: `mcp__*`)
2. 호출 시간/도구명을 `.claude/logs/mcp_profile.jsonl`에 기록
3. `session_cleanup.py` (SessionEnd)에서 누적 리포트 생성:
   - 총 MCP 호출 수, 평균 응답 시간, 가장 느린 호출 Top 3
4. 응답 시간 5초 초과 시 `PostToolUse` 출력에 경고 추가

### 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\hooks\post_edit_check.js` | MCP 도구 감지 + 시간 로깅 추가 (또는 별도 Hook) |
| `C:\claude\.claude\hooks\session_cleanup.py` | MCP 리포트 출력 로직 추가 |
| `C:\claude\.claude\logs\mcp_profile.jsonl` | 신규 생성 (로그 파일) |

### 리스크

- **Hook에서 응답 시간 측정 불가**: `PostToolUse`는 도구 실행 완료 후 호출되므로 실행 시간 직접 측정 불가 → `tool_input`의 타임스탬프 기반 간접 추정 또는 `PreToolUse`+`PostToolUse` 쌍으로 측정
- **로그 파일 비대화**: 장기 세션 시 `mcp_profile.jsonl` 무한 증가 → SessionStart에서 이전 로그 아카이브/삭제

### Acceptance Criteria

- [ ] MCP 도구 호출 시 `mcp_profile.jsonl`에 기록 생성
- [ ] 세션 종료 시 MCP 사용 요약 리포트 출력
- [x] ~~5초 초과 응답 시 경고 메시지 출력~~ — 불가(기술 제약: PostToolUse에 실행 시간 정보 없음)

---

## 액션 3: Persistent Memory 확대 (중간)

### 현황 분석

현재 `.claude/projects/` 디렉토리에 수동 memory 파일만 존재한다. 에이전트 실행 패턴(어떤 에이전트가 자주 실패하는지, 어떤 파일이 자주 수정되는지)은 축적되지 않는다.

`session_init.py`의 `check_fatigue_signals()`가 편집 패턴을 부분적으로 추적하지만, 에이전트 단위 학습 데이터는 없다.

### 목표

- 에이전트 실행 결과(성공/실패/소요 시간) 자동 기록
- 반복 실패 패턴 감지 → 세션 시작 시 경고

### 구현 방안

1. `subagent_zombie_detector.py` (SubagentStop) 확장: 에이전트 완료 시 결과를 `.claude/logs/agent_history.jsonl`에 기록
   - 기록 항목: `{agent_type, name, status, duration_sec, timestamp}`
2. `session_init.py`에 에이전트 이력 분석 함수 추가:
   - 최근 7일간 실패율 30% 초과 에이전트 경고
   - 자주 수정되는 파일 Top 5 표시 (fatigue_signals 기반)
3. 이력 파일 TTL: 30일 초과 항목 자동 정리 (SessionStart)

### 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\hooks\subagent_zombie_detector.py` | 에이전트 완료 기록 로직 추가 |
| `C:\claude\.claude\hooks\session_init.py` | 에이전트 이력 분석 함수 추가 |
| `C:\claude\.claude\logs\agent_history.jsonl` | 신규 생성 (에이전트 실행 이력) |

### 리스크

- **SubagentStop 이벤트 미발화**: Agent Teams 종료 실패 시 (garimto81/claude#140) 이력 기록 누락 → SessionStart에서 orphan team 감지 시 "unknown" 상태로 기록
- **로그 파일 비대화**: 30일 TTL 자동 정리로 완화

### Acceptance Criteria

- [ ] 에이전트 실행 완료 시 `agent_history.jsonl`에 기록 생성
- [ ] 세션 시작 시 실패율 30% 초과 에이전트 경고 출력
- [ ] 30일 초과 이력 자동 정리

---

## 액션 4: eco 모드 자동 선택 (낮음)

### 현황 분석

사용자가 `--eco` / `--eco-2` / `--eco-3`를 수동 지정한다. Adaptive Model Routing (v25.1)이 Task 복잡도를 자동 분류하지만, eco 레벨은 자동 선택하지 않는다.

현재 Adaptive 분류: Trivial / Standard / Complex / Critical (`model-routing-guide.md` 참조)

### 목표

- Adaptive 분류 결과를 eco 레벨에 자동 매핑
- 사용자 명시적 `--eco` 지정 시 자동 선택 오버라이드

### 구현 방안

1. Phase 0 InitContract의 `adaptive_tier` 결과를 eco 레벨에 매핑:

| adaptive_tier | 자동 eco 레벨 | 근거 |
|:------------:|:------------:|------|
| Trivial | --eco-3 | Haiku 충분 |
| Standard | --eco | 비용 최적화 |
| Complex | (없음) | 품질 우선 |
| Critical | (없음) | 품질 최우선 |

2. SKILL.md Phase 0.3 Adaptive Model Routing 섹션에 eco 자동 선택 규칙 추가
3. `--no-eco` 플래그로 자동 선택 비활성화 지원

### 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\skills\auto\SKILL.md` | Phase 0.3에 eco 자동 선택 규칙 추가 |
| `C:\claude\.claude\references\model-routing-guide.md` | eco 자동 선택 섹션 추가 |

### 리스크

- **과도한 다운그레이드**: Trivial로 잘못 분류된 Complex 작업에 --eco-3 적용 → 품질 저하. 완화: `--no-eco` 오버라이드 + 사용자 확인 프롬프트
- **분류 정확도 의존**: adaptive_tier 분류가 부정확하면 eco 선택도 부정확 → 기존 수동 모드 유지를 기본으로, 자동 선택은 opt-in

### Acceptance Criteria

- [ ] adaptive_tier 결과에 따라 eco 레벨 자동 제안
- [ ] 사용자 명시적 `--eco` 지정 시 자동 선택 오버라이드
- [ ] `--no-eco` 플래그 동작

---

## 액션 5: TDD Red 단계 자동 생성 (낮음)

### 현황 분석

현재 TDD 워크플로우는 `tdd-guide` 에이전트(Sonnet)가 테스트 작성 순서를 강제한다. 하지만 테스트 자체는 개발자/에이전트가 수동 작성한다.

`04-tdd.md` 규칙: Red → Green → Refactor

### 목표

- PRD 요구사항에서 실패 테스트(Red) 자동 생성
- pytest (Python) / jest (TypeScript) 테스트 스켈레톤 자동 생성

### 구현 방안

1. `tdd-guide.md` 에이전트에 "generate-red" 모드 추가:
   - 입력: PRD 파일 경로 또는 요구사항 텍스트
   - 출력: 실패하는 테스트 파일 생성
2. PRD `## 요구사항` → 테스트 함수 매핑 규칙:
   - 기능 요구사항 1개 → `test_` 함수 1개 (최소)
   - 비기능 요구사항 → 성능/보안 테스트 스켈레톤
3. `/tdd --generate-red <prd-path>` 커맨드 확장

### 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\agents\tdd-guide.md` | generate-red 모드 프롬프트 추가 |
| `C:\claude\.claude\commands\tdd.md` | `--generate-red` 서브커맨드 추가 |

### 리스크

- **테스트 품질**: 자동 생성 테스트가 피상적(함수 존재 여부만 확인)일 수 있음 → 생성 후 수동 보강 필수 가이드 추가
- **PRD 형식 의존**: PRD가 비표준 형식이면 파싱 실패 → `## 요구사항` 섹션 필수 검증 + 파싱 실패 시 경고

### Acceptance Criteria

- [ ] `/tdd --generate-red <prd-path>` 실행 시 실패 테스트 파일 생성
- [ ] 생성된 테스트가 `pytest` / `jest` 실행 시 FAIL (Red 상태)
- [ ] PRD 요구사항 1개 이상 → 테스트 함수 1개 이상 매핑

---

## 실행 일정

| 기간 | 액션 | 예상 작업량 | 우선순위 |
|------|------|:----------:|:--------:|
| 즉시 (1-2주) | 액션 1: Hook 조건 분기 | 소형 | 높음 |
| 1개월 | 액션 2: MCP 프로파일링 | 중형 | 중간 |
| 1개월 | 액션 3: Persistent Memory | 중형 | 중간 |
| 분기 | 액션 4: eco 자동 선택 | 소형 | 낮음 |
| 분기 | 액션 5: TDD Red 자동 생성 | 중형 | 낮음 |

## 의존성

```
  액션 1 (Hook 조건 분기)
     |
     v
  액션 2 (MCP 프로파일링) ──── post_edit_check.js 공유
     |
     v
  액션 3 (Persistent Memory) ── session_init.py 공유

  액션 4 (eco 자동 선택) ────── 독립 (SKILL.md만)

  액션 5 (TDD Red 자동 생성) ── 독립 (tdd-guide.md만)
```

## 위험 요소 (Risks)

1. **Hook 파일 동시 수정 충돌**: 액션 1, 2, 3이 모두 Hook 파일을 수정 → 순차 실행 필수 (액션 1 → 2 → 3)
2. **Agent Teams 종료 실패 (#140)**: 액션 3의 SubagentStop 이벤트 의존 → orphan 감지 fallback 필수
3. **SKILL.md 동시 수정**: 액션 1, 4가 SKILL.md 수정 → 별도 브랜치 관리 권장

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-03-23 | v1.0 | 최초 작성 |
