# 워크플로우 개선 전략 PRD

**버전**: v1.0 | **날짜**: 2026-02-26 | **브랜치**: feat/prd-chunking-strategy

---

## 개요

- **목적**: Claude Code SDK 제약 내에서 달성 가능한 실용적 워크플로우 개선 전략 수립 및 구현
- **배경**: Context Specialization Strategy (arxiv:2602.11988) 검증 결과, 전략 A/B/C/D 중 실현 가능한 경로는 정적 슬림화 + 참조 분리 조합뿐임을 확인. 이 PRD는 검증 결과를 기반으로 즉시 실행 가능한 4개 개선 항목을 정의한다. 검증 보고서: `docs/04-report/strategy-validation-report.md`
- **범위**: /auto SKILL.md 리팩토링 + CLAUDE.md 정적 슬림화 + Hook 안전성 강화 + rules 물리적 분리 설계

---

## 개선 목표 (측정 가능)

| 목표 | 현재값 | 목표값 | 측정 방법 |
|------|--------|--------|-----------|
| 항상 로드 context 크기 | 857줄 (CLAUDE.md 336줄 + rules 521줄) | 681줄 이하 (20.5%+ 감소) | `wc -l` |
| /auto SKILL.md 크기 | 426줄 | 100줄 이하 | `wc -l C:\claude\.claude\skills\auto\SKILL.md` |
| CLAUDE.md 합계 | 336줄 (global 165 + project 171) | 160줄 이하 (각 80줄) | `wc -l` |
| API 키 금지 선언 보존률 | 100% | 100% | 코드 검토 |
| Agent Teams 프로토콜 보존 | 100% | 100% | /auto 실행 검증 |
| tool_validator.py API 키 패턴 차단 | 없음 | `sk-`, `AKIA`, `AIza` 3개 패턴 추가 | 차단 테스트 |

---

## 요구사항

### 기능 요구사항

#### R-1: /auto SKILL.md 참조 분리 (P-1 최우선)

**목적**: SKILL.md에서 상세 내용을 분리하여 스킬 호출 시 context 로드량 감소

**현재 구조**:
- `/auto/SKILL.md` — 426줄 단일 파일 (핵심 흐름 + Phase 상세 + 예외 케이스 혼재)

**목표 구조**:
```
C:\claude\.claude\skills\auto\
├── SKILL.md       — 100줄 이하 (Phase 0-5 흐름 + 에이전트 호출 규칙만)
└── REFERENCE.md   — 326줄 (Phase 상세 prompt, 복잡도 분기 상세, 예외 케이스, 옵션 워크플로우 등)
```

**분리 기준**:
- SKILL.md 유지 항목: Phase 0-5 흐름 요약, TeamCreate/TeamDelete 패턴, 금지 사항 핵심 목록
- REFERENCE.md 이동 항목: impl-manager 5조건 상세 prompt, QA Runner 6종 goal, Architect 진단 prompt, Vercel BP 주입 규칙, 복잡도 세부 분기, 자율 발견 모드 Tier 0-5, 세션 관리 상세, Nuclear Option

**에이전트 참조 방식**: 에이전트가 SKILL.md 처리 후 필요 시 `Read("REFERENCE.md")`로 상세 참조

**성공 기준**:
- `wc -l SKILL.md` ≤ 100줄
- `wc -l REFERENCE.md` 존재 + 내용 있음
- /auto PDCA Phase 0-5 정상 실행 (Agent Teams 동작 확인)
- 금지 사항 핵심 보존: architect 파일 생성 금지, designer 경유 규칙, shutdown_response 금지

**위험 및 완화**:
- 위험: 에이전트가 REFERENCE.md 참조 누락 → 상세 지침 미적용
- 완화: SKILL.md에 "상세: `REFERENCE.md`" 명시적 참조 지시 포함 (현재 패턴 유지)

**SDK 제약 내 실현 가능성**: SDK 제약 없음. 파일 분리는 항상 가능. REFERENCE.md는 `/auto/` 디렉토리에 위치하므로 에이전트가 `Read()`로 접근 가능.

---

#### R-2: CLAUDE.md 정적 슬림화 (P-2)

**목적**: 두 CLAUDE.md에서 중복·불필요 정보를 제거하여 항상 로드 context 감소

**현재 구조**:
- `~/.claude/CLAUDE.md` — 165줄 (글로벌 지침)
- `C:\claude\CLAUDE.md` — 171줄 (프로젝트 지침)

**슬림화 원칙** (논문 황금 규칙 적용):
- 에이전트가 파일/코드 탐색으로 알 수 있는 정보는 제거
- 두 파일에 중복으로 존재하는 내용은 하나에만 유지
- 참조 문서 목록은 링크로 대체 (내용 요약 불필요)

**제거 대상 후보**:
- 아키텍처 섹션 (코드 탐색으로 확인 가능한 구조 설명)
- 에이전트 목록 (`.claude/agents/`에서 직접 로드됨)
- 빠른 참조 커맨드 표 (docs/COMMAND_REFERENCE.md 링크로 대체)
- 중복된 핵심 원칙 (양 파일 교차 중복 항목)

**절대 보존 항목** (제거 금지):
1. API 키 금지 선언 — hook으로 100% 차단 불가, CLAUDE.md 텍스트로만 제어 가능
2. Agent Teams 프로토콜 (`TeamCreate → Task → SendMessage → TeamDelete`) — 시스템 기능 정의
3. 절대 경로 원칙 — 런타임 동작에 직접 영향
4. 프로세스 전체 종료 금지 원칙

**성공 기준**:
- `wc -l ~/.claude/CLAUDE.md` ≤ 80줄
- `wc -l C:\claude\CLAUDE.md` ≤ 80줄
- API 키 금지 선언 존재 확인
- Agent Teams 프로토콜 존재 확인
- /auto 실행 시 정상 동작 (회귀 없음)

**위험 및 완화**:
- 위험: 필수 선언 누락 → 에이전트 API 키 방식 시도
- 완화: 슬림화 후 핵심 보존 항목 체크리스트 수동 검토 + R-3 Hook 강화 선행

**SDK 제약 내 실현 가능성**: SDK 제약 없음. CLAUDE.md 편집은 항상 가능.

---

#### R-3: Hook 안전성 강화 (P-3)

**목적**: CLAUDE.md 슬림화와 병행하여 API 키 패턴을 tool_validator.py에서 차단

**현재 상태**: `tool_validator.py`는 프로세스 전체 종료 명령만 차단. API 키 패턴 차단 없음.

**추가 구현 내용**:

```python
# tool_validator.py에 추가할 API 키 패턴 차단
API_KEY_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",    # OpenAI API 키
    r"AKIA[A-Z0-9]{16}",        # AWS Access Key
    r"AIza[A-Za-z0-9\-_]{35}",  # Google API 키
    r"Bearer [A-Za-z0-9\-._~+/]{20,}",  # Bearer 토큰 하드코딩
]
# Write/Edit 도구 실행 시 파일 내용에 이 패턴이 존재하면 차단 + 경고 메시지 출력
```

**세션 시작 시 규칙 보충 메시지 강화 (`session_init.py`)**:
```python
# 기존 메시지에 추가
message += "\n[필수 규칙] API 키 금지 (Browser OAuth만), 절대 경로 사용, PRD-First"
```

**성공 기준**:
- `sk-test123456789012345` 패턴이 포함된 파일 Write 시도 → 차단 확인
- `session_init.py` 메시지에 API 키 금지 규칙 포함 확인
- 기존 tool_validator.py 프로세스 종료 차단 기능 회귀 없음

**위험 및 완화**:
- 위험: 정규식 패턴이 정상 코드 (예: 테스트 코드의 dummy key)를 오탐
- 완화: 오탐 허용 목록 (`# noqa: api-key`, `# test-only` 주석 무시) 또는 경고만 (차단 아님) 모드
- 주의: hook 패턴 매칭은 100% 차단을 보장하지 않으므로 CLAUDE.md 선언을 완전히 대체하지 않음

**SDK 제약 내 실현 가능성**: SDK 제약 없음. PreToolUse hook은 Write/Edit 도구에 접근 가능.

---

#### R-4: rules 물리적 분리 설계 (P-4 장기)

**목적**: 서브 프로젝트별로 필요한 rules 파일만 로드하여 context 절감

**현재 구조**: `C:\claude\.claude\rules\` — 6개 파일 521줄 항상 로드

**설계 방향** (구현은 M-3 확인 후):
```
C:\claude\.claude\rules\          — 공통 규칙 (04-tdd.md, 항상 필요)
C:\claude\.claude\rules-media\    — 미디어 전용 (10-image-analysis.md)
C:\claude\.claude\rules-dev\      — 개발 전용 (상세 개발 규칙)

서브 프로젝트 적용 예시:
  wsoptv_ott\.claude\rules\ → Junction → rules\ + rules-media\
  investment\.claude\rules\ → Junction → rules\ (rules-media 불필요)
```

**전제 조건** (이 요구사항 구현 전 반드시 확인):
- M-3 해소: `.claude/rules/*.md` 파일의 SDK 자동 로드 동작 공식 문서 확인
- session_init.py에 프로젝트 타입 기반 Junction 자동 생성 로직 구현 가능성 검토

**현재 상태**: 설계 중 (M-3 미확인으로 보류)

**성공 기준 (구현 시)**:
- 미디어 프로젝트에서 개발 전용 rules 로드 안 됨 확인
- 공통 rules (04-tdd.md) 모든 프로젝트에서 로드됨 확인
- Junction 자동 생성 로직으로 수동 설정 불필요

---

#### R-5: Agent Teams 안정성 강화

**목적**: 팀 고아 상태(orphaned team) 발생률 감소 및 자동 복구 강화

**현재 문제**: SDK 레벨 이슈 — Context Compaction 시 팀 상태 소실 (#23620 OPEN), VS Code `isTTY=false` 메시지 전달 실패 (#25254)

**구현 가능한 완화책**:
1. `session_init.py` stale 팀 정리 강화 — 현재 로직 검토 후 보완
2. TeamCreate 실패 시 자동 복구 절차 SKILL.md에 명시 (이미 v22.4에 포함, 확인)
3. 팀 정리 fallback Python 스크립트를 `/auto stop` 명령어로 자동 실행

**성공 기준**:
- 세션 종료 후 `~/.claude/teams/` 디렉토리 비어있음 확인
- TeamCreate 실패 시 자동 복구 후 정상 진행 확인

---

### 비기능 요구사항

| 항목 | 요구사항 |
|------|----------|
| 보안 | API 키 금지 선언 반드시 보존. tool_validator.py 기존 차단 기능 회귀 없음 |
| 유지보수성 | 단일 파일 패치 원칙 유지. /auto 보안 패치는 SKILL.md 1개 파일 수정으로 전파 가능해야 함 |
| 안정성 | 기존 /auto PDCA Phase 0-5 흐름 100% 보존. 회귀 테스트 필수 |
| 호환성 | 기존 22개 커맨드, 42개 에이전트, 37개 스킬 정상 동작 보장 |
| 원자성 | 각 R-1~R-5는 독립적으로 배포 가능해야 함. 롤백 가능 |

---

## 구현 우선순위

| 우선순위 | 요구사항 | 예상 절감 효과 | 위험도 | 실행 방식 |
|---------|---------|--------------|--------|-----------|
| P-1 (즉시) | R-1: SKILL.md 참조 분리 | 326줄 절감 | 낮음 | executor |
| P-2 (즉시) | R-2: CLAUDE.md 정적 슬림화 | 176줄 절감 | 중간 | executor |
| P-3 (단기) | R-3: Hook 안전성 강화 | 보안 강화 (줄 수 무관) | 낮음 | executor |
| P-4 (장기) | R-4: rules 물리적 분리 | 추가 절감 (미확정) | 높음 | 설계 단계 |
| P-5 (지속) | R-5: Agent Teams 안정성 | 고아 팀 감소 | 중간 | executor |

**실행 순서 권장**:
```
P-3 (Hook 강화) → P-1 (SKILL.md 분리) → P-2 (CLAUDE.md 슬림화) → P-5 (Teams 안정성)
↑ P-3를 먼저 실행하여 P-2 슬림화 후에도 API 키 보호 유지
```

---

## 제약사항

| 제약 | 내용 | 출처 |
|------|------|------|
| F-1: SDK CLAUDE.md 런타임 교체 불가 | CLAUDE.md는 세션 시작 시 정적 로드. 런타임 교체 API 없음 | 실증 검증 |
| F-2: rules 자동 로드 동작 미확인 | `.claude/rules/*.md` 자동 로드가 공식 문서에 명문화 안 됨 | M-3 미해소 |
| F-3: 에이전트 42개 항상 로드 미확인 | 로컬 에이전트가 메인 context에 항상 전체 포함되는지 미확인 | M-4 미해소 |
| S-1: 마이크로 스킬 분기 금지 | 유지보수 5배 증가 + 안전 규칙 우회 위험 | 전략 B 기각 |
| API 키 금지 선언 절대 제거 금지 | hook으로 100% 차단 불가. 텍스트 선언 필수 | S-3 확정 |
| Agent Teams 프로토콜 절대 제거 금지 | 시스템 기능 정의 자체. 제거 시 동작 불가 | M-2 확정 |

---

## 실행하지 말아야 할 것

| 항목 | 이유 |
|------|------|
| 전략 C (동적 프로파일링) | F-1 확정 — SDK context 로딩 제어 API 없음 |
| 전략 D (규칙 태그) | 태그 기반 선택 로드 API 없음 |
| 전략 B 마이크로 스킬 분기 | 보안 패치 전파 5배 비용 + 안전 우회 위험 |
| profile.yaml skip_rules/active_rules | 가상 API — 실행 런타임 없음 |
| 에이전트 Lazy Loading | GitHub Issue #8997 OPEN |

---

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| R-1: SKILL.md 참조 분리 | 예정 | P-1 최우선 — REFERENCE.md 신규 생성 |
| R-2: CLAUDE.md 정적 슬림화 | 예정 | P-2 — R-3 선행 필수 |
| R-3: Hook 안전성 강화 | 예정 | P-3 — tool_validator.py + session_init.py |
| R-4: rules 물리적 분리 | 설계 중 | P-4 장기 — M-3 확인 후 |
| R-5: Agent Teams 안정성 | 예정 | P-5 지속 개선 |

---

## 검증 계획

### R-1 검증 (SKILL.md 분리 후)
```bash
wc -l C:\claude\.claude\skills\auto\SKILL.md    # ≤ 100줄
wc -l C:\claude\.claude\skills\auto\REFERENCE.md  # 존재 + 200줄+
```
- /auto 실행 → Phase 0-5 정상 진행 확인
- Agent Teams `pdca-*` 팀 생성/삭제 정상 확인

### R-2 검증 (CLAUDE.md 슬림화 후)
```bash
wc -l ~/.claude/CLAUDE.md          # ≤ 80줄
wc -l C:\claude\CLAUDE.md          # ≤ 80줄
grep "API 키 금지\|Browser OAuth" ~/.claude/CLAUDE.md  # 존재 확인
grep "TeamCreate\|TeamDelete" ~/.claude/CLAUDE.md       # 존재 확인
```

### R-3 검증 (Hook 강화 후)
```bash
# test: sk-fake1234567890 패턴이 포함된 파일 Write 시도 → 차단 확인
python -c "print('API_KEY = \"sk-test12345678901234567\"')" > /tmp/test_block.py
# tool_validator.py가 차단하는지 확인
```

---

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-02-26 | v1.0 | 최초 작성 | Context Specialization Strategy 검증 결과 (전략 A/B/C/D 판정) 반영. 실현 가능한 4개 대안 정의 |
