# karpathy-guidelines 개선 PRD

## 개요
- **목적**: 외부 레포 `forrestchang/andrej-karpathy-skills` 분석 결과를 바탕으로 로컬 `karpathy-guidelines` 스킬을 현행 agentskills.io 표준에 맞게 개선
- **배경**: 해당 레포(6.9k★)는 Andrej Karpathy의 개발 원칙을 Claude Code 스킬로 구현한 인기 레포이나, 6개 기술 갭(deprecated 형식, 누락 원칙, 잘못된 설치 명령)이 발견됨. 로컬 적용 시 최신 스펙 준수 및 원칙 확장이 필요.
- **범위**: `C:\claude\.claude\skills\karpathy-guidelines\` 디렉토리 내 4개 파일 생성/수정 (SKILL.md, CLAUDE.md, EXAMPLES.md, README.md)

---

## 요구사항

### 기능 요구사항

#### Phase A — 즉시 (1-2일)

1. **SKILL.md 프론트매터 표준화** (agentskills.io 스펙 준수)
   - 현재: `name`, `description` 2개 필드만 존재
   - 목표: 다음 필드 추가
     - `license`: MIT (또는 적합한 라이선스)
     - `compatibility`: claude-code >= 1.0
     - `user-invocable`: false (에이전트 내부 호출 전용)
     - `disable-model-invocation`: false
   - 검증: agentskills.io 스펙 문서 기준으로 필수 필드 충족

2. **deprecated 형식 마이그레이션**
   - 현재: `.claude-plugin/plugin.json` 형식 (구 OMC 플러그인 스펙)
   - 목표: `skills/` 디렉토리 기반 표준 스킬 형식으로 전환
   - 기존 `plugin.json`은 삭제 또는 하위 호환 메모로 대체

3. **README 설치 명령 수정**
   - 현재: `claude plugins add <url>` (존재하지 않는 명령)
   - 목표: Claude Code 실제 설치 방법으로 교체
     - `~/.claude/skills/` 디렉토리에 직접 복사 방식
     - 또는 심볼릭 링크 방식

#### Phase B — 단기 (1-2주)

4. **원칙 5 추가: `Documents over Documentation`**
   - 정의: One document, one truth. No meta-docs.
   - 적용: 문서를 위한 문서 작성 금지, 실제 동작을 설명하는 단일 문서 유지
   - CLAUDE.md에 원칙 5로 추가 (현재 4개 → 5개)

5. **원칙 6 추가: `Context Awareness`**
   - 정의: Know what you know. Know what you don't.
   - 적용: 불확실한 정보를 확실한 것처럼 제시 금지, 지식 경계를 명시적으로 인정
   - CLAUDE.md에 원칙 6으로 추가 (5개 → 6개)

6. **CLAUDE.md 모듈화**
   - core 파일: 6개 원칙 정의 (변경 빈도 낮음)
   - extensions 파일: 언어/프레임워크별 적용 예시 (변경 빈도 높음)
   - EXAMPLES.md: 원칙 5, 6 실전 예시 포함하여 새로 작성

#### Phase C — 중기 (1-2개월)

7. **멀티 에이전트 지원 확장**
   - Claude Code Hooks 통합 (SessionStart, PreToolUse 등)
   - 원칙 위반 자동 감지 hook 추가
   - Agent Teams 환경에서의 원칙 적용 가이드

8. **언어별 확장**
   - Python 특화 가이드 (타입 힌트, docstring 스타일)
   - TypeScript 특화 가이드 (인터페이스 설계, 타입 활용)

---

### 비기능 요구사항

1. **하위 호환성**: 기존 로컬 사용 패턴을 깨지 않아야 함 (SKILL.md 트리거 키워드 유지)
2. **표준 준수**: agentskills.io 스펙 필드 형식 엄수
3. **문서 일관성**: 수정 후 CLAUDE.md의 원칙 번호 체계 일관성 유지
4. **Windows 경로 호환**: `C:\claude\.claude\skills\karpathy-guidelines\` 절대 경로 기준

---

## 구현 범위

### 포함

- `SKILL.md` — agentskills.io 표준 프론트매터 추가 (Phase A-1)
- `CLAUDE.md` — 원칙 5, 6 추가 및 모듈화 (Phase A-2 일부, Phase B-4, 5, 6)
- `EXAMPLES.md` — 원칙 5, 6 실전 예시 포함 신규 작성 (Phase B-6)
- `README.md` — 올바른 설치 방법으로 수정 (Phase A-3)
- deprecated `.claude-plugin/plugin.json` 마이그레이션 (Phase A-2)

### 제외

- Phase C (멀티 에이전트 Hooks 통합, 언어별 확장): 이번 구현 범위 외
- 원본 외부 레포(`forrestchang/andrej-karpathy-skills`) 수정: 로컬 전용
- agentskills.io 마켓플레이스 게시: 비공개 로컬 스킬로만 운용

---

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| SKILL.md 프론트매터 표준화 (Phase A-1) | 완료 | license, compatibility, user-invocable, disable-model-invocation 추가 |
| deprecated plugin.json 마이그레이션 (Phase A-2) | 완료 | skills/ 디렉토리 구조로 전환, plugin.json 참조 제거 |
| README 설치 명령 수정 (Phase A-3) | 완료 | xcopy, 심볼릭 링크, macOS/Linux 3가지 실제 설치 방법 포함 |
| 원칙 5 추가 (Phase B-4) | 완료 | Documents over Documentation — 단일 문서, 단일 진실 |
| 원칙 6 추가 (Phase B-5) | 완료 | Context Awareness — 아는 것과 모르는 것 구분 |
| CLAUDE.md 모듈화 (Phase B-6) | 완료 | 6개 원칙 정의 완료 (확장 예시는 EXAMPLES.md 분리) |
| EXAMPLES.md 신규 작성 (Phase B-6) | 완료 | 6개 원칙 Bad/Good 대비 예시, 원칙 5/6 포함 |
| 멀티 에이전트 Hooks 통합 (Phase C-7) | 예정 (중기) | 이번 범위 외 |
| 언어별 확장 (Phase C-8) | 예정 (중기) | 이번 범위 외 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-02-25 | v1.1 | Phase A+B 구현 완료, 구현 상태 업데이트 | Architect APPROVE (6/6 PASS) |
| 2026-02-25 | v1.0 | 최초 작성 | 외부 레포 정밀 분석 결과 6개 기술 갭 발견 |
