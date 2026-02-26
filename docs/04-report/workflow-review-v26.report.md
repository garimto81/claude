# 워크플로우 종합 검토 보고서 v26

**작성일**: 2026-02-19
**검토 범위**: /auto PDCA 5-Phase 워크플로우 전체 (SKILL.md + REFERENCE.md + 에이전트 42개)
**분석 방법**: 3개 병렬 분석 — 외부 BP 리서치 (web-researcher-1, web-researcher-2) + 내부 약점 분석 (internal-analyst)
**총 발견**: 17건 내부 이슈 + 8개 외부 개선 기회

---

## 1. Executive Summary

이번 v26 검토는 내부 코드 감사와 외부 AI 개발 베스트 프랙티스 리서치를 병행한 첫 번째 종합 검토다.

### 주요 수치

| 카테고리 | 건수 | 설명 |
|----------|------|------|
| CRITICAL | 3 | 즉시 수정 필수 — 런타임 오류 유발 가능 |
| HIGH | 9 | 계획적 수정 필요 — 비효율 및 실패 위험 |
| MEDIUM | 5 | 개선 기회 — 장기 아키텍처 부채 |
| 외부 BP 대비 개선 기회 | 8 | 업계 표준 대비 미구현 패턴 |

### 외부 벤치마크 비교 핵심 메시지

- **PDCA 구조의 유효성 확인**: 구조화 세션이 비구조 세션 대비 토큰 13% 절약, 코드 35% 감소 (InfoQ)
- **Anthropic Context Engineering 4패턴**: Write/Select/Compress/Isolate 중 현재 Compress(sub-agent)만 부분 구현
- **Hallucination 방어 부재**: AI 생성 코드 29-45%가 보안 취약점 포함 (arxiv), 패키지 검증 로직 없음
- **Cross-model Verification 미구현**: Multi-model consensus가 false positive 60% 감소 효과 (CodeAnt AI), 현재 동일 모델 계열 사용

---

## 2. 현재 워크플로우 강점

v26 검토를 시작하기 전, 현재 워크플로우의 검증된 강점을 먼저 인정한다.

### 2-1. PDCA 구조 자체의 효과
InfoQ의 AI 코드 생성 PDCA 프레임워크 연구에 따르면, PDCA 구조 세션이 비구조 세션 대비 13% 토큰 절약, 35% 적은 코드를 생성하며, 비구조 세션의 경우 "완료 선언 후" 디버깅에 80% 시간을 소비하는 것으로 나타났다. 현재 /auto의 5-Phase 설계는 이 연구 결과와 일치한다.

### 2-2. Agent Teams Context 분리
Anthropic 공식 Context Engineering 가이드의 "Isolate" 패턴(경량 식별자로 context 분리)을 Agent Teams가 구현하고 있다. Phase별 전담 에이전트 분리로 Lead context 보호가 이루어진다.

### 2-3. 3-tier 복잡도 분기
AWS AI-DLC의 "복잡도에 맞게 각 단계의 폭과 깊이를 조정" 원칙과 LIGHT/STANDARD/HEAVY 분기가 정확히 일치한다. Opus 과다 사용 60% 절감 효과가 실증되었다.

### 2-4. Domain-Smart Fix Routing
Phase 3에서 5개 도메인(api/db/auth/ui/perf)을 전문 에이전트로 라우팅하는 설계는 업계 표준 "specialized agent routing" 패턴과 일치한다.

### 2-5. Phase 4↔5 루프 가드 (부분적 Circuit Breaker)
phase4_reentry max 3, cumulative max 5 제한이 구현되어 있다. 완전하지는 않지만 Galileo의 Multi-Agent 실패 복구 패턴인 Circuit Breaker의 기초가 존재한다.

---

## 3. CRITICAL 발견 (즉시 수정 필요)

### CRITICAL-1: gap-checker subagent_type 불일치

**문제**
REFERENCE.md:904에서 gap-checker를 `architect` subagent_type으로 spawn한다. 그러나 architect는 READ-ONLY 에이전트다 — 파일 저장 불가. REFERENCE.md:934에서 `code-reviewer`로 정정하지만, 904줄이 우선 실행되어 갭 분석 결과 저장에 실패한다.

**근거**
- `C:/claude/.claude/agents/architect.md`: READ-ONLY 정의 명시
- SKILL.md v22.1 교훈 섹션: "architect는 READ-ONLY — 파일 생성 필요한 Phase에서 사용 금지"
- v25 검토에서 이미 수정했으나 REFERENCE.md:904가 재발

**영향**
Phase 4 갭 분석 결과가 저장되지 않아 REFERENCE.md:934 이후 로직이 빈 데이터로 동작. 갭 미탐지 → 불완전한 코드가 완료 처리됨.

**수정안**
```
REFERENCE.md:904: subagent_type="architect" → subagent_type="gap-detector"
```

gap-detector.md 에이전트가 별도 존재하며 쓰기 가능. 또는 gap-checker 역할 전체를 code-reviewer로 일원화.

---

### CRITICAL-2: qa-tester 에이전트 정의와 REFERENCE.md 기대 불일치

**문제**
qa-tester.md는 "tmux 전문가"로 정의되어 있으며 QA_PASSED/QA_FAILED 형식을 지원하지 않는다. 그러나 REFERENCE.md는 qa-tester에게 lint/test/build/typecheck 4종 실행과 QA_PASSED/QA_FAILED 형식 반환을 기대한다.

**근거**
- `C:/claude/.claude/agents/qa-tester.md`: tmux 기반 QA 정의, 형식 불일치
- REFERENCE.md Phase 4 QA 섹션: QA_PASSED/QA_FAILED 명시

**영향**
Phase 4 QA 사이클 전체가 오동작. qa-tester가 올바른 형식으로 결과를 반환하지 않아 Lead가 QA 결과를 파싱 실패 → Phase 4 무한 루프 또는 잘못된 Phase 5 진입.

**수정안**
qa-tester.md를 재작성하여:
1. tmux 의존성 제거
2. lint(ruff check) + test(pytest) + build + typecheck 4종 직접 실행
3. `QA_PASSED: {details}` / `QA_FAILED: {failures}` 형식 출력 추가

---

### CRITICAL-3: SKILL.md Phase 5 writer model=haiku 고정

**문제**
SKILL.md Phase 5에서 writer를 항상 `model=haiku`로 호출한다. REFERENCE.md는 모드별 분기를 명시한다 — LIGHT=haiku, STANDARD=sonnet, HEAVY=sonnet. HEAVY 모드 보고서가 haiku로 작성된다.

**근거**
- SKILL.md Phase 5 라인: `model="haiku"` 고정
- REFERENCE.md Phase 5: "LIGHT→haiku, STANDARD/HEAVY→sonnet"
- v23.0 설계: "Phase 5 Writer: STANDARD/HEAVY sonnet → haiku" — 이 표현은 "sonnet으로 실행했던 것을 haiku로 변경"이 아니라 "STANDARD/HEAVY는 sonnet, LIGHT는 haiku" 의미였음

**영향**
HEAVY 모드(가장 복잡한 작업)의 최종 보고서가 가장 저성능 모델로 작성됨. 품질 저하 및 REFERENCE.md 설계 의도 위반.

**수정안**
SKILL.md Phase 5:
```
complexity == LIGHT → writer model=haiku
complexity == STANDARD|HEAVY → writer model=sonnet
```

---

## 4. HIGH 발견 (계획적 수정)

### HIGH-1: Phase 4↔5 루프 가드 카운터가 Lead 메모리에만 존재

**문제**: phase4_reentry, cumulative 카운터가 Lead의 in-context 메모리에만 있어 Context Compaction 발생 시 소실된다.

**영향**: Context Compaction 후 카운터가 0으로 리셋 → 루프 가드 우회 → 무한 루프 가능. MEMORY.md에 이미 "Context Compaction 시 팀 상태 소실" 문제가 기록되어 있으며 동일 메커니즘.

**수정안**: `.claude/state/phase4-counter.json` 파일에 카운터 외부화. 각 Phase 4 진입/종료 시 파일 업데이트. 다음 진입 시 파일에서 읽어 복원.

---

### HIGH-2: Phase 1 Explore x2가 LIGHT에서도 항상 실행

**문제**: LIGHT 모드에서도 Phase 1.0 Explore를 2회 실행한다. LIGHT는 단순 작업(복잡도 0-1)이므로 단일 Explore로 충분하다.

**영향**: LIGHT 모드의 불필요한 overhead. AWS AI-DLC의 "복잡도에 맞게 깊이 조정" 원칙에 위배.

**수정안**: LIGHT에서 Explore 1회만 실행. STANDARD에서 2회, HEAVY에서 상세 Explore 유지.

---

### HIGH-3: Phase 4.2 verifier/gap-checker/quality-checker 순차 실행

**문제**: Phase 4.2에서 verifier→gap-checker→quality-checker가 순차 실행된다. 세 에이전트는 독립적이다.

**영향**: 3개 에이전트가 순차 실행되면 실제 소요 시간이 3배. 병렬화 시 최장 에이전트 시간만 소요.

**수정안**: Agent Teams 패턴으로 3개 병렬 spawn:
```
TeamCreate → Task(verifier) + Task(gap-checker) + Task(quality-checker)
모든 완료 대기 → 결과 통합 → TeamDelete
```

---

### HIGH-4: Phase 1 HEAVY 5회 APPROVE 강제 시 사용자 알림 없음

**문제**: HEAVY 모드 Planner-Critic 루프에서 5회 반복 후 강제 APPROVE 처리되지만 사용자에게 알림이 없다.

**영향**: 불완전한 계획이 자동 승인되어 Phase 3 구현에 진입. 사용자는 계획 품질 저하를 인지하지 못함.

**수정안**: 5회 강제 APPROVE 시 사용자에게 명시적 알림:
```
"경고: 계획 검토 5회 완료 후 자동 승인됨. 계획 품질이 최적이 아닐 수 있습니다. 계속할까요? [Y/n]"
```

---

### HIGH-5: HEAVY 병렬 impl-manager 공유 파일 충돌 감지 없음

**문제**: HEAVY 모드에서 여러 impl-manager를 병렬 실행할 때 공유 파일(types.ts, utils.py, config.json 등)에 동시 쓰기가 발생할 수 있다.

**영향**: race condition → 파일 손상 또는 한 에이전트의 변경이 다른 에이전트에게 덮어쓰임. 미탐지 시 빌드 오류 또는 런타임 버그.

**수정안**: 병렬 impl-manager 실행 전 파일 충돌 분석 수행:
1. 각 impl-manager의 예상 변경 파일 목록 수집
2. 교집합 감지 → 충돌 파일은 순차 처리로 전환
3. 비충돌 파일만 병렬 처리

---

### HIGH-6: Architect 2회 REJECT 후 Phase 4 진입 처리 불명확

**문제**: Phase 3에서 Architect가 2회 연속 REJECT 시 Phase 4 재진입하는 로직이 SKILL.md/REFERENCE.md에 명확히 정의되어 있지 않다. --interactive 연계도 없다.

**영향**: Architect 2회 REJECT 상황에서 Lead가 임의 판단으로 진행 → 일관성 없는 동작.

**수정안**: REFERENCE.md에 명시:
```
Architect 2회 REJECT → Phase 4 재진입 (QA 사이클로 처리)
--interactive 모드: 사용자에게 수정 방향 선택 제시
자동 모드: Phase 4 standard 경로로 자동 진입, Phase 4 카운터에 포함
```

---

### HIGH-7: pdca-status.json과 Agent Teams 간 Resume 동기화 부재

**문제**: Context Compaction 또는 세션 중단 후 재개 시 pdca-status.json의 Phase 정보와 실제 Agent Teams 상태가 동기화되지 않는다.

**영향**: 중단된 세션 재개 시 orphan 에이전트 생성 또는 동일 Phase 중복 실행. MEMORY.md에 기록된 "고아 팀 7개 수동 정리" 사례의 근본 원인 중 하나.

**수정안**: Phase 전환 시 pdca-status.json에 현재 활성 team_name 및 teammate 목록 기록. 세션 시작 시 pdca-status.json 확인 → 고아 팀 자동 정리 로직 추가.

---

### HIGH-8: 복잡도 판단 5번째 조건 `ralplan` 데드 조건

**문제**: 복잡도 점수 계산에서 5번째 조건으로 `ralplan` 키워드가 참조된다. ralplan은 OMC 전용 에이전트로 2026-02-18에 제거되었다.

**영향**: 복잡도 최대 점수가 실질적으로 4점(5번째 조건 항상 false). HEAVY 모드 도달이 의도보다 어려워짐. 조건 분기 로직 오염.

**수정안**: `ralplan` 조건 제거 후 현재 워크플로우에 맞는 조건으로 대체:
```
5번째 조건: 영향 파일 10개 이상 OR Phase 3에서 5개+ 에이전트 필요 예상
```

---

### HIGH-9: 새 에이전트 추가 시 변경 범위 4개 파일 분산

**문제**: 에이전트를 추가할 때 4개 파일을 동시에 수정해야 한다: (1) agents/{name}.md, (2) SKILL.md frontmatter, (3) SKILL.md routing, (4) REFERENCE.md routing.

**영향**: 변경 범위 분산 → 하나라도 누락 시 에이전트 미동작. v25 검토에서 발견된 "존재하지 않는 에이전트명" 문제의 구조적 원인.

**수정안**: SKILL.md에 에이전트 레지스트리 단일 진실 소스(Single Source of Truth) 도입:
```yaml
agents:
  - name: gap-detector
    model: sonnet
    domains: [gap, verification]
    phases: [4]
```
빌드 시 frontmatter와 routing 자동 생성. 단기 대안: 에이전트 추가 체크리스트 문서화.

---

## 5. MEDIUM 발견 (개선 기회)

### MEDIUM-1: 복잡도 자동 승격이 사후 감지

**문제**: LIGHT→STANDARD 자동 승격이 Phase 3 구현 중 감지된다 (빌드 실패 2회 또는 영향 파일 5개+). 이미 작업이 시작된 후 승격이 일어난다.

**개선안**: Phase 0 복잡도 분석 단계에서 영향 파일 수 사전 예측. 5개 이상 예상 시 사전 승격 → Phase 1부터 더 깊은 계획 실행.

---

### MEDIUM-2: 메트릭/로깅 완전 부재

**문제**: 각 Phase 소요 시간, 에이전트 호출 횟수, 토큰 사용량 등 어떤 메트릭도 수집되지 않는다.

**개선안**: `.claude/logs/auto-metrics.jsonl`에 Phase별 시작/종료 시간, 에이전트 호출, 결과(APPROVE/REJECT) 기록. 이후 /audit 커맨드에서 활용 가능.

---

### MEDIUM-3: 롤백 메커니즘 부재

**문제**: Phase 3 구현 실패 시 git reset --hard로 수동 롤백해야 한다. 자동화된 복구 경로가 없다.

**개선안**: Phase 3 시작 전 git stash 또는 임시 브랜치 생성. 빌드/테스트 실패 시 자동 롤백 + 실패 원인 보존. Saga Pattern의 compensating transaction 개념 적용.

---

### MEDIUM-4: Domain Routing 테이블 SKILL.md↔REFERENCE.md 미세 차이

**문제**: Domain Routing이 SKILL.md와 REFERENCE.md 두 곳에 정의되어 있으며 일부 항목이 불일치한다 (예: performance → perf 약어 차이, ui vs frontend).

**개선안**: REFERENCE.md를 단일 진실 소스로 지정. SKILL.md에서는 "REFERENCE.md Phase 3.3 참조"로 단순화.

---

### MEDIUM-5: Phase 2 DESIGN 에이전트 프로젝트 유형별 미분기

**문제**: React/Next.js 프로젝트에서도 Phase 2에서 designer 에이전트가 아닌 executor를 사용한다. v24.0에서 `is_react_project` 자동 감지를 설계했지만 미구현 상태다.

**개선안**: Phase 0에서 `next.config.*` 또는 package.json의 `"react"` 의존성 감지 → `is_react_project=true` 설정 → Phase 2에서 designer 에이전트로 분기.

---

## 6. 외부 베스트 프랙티스 대비 개선 기회

웹 리서치(web-researcher-1, web-researcher-2)에서 확인된 업계 표준과의 현재 상태 비교.

| 카테고리 | 외부 트렌드 | 현재 상태 | 개선안 | 우선순위 |
|----------|-------------|-----------|--------|----------|
| **Context Engineering** | Anthropic 4패턴: Write/Select/Compress/Isolate | Compress(sub-agent)만 부분 구현 | `--note` 옵션으로 Write 패턴 구현. Phase Act에서 MEMORY.md 자동 업데이트 | P1 |
| **Phase별 자동 커밋** | Saga Pattern: Phase 경계마다 체크포인트 커밋 (Addy Osmani 권고) | 수동 커밋만 | Phase 0 시작, Phase 3 완료, Phase 4 통과 후 자동 커밋 | P2 |
| **Multi-model Consensus** | 3 LLM 병렬 → 2+ 동의 시 이슈 표시 → false positive 60% 감소 (CodeAnt AI) | 동일 모델 계열만 사용 | Phase 4 QA에서 Architect Gate를 다른 모델로 교차 검증 (예: opus architect vs sonnet architect) | P3 |
| **LIGHT 공격적 단순화** | AWS AI-DLC: 단순 작업은 단계 대폭 축소 | LIGHT도 Phase 1-5 완전 실행 | LIGHT에서 Phase 2(설계 단계) 스킵, Phase 1→3 직행 허용 | P2 |
| **Phase Act 자동 회고** | 성공 패턴 자동 저장 → MEMORY.md 업데이트 | 수동 업데이트만 | Phase 5 완료 시 성공한 도메인/에이전트 조합을 MEMORY.md에 자동 기록 | P2 |
| **Model Version Pinning** | 프로덕션 에이전트 실패 40%가 model drift 원인 | 에이전트별 model 파라미터 명시 (부분) | 각 에이전트 frontmatter에 정확한 model ID 고정 (claude-sonnet-4-6, not sonnet) | P1 |
| **Hallucination 방어** | AI 생성 코드 29-45% 보안 취약점 (arxiv), Slopsquatting 공격 (존재하지 않는 패키지명) | 검증 로직 없음 | Phase 3 완료 후 `pip install --dry-run` / `npm install --dry-run`으로 패키지 존재 검증 | P1 |
| **Circuit Breaker 완전화** | Exponential backoff + jitter로 에이전트 재시도 (Galileo) | max 횟수 제한만 (부분) | 동일 실패 3회 연속 시 exponential backoff (1s, 2s, 4s) 후 재시도, 5회 후 Circuit Open | P2 |

### 상세: Context Engineering 4패턴 현재 상태

Anthropic Engineering (2026) 공식 가이드의 4패턴과 현재 구현:

1. **Write** (외부 저장): `--note` 옵션 설계됨(v24.0) → **미구현**. Phase Act 회고 자동화 필요.
2. **Select** (동적 풀링): REFERENCE.md 동적 섹션 선택 → **부분 구현** (정적 전체 로드).
3. **Compress** (sub-agent 압축): Agent Teams context 분리 → **구현됨**.
4. **Isolate** (경량 식별자): team_name 기반 격리 → **구현됨**.

### 상세: Hallucination 방어 필요성

arXiv 연구(SOK Hallucinations in AI-Assisted Development)에 따르면:
- AI 생성 코드의 29-45%가 보안 취약점 포함
- 20% 확률로 존재하지 않는 패키지 추천 (Slopsquatting 공격 경로)
- **Slopsquatting**: 공격자가 AI가 hallucinate하는 패키지명을 실제 PyPI/npm에 등록하여 악성 코드 배포

Phase 3 executor 완료 후 의존성 검증 단계 추가가 필수적이다.

---

## 7. 수정 우선순위 로드맵

### P0 — 즉시 수정 (이번 세션 내)

| # | 항목 | 파일 | 수정 내용 |
|---|------|------|---------|
| 1 | CRITICAL-1 | REFERENCE.md:904 | `architect` → `gap-detector` |
| 2 | CRITICAL-2 | `.claude/agents/qa-tester.md` | tmux 제거, QA_PASSED/QA_FAILED 형식 추가 |
| 3 | CRITICAL-3 | SKILL.md Phase 5 | `model=haiku` → 복잡도 분기 |

### P1 — 1주 내

| # | 항목 | 설명 |
|---|------|------|
| 4 | HIGH-1 | 루프 가드 카운터 외부화 (`.claude/state/`) |
| 5 | HIGH-8 | `ralplan` 데드 조건 제거 및 교체 |
| 6 | 외부 BP: Model Version Pinning | 에이전트 frontmatter에 정확한 model ID 고정 |
| 7 | 외부 BP: Hallucination 방어 | Phase 3 후 패키지 존재 검증 |
| 8 | 외부 BP: Context Engineering Write 패턴 | `--note` 옵션 구현 |

### P2 — 2주 내

| # | 항목 | 설명 |
|---|------|------|
| 9 | HIGH-2 | LIGHT Explore 1회 단순화 |
| 10 | HIGH-3 | Phase 4.2 병렬화 (verifier/gap-checker/quality-checker) |
| 11 | HIGH-7 | pdca-status.json + Agent Teams 동기화 |
| 12 | 외부 BP: Phase별 자동 커밋 | Saga Pattern 체크포인트 |
| 13 | 외부 BP: LIGHT 공격적 단순화 | Phase 2 스킵 허용 |
| 14 | 외부 BP: Phase Act 자동 회고 | MEMORY.md 자동 업데이트 |
| 15 | 외부 BP: Circuit Breaker 완전화 | exponential backoff 추가 |

### P3 — 장기 (아키텍처 개선)

| # | 항목 | 설명 |
|---|------|------|
| 16 | HIGH-4 | Phase 1 강제 APPROVE 사용자 알림 |
| 17 | HIGH-5 | HEAVY 병렬 impl-manager 충돌 감지 |
| 18 | HIGH-6 | Architect 2회 REJECT 처리 명확화 |
| 19 | HIGH-9 | 에이전트 레지스트리 단일 진실 소스 |
| 20 | MEDIUM-1~5 | 복잡도 사전 감지, 메트릭, 롤백, Domain 일원화, React 분기 |
| 21 | 외부 BP: Multi-model Consensus | cross-model 교차 검증 |

---

## 8. MEMORY.md 정정 사항

web-researcher-2의 분석에서 MEMORY.md의 잘못된 기록이 확인되었다.

### 정정 필요 항목

**현재 MEMORY.md 기록 (잘못된 내용)**:
```
- `teammateMode: "in-process"` → settings.json 스키마에 없는 필드로 확인.
```

**정정 내용**:
`teammateMode`는 Claude Code 공식 Agent Teams 문서에 존재하는 유효 필드다. 다만 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수가 Agent Teams 자체를 활성화하는 것이고, `teammateMode`는 그 내부 동작 방식을 제어한다. "스키마에 없는 필드"라는 기록은 버전 시점의 오류이거나 확인 오류일 가능성이 있다.

**권장 조치**: settings.json에서 `teammateMode` 필드 직접 확인 후 MEMORY.md 갱신.

---

## 9. 출처

### 외부 리서치 소스 (web-researcher-1)
- Addy Osmani: "My LLM coding workflow going into 2026" (2026)
- InfoQ: "PDCA Framework for AI Code Generation" (2025)
- Anthropic Engineering: "Effective context engineering for AI agents" (2025)
- Galileo: "Multi-Agent AI Failure Recovery" (2025)

### 외부 리서치 소스 (web-researcher-2)
- Claude Code 공식 Agent Teams 문서 (anthropic.com)
- GitHub Issues: #23620 (팀 상태 소실), #26317 (compaction 실패), #21961, #23063
- CodeAnt AI: "Multi-model consensus in code review" (2025)
- CodeRabbit, Datadog: Code review accuracy reports
- ttoss.dev: "Mastering Context Window in Agentic Development" (2025)
- arXiv: "SOK: Hallucinations in AI-Assisted Software Development" (2025)
- AWS AI-DLC: Agentic Development complexity scaling

### 내부 분석 소스 (internal-analyst)
- `C:/claude/.claude/skills/auto/SKILL.md` (v22.2)
- `C:/claude/.claude/references/REFERENCE.md`
- `C:/claude/.claude/agents/` (42개 에이전트 정의)
- 이전 보고서: workflow-review-v25.report.md, workflow-review-precision.report.md

---

*보고서 종료 — 워크플로우 검토 v26 | 작성: writer 에이전트 | 2026-02-19*
