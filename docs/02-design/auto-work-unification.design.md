# /auto + /work 통합 설계

**Version**: 1.0.0 | **Date**: 2026-02-15 | **Status**: APPROVED
**Plan**: `docs/01-plan/auto-work-unification.plan.md`

---

## 1. 핵심 변경 요약

- `/auto` v18.0 → v19.0: Phase 1 확장 (Step 1.0, 1.3), Phase 4 확장 (Step 4.3, 4.4), 복잡도 3분기 (LIGHT/STANDARD/HEAVY)
- `/work` → `/auto` 리다이렉트 stub 전환
- 총 16개 파일 변경 (핵심 6 + 참조 4 + 교차 참조 6)

## 2. 복잡도 분기

| 복잡도 | 모드 | Phase 2 | Phase 3 | Phase 4 | 예상 토큰 |
|:------:|------|---------|---------|---------|:---------:|
| 0-1 | LIGHT | 스킵 | executor(sonnet) | UltraQA only | ~5,000t |
| 2-3 | STANDARD | architect(sonnet) | Ralph(sonnet) | UltraQA + 이중검증 | ~12,000t |
| 4-5 | HEAVY | architect(opus) | Ralph(opus) | UltraQA + 이중검증 + E2E | ~20,000t |

자동 승격: LIGHT에서 빌드 실패 2회 / UltraQA 3사이클 / 영향 파일 5개+ → STANDARD

## 3. 구현 대상 파일

| # | 파일 | 변경 |
|:-:|------|------|
| 1 | `.claude/skills/auto/SKILL.md` | Phase 0/1/2/3/4 확장, 복잡도 테이블 |
| 2 | `.claude/skills/auto/REFERENCE.md` | Step 1.0/1.3/4.3/4.4 상세, 분기 상세 |
| 3 | `.claude/commands/auto.md` | 옵션 4개 추가, /work 레거시 매핑 |
| 4 | `.claude/commands/work.md` | stub 전환 |
| 5 | `.claude/references/skill-causality-graph.md` | Phase 확장 반영 |
| 6 | `.claude/rules/08-skill-routing.md` | /work deprecated 추가 |
| 7 | `CLAUDE.md` | /work → /auto 변경 |
| 8 | `docs/COMMAND_REFERENCE.md` | /work stub, /auto 확장 |

## 4. 데이터 흐름

```
Phase 0 → options
Phase 1 → analysis_result, complexity_score, mode, plan_doc, issue_number
Phase 2 → design_doc (STANDARD/HEAVY)
Phase 3 → implementation (executor or Ralph)
Phase 4 → ultraqa_result, gap_score, e2e_result, tdd_report
Phase 5 → report_doc or Phase 4 재실행
```
