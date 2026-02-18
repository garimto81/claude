# Vercel Best Practice 통합 설계 분석 - PDCA Plan

**Version**: 1.1.0
**Created**: 2026-02-05
**Status**: ✅ COMPLETED (PDCA Check Phase 통과)

---

## 1. 개요

### 1.1 목표
`vercel-react-best-practices` 스킬(49개 규칙, 8개 카테고리)을 프로젝트 워크플로우에 효과적으로 통합

### 1.2 범위
- 스킬 자동 트리거 개선
- frontend-dev, code-reviewer 에이전트 연동 강화
- /check --react 옵션 검증
- 서브프로젝트 배포 전략 검토

### 1.3 복잡도 점수
**4/5** (Ralplan 실행 대상)
- 파일 범위: 1점 (다수 파일 수정)
- 아키텍처: 1점 (스킬 라우팅 패턴)
- 의존성: 0점 (기존 인프라)
- 모듈 영향: 1점 (스킬, 에이전트, 워크플로우)
- 사용자 명시: 1점 (ralplan 키워드)

---

## 2. 현재 상태 분석

### 2.1 스킬 상태

| 항목 | 상태 | 상세 |
|------|:----:|------|
| SKILL.md | ✅ OK | 159줄, auto_trigger: true |
| AGENTS.md | ✅ OK | 2411줄, 49개 규칙 |
| 키워드 | ⚠️ 부분 | 한글 일부, 영어 일부 |

### 2.2 에이전트 연동 상태

| 에이전트 | 연동 상태 | 문제점 |
|----------|:--------:|--------|
| frontend-dev | ⚠️ PARTIAL | Performance Guidelines 존재, 구체적 통합 메커니즘 부족 |
| code-reviewer | ❌ MISSING | React 성능 규칙 참조 없음 |

### 2.3 서브프로젝트 배포

| 항목 | 수치 |
|------|------|
| 총 서브프로젝트 | 12개 |
| 배포 완료 | 11개 |
| 누락 | 1개 (shorts-generator) |

---

## 3. 핵심 문제점

### 3.1 CRITICAL - code-reviewer 미연동
- **현상**: React 성능 규칙 참조 없음
- **영향**: PR 리뷰에서 waterfall, bundle size 이슈 누락
- **근거**: 87줄 전체에 React/Next.js 언급 없음

### 3.2 HIGH - frontend-dev 트리거 미흡
- **현상**: "자동 참조" 언급만, 구체적 메커니즘 없음
- **영향**: 명시적 `/check --react` 호출 필요
- **근거**: 90-109줄 Performance Guidelines 섹션

### 3.3 MEDIUM - shorts-generator 누락
- **현상**: 12개 중 1개 스킬 미배포
- **영향**: 해당 프로젝트 React 성능 검사 불가
- **근거**: 19개 .tsx 파일 존재, next.config.ts 존재

---

## 4. 개선 방안

### 4.1 code-reviewer 에이전트 React 규칙 추가

**파일**: `.claude/agents/code-reviewer.md`

```markdown
### 7. React/Next.js Performance (Important)
- Waterfalls: sequential await 감지 (→ Promise.all)
- Bundle Size: barrel file import 감지 (lucide-react, @mui 등)
- RSC Serialization: 과도한 props 전달 감지
- Re-render: stale closure, 불필요한 리렌더링

상세 규칙: `.claude/skills/vercel-react-best-practices/AGENTS.md`
```

### 4.2 frontend-dev 트리거 강화

**파일**: `.claude/agents/frontend-dev.md`

Performance Guidelines 섹션에 필수 적용 규칙 테이블 추가:

| 이슈 | 감지 패턴 | 즉시 수정 |
|------|----------|----------|
| Waterfall | `await A(); await B();` | `Promise.all([A(), B()])` |
| Barrel Import | `from 'lucide-react'` | Direct import |
| RSC Over-serialization | 50+ fields to client | Pick 필요 필드만 |

### 4.3 shorts-generator 스킬 배포

```powershell
# 심볼릭 링크 (권장)
mklink /D "C:\claude\shorts-generator\.claude\skills\vercel-react-best-practices" "C:\claude\.claude\skills\vercel-react-best-practices"

# 대안: 복사
xcopy /E /I "C:\claude\.claude\skills\vercel-react-best-practices" "C:\claude\shorts-generator\.claude\skills\vercel-react-best-practices"
```

### 4.4 스킬 키워드 확장

**파일**: `.claude/skills/vercel-react-best-practices/SKILL.md`

추가 키워드:
- `번들 크기` (한글)
- `async waterfall` (영어)
- `Promise.all` (영어)
- `barrel import` (영어)
- `dynamic import` (영어)

---

## 5. Acceptance Criteria

### AC-1: code-reviewer React 규칙 ✅
- [x] Section 7 "React/Next.js Performance" 존재 (line 60)
- [x] "sequential await" 문구 포함
- [x] AGENTS.md 경로 참조 (line 75)

### AC-2: frontend-dev 트리거 ✅
- [x] 필수 적용 규칙 테이블 존재 (4개 규칙)
- [x] "반드시 로드" 문구 포함 (line 90, 114)
- [x] AGENTS.md 경로 명시 (line 114, 121)

### AC-3: shorts-generator 배포 ✅
- [x] `.claude/skills/vercel-react-best-practices/` 디렉토리 존재
- [x] SKILL.md 접근 가능 (xcopy 방식 배포)

### AC-4: 키워드 확장 ✅
- [x] "번들 크기" 포함
- [x] "dynamic import" 포함 (+ async waterfall, Promise.all, barrel import, sequential await, stale closure)

### AC-5: /check --react 검증 ⏭️ (Out of Scope)
- [ ] 커맨드 인식 → 이미 존재 (check/SKILL.md line 299-348)
- [ ] CRITICAL 이슈 출력 → E2E 테스트 대상 (후속 작업)

---

## 6. 구현 우선순위

| Phase | 작업 | 예상 시간 |
|:-----:|------|----------|
| **1** | code-reviewer, frontend-dev 수정 | 25분 |
| **2** | shorts-generator 배포, 키워드 확장 | 10분 |
| **3** | 검증 | 20분 |

**총 예상**: 55분

---

## 7. 위험 및 완화

| 위험 | 완화 방안 |
|------|----------|
| 심볼릭 링크 권한 | xcopy 대안 사용 |
| 에이전트 동작 변경 | 기존 섹션 유지, 신규만 추가 |
| AGENTS.md 컨텍스트 소모 | Quick Reference 우선 로드 |

---

## 8. Ralplan 승인 정보

| 항목 | 값 |
|------|-----|
| **Iteration** | 1/5 |
| **Planner** | 계획 수립 완료 |
| **Architect** | 상담 불필요 |
| **Critic Verdict** | **OKAY** |

### Critic 피드백 요약

**Minor Issues (구현 시 추론 가능):**
1. Task 3.1 테스트 파일 명세 미흡 → 의도적 anti-pattern 파일 생성 필요
2. shorts-generator 필요성 근거 미흡 → 19개 .tsx 파일로 확인됨

---

## 9. 후속 작업 (Out of Scope)

- [ ] `/check --react` E2E 테스트 추가
- [ ] PR CI 통합
- [ ] 스킬 사용 빈도 메트릭
- [ ] AGENTS.md Quick Reference 분리

---

## 관련 문서

| 문서 | 경로 |
|------|------|
| 상세 계획 | `.omc/plans/vercel-best-practice-integration.md` |
| 스킬 정의 | `.claude/skills/vercel-react-best-practices/SKILL.md` |
| 49개 규칙 | `.claude/skills/vercel-react-best-practices/AGENTS.md` |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-05 | 초기 계획 수립 (Ralplan 승인) |
| 1.1.0 | 2026-02-05 | 구현 완료, AC 검증 통과 |
