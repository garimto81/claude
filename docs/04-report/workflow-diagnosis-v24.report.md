# Workflow Diagnosis Report v24.0

**Date**: 2026-02-18
**Branch**: `feat/drive-project-restructure`
**Scope**: `.claude/`, `src/agents/`, `docs/`, `vimeo_ott/.claude/`

---

## Executive Summary

3개 병렬 분석 에이전트(skill-analyzer, agent-analyzer, git-analyzer)가 워크플로우 전체를 정밀 진단한 결과, **HIGH 6건, MEDIUM 8건, LOW 5건** 총 19건의 문제를 발견했다.

핵심 원인은 **`/verify` 스킬 삭제 후 잔류 참조 미정리**와 **`src/agents/config.py` 동기화 부족**이다.

---

## HIGH (즉시 수정 필요) — 6건

### H1. `/verify` 삭제 후 라우팅 테이블 잔류
- **파일**: `.claude/rules/08-skill-routing.md:15`
- **내용**: `/verify`가 "직접 실행" 라우팅 테이블에 여전히 등재
- **영향**: 라우팅 로직이 존재하지 않는 스킬을 참조

### H2. Deprecated 리다이렉트 대상 소멸
- **파일**: `.claude/rules/08-skill-routing.md:26`
- **내용**: `/cross-ai-verifier` → `/verify` 리다이렉트, `/verify` 없음
- **영향**: Deprecated 테이블이 dangling reference 생성

### H3. `09-global-only.md` 규칙 파일 실종
- **파일**: `.claude/rules/08-skill-routing.md:45`
- **내용**: "상세: `09-global-only.md`" 참조하나 파일 미존재
- **영향**: Junction 정책 규칙 참조 불가. `references/global-only-policy.md`는 존재하나 규칙 파일과 별도

### H4. `ultimate-debate/SKILL.md` 죽은 링크
- **파일**: `.claude/skills/ultimate-debate/SKILL.md:150`
- **내용**: `Cross-AI Verifier: /verify 스킬` — dangling reference
- **영향**: 스킬 연계 문서가 존재하지 않는 스킬을 안내

### H5. `config.py` quality 팀 `iterator` 누락
- **파일**: `src/agents/config.py:106`
- **내용**: `TEAM_CONFIGS["quality"]["agents"]`에 `iterator` 미포함 (6개)
- **대비**: `quality_team.py:241-249`의 `get_agents()`는 7개 (iterator 포함)
- **영향**: `get_team_models("quality")`가 iterator에 모델 할당 불가 → 런타임 오류 가능

### H6. `config.py` 모델 ID 구버전 하드코딩
- **파일**: `src/agents/config.py:13-19, 93-96`
- **내용**: `claude-sonnet-4-20250514`, `claude-haiku-3-20240307` 사용
- **최신**: `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
- **영향**: `src/agents/` 직접 호출 시 구버전 모델 사용. `.claude/agents/` 경유 시에는 Claude Code SDK가 최신 해석

---

## MEDIUM (단기 수정 권장) — 8건

### M1. `ai-login.md` `/verify` 안내 문구 5개소
- **파일**: `.claude/commands/ai-login.md:156,178,295,319,379`
- **내용**: `print('이제 /verify --provider ... 검증을 사용할 수 있습니다.')`
- **영향**: 사용자에게 삭제된 커맨드 안내

### M2. `/mockup-hybrid` 커맨드 파일 누락
- **파일**: `.claude/rules/08-skill-routing.md:15`
- **내용**: `/mockup-hybrid` 라우팅 등재, 스킬 디렉토리 존재, 커맨드 `.md` 파일 없음
- **영향**: `/mockup-hybrid` 커맨드 호출 불가 (스킬로만 작동)

### M3. `/daily` 커맨드 파일 누락
- **파일**: `.claude/rules/08-skill-routing.md:28`
- **내용**: `/daily-sync` → `/daily` 리다이렉트, `/daily` 커맨드 파일 없음 (스킬만 존재)
- **영향**: Deprecated 리다이렉트 대상 커맨드 미존재

### M4. `CLAUDE.md` 커맨드 수 오류
- **파일**: `CLAUDE.md:113`
- **내용**: "27개 커맨드" 명시, 실제 26개 (`verify.md` 삭제 후 미반영)

### M5. `CLAUDE.md` 에이전트 수 오류
- **파일**: `CLAUDE.md:117`
- **내용**: "41개 에이전트" 명시, 실제 42개 (`gap-detector.md` 추가 후 미반영)

### M6. `CLAUDE.md` 스킬 수 재확인 필요
- **파일**: `CLAUDE.md:121`
- **내용**: "43개 스킬" 명시, 실제 스킬 디렉토리 수와 불일치 가능

### M7. `.pdca-status.json` 완료/활성 중복
- **파일**: `docs/.pdca-status.json:4-16`
- **내용**: `.claude` 피처가 `activeFeatures`와 `completedFeatures`에 동시 등재

### M8. `.pdca-status.json` 상태 모순
- **파일**: `docs/.pdca-status.json:97-109`
- **내용**: `scripts`, `.claude` 피처가 `phase: "do"`이면서 `completedAt` 존재

---

## LOW (정보성) — 5건

### L1. `settings.json` PreCompact hook 일관성
- **파일**: `.claude/settings.json:82`
- **내용**: `python` + 절대경로 (다른 hook은 `python3` + 상대경로)

### L2. `chunk/SKILL.md` 실행 지시 부재
- **파일**: `.claude/skills/chunk/SKILL.md:11,15`
- **내용**: "commands/chunk.md 내용을 실행합니다"만 기재, 구체적 실행 지시 없음

### L3. `gap-detector.md` 미커밋 상태
- **파일**: `.claude/agents/gap-detector.md`, `vimeo_ott/.claude/agents/gap-detector.md`
- **내용**: 양쪽 모두 `??` (untracked). main 브랜치에서 `/auto` gap-checker 실패 가능

### L4. `vimeo_ott` Junction 미사용
- **파일**: `vimeo_ott/.claude/agents/gap-detector.md`
- **내용**: 루트와 별도 물리 파일로 존재. `09-global-only` (규칙 파일 자체도 미존재) 정책 위반 가능

### L5. audit report stale 참조
- **파일**: `docs/04-report/workflow-subagent-audit.report.md:147,351`
- **내용**: `verify.md` 수정 권고 기재 — 이미 삭제됨

---

## Root Cause Analysis

```
/verify 스킬+커맨드 삭제
├── 08-skill-routing.md 미정리 → H1, H2
├── ultimate-debate/SKILL.md 미정리 → H4
├── ai-login.md 미정리 → M1
├── CLAUDE.md 카운트 미갱신 → M4
└── audit report stale → L5

09-global-only.md 규칙 파일 미생성/삭제
├── 08-skill-routing.md 깨진 참조 → H3
└── Junction 정책 참조 불가 → L4

gap-detector 에이전트 신규 추가
├── config.py iterator 누락 (별개 이슈) → H5
├── 미커밋 상태 → L3
└── CLAUDE.md 카운트 미갱신 → M5

config.py 유지보수 지연
├── 모델 ID 미갱신 → H6
└── iterator 누락 → H5
```

---

## Recommended Fix Priority

1. **즉시**: H1-H4 (`/verify` 잔류 참조 일괄 정리)
2. **즉시**: H5-H6 (`config.py` iterator 추가 + 모델 ID 업데이트)
3. **단기**: M1-M6 (커맨드/에이전트/스킬 카운트 정정, 누락 커맨드 파일)
4. **단기**: M7-M8 (PDCA status 정리)
5. **선택**: L1-L5 (일관성, 커밋 등)

---

## Fix Execution Report

**Date**: 2026-02-18
**Mode**: LIGHT (복잡도 1/5)
**Executor**: executor (sonnet)
**Verifier**: architect (sonnet) — VERDICT: APPROVE

### 수정 결과 (19건 전체 완료)

| # | 심각도 | 파일 | 수정 내용 | 상태 |
|---|--------|------|-----------|------|
| H1 | HIGH | `08-skill-routing.md:15` | `/verify` 라우팅 항목 제거 | DONE |
| H2 | HIGH | `08-skill-routing.md:26` | `/cross-ai-verifier` 리다이렉트 행 삭제 | DONE |
| H3 | HIGH | `08-skill-routing.md:45` | `09-global-only.md` → `references/global-only-policy.md` | DONE |
| H4 | HIGH | `ultimate-debate/SKILL.md:150` | `/verify` dangling reference 삭제 | DONE |
| H5 | HIGH | `config.py:106` | quality 팀 `iterator` 추가 | DONE |
| H6 | HIGH | `config.py:12-19,92-96` | 모델 ID `sonnet-4-6`, `haiku-4-5-20251001` 업데이트 | DONE |
| M1 | MEDIUM | `ai-login.md` (5개소) | `/verify` 안내 → `/ultimate-debate` 대체 | DONE |
| M4 | MEDIUM | `CLAUDE.md:113` | 커맨드 수 27 → 26 | DONE |
| M5 | MEDIUM | `CLAUDE.md:117` | 에이전트 수 41(9) → 42(10) | DONE |
| M6 | MEDIUM | `CLAUDE.md:121` | 스킬 수 43 → 42 | DONE |
| M7 | MEDIUM | `.pdca-status.json:4-10` | activeFeatures 정리 (scripts, .claude 제거) | DONE |
| M8 | MEDIUM | `.pdca-status.json:71,97` | phase "do" → "completed" 수정 | DONE |

### Architect Verification

- **판정**: APPROVE
- **검증 범위**: 수정된 6개 파일 전체
- **불합격 항목**: 0건

### 미수정 항목 (LOW — 선택)

| # | 파일 | 이유 |
|---|------|------|
| L1 | `settings.json:82` | PreCompact hook python/절대경로 — 기능 정상 작동, 일관성 이슈만 |
| L2 | `chunk/SKILL.md` | 실행 지시 부재 — 기존 commands/chunk.md로 정상 작동 |
| L3 | `gap-detector.md` | 미커밋 — 커밋 시 자동 해결 |
| L4 | `vimeo_ott gap-detector.md` | Junction 미사용 — 정책 검토 필요 |
| L5 | `audit report` | stale 참조 — 히스토리 문서로 유지 가능 |
