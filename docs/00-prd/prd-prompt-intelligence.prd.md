# Prompt Intelligence PRD

## 개요
- **목적**: history.jsonl 기반 프롬프트 패턴 분석 및 /audit 통합
- **배경**: Claude Code가 `~/.claude/history.jsonl`에 모든 프롬프트를 자동 저장 (10,054건+). 이 기존 데이터를 분석하여 반복 패턴 감지 및 자동화/스킬 전환 후보 제안
- **범위**: Tier 1 통계 분석 (Python) + Tier 2 패턴 분석 (LLM) + /audit Phase 1.7 통합

## Market Context
- **페인포인트**: 반복적인 프롬프트 패턴을 수동으로 인지하기 어려움. 스킬/커맨드 커버리지 갭 파악 불가
- **비즈니스 Impact**: 반복 작업 자동화로 프롬프트 효율성 향상
- **Appetite**: Small 2주

## 요구사항

### 기능 요구사항
1. history.jsonl 파싱 및 프롬프트 추출 (project 필터링 지원)
2. Snapshot+Delta 증분 처리 (워터마크 기반)
3. Tier 1 통계: 카테고리 분류, 키워드 빈도, 스킬 사용 빈도, 시간대 분포, 반복 감지
4. CLI 인터페이스: --stats, --full, --project, --new-prompts, --json
5. /audit Phase 1.7 자동 통합 (기본 실행 시 포함)
6. Tier 2 LLM 분석: analyst 에이전트를 통한 패턴 클러스터링 및 스킬 제안

### 비기능 요구사항
1. 10K+ 건 전체 분석 60초 이내 완료
2. 증분 분석 (Delta) 5초 이내
3. /audit config, /audit quick 실행 시 Phase 1.7 스킵
4. 기존 /audit 동작 회귀 없음

## 아키텍처

데이터 소스: `~/.claude/history.jsonl` (자동 축적)
분석기: `.claude/lib/prompt_analyzer.py`
워터마크: `.claude/data/prompt-watermark.json`
누적 통계: `.claude/data/prompt-stats.json`
캐싱: `.claude/research/audit-prompt-<date>.md`

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| prompt_analyzer.py | 진행 중 | Tier 1 통계 엔진 |
| 워터마크 시스템 | 진행 중 | Snapshot+Delta |
| 테스트 | 진행 중 | 8개 Red 케이스 |
| /audit Phase 1.7 | 진행 중 | SKILL.md + audit.md |

## Changelog

| 날짜 | 버전 | 변경 내용 | 변경 유형 | 결정 근거 |
|------|------|-----------|----------|----------|
| 2026-03-23 | v1.0 | 최초 작성 | - | - |
