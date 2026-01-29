---
name: auto
description: >
  하이브리드 자율 발견 워크플로우. /auto = WHAT Discovery + Loop Control, OMC = HOW Planning + Execution.
  5계층 자율 발견 엔진으로 작업을 탐지하고 OMC에 실행을 위임합니다.
version: 15.0.0

triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "ulw"
    - "ultrawork"
    - "ralph"
  context:
    - "자동화"
    - "자율 완성"
    - "통합 워크플로우"

capabilities:
  - autonomous_discovery
  - loop_control
  - session_management
  - option_routing
  - omc_delegation

model_preference: opus

auto_trigger: true
---

# Auto Skill - 하이브리드 자율 발견 워크플로우

> **v15.0 핵심 철학**: "할 일 없음 → 종료"가 아닌 **"할 일 없음 → 스스로 발견"**

이 스킬은 `.claude/commands/auto.md` 커맨드 파일의 내용을 실행합니다.

## 아키텍처

```
┌────────────────────────────────────────────────────────────────────┐
│                    /auto (v15.0 Hybrid Architecture)               │
├────────────────────────────────────────────────────────────────────┤
│  WHAT Layer (/auto)          │  HOW Layer (OMC)                   │
│  ─────────────────────────   │  ─────────────────────────         │
│  • 5-Tier Discovery Engine   │  • Ralplan (Planning)              │
│  • Context Prediction        │  • Ultrawork (Parallel Exec)       │
│  • Loop Control              │  • Architect Verification          │
│  • Session Management        │  • Agent Orchestration             │
└────────────────────────────────────────────────────────────────────┘
```

## 옵션 라우팅

| 옵션 | 스킬 | 설명 |
|------|------|------|
| `--mockup` | `mockup` | 목업 생성 + ASCII 교체 |
| `--bnw` | (mockup과 함께) | B&W 스타일 + ASCII→이미지 |
| `--gdocs` | `prd-sync` | Google Docs 동기화 |
| `--debate` | `ultimate-debate` | 3AI 토론 |
| `--research` | `research` | 리서치 모드 |

## 사용법

```bash
# 기본 사용
/auto "작업 설명"

# 목업 생성 + ASCII 교체
/auto --mockup --bnw "화면명"

# PRD 동기화 후 목업
/auto --gdocs --mockup --bnw "화면명"

# 자율 발견 모드
/auto
```

## 세션 관리

```bash
/auto status    # 현재 상태
/auto stop      # 중지
/auto resume    # 재개
/auto --restore # 이전 세션 복원
```

## 커맨드 파일 참조

상세 워크플로우: `.claude/commands/auto.md`

## 변경 로그

### v15.0.0 (2026-01-29)

- 하이브리드 아키텍처 도입 (WHAT/HOW 분리)
- 5계층 자율 발견 엔진
- OMC 위임 체계
