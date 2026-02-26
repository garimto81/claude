# Context Hierarchy (4-Level)

> bkit Context Engineering FR-01 기반 OMC 적용

## 계층 구조

```
L4: Session (인메모리, 런타임) ← 최고 우선순위
L3: Project (./CLAUDE.md, .claude/rules/)
L2: User (~/.claude/CLAUDE.md)
L1: Plugin (OMC, bkit 플러그인 설정) ← 최저 우선순위
```

## 우선순위 규칙

1. 상위 레벨이 하위 레벨을 override
2. 동일 레벨 내에서는 나중에 로드된 것이 우선
3. 충돌 발생 시 사용자에게 질문 (CLAUDE.md 핵심 원칙)

## 레벨별 설정 범위

| 레벨 | 소스 | 범위 | 예시 |
|:----:|------|------|------|
| L1 | OMC/bkit 플러그인 | 전역 기본값 | 에이전트 티어, 모델 라우팅 |
| L2 | ~/.claude/CLAUDE.md | 사용자 전역 | 위임 규칙, 스킬 라우팅 |
| L3 | ./CLAUDE.md, .claude/rules/ | 프로젝트 | 빌드 명령, TDD 규칙, 경로 규칙 |
| L4 | /auto 실행 중 동적 주입 | 현재 세션 | Phase 상태, 복잡도 점수, 팀 구성 |

## 충돌 해결

하위 레벨(L1)에서 "API 키 사용 허용"이고 상위 레벨(L3)에서 "API 키 금지"이면 → L3 우선 → API 키 금지.

## 적용 시점

- SessionStart: L1→L2→L3 순서로 로드
- /auto Phase 0: L4 동적 컨텍스트 생성
- PreCompact: L4 상태를 파일로 직렬화 (compact_summary.md)
- SessionRestore: 직렬화된 L4를 복원
