# Plan: 서브 프로젝트 스킬 일원화

**Feature**: skill-unification
**Phase**: Plan
**Created**: 2026-02-06

## 문제 정의

12개 서브 프로젝트에 루트 `.claude/skills/`가 물리적으로 복제되어 있어 500개+ SKILL.md가 중복. `08-skill-routing.md` 규칙(심볼릭 링크 사용)이 미적용.

## 현황

| 항목 | 수치 |
|------|------|
| 루트 스킬 | 48개 |
| 서브 프로젝트 | 13개 |
| 복제 SKILL.md | ~500개+ |
| 심볼릭 링크 사용 | 0개 |
| 이중 중첩 | wsoptv_ott 1건 |
| 고유 스킬 보유 | 3개 프로젝트 |

### 고유 스킬

| 프로젝트 | 스킬 | 설명 |
|----------|------|------|
| ebs | daily (v3.0.0) | EBS 데일리 브리핑 (morning-automation Python 도구) |
| ebs | update-slack-list (v2.0.0) | EBS Slack Lists 업체 관리 |
| wsoptv_ott | daily-sync (v1.2.0) | WSOPTV 업체 견적/협상 AI 분석 |
| shorts-generator | ai-subtitle (v1.0.0) | Claude Vision 이미지 분석 자막 |
| shorts-generator | shorts-generator (v2.0.0) | 쇼츠 영상 생성 통합 |

## 전략

1. **심볼릭 링크 전환**: 복제 스킬 삭제 후 루트 심볼릭 링크 연결
2. **고유 스킬 루트 승격**: 서브 프로젝트 고유 스킬을 루트로 이동
3. **ebs daily 통합**: 루트 daily 스킬에 EBS 브리핑 기능 통합

## 실행 계획

### Task 1: wsoptv_ott 이중 중첩 제거
- `C:\claude\wsoptv_ott\.claude\skills\skills\` 디렉토리 삭제
- 42개 중복 SKILL.md 제거

### Task 2: 고유 스킬 루트 승격
- `ebs/daily` → 루트 `daily`에 `--ebs` 서브커맨드로 통합
- `ebs/update-slack-list` → 루트 `C:\claude\.claude\skills\update-slack-list\` 이동
- `wsoptv_ott/daily-sync` → 루트 `C:\claude\.claude\skills\daily-sync\` 이동
- `shorts-generator/ai-subtitle` → 루트 `C:\claude\.claude\skills\ai-subtitle\` 이동
- `shorts-generator/shorts-generator` → 루트 `C:\claude\.claude\skills\shorts-generator\` 이동

### Task 3: 복제 스킬 디렉토리 삭제
- 12개 서브 프로젝트의 `.claude/skills/` 실제 디렉토리 삭제
- 대상: archive-analyzer, automation_aep_csv, ebs, gfx_json, kanban_board, shorts-generator, wsoptv_candidates, wsoptv_mvp, wsoptv_nbatv_clone, wsoptv_ott, youtuber_chatbot, youtuber_vertuber

### Task 4: 심볼릭 링크 생성
- 13개 서브 프로젝트에 루트 `.claude/skills` 심볼릭 링크 생성
- vimeo_ott 포함 (신규)
- 관리자 권한 필요

### Task 5: 검증
- 스킬 목록 일치 확인
- 심볼릭 링크 정상 작동 확인

## 위험 요소

| 위험 | 완화 |
|------|------|
| 관리자 권한 미확보 | PowerShell 관리자 실행 안내 |
| Git submodule 충돌 | submodule 내부는 별도 처리 |
| ebs daily 통합 복잡도 | --ebs 서브커맨드로 최소 침습 |

## 복잡도 점수

| 조건 | 점수 | 근거 |
|------|:----:|------|
| 파일 범위 | 1 | 13개 프로젝트 영향 |
| 아키텍처 | 1 | 심볼릭 링크 구조 변경 |
| 의존성 | 0 | 기존 도구만 사용 |
| 모듈 영향 | 1 | 다수 모듈 영향 |
| 사용자 명시 | 0 | - |
| **총점** | **3/5** | Ralplan 실행 |
